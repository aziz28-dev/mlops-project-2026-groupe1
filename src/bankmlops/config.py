"""Chargement de ``params.yaml`` et résolution des chemins du projet.

``params.yaml`` est la source unique des paramètres (split, modèles, seuils de drift).
Le code les lit ici, ``dvc.yaml`` les déclare dans ses stages : aucune valeur en dur ailleurs.
"""

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
"""Racine du dépôt (dossier qui contient ``params.yaml``)."""

PARAMS_PATH: Path = PROJECT_ROOT / "params.yaml"
"""Chemin par défaut du fichier de paramètres."""


def load_params(path: Path | str = PARAMS_PATH) -> dict[str, Any]:
    """Charge le fichier de paramètres YAML.

    Args:
        path: Chemin du fichier YAML. Par défaut, ``params.yaml`` à la racine du projet.

    Returns:
        Les paramètres sous forme de dictionnaire imbriqué.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        ValueError: Si le fichier ne contient pas un dictionnaire YAML.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Fichier de paramètres introuvable : {path}")

    with path.open(encoding="utf-8") as f:
        params = yaml.safe_load(f)

    if not isinstance(params, dict):
        kind = type(params).__name__
        raise ValueError(f"{path} doit contenir un dictionnaire YAML, reçu : {kind}")
    return params


def resolve_path(relative: Path | str) -> Path:
    """Transforme un chemin relatif à la racine du projet en chemin absolu.

    Permet de lancer le code depuis n'importe quel dossier (tests, Prefect, Docker).

    Args:
        relative: Chemin relatif à la racine, par exemple ``"data/raw/bank-additional-full.csv"``.

    Returns:
        Le chemin absolu correspondant.
    """
    return PROJECT_ROOT / relative
