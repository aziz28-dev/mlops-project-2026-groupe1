"""Préparation minimale (baseline) : suppression des fuites, split temporel puis stratifié.

Le fichier brut est trié par date (``bank-additional-names.txt``) : on coupe SANS mélanger.
- référence = premières lignes (``split.reference_ratio``) → découpée en train / test stratifiés ;
- production = dernières lignes → sert à mesurer la dérive et la dégradation du modèle.

Hors baseline (phase 3) : doublons, ``pdays = 999`` et ``"unknown"`` restent tels quels ici.

Usage (stage DVC ``prepare``) : ``python -m bankmlops.data.prepare``
"""

import pandas as pd
from sklearn.model_selection import train_test_split

from bankmlops.config import load_params, resolve_path


def drop_leakage_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Supprime les colonnes inconnues au moment de la prédiction (ex. ``duration``).

    Args:
        df: Données brutes.
        columns: Colonnes à retirer.

    Returns:
        Une copie du DataFrame sans ces colonnes.
    """
    return df.drop(columns=columns)


def temporal_split(df: pd.DataFrame, reference_ratio: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Coupe le DataFrame dans l'ordre des lignes, sans mélange.

    Args:
        df: Données triées chronologiquement.
        reference_ratio: Part des premières lignes gardées comme référence (entre 0 et 1).

    Returns:
        ``(reference, production)``.

    Raises:
        ValueError: Si ``reference_ratio`` n'est pas strictement entre 0 et 1.
    """
    if not 0 < reference_ratio < 1:
        raise ValueError(f"reference_ratio doit être entre 0 et 1, reçu : {reference_ratio}")
    cut = int(len(df) * reference_ratio)
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()


def stratified_train_test(
    reference: pd.DataFrame, target: str, test_size: float, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Découpe la référence en train / test en conservant la proportion de la cible.

    Args:
        reference: Données de référence.
        target: Nom de la colonne cible.
        test_size: Part du test (entre 0 et 1).
        seed: Graine pour un découpage reproductible.

    Returns:
        ``(train, test)``.
    """
    train, test = train_test_split(
        reference, test_size=test_size, stratify=reference[target], random_state=seed
    )
    return train, test


def main() -> None:
    """Lit le CSV brut et écrit train / test / production en Parquet dans ``data.processed_dir``."""
    params = load_params()
    data, split = params["data"], params["split"]

    raw = pd.read_csv(resolve_path(data["raw_csv"]), sep=data["separator"])
    clean = drop_leakage_columns(raw, data["drop_columns"])
    reference, production = temporal_split(clean, split["reference_ratio"])
    train, test = stratified_train_test(
        reference, data["target"], split["test_size"], params["seed"]
    )

    out_dir = resolve_path(data["processed_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in {"train": train, "test": test, "production": production}.items():
        frame.to_parquet(out_dir / f"{name}.parquet", index=False)
        rate = (frame[data["target"]] == data["positive_label"]).mean()
        print(f"{name:<10} : {len(frame):>6} lignes, taux de yes = {rate:.2%}")


if __name__ == "__main__":
    main()
