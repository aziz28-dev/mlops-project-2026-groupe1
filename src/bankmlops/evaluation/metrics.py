"""Métriques adaptées à une cible déséquilibrée (classe positive = souscription)."""

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def compute_metrics(y_true: np.ndarray, proba: np.ndarray, threshold: float) -> dict[str, float]:
    """Calcule les métriques de classification binaire.

    Args:
        y_true: Vraies étiquettes (0/1).
        proba: Probabilités prédites pour la classe positive.
        threshold: Seuil de décision (``train.decision_threshold``).

    Returns:
        ``pr_auc`` (average precision), ``roc_auc``, puis ``f1``, ``recall`` et ``precision``
        calculés au seuil donné.
    """
    y_pred = (proba >= threshold).astype(int)
    return {
        "pr_auc": float(average_precision_score(y_true, proba)),
        "roc_auc": float(roc_auc_score(y_true, proba)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
    }
