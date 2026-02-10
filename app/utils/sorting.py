import copy

def sort_n_uniquify(lns):
    lns.sort(key=sort_func)

    newlns = copy.deepcopy(lns)
    for i in reversed(range(1, len(lns))):
        if (newlns[i] == newlns[i-1]):
            newlns = newlns[:i] + newlns[i+1:]

    return newlns

def sort_func(ln):
    str = ""
    for i in range(0, len(ln)):
        str += ln[i][1]
    return str

def correct_tot_counts(lns, tax_set):
    for i in range(0, len(lns)):
        child = lns[i][-1][1] + " " + lns[i][-1][0]
        tax_set[child]["lnIndex"] = len(lns[i]) - 1
        for j in reversed(range(1, len(lns[i]) - 1)):
            name = lns[i][j][1]
            rank = lns[i][j][0]
            taxon = name + " " + rank
            tax_set[taxon]["totCount"] += tax_set[child]["unaCount"]
            tax_set[taxon]["children"] += [child]
            if len(tax_set[taxon]["directChildren"]) > 0:
                if tax_set[taxon]["directChildren"][-1] != lns[i][j+1][1] + " " + lns[i][j+1][0]:
                    tax_set[taxon]["directChildren"] += [lns[i][j+1][1] + " " + lns[i][j+1][0]]
            else:
                tax_set[taxon]["directChildren"] += [lns[i][j+1][1] + " " + lns[i][j+1][0]]
            tax_set[taxon]["lnIndex"] = j
        if child != "root root":
            tax_set["root root"]["totCount"] += tax_set[child]["unaCount"]
            tax_set["root root"]["children"] += [child]
    return tax_set

def sort_evalues(tax_set):
    for name, obj in tax_set.items():
        if "eValues" in obj and "fastaHeaders" in obj:
            srtd = sorted(zip(obj["eValues"], obj["fastaHeaders"], obj["geneNames"], obj["names"]), key=lambda pair: pair[0])
            obj["eValues"] = [e for e,f,g,n in srtd]
            obj["fastaHeaders"] = [f for e,f,g,n in srtd]
            obj["geneNames"] = [g for e,f,g,n in srtd]
            obj["names"] = [n for e,f,g,n in srtd]
        elif "eValues" in obj:
            srtd = sorted(zip(obj["eValues"], obj["geneNames"], obj["names"]), key=lambda pair: pair[0])
            obj["eValues"] = [e for e,g,n in srtd]
            obj["geneNames"] = [g for e,g,n in srtd]
            obj["names"] = [n for e,g,n in srtd]   
    return tax_set