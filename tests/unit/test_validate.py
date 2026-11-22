import pandas as pd
import pytest

from bankmlops.data.validate import EXPECTED_COLUMNS, DataValidationError, validate_dataframe


def test_valid_dataframe_returns_summary(raw_df: pd.DataFrame):
    summary = validate_dataframe(raw_df, expected_rows=4)
    assert summary == {"n_rows": 4, "n_columns": 21, "positive_rate": 0.25}


def test_expected_columns_match_official_schema():
    assert len(EXPECTED_COLUMNS) == 21
    assert EXPECTED_COLUMNS[-1] == "y"
    assert "duration" in EXPECTED_COLUMNS  # présente dans le brut, supprimée plus tard


def test_missing_column_raises(raw_df: pd.DataFrame):
    with pytest.raises(DataValidationError, match="manquantes"):
        validate_dataframe(raw_df.drop(columns=["age"]))


def test_wrong_column_order_raises(raw_df: pd.DataFrame):
    with pytest.raises(DataValidationError):
        validate_dataframe(raw_df[list(reversed(raw_df.columns))])


def test_wrong_row_count_raises(raw_df: pd.DataFrame):
    with pytest.raises(DataValidationError, match="lignes"):
        validate_dataframe(raw_df, expected_rows=41188)


def test_non_numeric_column_raises(raw_df: pd.DataFrame):
    raw_df["age"] = raw_df["age"].astype(str)
    with pytest.raises(DataValidationError, match="numériques"):
        validate_dataframe(raw_df)


def test_unexpected_target_value_raises(raw_df: pd.DataFrame):
    raw_df.loc[0, "y"] = "maybe"
    with pytest.raises(DataValidationError, match="maybe"):
        validate_dataframe(raw_df)


def test_missing_values_raise(raw_df: pd.DataFrame):
    raw_df.loc[0, "job"] = None
    with pytest.raises(DataValidationError, match="manquantes"):
        validate_dataframe(raw_df)
