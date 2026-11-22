import io
import zipfile
from pathlib import Path

import pytest

from bankmlops.data.ingest import INNER_ZIP, MEMBERS, download_file, extract_raw_files


def make_fake_uci_zip(path: Path, members: tuple[str, ...] = MEMBERS) -> Path:
    """Construit une archive imbriquée qui imite bank+marketing.zip (sans réseau)."""
    inner_buffer = io.BytesIO()
    with zipfile.ZipFile(inner_buffer, "w") as inner:
        for member in members:
            inner.writestr(member, f"contenu de {member}")
    with zipfile.ZipFile(path, "w") as outer:
        outer.writestr(INNER_ZIP, inner_buffer.getvalue())
        outer.writestr("bank.zip", b"autre archive ignoree")
    return path


def test_extract_raw_files_flattens_expected_members(tmp_path: Path):
    zip_path = make_fake_uci_zip(tmp_path / "uci.zip")
    out_dir = tmp_path / "raw"

    extracted = extract_raw_files(zip_path, out_dir)

    assert [p.name for p in extracted] == [
        "bank-additional-full.csv",
        "bank-additional-names.txt",
    ]
    assert (out_dir / "bank-additional-full.csv").read_text() == f"contenu de {MEMBERS[0]}"


def test_extract_raw_files_missing_member_raises(tmp_path: Path):
    zip_path = make_fake_uci_zip(tmp_path / "uci.zip", members=(MEMBERS[0],))
    with pytest.raises(KeyError):
        extract_raw_files(zip_path, tmp_path / "raw")


def test_download_file_from_local_uri(tmp_path: Path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"\x00\x01donnees")

    dest = download_file(source.as_uri(), tmp_path / "sub" / "dest.bin")

    assert dest.read_bytes() == b"\x00\x01donnees"
