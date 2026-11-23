"""Graphiques d'évaluation loggés comme artefacts MLflow.

On construit des ``matplotlib.figure.Figure`` sans passer par ``pyplot`` : pas d'état global,
pas de fenêtre, fonctionne pareil en local, en CI et dans un flow Prefect.
"""

import numpy as np
from matplotlib.figure import Figure
from sklearn.metrics import confusion_matrix, precision_recall_curve

BLUE, INK, INK2 = "#2a78d6", "#0b0b0b", "#52514e"


def confusion_matrix_figure(y_true: np.ndarray, y_pred: np.ndarray, title: str) -> Figure:
    """Matrice de confusion annotée (lignes = vrai, colonnes = prédit).

    Args:
        y_true: Vraies étiquettes (0/1).
        y_pred: Étiquettes prédites (0/1).
        title: Titre du graphique.

    Returns:
        La figure.
    """
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig = Figure(figsize=(4.2, 3.6))
    ax = fig.add_subplot()
    ax.imshow(cm, cmap="Blues")
    labels = ["no", "yes"]
    ax.set_xticks([0, 1], labels)
    ax.set_yticks([0, 1], labels)
    ax.set_xlabel("Prédit", color=INK2)
    ax.set_ylabel("Vrai", color=INK2)
    threshold = cm.max() / 2
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > threshold else INK
            ax.text(j, i, f"{cm[i, j]:,}".replace(",", " "), ha="center", va="center", color=color)
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    return fig


def pr_curve_figure(y_true: np.ndarray, proba: np.ndarray, title: str) -> Figure:
    """Courbe précision-rappel, avec la ligne du modèle aléatoire (taux de la classe positive).

    Args:
        y_true: Vraies étiquettes (0/1).
        proba: Probabilités prédites pour la classe positive.
        title: Titre du graphique.

    Returns:
        La figure.
    """
    precision, recall, _ = precision_recall_curve(y_true, proba)
    fig = Figure(figsize=(4.8, 3.6))
    ax = fig.add_subplot()
    ax.plot(recall, precision, color=BLUE, lw=2)
    ax.axhline(float(np.mean(y_true)), color=INK2, lw=1, ls="--")
    ax.text(0.98, float(np.mean(y_true)) + 0.02, "aléatoire", ha="right", color=INK2, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Recall", color=INK2)
    ax.set_ylabel("Précision", color=INK2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(title, loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    return fig
