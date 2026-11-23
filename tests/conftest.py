"""Fixtures partagées : petites données factices, sans réseau ni vrai dataset (CI-friendly)."""

import numpy as np
import pandas as pd
import pytest

from bankmlops.config import load_params
from bankmlops.data.validate import EXPECTED_COLUMNS


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Quatre lignes au format exact de bank-additional-full.csv."""
    rows = [
        [56, "housemaid", "married", "basic.4y", "no", "no", "no", "telephone", "may", "mon",
         261, 1, 999, 0, "nonexistent", 1.1, 93.994, -36.4, 4.857, 5191.0, "no"],
        [37, "services", "married", "high.school", "no", "yes", "no", "telephone", "may", "mon",
         226, 1, 999, 0, "nonexistent", 1.1, 93.994, -36.4, 4.857, 5191.0, "no"],
        [40, "admin.", "single", "unknown", "unknown", "no", "no", "cellular", "nov", "fri",
         139, 2, 6, 1, "success", -1.1, 94.767, -50.8, 1.028, 4963.6, "yes"],
        [74, "retired", "married", "professional.course", "no", "yes", "no", "cellular", "nov",
         "fri", 239, 3, 999, 1, "failure", -1.1, 94.767, -50.8, 1.028, 4963.6, "no"],
    ]  # fmt: skip
    return pd.DataFrame(rows, columns=list(EXPECTED_COLUMNS))


@pytest.fixture
def synthetic_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """200 lignes factices au format brut, 25 % de « yes » (assez pour stratifier et entraîner)."""
    rng = np.random.default_rng(0)
    df = raw_df.sample(n=200, replace=True, random_state=0).reset_index(drop=True)
    df["age"] = rng.integers(18, 90, size=len(df))
    df["campaign"] = rng.integers(1, 10, size=len(df))
    df["euribor3m"] = rng.uniform(0.6, 5.0, size=len(df))
    df["y"] = np.where(np.arange(len(df)) % 4 == 0, "yes", "no")
    return df


@pytest.fixture
def test_params() -> dict:
    """Paramètres réels du projet, réduits pour des tests rapides."""
    params = load_params()
    params["train"]["models_enabled"] = ["logreg", "random_forest"]
    params["train"]["models"]["random_forest"]["n_estimators"] = 10
    return params
