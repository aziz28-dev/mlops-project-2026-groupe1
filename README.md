# Plateforme MLOps — ciblage des campagnes de télémarketing bancaire

Projet de fin de module **MLOps & Industrialisation de l'IA** (TEK-UP, 2026-2027), binôme.

## Contexte

Une banque portugaise mène des campagnes de télémarketing pour vendre des dépôts à terme ; la
majorité des appels n'aboutit pas. Le modèle estime, pour chaque client, la probabilité de
souscription (`y` = yes/no) afin d'appeler en priorité les clients les plus prometteurs.

- **Dataset :** [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) —
  `bank-additional-full.csv`, 41 188 lignes, 20 variables, licence CC BY 4.0.
- **Tâche :** classification binaire déséquilibrée (métriques : PR-AUC, F1, ROC-AUC, recall).
- **Variable exclue :** `duration` (fuite de données — justification détaillée en phase 1).

## Statut

| Brique | État |
|---|---|
| Environnement (Poetry, pre-commit, structure `src/`) | ✅ phase 0 |
| DVC, MLflow, API, Docker, CI, Prefect, drift | ⏳ prévu — voir [docs/PROGRESS.md](docs/PROGRESS.md) |

## Installation

Prérequis : Python 3.11, [Poetry](https://python-poetry.org/) ≥ 2.0, Git.

```bash
git clone https://github.com/aziz28-dev/mlops-project-2026-groupe1.git
cd mlops-project-2026-groupe1
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
