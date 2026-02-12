import taxopy
from app.core.taxdb import taxdb

def resolve_id_by_name(taxon_name):
    taxid = taxopy.taxid_from_name(taxon_name, taxdb)
    print("taxid: ", taxid)
    return {"taxID": taxid[0]}