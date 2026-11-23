"""Entraînement de bout en bout sur données factices, avec un MLflow isolé dans tmp_path."""

import json
from pathlib import Path

import joblib
import pandas as pd
import pytest
from mlflow import MlflowClient

from bankmlops.data.prepare import drop_leakage_columns, stratified_train_test, temporal_split
from bankmlops.training.train import make_estimator, run_training


def test_unknown_model_name_raises():
    with pytest.raises(ValueError):
        make_estimator("svm", {}, seed=0)


def test_run_training_logs_registers_and_exports(
    synthetic_df: pd.DataFrame, test_params: dict, tmp_path: Path
):
    clean = drop_leakage_columns(synthetic_df, ["duration"])
    ref, prod = temporal_split(clean, 0.7)
    train, test = stratified_train_test(ref, "y", 0.2, seed=42)
    tracking_uri = f"sqlite:///{(tmp_path / 'mlflow.db').as_posix()}"
    model_path = tmp_path / "models" / "model.joblib"
    metrics_path = tmp_path / "metrics.json"

    summary = run_training(
        test_params,
        train,
        test,
        prod,
        tracking_uri=tracking_uri,
        model_path=model_path,
        metrics_path=metrics_path,
        artifact_location=(tmp_path / "artifacts").as_uri(),
    )

    # résumé cohérent et écrit sur disque
    assert summary["champion"] in {"logreg", "random_forest"}
    assert set(summary["models"]) == {"logreg", "random_forest"}
    assert json.loads(metrics_path.read_text(encoding="utf-8")) == summary
    for split in ("test", "production"):
        assert 0.0 <= summary[split]["pr_auc"] <= 1.0

    # modèle exporté utilisable directement (ce que fera l'API)
    model = joblib.load(model_path)
    proba = model.predict_proba(prod.drop(columns=["y"]))[:, 1]
    assert len(proba) == len(prod) and ((proba >= 0) & (proba <= 1)).all()

    # champion enregistré dans le Model Registry avec l'alias
    mlf = test_params["mlflow"]
    version = MlflowClient(tracking_uri).get_model_version_by_alias(
        mlf["registered_model_name"], mlf["champion_alias"]
    )
    assert int(version.version) == summary["registered_version"]
