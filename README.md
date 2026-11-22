# Plateforme MLOps — ciblage des campagnes de télémarketing bancaire

Projet de fin de module **MLOps & Industrialisation de l'IA** (TEK-UP, 2026-2027), binôme.

## Contexte

Une banque portugaise mène des campagnes de télémarketing pour vendre des dépôts à terme ; la
majorité des appels n'aboutit pas. Le modèle estime, pour chaque client, la probabilité de
souscription (`y` = yes/no) afin d'appeler en priorité les clients les plus prometteurs.

- **Dataset :** [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) —
  `bank-additional-full.csv`, 41 188 lignes, 20 variables, licence CC BY 4.0.
- **Tâche :** classification binaire déséquilibrée (métriques : PR-AUC, F1, ROC-AUC, recall).
- **Variable exclue :** `duration` (fuite de données, voir ci-dessous).

## Données

Source officielle : `bank-additional-names.txt`, fourni dans le zip UCI et versionné avec DVC dans
`data/raw/`.

- **Ordre chronologique.** Le fichier contient « *all examples, ordered by date (from May 2008 to
  November 2010)* ». On ne mélange donc pas les lignes avant le split : les premières servent de
  référence, les dernières jouent la « production ».
- **`duration` est exclue.** Note officielle : « *the duration is not known before a call is performed.
  Also, after the end of the call y is obviously known. Thus, this input should only be included for
  benchmark purposes and should be discarded if the intention is to have a realistic predictive
  model.* »
- **Valeurs manquantes.** Elles sont codées `"unknown"` dans les catégorielles ; le traitement retenu
  sera documenté en phase 3. `pdays = 999` signifie « jamais contacté auparavant ».
- **Validation** (`reports/validation.json`) : 41 188 lignes, 21 colonnes, 11,27 % de `y = "yes"`.

## Pipeline de données (DVC)

```bash
poetry run dvc repro     # ingest (téléchargement UCI) -> validate (schéma)
poetry run dvc dag       # affiche le DAG
poetry run dvc pull      # récupère les données depuis le remote (remote partagé : décision D1)
```

## Statut

| Brique | État |
|---|---|
| Environnement (Poetry, pre-commit, structure `src/`) | ✅ phase 0 |
| DVC : ingestion + validation, remote local | ✅ phase 1 (remote partagé : décision D1 en attente) |
| MLflow, API, Docker, CI, Prefect, drift | ⏳ prévu — voir [docs/PROGRESS.md](docs/PROGRESS.md) |

## Installation

Prérequis : Python 3.11, [Poetry](https://python-poetry.org/) ≥ 2.0, Git.

```bash
git clone https://github.com/aziz28-dev/mlops-project-2026-groupeB.git
cd mlops-project-2026-groupeB
poetry install                    # crée .venv et installe les dépendances
poetry run pre-commit install     # active ruff + black à chaque commit
poetry run pytest                 # lance les tests
```

## Structure

```text
src/bankmlops/      package Python (config, data, features, training, evaluation, inference, monitoring)
api/                API FastAPI (phase 6)
pipelines/          flows Prefect (phase 10)
tests/              tests unitaires et d'intégration
params.yaml         tous les paramètres (split, modèles, seuils de drift)
docs/               architecture, roadmap, suivi d'avancement, documents officiels
```

Architecture cible : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
