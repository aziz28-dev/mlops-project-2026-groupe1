import pandas as pd
import pytest

from bankmlops.data.prepare import drop_leakage_columns, stratified_train_test, temporal_split


def test_duration_is_removed(raw_df: pd.DataFrame):
    clean = drop_leakage_columns(raw_df, ["duration"])
    assert "duration" not in clean.columns
    assert "duration" in raw_df.columns  # l'original n'est pas modifié


def test_temporal_split_keeps_order_without_shuffle(synthetic_df: pd.DataFrame):
    ref, prod = temporal_split(synthetic_df, 0.7)
    assert len(ref) == 140 and len(prod) == 60
    assert list(ref.index) == list(range(0, 140))  # premières lignes = référence
    assert list(prod.index) == list(range(140, 200))  # dernières lignes = production


@pytest.mark.parametrize("ratio", [0, 1, 1.5, -0.1])
def test_temporal_split_rejects_invalid_ratio(synthetic_df: pd.DataFrame, ratio: float):
    with pytest.raises(ValueError):
        temporal_split(synthetic_df, ratio)


def test_stratified_split_has_no_overlap_and_keeps_rate(synthetic_df: pd.DataFrame):
    ref, _ = temporal_split(synthetic_df, 0.7)
    train, test = stratified_train_test(ref, "y", test_size=0.2, seed=42)

    assert set(train.index).isdisjoint(test.index)  # aucune fuite entre train et test
    assert len(train) + len(test) == len(ref)
    rate = lambda d: (d["y"] == "yes").mean()  # noqa: E731
    assert rate(train) == pytest.approx(rate(ref), abs=0.02)
    assert rate(test) == pytest.approx(rate(ref), abs=0.02)


def test_stratified_split_is_reproducible(synthetic_df: pd.DataFrame):
    a, _ = stratified_train_test(synthetic_df, "y", 0.2, seed=42)
    b, _ = stratified_train_test(synthetic_df, "y", 0.2, seed=42)
    assert list(a.index) == list(b.index)
