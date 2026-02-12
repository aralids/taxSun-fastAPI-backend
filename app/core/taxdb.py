import os
import time
import tarfile
import urllib.request
from pathlib import Path
from functools import lru_cache

import taxopy

DATA_DIR = Path("data/taxonomy")
NODES = DATA_DIR / "nodes.dmp"
NAMES = DATA_DIR / "names.dmp"
MERGED = DATA_DIR / "merged.dmp"

TAXDUMP_URL = "https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz"
TAXDUMP_ARCHIVE = DATA_DIR / "taxdump.tar.gz"
LOCKFILE = DATA_DIR / ".taxdump.lock"


def _missing_taxdump_files() -> list[str]:
    return [p.name for p in (NODES, NAMES, MERGED) if not p.exists()]


def _acquire_lock(timeout_seconds: int = 300) -> None:
    """
    Create a lock file to prevent concurrent downloads/extractions,
    e.g., due to uvicorn --reload spawning processes.

    This is a simple best-effort lock for local dev.
    """
    start = time.time()
    while True:
        try:
            # O_EXCL ensures it fails if file already exists
            fd = os.open(str(LOCKFILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return
        except FileExistsError:
            if time.time() - start > timeout_seconds:
                raise RuntimeError(
                    f"Timeout waiting for taxonomy download lock: {LOCKFILE}"
                )
            time.sleep(0.5)


def _release_lock() -> None:
    try:
        LOCKFILE.unlink(missing_ok=True)
    except Exception:
        # best-effort; don’t crash app shutdown because of lock cleanup
        pass


def _download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Download atomically: write to temp then rename
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        f.write(r.read())
    tmp.replace(dest)


def _extract_needed_files(archive_path: Path, target_dir: Path) -> None:
    needed = {"nodes.dmp", "names.dmp", "merged.dmp"}
    with tarfile.open(archive_path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if Path(m.name).name in needed]
        tar.extractall(path=target_dir, members=members)

    # Some tarballs include paths; normalize to flat files in target_dir
    for name in needed:
        candidates = list(target_dir.rglob(name))
        if not candidates:
            continue
        # Move the first occurrence to the expected path
        src = candidates[0]
        dst = target_dir / name
        if src.resolve() != dst.resolve():
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.replace(dst)


def ensure_taxdump_present() -> None:
    """
    Ensure required NCBI taxonomy dump files exist in data/taxonomy.
    Downloads + extracts them if missing.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    missing = _missing_taxdump_files()
    if not missing:
        return

    _acquire_lock()
    try:
        # Re-check after acquiring lock (another process may have finished)
        missing = _missing_taxdump_files()
        if not missing:
            return

        print(f"[taxSun] Missing taxonomy files: {missing}. Downloading taxdump...")

        _download_file(TAXDUMP_URL, TAXDUMP_ARCHIVE)
        _extract_needed_files(TAXDUMP_ARCHIVE, DATA_DIR)

        # Final check
        missing = _missing_taxdump_files()
        if missing:
            raise RuntimeError(
                f"Download/extract finished but files are still missing: {missing}"
            )

        # optional: keep archive to avoid re-download; or delete it:
        # TAXDUMP_ARCHIVE.unlink(missing_ok=True)

        print("[taxSun] Taxonomy files ready.")
    finally:
        _release_lock()


@lru_cache(maxsize=1)
def get_taxdb() -> taxopy.TaxDb:
    """
    Lazy, one-time initialization per process.
    Safe for requests: the DB is created once and reused.
    """
    ensure_taxdump_present()

    print(f"[taxSun] Using local taxonomy database from {DATA_DIR}")
    return taxopy.TaxDb(
        nodes_dmp=str(NODES),
        names_dmp=str(NAMES),
        merged_dmp=str(MERGED),
    )
