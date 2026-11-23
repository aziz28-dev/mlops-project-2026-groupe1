"""Construction des features : pipeline scikit-learn de prétraitement.

Version baseline : standardisation des numériques et one-hot des catégorielles.
Le même objet est intégré au modèle (``Pipeline``), donc l'API applique exactement le même
prétraitement qu'à l'entraînement.
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from bankmlops.data.validate import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS


def feature_columns(drop_columns: list[str]) -> tuple[list[str], list[str]]:
    """Renvoie les colonnes numériques et catégorielles utilisées comme features.

    Args:
        drop_columns: Colonnes exclues (fuite de données, ex. ``duration``).

    Returns:
        ``(numeriques, categorielles)`` dans l'ordre du schéma officiel.
    """
    numeric = [c for c in NUMERIC_COLUMNS if c not in drop_columns]
    categorical = [c for c in CATEGORICAL_COLUMNS if c not in drop_columns]
    return numeric, categorical


def build_preprocessor(numeric: list[str], categorical: list[str]) -> ColumnTransformer:
    """Crée le ``ColumnTransformer`` de prétraitement.

    Args:
        numeric: Colonnes numériques à standardiser.
        categorical: Colonnes catégorielles à encoder en one-hot.

    Returns:
        Le transformateur (non entraîné). Une modalité inconnue à l'inférence est ignorée
        (vecteur nul) au lieu de provoquer une erreur.
    """
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )
