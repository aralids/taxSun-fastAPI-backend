from app.core.config import rankPatternFull
from app.utils.parsing import calc_raw_tax_set, calc_tax_set
from app.utils.sorting import sort_n_uniquify, correct_tot_counts, sort_evalues

async def process_tsv_dataset(file):
    file = await file.read()
    file_lines = (file.decode("utf-8")[:-1]).split("\n")
    header_line = file_lines[0]
    lines = file_lines[1:]
    
    raw_tax_set, raw_lns, e_value_enabled, fasta_enabled = calc_raw_tax_set(header_line, lines)
    print("size: ", len(lines))
    id_lst = []
    for obj in raw_tax_set.values():
        if not (obj["taxID"] in id_lst):
            id_lst += [obj["taxID"]]
    tax_set, lns = calc_tax_set(raw_tax_set, raw_lns, e_value_enabled, fasta_enabled)
    lns = sort_n_uniquify(lns)
    tax_set = correct_tot_counts(lns, tax_set)
    tax_set = sort_evalues(tax_set)

    return {"lns": lns, "taxSet": tax_set, "eValueEnabled": e_value_enabled, "fastaEnabled": fasta_enabled, "rankPatternFull": rankPatternFull}

async def process_faa_dataset(file):
    file = await file.read()
    fasta_file = (file.decode("utf-8")[:-1]).split(">")
    dict = {}
    for seq in fasta_file:
        seq2list = seq.split("\n")
        if len(seq2list) > 1:
            seq_name = seq2list[0]
            seq_body = seq2list[1].replace("*", "")
            dict[seq_name] = seq_body
    return {"faaObj": dict}