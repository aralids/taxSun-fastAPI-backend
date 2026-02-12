import taxopy
from pathlib import Path
from typing import Optional
from threading import Lock

DATA_DIR = Path("data/taxonomy")
NODES = DATA_DIR / "nodes.dmp"
NAMES = DATA_DIR / "names.dmp"
MERGED = DATA_DIR / "merged.dmp"

_taxdb: Optional[taxopy.TaxDb] = None
_taxdb_lock = Lock()


def init_taxdb() -> taxopy.TaxDb:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if NODES.exists() and NAMES.exists() and MERGED.exists():
        print("Using local taxonomy database.")
        return taxopy.TaxDb(
            nodes_dmp=str(NODES),
            names_dmp=str(NAMES),
            merged_dmp=str(MERGED),
        )

    print("Local taxonomy DB not found. Downloading...")
    return taxopy.TaxDb()


def get_taxdb() -> taxopy.TaxDb:
    global _taxdb

    # Fast path (already initialized)
    if _taxdb is not None:
        return _taxdb

    # Slow path (initialize once)
    with _taxdb_lock:
        if _taxdb is None:
            _taxdb = init_taxdb()

    return _taxdb
