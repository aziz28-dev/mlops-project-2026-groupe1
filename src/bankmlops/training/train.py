"""Entraînement, suivi MLflow et sélection du modèle champion.

Pour chaque modèle activé (``train.models_enabled``) :
1. pipeline = prétraitement (``features.build``) + modèle ;
2. entraînement sur le train de la référence ;
3. évaluation sur le test (sélection) ET sur la production (mesure de l'effet du drift) ;
4. run MLflow : hyperparamètres, métriques, matrice de confusion, courbe PR, modèle signé.

Le meilleur selon ``train.selection_metric`` est enregistré dans le Model Registry avec l'alias
``mlflow.champion_alias``, exporté en ``train.model_path`` (chargé par l'API, décision D3) et
résumé dans ``train.metrics_path`` (lu par DVC et CML).

Usage (stage DVC ``train``) : ``python -m bankmlops.training.train``
"""

import json
from pathlib import Path
from typing import Any

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import MlflowClient
from mlflow.models import infer_signature
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from bankmlops.config import load_params, resolve_path
from bankmlops.evaluation.metrics import compute_metrics
from bankmlops.evaluation.plots import confusion_matrix_figure, pr_curve_figure
from bankmlops.features.build import build_preprocessor, feature_columns

SKOPS_TRUSTED_TYPES: list[str] = ["sklearn.tree._tree.Tree"]
"""Types que MLflow (format skops) doit accepter : les arbres du RandomForest.

skops refuse par défaut les types qu'il ne peut pas vérifier. On les déclare un par un, et
seulement parce que ces modèles sont produits par notre propre pipeline.
"""


def make_estimator(name: str, hyperparams: dict[str, Any], seed: int) -> ClassifierMixin:
    """Instancie le modèle demandé avec ses hyperparamètres.

    Args:
        name: ``logreg``, ``random_forest`` ou ``xgboost``.
        hyperparams: Hyperparamètres lus dans ``train.models.<name>``.
        seed: Graine (``random_state``) pour la reproductibilité.

    Returns:
        L'estimateur scikit-learn (non entraîné).

    Raises:
        ValueError: Si le nom de modèle est inconnu.
    """
    if name == "logreg":
        return LogisticRegression(**hyperparams, random_state=seed)
    if name == "random_forest":
        return RandomForestClassifier(**hyperparams, random_state=seed, n_jobs=-1)
    if name == "xgboost":
        return XGBClassifier(**hyperparams, random_state=seed, eval_metric="logloss")
    raise ValueError(f"Modèle inconnu : {name!r}")


def build_pipeline(
    name: str, hyperparams: dict[str, Any], seed: int, numeric: list[str], categorical: list[str]
) -> Pipeline:
    """Assemble prétraitement + modèle dans un seul ``Pipeline``.

    Args:
        name: Nom du modèle (voir ``make_estimator``).
        hyperparams: Hyperparamètres du modèle.
        seed: Graine.
        numeric: Colonnes numériques.
        categorical: Colonnes catégorielles.

    Returns:
        Le pipeline non entraîné.
    """
    return Pipeline(
        [
            ("preprocess", build_preprocessor(numeric, categorical)),
            ("model", make_estimator(name, hyperparams, seed)),
        ]
    )


def split_xy(
    df: pd.DataFrame, features: list[str], target: str, positive_label: str
) -> tuple[pd.DataFrame, pd.Series]:
    """Sépare les features et la cible encodée en 0/1.

    Args:
        df: Données préparées.
        features: Colonnes utilisées comme features.
        target: Nom de la colonne cible.
        positive_label: Valeur de la classe positive (``"yes"``).

    Returns:
        ``(X, y)``.
    """
    return df[features], (df[target] == positive_label).astype(int)


def run_training(
    params: dict[str, Any],
    train: pd.DataFrame,
    test: pd.DataFrame,
    production: pd.DataFrame,
    tracking_uri: str,
    model_path: Path,
    metrics_path: Path,
    artifact_location: str | None = None,
) -> dict[str, Any]:
    """Entraîne les modèles activés, logge dans MLflow et publie le champion.

    Args:
        params: Contenu de ``params.yaml``.
        train: Train de la référence.
        test: Test de la référence (sert à choisir le champion).
        production: Données récentes (mesure de la dégradation due au drift).
        tracking_uri: URI MLflow (ex. ``sqlite:///mlflow.db``).
        model_path: Où exporter le pipeline champion (joblib).
        metrics_path: Où écrire le résumé JSON des métriques.
        artifact_location: Emplacement des artefacts si l'expérience doit être créée
            (``None`` = défaut MLflow ; utile pour isoler les tests).

    Returns:
        Le résumé écrit dans ``metrics_path``.
    """
    data, train_cfg, mlf = params["data"], params["train"], params["mlflow"]
    numeric, categorical = feature_columns(data["drop_columns"])
    features = numeric + categorical
    threshold = train_cfg["decision_threshold"]
    selection = train_cfg["selection_metric"]

    sets = {
        split: split_xy(df, features, data["target"], data["positive_label"])
        for split, df in {"train": train, "test": test, "production": production}.items()
    }
    x_train, y_train = sets["train"]

    mlflow.set_tracking_uri(tracking_uri)
    if mlflow.get_experiment_by_name(mlf["experiment_name"]) is None:
        mlflow.create_experiment(mlf["experiment_name"], artifact_location=artifact_location)
    mlflow.set_experiment(mlf["experiment_name"])

    results: dict[str, dict[str, Any]] = {}
    for name in train_cfg["models_enabled"]:
        hyperparams = train_cfg["models"][name]
        pipeline = build_pipeline(name, hyperparams, params["seed"], numeric, categorical)
        pipeline.fit(x_train, y_train)

        with mlflow.start_run(run_name=name) as run:
            mlflow.log_params({"model": name, "decision_threshold": threshold, **hyperparams})
            scores: dict[str, dict[str, float]] = {}
            for split in ("test", "production"):
                x, y = sets[split]
                proba = pipeline.predict_proba(x)[:, 1]
                scores[split] = compute_metrics(y.to_numpy(), proba, threshold)
                mlflow.log_metrics({f"{split}_{k}": v for k, v in scores[split].items()})
                y_pred = (proba >= threshold).astype(int)
                mlflow.log_figure(
                    confusion_matrix_figure(y.to_numpy(), y_pred, f"{name} — {split}"),
                    f"plots/confusion_matrix_{split}.png",
                )
                mlflow.log_figure(
                    pr_curve_figure(y.to_numpy(), proba, f"{name} — {split}"),
                    f"plots/pr_curve_{split}.png",
                )

            example = x_train.head(5)
            signature = infer_signature(example, pipeline.predict_proba(example)[:, 1])
            info = mlflow.sklearn.log_model(
                pipeline,
                name="model",
                signature=signature,
                input_example=example,
                skops_trusted_types=SKOPS_TRUSTED_TYPES,
            )
        results[name] = {
            "run_id": run.info.run_id,
            "model_uri": info.model_uri,
            "pipeline": pipeline,
            **scores,
        }
        print(f"{name:<14} test {selection} = {scores['test'][selection]:.4f}")

    champion = max(results, key=lambda n: results[n]["test"][selection])
    best = results[champion]

    version = mlflow.register_model(best["model_uri"], mlf["registered_model_name"])
    MlflowClient().set_registered_model_alias(
        mlf["registered_model_name"], mlf["champion_alias"], version.version
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best["pipeline"], model_path)

    summary = {
        "champion": champion,
        "registered_version": int(version.version),
        "selection_metric": selection,
        "test": best["test"],
        "production": best["production"],
        "models": {
            n: {"test": r["test"], "production": r["production"]} for n, r in results.items()
        },
    }
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    # newline="\n" : même fichier sous Windows et en CI Linux (pas de CRLF)
    metrics_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Champion : {champion} (version {version.version}, alias @{mlf['champion_alias']})")
    return summary


def main() -> None:
    """Lit les données préparées et lance l'entraînement avec les chemins de ``params.yaml``."""
    params = load_params()
    processed = resolve_path(params["data"]["processed_dir"])
    frames = {
        n: pd.read_parquet(processed / f"{n}.parquet") for n in ("train", "test", "production")
    }
    run_training(
        params,
        frames["train"],
        frames["test"],
        frames["production"],
        tracking_uri=params["mlflow"]["tracking_uri"],
        model_path=resolve_path(params["train"]["model_path"]),
        metrics_path=resolve_path(params["train"]["metrics_path"]),
    )


if __name__ == "__main__":
    main()
