# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Projet MLOps TEK-UP 2026-2027 (binôme)

Ce fichier est lu automatiquement par Claude Code au démarrage de chaque session.
Il décrit le projet, le périmètre, les conventions et la manière dont Claude doit travailler avec nous.

## 0. Point d'étape (mis à jour le 23/11/2026 au soir) — À LIRE EN PREMIER

Dépôt GitHub : `aziz28-dev/mlops-project-2026-groupeB` (ancien nom `...-groupe1`, GitHub redirige).
Séance de suivi notée : **mardi 24/11** (objectif : phases 0 → 5). Avancement détaillé + preuves :
`docs/PROGRESS.md`. Guide d'installation pour le Membre B : `docs/GUIDE_BINOME.md`.

| Phase | Qui | État |
|---|---|---|
| 0 Environnement (Poetry, pre-commit, structure) | A | ✅ PR #1 |
| 1 Ingestion + validation + DVC | A | ✅ PR #2 |
| 2 EDA courte (2 figures) | A | ✅ PR #4 |
| 3 Préparation complète | A | ⚠️ partielle (minimal dans la baseline) ; reste : doublons, `pdays=999`, `unknown` |
| 4 Baseline LogReg + RandomForest + MLflow | A | ✅ code fini, branche `feature/mlflow` (PR à merger) ; XGBoost plus tard |
| **5 CI GitHub Actions** | **B** | **⏳ à faire en priorité** (branche `feature/ci`) |
| 6 API FastAPI | B | ⏳ après la phase 5 |
| 7 Docker · 8 Couverture + CML · 9 Drift · 10 Prefect · 11 Final | — | ⏳ prévu |

**Ce qui existe dans le code :** `config.py` ; `data/ingest.py`, `data/validate.py`, `data/prepare.py` ;
`features/build.py` (scaler + one-hot) ; `evaluation/metrics.py`, `evaluation/plots.py` ;
`training/train.py` ; `notebooks/01_eda.ipynb`. Pipeline DVC : `ingest → validate → prepare → train`.
33 tests, couverture 87 %, **sans réseau ni vrai dataset** (fixtures de `tests/conftest.py` ; le test
d'entraînement isole MLflow dans `tmp_path`). `api/`, `inference/`, `monitoring/`, `pipelines/` sont vides.

**Résultats réels (baseline, `reports/metrics.json`) :** champion = random_forest. Test (référence) :
RF PR-AUC 0,164 / ROC-AUC 0,629 ; LogReg 0,163 / 0,610 (aléatoire ≈ 0,056). Production : ROC-AUC RF
0,543, LogReg 0,633 → le drift dégrade le modèle. EDA : taux de yes 5,6 % (référence) → 24,6 %
(production), euribor3m 4,69 → 1,14, contact cellular 52 % → 90 %.

**Décisions :** D3 ✅ l'API charge `models/model.joblib`. D4 ✅ Python 3.11 avec `numpy<2.5`, `xgboost<3.3`.
D1 ⏳ remote DVC partagé (DagsHub recommandé) : tant qu'il n'est pas choisi, `dvc pull` ne marche que sur
le PC de A ; le Membre B obtient les données avec `poetry run dvc repro`. D2 : aliases MLflow (`@champion`).

**Pièges techniques déjà réglés (ne pas les réintroduire) :**
- MLflow **3.18** écrit dans `sqlite:///mlflow.db` (pas de serveur ; UI :
  `poetry run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000`). `log_model(name=...)`,
  pas `artifact_path`. Sérialisation skops : `SKOPS_TRUSTED_TYPES` dans `training/train.py`.
- DVC est en dépendance **dev** (pas dans l'image Docker). `dvc.lock` est exclu du hook trailing-whitespace.
  Une sortie DVC ne doit jamais être ignorée par le `.gitignore` racine.
- Les JSON générés sont écrits avec `newline="\n"` (identiques Windows / CI Linux).
- Poetry peut manquer du PATH d'un terminal déjà ouvert : `$env:APPDATA\Python\Scripts\poetry.exe`.

**Mission du Membre B (si c'est lui qui lit ceci) :**
1. Installer : `git clone`, `poetry install`, `poetry run pre-commit install`, `poetry run pytest`
   (33 passed attendu). Données si besoin : `poetry run dvc repro` (télécharge le zip UCI).
2. Phase 5 : coller le prompt « Phase 5 » de `docs/ROADMAP_PROMPTS.md`. La CI fait `poetry install`,
   ruff + `black --check`, `pytest --cov=src` ; **pas de `dvc pull`** (les tests n'en ont pas besoin).
   Fini quand : CI verte sur une PR, badge dans le README, protection de `main`.
3. Phase 6 : l'API charge `models/model.joblib` (un `Pipeline` sklearn complet : prétraitement + modèle,
   `predict_proba(df)[:, 1]`). Entrée = **19 colonnes** (`feature_columns(["duration"])` dans
   `features/build.py`) ; plusieurs noms contiennent un point (`emp.var.rate`, `cons.price.idx`,
   `cons.conf.idx`, `nr.employed`) → alias Pydantic. Seuil : `train.decision_threshold`. Tant que D1
   n'est pas tranché, tester l'API avec un petit modèle factice entraîné dans les tests.

---

## 1. Contexte

- **Module :** MLOps & Industrialisation de l'IA — enseignant Haythem Ghazouani.
- **Poids :** projet = 40 % du module ; séance de suivi = 30 % de la note projet.
- **Équipe :** binôme (Membre A et Membre B — voir `SYNOPSIS.md`).
- **Sujet :** Plateforme MLOps de ciblage des campagnes de télémarketing bancaire.
- **Dataset :** UCI Bank Marketing — fichier `bank-additional-full.csv` (41 188 lignes, 20 variables,
  mai 2008 → nov. 2010, licence CC BY 4.0). Source : https://archive.ics.uci.edu/dataset/222/bank+marketing
- **Tâche ML :** classification binaire, cible `y` (yes/no : le client souscrit un dépôt à terme).
- **Documents officiels :** `docs/reference/` (guide PDF + version texte, template synopsis, 2 mails).
  **En cas de doute sur une exigence, relire `docs/reference/GUIDE_PROJET_MODULE_MLOPS.txt`.**

## 2. Périmètre exigé pour un binôme (guide, section 2.1)

Tronc commun : DVC (+ remote), MLflow Tracking & Model Registry, API FastAPI (Pydantic),
Dockerfile (multi-stage, non-root), CI GitHub Actions (lint + pytest), détection de drift statistique avec test.
**+ Binôme :** Prefect 3.x (flow, retries, Work Pool, CRON), rapport CML avec courbes sur Pull Request,
simulateur de dérive.

**Dans le périmètre (décision binôme) :** la boucle de réentraînement déclenchée par le drift
(`drift_share >= 0.30` → `training_flow`), implémentée en phase 10 — 1 pt au barème.

**Hors périmètre binôme (bonus seulement si tout le reste est fini) :** Blue/Green ou Canary,
export Prometheus, Streamlit/Gradio. Rien d'autre n'est un bonus.

**Format de la soutenance finale : NON confirmé.** Le guide prévoit 10 min de pitch avec slides,
le mail 1 dit « sans slides ». Question ouverte pour le prof (`docs/PROGRESS.md`) : préparer les deux.

## 3. Grille d'évaluation (/20) — à garder en tête

| Composante | Pts | Ce qui rapporte les points |
|---|---|---|
| Code & DVC | 3 | `src/` modulaire, typage, docstrings, ruff/black ; `dvc.yaml` reproductible + remote |
| MLflow | 3 | runs complets (params, métriques, artefacts, courbes) ; champion dans le Registry |
| API & Docker | 3 | `/predict`, `/health` avec Pydantic ; image légère, non-root, multi-stage |
| CI/CD | 4 | pytest (unitaires, schéma, inférence) couverture > 75 % ; CI lint+tests + CML sur PR |
| Prefect | 3 | flow DAG avec retries ; Work Pool + CRON |
| Drift | 4 | KS + χ² + PSI calculés formellement ; rapport HTML ; retrain déclenché par le drift = 1 pt (prévu phase 10) |

Règle d'or du guide : le projet doit se reproduire avec `git clone` → `dvc pull` → `pytest`.

## 4. Stack technique

- Python **3.11**, gestion d'env avec **Poetry** (`pyproject.toml`), `requirements.txt` exporté pour Docker.
- Qualité : **ruff** (lint) + **black** (format) via **pre-commit** ; typage + docstrings (style Google).
- ML : pandas, numpy, scikit-learn, xgboost.
- Data versioning : **DVC** (remote — voir décision D1 ci-dessous).
- Tracking : **MLflow** (serveur local `http://127.0.0.1:5000`, backend SQLite `mlflow.db`).
- Serving : **FastAPI** + **Pydantic v2** + uvicorn.
- Packaging : **Docker** multi-stage (`python:3.11-slim`), utilisateur non-root, `docker-compose.yml`.
- CI : **GitHub Actions** + **CML**.
- Orchestration : **Prefect 3.x**.
- Drift : implémentation maison KS / χ² / PSI (scipy) **+** rapport **Evidently AI** HTML.
- Tests : **pytest** + pytest-cov.

> ⚠️ Les API de MLflow, Prefect et Evidently ont changé selon les versions.
> **Avant d'écrire du code qui les utilise, vérifier la version installée (`poetry show <pkg>`)
> et suivre la doc officielle de CETTE version.** Ne jamais deviner une API.

## 5. Structure cible du dépôt

```text
mlops-project-2026-groupeX/
├── CLAUDE.md                 # ce fichier
├── SYNOPSIS.md               # fiche de cadrage (Jalon 1)
├── README.md                 # badges CI, reproduction en 3 commandes, schéma
├── pyproject.toml / poetry.lock / requirements.txt
├── .pre-commit-config.yaml / .gitignore / .dvcignore
├── params.yaml               # TOUS les hyperparamètres et seuils (lus par dvc.yaml)
├── dvc.yaml / dvc.lock
├── data/
│   ├── raw/                  # suivi par DVC, jamais par Git
│   ├── processed/            # reference.parquet, production.parquet, train/test
│   └── drift/                # lots de production simulés
├── src/bankmlops/
│   ├── __init__.py
│   ├── config.py             # chargement params.yaml + chemins
│   ├── data/                 # ingest.py, validate.py, prepare.py
│   ├── features/             # build.py (pipeline sklearn ColumnTransformer)
│   ├── training/             # train.py (MLflow), register.py
│   ├── evaluation/           # metrics.py, plots.py
│   ├── inference/            # predictor.py (chargement modèle + prédiction)
│   └── monitoring/           # drift_stats.py (KS, χ², PSI), drift_simulator.py, evidently_report.py
├── api/                      # main.py (FastAPI), schemas.py (Pydantic)
├── pipelines/                # flows Prefect : training_flow.py, monitoring_flow.py ; prefect.yaml
├── tests/                    # unit/, integration/, conftest.py
├── notebooks/                # 01_eda.ipynb (exploration seulement, aucune logique métier)
├── reports/                  # figures/, metrics.json, drift_report.html
├── docker/ ou Dockerfile + docker-compose.yml
├── docs/                     # ARCHITECTURE.md, ROADMAP_PROMPTS.md, reference/
└── .github/workflows/        # ci.yml, cml.yml
```

### Flux de bout en bout (schéma complet : `docs/ARCHITECTURE.md`)

`ingest → validate → prepare` (stages DVC) produit la **référence** (70 % premières lignes, cf.
`split.reference_ratio`) et la **production** (30 % restantes) — l'ordre chronologique du fichier reste
à vérifier en phase 1, ne pas le tenir pour acquis. La référence est elle-même découpée en train/test
**stratifié** (`split.test_size` = 0.2, `random_state` = `seed`). `train` entraîne LogReg / RF / XGBoost
sur le train de la référence, logge tout dans MLflow, choisit le meilleur selon `train.selection_metric` (pr_auc),
le pose en `@champion` dans le Registry **et** l'exporte en `models/model.joblib` que l'API charge
(D3). Le monitoring compare référence vs production (ou lots du `DriftSimulator` dans `data/drift/`)
avec KS/χ²/PSI ; si la part de features en dérive ≥ `drift.drift_share_threshold` (0.30), le
`monitoring_flow` Prefect déclenche le `training_flow`. `reports/metrics.json` est lu par DVC et par CML.

**`params.yaml` est la source unique** des seuils, ratios, hyperparamètres et noms MLflow : le code
les lit via `src/bankmlops/config.py`, `dvc.yaml` les déclare en `params:`. Ne jamais les coder en dur.

## 6. Règles métier & données (à respecter dans tout le code)

1. **Supprimer `duration`** des features : elle n'est connue qu'après l'appel (data leakage).
   Vérifier la note officielle dans `bank-additional-names.txt` (dans le zip) et citer-la dans le README.
2. Le fichier est **ordonné chronologiquement** (à confirmer dans `bank-additional-names.txt`).
   On ne mélange PAS les lignes avant le split : les premières lignes = **référence** (entraînement),
   les dernières = **"production"** (sert à mesurer le drift naturel). Ratio dans `params.yaml`.
3. Le séparateur du CSV est `;`. Les valeurs `"unknown"` dans les catégorielles sont une modalité,
   pas forcément des NaN : décision documentée dans le README. `pdays = 999` = jamais contacté : à traiter explicitement.
4. Cible déséquilibrée → métriques principales : **PR-AUC, F1, ROC-AUC, recall** (pas l'accuracy seule).
   Le seuil de décision est un paramètre (`params.yaml`).
5. Le split train/test À L'INTÉRIEUR de la référence est stratifié, avec `random_state` fixé.

## 7. Décisions ouvertes (à trancher avec nous, ne pas décider seul)

- **D1 — Remote DVC accessible depuis GitHub Actions.** Un remote local ne marche pas en CI.
  Options : (a) DagsHub (remote S3 gratuit), (b) Google Drive, (c) en CI, re-télécharger le zip UCI
  puis `dvc repro`. Proposer les options avec avantages/inconvénients, nous laisser choisir.
- **D2 — MLflow "Staging/Production".** Le guide parle de stages ; les versions récentes de MLflow
  privilégient les **aliases** (`@champion`). Utiliser les aliases et l'expliquer dans le rapport,
  sauf si le prof exige les stages.
- **D3 — Chargement du modèle par l'API.** Recommandé : l'API charge un artefact exporté
  (`models/model.joblib` suivi par DVC) pour fonctionner en Docker/CI sans serveur MLflow ;
  le Registry sert à la gouvernance. **Décidé le 23/11 : artefact exporté `models/model.joblib`.**

## 8. Comment Claude doit travailler avec nous (IMPORTANT)

- **Langue :** explications en **français**, avec une explication intuitive en **derja tunisienne
  (arabizi)** pour les concepts difficiles. Code, commandes, noms de fichiers en anglais.
- **Pédagogie d'abord :** on sera interrogés individuellement à la soutenance. Pour chaque fichier
  créé : expliquer son rôle, comment il s'intègre dans l'architecture, et comment le tester.
  Terminer chaque étape par **2–3 questions qu'un jury pourrait poser** sur ce qu'on vient de faire.
- **Petites étapes :** une phase de `docs/ROADMAP_PROMPTS.md` à la fois. Montrer le plan avant
  d'écrire beaucoup de code. Pas de génération massive de fichiers sans validation.
- **Git :** travail sur des branches `feature/...`, merge via Pull Request. **Ne pas faire les commits
  à notre place** : proposer un message de commit (Conventional Commits) et nous laisser committer —
  le prof inspecte `git log` pour vérifier la contribution réelle de chaque membre.
- **Honnêteté :** ne jamais inventer de métrique, de résultat ou de capture. Si une commande n'a pas
  été exécutée, le dire. Distinguer clairement "fait" / "prévu".
- **Simplicité :** ne pas ajouter d'outil hors de la stack ci-dessus sans nous demander.
- **Qualité :** tout nouveau module a des tests ; `pre-commit run --all-files` et `pytest` doivent
  passer avant de proposer un commit.
- **Suivi :** après chaque phase terminée, mettre à jour `docs/PROGRESS.md` (tâche, statut, preuve,
  prochaine action). Ce fichier sert à préparer les slides de suivi.

## 9. Commandes utiles

```bash
poetry install                     # installer l'env
poetry run pre-commit install      # activer les hooks
poetry run pytest --cov=src        # tests + couverture
poetry run pytest tests/unit/test_config.py::test_name -v   # un seul test
poetry run pre-commit run --all-files                         # ruff --fix + black + contrôles
dvc repro                          # rejouer le pipeline
dvc dag / dvc status               # preuves pour les slides
dvc push / dvc pull                # synchroniser les données avec le remote
mlflow server --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
poetry run uvicorn api.main:app --reload
docker compose up --build
```

Environnement de dev : **Windows** (PowerShell / Git Bash) — adapter les commandes shell en conséquence.
`pre-commit` bloque les fichiers > 1000 Ko (`check-added-large-files`) : les données passent par DVC.

Commandes Claude du projet (`.claude/commands/`) : `/explique <concept|fichier>`,
`/verifie-phase <n>` (vérifie la « Définition de fini » de la phase et met à jour `docs/PROGRESS.md`),
`/prepare-suivi` (produit `docs/SUIVI_CONTENU.md` pour les 5 diapos de la séance de suivi).
Chaque phase de `docs/ROADMAP_PROMPTS.md` indique son responsable (A/B), sa branche `feature/...`
et sa « Définition de fini » — s'y référer avant de déclarer une phase terminée.
