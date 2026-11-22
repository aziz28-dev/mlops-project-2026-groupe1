from pathlib import Path

import pytest

from bankmlops.config import PARAMS_PATH, PROJECT_ROOT, load_params, resolve_path


def test_project_root_contains_params_file():
    assert (PROJECT_ROOT / "params.yaml") == PARAMS_PATH
    assert PARAMS_PATH.is_file()


def test_load_params_has_expected_sections():
    params = load_params()
    for section in ("seed", "data", "split", "train", "mlflow", "drift"):
        assert section in params, f"section manquante dans params.yaml : {section}"


def test_duration_is_dropped_to_avoid_leakage():
    params = load_params()
    assert "duration" in params["data"]["drop_columns"]


def test_split_ratios_are_valid():
    split = load_params()["split"]
    assert 0 < split["reference_ratio"] < 1
    assert 0 < split["test_size"] < 1


def test_load_params_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_params(tmp_path / "absent.yaml")


def test_load_params_rejects_non_dict(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("- juste\n- une liste\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_params(bad)


def test_resolve_path_is_absolute_and_under_root():
    p = resolve_path("data/raw")
    assert p.is_absolute()
    assert p == PROJECT_ROOT / "data" / "raw"
