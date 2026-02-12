import taxopy
from pathlib import Path
from functools import lru_cache

DATA_DIR = Path("data/taxonomy")
NODES = DATA_DIR / "nodes.dmp"
NAMES = DATA_DIR / "names.dmp"
MERGED = DATA_DIR / "merged.dmp"


def _assert_taxdump_present() -> None:
    missing = [p.name for p in (NODES, NAMES, MERGED) if not p.exists()]
    if missing:
        raise RuntimeError(
            f"Missing taxonomy files in {DATA_DIR}: {missing}. "
            "In production, these should be baked into the Docker image."
        )


@lru_cache(maxsize=1)
def get_taxdb() -> taxopy.TaxDb:
    """
    Lazy, one-time initialization per process.
    Safe for requests: the DB is created once and reused.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _assert_taxdump_present()

    print(f"Using local taxonomy database from {DATA_DIR}")
    return taxopy.TaxDb(
        nodes_dmp=str(NODES),
        names_dmp=str(NAMES),
        merged_dmp=str(MERGED),
    )
