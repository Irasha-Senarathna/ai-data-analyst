"""Build the warehouse in a temp file and swap it in only when the build succeeds.

The API holds read-only connections to the warehouse file, so the pipeline never
writes to it in place (see docs/architecture.md, D2).

The temp file lives in a `.build/` folder with the *same file name*, because
DuckDB names the database after the file stem and views store that name.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def temp_path_for(final: Path) -> Path:
    return final.parent / ".build" / final.name


def remove_with_wal(path: Path) -> None:
    path.unlink(missing_ok=True)
    path.with_name(f"{path.name}.wal").unlink(missing_ok=True)


@contextmanager
def atomic_build(final: Path) -> Iterator[Path]:
    """Yield an empty temp path; on success it replaces `final`, on error it is deleted."""
    tmp = temp_path_for(final)
    remove_with_wal(tmp)
    tmp.parent.mkdir(parents=True, exist_ok=True)
    try:
        yield tmp
        wal = tmp.with_name(f"{tmp.name}.wal")
        if wal.exists():
            raise RuntimeError(f"{tmp} still has an open write-ahead log; close it before swapping")
        tmp.replace(final)
    finally:
        remove_with_wal(tmp)
