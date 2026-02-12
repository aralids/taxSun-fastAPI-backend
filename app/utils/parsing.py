from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

import taxopy

from app.core.config import ALLOWED_RANKS
from app.core.taxdb import get_taxdb


TaxonKey = str
Lineage = List[List[str]]  # list of [rank, name] pairs
TaxonEntry = Dict[str, Any]
TaxonSet = Dict[TaxonKey, TaxonEntry]


def build_raw_taxon_index(
    header_line: str,
    lines: List[str],
) -> Tuple[TaxonSet, List[Lineage], bool, bool]:
    """
    Parse TSV-like input lines and build a raw taxon index.

    Expected columns per line:
      0: gene_name (string)
      1: taxID (string; "NA" or "" will be mapped to root)
      2: e-value (optional)
      3: fasta header (optional)

    Returns:
      raw_taxa:
        A dict keyed by "<name> <rank>" with rawCounts/totCounts and collected metadata.
      raw_lineages:
        A list of full taxonomic paths (each path is [ [rank,name], ... ]) for each *new* taxID encountered.
      has_evalues:
        Whether the input appears to include e-values.
      has_fasta_headers:
        Whether the input appears to include fasta headers.
    """
    taxdb = get_taxdb()

    has_evalues = "value" in header_line.lower()
    has_fasta_headers = "fasta" in header_line.lower()

    # We key nodes by "name rank" everywhere in your pipeline.
    root_key = "root root"
    raw_taxa: TaxonSet = {
        root_key: {
            "taxID": "1",
            "rawCount": 0,
            "totCount": 0,
            "name": "root",
            "rank": "root",
            "lnIndex": 0,
            "names": [],
            "geneNames": [],
            "eValues": [],
            "fastaHeaders": [],
            "children": [],
            "directChildren": [],
        }
    }

    # Map taxID -> "<name> <rank>" key to avoid re-creating nodes.
    taxid_to_key: Dict[str, TaxonKey] = {"1": root_key}

    # Store lineages only for newly discovered taxIDs (your later step uses this list).
    raw_lineages: List[Lineage] = [[["root", "root"]]]

    for line in lines:
        cols = [c.replace("\r", "") for c in line.split("\t")]

        gene_name = cols[0] if len(cols) > 0 else ""
        tax_id = cols[1] if len(cols) > 1 else "1"

        e_value = cols[2] if len(cols) > 2 else ""
        fasta_header = cols[3] if len(cols) > 3 else ""

        if tax_id in ("NA", ""):
            tax_id = "1"

        # New taxon
        if tax_id not in taxid_to_key:
            taxon = taxopy.Taxon(int(tax_id), taxdb)
            name = taxon.name
            rank = taxon.rank
            key = f"{name} {rank}"

            # taxopy provides rank->name; we convert to [rank,name] pairs and reverse to get root->... order.
            lineage_rank_name = taxon.rank_name_dictionary
            rank_name_path: Lineage = [["root", "root"]] + [[k, v] for k, v in lineage_rank_name.items()][::-1]

            # Ensure leaf is included
            if not (rank_name_path[-1][0] == rank and rank_name_path[-1][1] == name):
                rank_name_path.append([rank, name])

            raw_taxa[key] = {
                "taxID": tax_id,
                "rawCount": 1,
                "totCount": 1,
                "name": name,
                "rank": rank,
                "names": [key],
                "geneNames": [gene_name],
                "children": [],
                "directChildren": [],
            }

            if has_evalues:
                raw_taxa[key]["eValues"] = [float(e_value)] if e_value != "" else [1.0]

            if has_fasta_headers:
                raw_taxa[key]["fastaHeaders"] = [fasta_header] if fasta_header != "" else [None]

            taxid_to_key[tax_id] = key
            raw_lineages.append(rank_name_path)
            continue

        # Existing taxon
        key = taxid_to_key[tax_id]
        raw_taxa[key]["totCount"] += 1
        raw_taxa[key]["rawCount"] += 1
        raw_taxa[key]["geneNames"].append(gene_name)
        raw_taxa[key]["names"].append(key)

        if has_evalues:
            raw_taxa[key]["eValues"].append(float(e_value) if e_value != "" else 1.0)

        if has_fasta_headers:
            raw_taxa[key]["fastaHeaders"].append(fasta_header if fasta_header != "" else None)

    return raw_taxa, raw_lineages, has_evalues, has_fasta_headers


def build_rank_filtered_taxon_set(
    raw_taxa: TaxonSet,
    raw_lineages: List[Lineage],
    has_evalues: bool,
    has_fasta_headers: bool,
) -> Tuple[TaxonSet, List[Lineage]]:
    """
    Build a taxon set filtered to `rankPatternFull` (allowed ranks), while *inheriting* counts upward.

    Core idea:
      - Some lineages include ranks you don't want to display.
      - The "leaf" (original hit taxon) may be at a filtered-out rank.
      - We propagate that leaf's counts + metadata upward until we hit the next kept rank.
      - We also prune those filtered ranks from the lineage paths.

    Returns:
      tax_set: dict of taxa restricted to allowed ranks (existing + created intermediate nodes).
      filtered_lineages: lineage paths with filtered-out ranks removed.
    """
    allowed_ranks = ALLOWED_RANKS

    existing_taxa: TaxonSet = {}
    created_taxa: TaxonSet = {}
    dropped_taxa: TaxonSet = {}

    filtered_lineages = copy.deepcopy(raw_lineages)

    # Iterate lineages from bottom-up to propagate leaf info upward.
    for i in reversed(range(len(raw_lineages))):
        lineage = raw_lineages[i]

        inherited_key: str = ""
        inherited_count: int = 0
        inherited_gene_names: List[str] = []
        inherited_evalues: List[float] = []
        inherited_fasta_headers: List[str | None] = []

        for j in reversed(range(len(lineage))):
            rank, name = lineage[j][0], lineage[j][1]
            key = f"{name} {rank}"

            if rank in allowed_ranks:
                # If node exists in raw_taxa, copy it once into existing_taxa.
                if key in raw_taxa:
                    if key not in existing_taxa:
                        existing_taxa[key] = raw_taxa[key]
                        existing_taxa[key]["unaCount"] = raw_taxa[key]["rawCount"]

                    # Push inherited counts/metadata into this kept rank node.
                    if inherited_count > 0:
                        existing_taxa[key]["unaCount"] += inherited_count
                        existing_taxa[key]["totCount"] += inherited_count
                        existing_taxa[key]["geneNames"] += inherited_gene_names
                        existing_taxa[key]["names"] += [inherited_key] * inherited_count

                        if has_evalues:
                            existing_taxa[key]["eValues"] += inherited_evalues
                            inherited_evalues = []

                        if has_fasta_headers:
                            existing_taxa[key]["fastaHeaders"] += inherited_fasta_headers
                            inherited_fasta_headers = []

                        inherited_key = ""
                        inherited_gene_names = []
                        inherited_count = 0

                # Node does not exist in raw_taxa → create it if needed (intermediate kept rank).
                else:
                    if key not in created_taxa:
                        created_taxa[key] = {
                            "taxID": "",
                            "children": [],
                            "directChildren": [],
                            "unaCount": 0,
                            "rawCount": 0,
                            "totCount": 0,
                            "name": name,
                            "rank": rank,
                            "names": [],
                            "geneNames": [],
                        }
                        if has_evalues:
                            created_taxa[key]["eValues"] = []
                        if has_fasta_headers:
                            created_taxa[key]["fastaHeaders"] = []

                    if inherited_count > 0:
                        created_taxa[key]["unaCount"] += inherited_count
                        created_taxa[key]["totCount"] += inherited_count
                        created_taxa[key]["geneNames"] += inherited_gene_names
                        created_taxa[key]["names"] += [inherited_key] * inherited_count

                        if has_evalues:
                            created_taxa[key]["eValues"] += inherited_evalues
                            inherited_evalues = []

                        if has_fasta_headers:
                            created_taxa[key]["fastaHeaders"] += inherited_fasta_headers
                            inherited_fasta_headers = []

                        inherited_key = ""
                        inherited_gene_names = []
                        inherited_count = 0

            else:
                # Filtered-out rank: prune it from the lineage and (if it's the leaf) inherit its data upward.
                if j == len(lineage) - 1:
                    # Leaf taxon at a disallowed rank → inherit its counts/metadata upward.
                    dropped_taxa[key] = raw_taxa[key]
                    inherited_key = key
                    inherited_gene_names = raw_taxa[key]["geneNames"]
                    inherited_count = raw_taxa[key]["rawCount"]

                    if has_evalues:
                        inherited_evalues = raw_taxa[key]["eValues"]
                    if has_fasta_headers:
                        inherited_fasta_headers = raw_taxa[key]["fastaHeaders"]

                    # Remove leaf and everything after it (there is nothing after leaf, but keeps your old intent)
                    filtered_lineages[i] = filtered_lineages[i][:j]
                else:
                    # Middle rank filtered out → remove just that element.
                    filtered_lineages[i] = filtered_lineages[i][:j] + filtered_lineages[i][j + 1 :]

    tax_set: TaxonSet = {**created_taxa, **existing_taxa}
    return tax_set, filtered_lineages
