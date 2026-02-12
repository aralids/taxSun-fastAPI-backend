import taxopy
from pathlib import Path

DATA_DIR = Path("data/taxonomy")
NODES = DATA_DIR / "nodes.dmp"
NAMES = DATA_DIR / "names.dmp"
MERGED = DATA_DIR / "merged.dmp"

def init_taxdb() -> taxopy.TaxDb:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # If all required files exist → use local DB
    if NODES.exists() and NAMES.exists() and MERGED.exists():
        print("Using local taxonomy database.")
        return taxopy.TaxDb(
            nodes_dmp=str(NODES),
            names_dmp=str(NAMES),
            merged_dmp=str(MERGED),
        )

    # Otherwise download and cache automatically
    print("Local taxonomy DB not found. Downloading...")
    db = taxopy.TaxDb()

    # taxopy stores downloaded files internally; optionally copy them:
    # (depends on taxopy version, sometimes not necessary)

    return db


# Create singleton instance
taxdb = taxopy.TaxDb()
