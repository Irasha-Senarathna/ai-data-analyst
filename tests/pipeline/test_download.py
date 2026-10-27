from pathlib import Path

import httpx
import pytest

from pipeline.download import DownloadError, download_file, sha256_of


def make_client(body: bytes, calls: list[httpx.Request], status: int = 200) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(status, content=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_downloads_file_and_writes_checksum_sidecar(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []
    dest = tmp_path / "data.zip"

    result = download_file(make_client(b"hello", calls), "https://example.test/data.zip", dest)

    assert dest.read_bytes() == b"hello"
    assert result.skipped is False
    assert result.sha256 == sha256_of(dest)
    assert Path(f"{dest}.sha256").read_text().splitlines()[0] == result.sha256
    assert len(calls) == 1


def test_changed_url_downloads_again(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []
    client = make_client(b"hello", calls)
    dest = tmp_path / "data.json"

    download_file(client, "https://example.test/data?timezone=old", dest)
    result = download_file(client, "https://example.test/data?timezone=auto", dest)

    assert result.skipped is False
    assert len(calls) == 2


def test_second_run_skips_download(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []
    client = make_client(b"hello", calls)
    dest = tmp_path / "data.zip"

    download_file(client, "https://example.test/data.zip", dest)
    second = download_file(client, "https://example.test/data.zip", dest)

    assert second.skipped is True
    assert len(calls) == 1


def test_corrupted_file_is_downloaded_again(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []
    client = make_client(b"hello", calls)
    dest = tmp_path / "data.zip"
    download_file(client, "https://example.test/data.zip", dest)

    dest.write_bytes(b"truncat")
    result = download_file(client, "https://example.test/data.zip", dest)

    assert result.skipped is False
    assert dest.read_bytes() == b"hello"
    assert len(calls) == 2


def test_http_error_raises_and_leaves_no_partial_file(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []
    dest = tmp_path / "data.zip"

    with pytest.raises(DownloadError):
        download_file(make_client(b"nope", calls, status=500), "https://example.test/x", dest)

    assert list(tmp_path.iterdir()) == []


def test_auth_is_sent_when_given(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []

    download_file(
        make_client(b"x", calls),
        "https://example.test/x",
        tmp_path / "x",
        auth=("user", "secret"),
    )

    assert calls[0].headers["authorization"].startswith("Basic ")
