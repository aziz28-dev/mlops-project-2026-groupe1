import numpy as np
import pandas as pd
import pytest

from bankmlops.evaluation.metrics import compute_metrics
from bankmlops.evaluation.plots import confusion_matrix_figure, pr_curve_figure
from bankmlops.features.build import build_preprocessor, feature_columns


def test_feature_columns_exclude_duration_and_target():
    numeric, categorical = feature_columns(["duration"])
    assert "duration" not in numeric
    assert "y" not in numeric + categorical
    assert len(numeric) == 9 and len(categorical) == 10


def test_preprocessor_output_is_stable_and_ignores_unknown_category(synthetic_df: pd.DataFrame):
    numeric, categorical = feature_columns(["duration"])
    pre = build_preprocessor(numeric, categorical).fit(synthetic_df)
    n_out = pre.transform(synthetic_df).shape[1]

    new = synthetic_df.head(2).copy()
    new["job"] = "astronaut"  # modalité jamais vue à l'entraînement
    assert pre.transform(new).shape[1] == n_out


def test_compute_metrics_perfect_classifier():
    y = np.array([0, 0, 1, 1])
    m = compute_metrics(y, np.array([0.1, 0.2, 0.8, 0.9]), threshold=0.5)
    assert m == {"pr_auc": 1.0, "roc_auc": 1.0, "f1": 1.0, "recall": 1.0, "precision": 1.0}


def test_compute_metrics_threshold_changes_decisions():
    y = np.array([0, 1, 1, 0])
    proba = np.array([0.3, 0.4, 0.9, 0.6])
    low = compute_metrics(y, proba, threshold=0.35)
    high = compute_metrics(y, proba, threshold=0.95)
    assert low["recall"] == 1.0
    assert high["recall"] == 0.0 and high["f1"] == 0.0  # zero_division géré
    assert low["roc_auc"] == pytest.approx(high["roc_auc"])  # ne dépend pas du seuil


def test_plots_return_figures():
    y = np.array([0, 1, 1, 0, 1])
    proba = np.array([0.2, 0.7, 0.6, 0.4, 0.9])
    assert confusion_matrix_figure(y, (proba >= 0.5).astype(int), "t").axes
    assert pr_curve_figure(y, proba, "t").axes
