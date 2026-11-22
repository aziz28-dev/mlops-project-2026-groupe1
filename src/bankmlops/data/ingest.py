"""Ingestion : téléchargement du zip officiel UCI et extraction des fichiers bruts.

Le zip UCI est imbriqué : ``bank+marketing.zip`` contient ``bank-additional.zip``, qui contient
``bank-additional/bank-additional-full.csv`` et ``bank-additional/bank-additional-names.txt``.

Usage (stage DVC ``ingest``) : ``python -m bankmlops.data.ingest``
"""

import io
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from bankmlops.config import load_params, resolve_path

INNER_ZIP = "bank-additional.zip"
"""Nom du zip imbriqué dans l'archive UCI."""

MEMBERS = (
    "bank-additional/bank-additional-full.csv",
    "bank-additional/bank-additional-names.txt",
)
"""Fichiers à extraire du zip imbriqué."""


def download_file(url: str, dest: Path, timeout: int = 60) -> Path:
    """Télécharge ``url`` vers ``dest``.

    Args:
        url: Adresse du fichier (``https://`` ou ``file://`` pour les tests).
        dest: Chemin de destination.
        timeout: Délai maximal de connexion, en secondes.

    Returns:
        Le chemin du fichier téléchargé.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=timeout) as response, dest.open("wb") as f:
        shutil.copyfileobj(response, f)
    return dest


def extract_raw_files(zip_path: Path, out_dir: Path) -> list[Path]:
    """Extrait le CSV complet et sa documentation depuis l'archive UCI imbriquée.

    Args:
        zip_path: Archive UCI ``bank+marketing.zip``.
        out_dir: Dossier de sortie (``data/raw``). Les fichiers y sont posés à plat.

    Returns:
        Les chemins des fichiers extraits.

    Raises:
        KeyError: Si le zip imbriqué ou un fichier attendu est absent de l'archive.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    with zipfile.ZipFile(zip_path) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read(INNER_ZIP))) as inner:
            for member in MEMBERS:
                target = out_dir / Path(member).name
                target.write_bytes(inner.read(member))
                extracted.append(target)
    return extracted


def main() -> None:
    """Télécharge l'archive UCI et dépose les fichiers bruts dans ``data.raw_dir``."""
    params = load_params()["data"]
    out_dir = resolve_path(params["raw_dir"])
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = download_file(params["source_url"], Path(tmp) / "bank_marketing.zip")
        for path in extract_raw_files(zip_path, out_dir):
            print(f"Extrait : {path} ({path.stat().st_size} octets)")


if __name__ == "__main__":
    main()
