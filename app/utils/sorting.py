from __future__ import annotations

import copy
from typing import Any, Dict, List, Sequence, Tuple


Lineage = List[List[str]]  # list of [rank, name]
TaxonKey = str
TaxonEntry = Dict[str, Any]
TaxonSet = Dict[TaxonKey, TaxonEntry]


def dedupe_and_sort_lineages(lineages: List[Lineage]) -> List[Lineage]:
    """
    Sort lineage paths deterministically and remove exact duplicates.

    Sorting key is a concatenation of taxon names along the lineage.
    Duplicates are removed only if two neighboring lineages are identical after sorting.
    """
    # NOTE: original code sorts in-place; we keep that behavior but return a new list.
    lineages.sort(key=_lineage_sort_key)

    unique = copy.deepcopy(lineages)
    for i in reversed(range(1, len(unique))):
        if unique[i] == unique[i - 1]:
            unique = unique[:i] + unique[i + 1 :]

    return unique


def _lineage_sort_key(lineage: Lineage) -> str:
    """
    Sorting key for a lineage.

    Original behavior: concatenates names (not ranks) in order.
    """
    # Avoid shadowing built-in "str" like the original did.
    return "".join(node[1] for node in lineage)


def propagate_counts_and_build_children(
    lineages: Sequence[Lineage],
    tax_set: TaxonSet,
) -> TaxonSet:
    """
    Propagate unaCount from each lineage's leaf taxon up to its ancestors.

    For each lineage:
      - leaf = last element in lineage
      - For each ancestor node (excluding root and leaf):
          * tax_set[ancestor]["totCount"] += tax_set[leaf]["unaCount"]
          * tax_set[ancestor]["children"] appends the leaf key
          * tax_set[ancestor]["directChildren"] appends the next node in the path (deduped)
          * tax_set[ancestor]["lnIndex"] is updated to the node's index within the lineage
      - Additionally, root gets totCount + children for every non-root leaf.

    This mutates `tax_set` (same as the original) and returns it for convenience.
    """
    for ln in lineages:
        # Leaf (child) taxon key: "<name> <rank>"
        leaf_key = f"{ln[-1][1]} {ln[-1][0]}"
        tax_set[leaf_key]["lnIndex"] = len(ln) - 1

        # Walk ancestors bottom-up, skipping:
        # - index 0 (root)
        # - last index (leaf)
        for j in reversed(range(1, len(ln) - 1)):
            rank, name = ln[j][0], ln[j][1]
            ancestor_key = f"{name} {rank}"

            tax_set[ancestor_key]["totCount"] += tax_set[leaf_key]["unaCount"]
            tax_set[ancestor_key]["children"].append(leaf_key)

            # direct child is the next node down the path
            next_key = f"{ln[j + 1][1]} {ln[j + 1][0]}"
            direct_children = tax_set[ancestor_key]["directChildren"]

            if len(direct_children) == 0 or direct_children[-1] != next_key:
                direct_children.append(next_key)

            tax_set[ancestor_key]["lnIndex"] = j

        # Update root totals for every non-root leaf
        if leaf_key != "root root":
            tax_set["root root"]["totCount"] += tax_set[leaf_key]["unaCount"]
            tax_set["root root"]["children"].append(leaf_key)

    return tax_set


def sort_hits_by_evalue(tax_set: TaxonSet) -> TaxonSet:
    """
    For each taxon that has e-value data, sort hit-related arrays by ascending e-value.

    Keeps parallel arrays aligned:
      - eValues
      - fastaHeaders (if present)
      - geneNames
      - names
    """
    for _, obj in tax_set.items():
        if "eValues" in obj and "fastaHeaders" in obj:
            sorted_rows = sorted(
                zip(obj["eValues"], obj["fastaHeaders"], obj["geneNames"], obj["names"]),
                key=lambda row: row[0],
            )
            obj["eValues"] = [e for e, f, g, n in sorted_rows]
            obj["fastaHeaders"] = [f for e, f, g, n in sorted_rows]
            obj["geneNames"] = [g for e, f, g, n in sorted_rows]
            obj["names"] = [n for e, f, g, n in sorted_rows]

        elif "eValues" in obj:
            sorted_rows = sorted(
                zip(obj["eValues"], obj["geneNames"], obj["names"]),
                key=lambda row: row[0],
            )
            obj["eValues"] = [e for e, g, n in sorted_rows]
            obj["geneNames"] = [g for e, g, n in sorted_rows]
            obj["names"] = [n for e, g, n in sorted_rows]

    return tax_set
