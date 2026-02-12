from app.core.config import ALLOWED_RANKS
from app.utils.parsing import build_raw_taxon_index, build_rank_filtered_taxon_set
from app.utils.sorting import dedupe_and_sort_lineages, propagate_counts_and_build_children, sort_hits_by_evalue

async def process_tsv_dataset(file):
    file = await file.read()
    file_lines = (file.decode("utf-8")[:-1]).split("\n")
    header_line = file_lines[0]
    lines = file_lines[1:]
    
    raw_tax_set, raw_lns, e_value_enabled, fasta_enabled = build_raw_taxon_index(header_line, lines)
    tax_set, lns = build_rank_filtered_taxon_set(raw_tax_set, raw_lns, e_value_enabled, fasta_enabled)
    lns = dedupe_and_sort_lineages(lns)
    tax_set = propagate_counts_and_build_children(lns, tax_set)
    tax_set = sort_hits_by_evalue(tax_set)

    return {"lns": lns, "taxSet": tax_set, "eValueEnabled": e_value_enabled, "fastaEnabled": fasta_enabled, "rankPatternFull": ALLOWED_RANKS}

async def process_faa_dataset(file):
    file = await file.read()
    fasta_file = (file.decode("utf-8")[:-1]).split(">")
    
    seq_dict = {}
    for seq in fasta_file:
        seq2list = seq.split("\n")
        if len(seq2list) > 1:
            seq_name = seq2list[0]
            seq_body = seq2list[1].replace("*", "")
            seq_dict[seq_name] = seq_body

    return {"faaObj": seq_dict}