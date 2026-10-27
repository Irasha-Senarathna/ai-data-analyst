"""Idempotent file downloads.

A finished download writes a `<file>.sha256` sidecar holding the checksum and
the source URL. A later run skips the download when the file still matches the
checksum and the URL is the same, and downloads again when the file is missing,
truncated or changed, or when the URL (e.g. its query parameters) changed.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path

import httpx

CHUNK_SIZE = 1024 * 1024


class DownloadError(RuntimeError):
    """The server did not return the file."""


@dataclass(frozen=True)
class DownloadResult:
    path: Path
    skipped: bool
    sha256: str


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sidecar_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.sha256")


def is_complete(path: Path, url: str) -> bool:
    sidecar = sidecar_path(path)
    if not path.is_file() or not sidecar.is_file():
        return False
    return sidecar.read_text().splitlines() == [sha256_of(path), url]


def download_file(
    client: httpx.Client,
    url: str,
    dest: Path,
    *,
    auth: tuple[str, str] | None = None,
) -> DownloadResult:
    """Download `url` to `dest` unless a verified copy is already there."""
    if is_complete(dest, url):
        return DownloadResult(dest, skipped=True, sha256=sha256_of(dest))

    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(f"{dest.name}.part")
    try:
        with client.stream("GET", url, auth=auth, follow_redirects=True) as response:
            if response.status_code != httpx.codes.OK:
                raise DownloadError(f"GET {url} returned HTTP {response.status_code}")
            with partial.open("wb") as file:
                for chunk in response.iter_bytes(CHUNK_SIZE):
                    file.write(chunk)
        partial.replace(dest)
    finally:
        partial.unlink(missing_ok=True)

    checksum = sha256_of(dest)
    sidecar_path(dest).write_text(f"{checksum}\n{url}\n")
    return DownloadResult(dest, skipped=False, sha256=checksum)
