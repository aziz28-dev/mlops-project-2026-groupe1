"""Validation du schéma des données brutes.

Le schéma attendu vient de ``bank-additional-names.txt`` (section 7). En cas d'écart, une
``DataValidationError`` explicite est levée, ce qui fait échouer le stage DVC ``validate``.

Usage (stage DVC ``validate``) : ``python -m bankmlops.data.validate``
"""

import json
from typing import Any

import pandas as pd

from bankmlops.config import load_params, resolve_path

NUMERIC_COLUMNS: tuple[str, ...] = (
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
)
"""Colonnes numériques du fichier brut."""

CATEGORICAL_COLUMNS: tuple[str, ...] = (
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
)
"""Colonnes catégorielles du fichier brut (``"unknown"`` est une modalité, pas un NaN)."""

EXPECTED_COLUMNS: tuple[str, ...] = (
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
    "y",
)
"""Les 21 colonnes du fichier brut, dans l'ordre officiel."""

TARGET_VALUES: frozenset[str] = frozenset({"yes", "no"})
"""Valeurs autorisées pour la cible ``y``."""


class DataValidationError(ValueError):
    """Les données ne respectent pas le schéma attendu."""


def validate_dataframe(
    df: pd.DataFrame, target: str = "y", expected_rows: int | None = None
) -> dict[str, Any]:
    """Vérifie le schéma du DataFrame brut et renvoie un résumé.

    Args:
        df: Données brutes.
        target: Nom de la colonne cible.
        expected_rows: Nombre de lignes attendu ; ``None`` pour ne pas le vérifier.

    Returns:
        Un résumé : nombre de lignes et de colonnes, taux de la classe positive.

    Raises:
        DataValidationError: Au premier contrôle qui échoue (colonnes, lignes, types, cible, NaN).
    """
    if tuple(df.columns) != EXPECTED_COLUMNS:
        missing = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
        extra = sorted(set(df.columns) - set(EXPECTED_COLUMNS))
        raise DataValidationError(
            f"Colonnes inattendues (noms ou ordre) — manquantes : {missing}, en trop : {extra}"
        )

    if expected_rows is not None and len(df) != expected_rows:
        raise DataValidationError(f"{len(df)} lignes au lieu de {expected_rows}")

    non_numeric = [c for c in NUMERIC_COLUMNS if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        raise DataValidationError(f"Colonnes censées être numériques : {non_numeric}")

    bad_target = set(df[target].unique()) - TARGET_VALUES
    if bad_target:
        raise DataValidationError(f"Valeurs inattendues dans {target!r} : {sorted(bad_target)}")

    null_counts = df.isna().sum()
    if null_counts.any():
        raise DataValidationError(f"Valeurs manquantes : {null_counts[null_counts > 0].to_dict()}")

    return {
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "positive_rate": round(float((df[target] == "yes").mean()), 4),
    }


def main() -> None:
    """Valide ``data.raw_csv`` et écrit le résumé dans ``reports/validation.json``."""
    params = load_params()["data"]
    df = pd.read_csv(resolve_path(params["raw_csv"]), sep=params["separator"])
    summary = validate_dataframe(df, target=params["target"], expected_rows=params["expected_rows"])

    out = resolve_path("reports/validation.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Validation OK : {summary}")


if __name__ == "__main__":
    main()
