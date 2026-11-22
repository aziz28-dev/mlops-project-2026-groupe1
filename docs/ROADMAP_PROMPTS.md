# ROADMAP — Prompts à coller dans Claude Code, phase par phase

**Mode d'emploi :** ouvrir le dossier du projet dans VS Code → lancer Claude Code → coller le prompt
de la phase en cours. Une phase = une branche Git = une Pull Request.
Ne passez à la phase suivante que quand la **Définition de "fini"** est cochée.

Rôles : **A** = Data, Modeling & Drift — **B** = Serving, CI/CD & Orchestration.

| Phase | Responsable | Remarque |
|---|---|---|
| 0 | A | Réattribuée (prévue pour B) : A démarre seul le premier soir |
| 1 → 4 | A | — |
| 5 | B | — |
| 6 → 7 | B | B commence la phase 6 juste après la phase 5 |
| 8 | A + B | — |
| 9 | A | — |
| 10 | B | — |
| 11 | A + B | — |

> 🎯 **Avant la séance de suivi (notée 30 %) : phases 0 → 5 terminées.**
> C'est ce qui remplit la diapo 4 « Travail réalisé » avec de vraies preuves.

---

## Phase 0 — Initialisation du dépôt et de l'environnement · A · branche `feature/setup`

```text
Lis CLAUDE.md et les documents de docs/reference/. Puis résume-moi en 10 lignes ce que tu as compris
du projet et du périmètre binôme, pour que je valide avant de commencer.

Ensuite, phase 0 : initialise le projet.
1. Vérifie les versions installées : python, poetry, git, docker, dvc (dis-moi ce qui manque et comment l'installer sur mon OS).
2. Crée pyproject.toml avec Poetry (Python 3.11, package src/bankmlops), dépendances de base
   (pandas, numpy, scikit-learn, xgboost, pyyaml) et dev (pytest, pytest-cov, ruff, black, pre-commit).
3. Crée l'arborescence décrite dans CLAUDE.md section 5 avec des __init__.py et un module config.py
   qui charge params.yaml.
4. Active pre-commit avec le .pre-commit-config.yaml fourni (lance `pre-commit autoupdate`).
5. Écris un README.md initial (titre, contexte, structure, commandes d'installation).
6. Écris un premier test tests/unit/test_config.py.
Explique chaque fichier. Propose-moi les messages de commit, je committe moi-même.
```

**Fini quand :** `poetry install` OK · `pre-commit run --all-files` vert · `pytest` vert · dépôt GitHub public
`mlops-project-2026-groupeX` poussé avec `SYNOPSIS.md`.
**Preuve slides :** arborescence + historique de commits + lien du dépôt.

---

## Phase 1 — Ingestion, validation et versioning DVC · A · branche `feature/dvc-data`

```text
Phase 1 (voir CLAUDE.md). Objectif : données brutes versionnées avec DVC.
1. Explique-moi d'abord DVC (rôle, .dvc, dvc.yaml, dvc.lock, remote, cache) avec une analogie en derja.
2. Écris src/bankmlops/data/ingest.py : télécharge le zip officiel UCI Bank Marketing, extrait
   bank-additional-full.csv et bank-additional-names.txt dans data/raw/. Vérifie toi-même l'URL
   de téléchargement depuis la page https://archive.ics.uci.edu/dataset/222/bank+marketing.
3. Écris src/bankmlops/data/validate.py : contrôles de schéma (colonnes attendues, types, valeurs
   de la cible, nombre de lignes) qui lèvent une erreur claire si quelque chose cloche.
4. dvc init, configure un remote LOCAL pour l'instant, et crée dvc.yaml avec les stages
   `ingest` et `validate`. Lance `dvc repro` puis `dvc push`.
5. Présente-moi les options pour la décision D1 (remote accessible en CI) — ne choisis pas à ma place.
6. Tests unitaires pour validate.py (avec un petit DataFrame factice dans conftest.py).
Lis bank-additional-names.txt et confirme-moi : l'ordre chronologique des lignes et la note sur `duration`.
```

**Fini quand :** `dvc repro` rejoue sans erreur · `dvc status` propre · data/raw absent de Git · tests verts.
**Preuve slides :** capture `dvc dag` + `dvc status` + extrait de `dvc.yaml`.

---

## Phase 2 — EDA (exploration) · A · branche `feature/eda`

```text
Phase 2 : crée notebooks/01_eda.ipynb (exploration uniquement, pas de logique réutilisable dedans).
Je veux : dimensions, types, taux de la classe positive, valeurs "unknown" par colonne, pdays=999,
distributions des numériques, cardinalité des catégorielles, et SURTOUT une comparaison
"premières lignes vs dernières lignes" (par ex. euribor3m, emp.var.rate, taux de y) pour montrer
que le drift est naturel. Sauvegarde 3–4 figures propres dans reports/figures/.
Après exécution, écris-moi un résumé des VRAIES observations (chiffres sortis du notebook,
rien d'inventé) que je pourrai mettre dans la diapo 2.
```

**Fini quand :** notebook exécuté de bout en bout · figures sauvegardées · résumé validé.
**Preuve slides :** 1–2 graphiques (déséquilibre de classe + drift macro dans le temps).

---

## Phase 3 — Préparation, split temporel et features · A · branche `feature/prepare`

```text
Phase 3. Écris :
- src/bankmlops/data/prepare.py : suppression de `duration`, traitement de pdays=999 et des
  "unknown" (propose-moi les options et justifie), split TEMPOREL reference / production selon
  params.yaml (sans shuffle), puis split train/test stratifié dans la référence.
- src/bankmlops/features/build.py : ColumnTransformer sklearn (scaling numériques, one-hot
  catégorielles) dans une fonction typée et documentée.
Ajoute le stage `prepare` à dvc.yaml (deps, params, outs). Tests : pas de `duration` dans les
features, pas de fuite entre train et test, colonnes de sortie stables.
```

**Fini quand :** `dvc repro` produit `data/processed/*` · tests verts.

---

## Phase 4 — Entraînement + MLflow Tracking & Registry · A · branche `feature/mlflow`

```text
Phase 4. Explique d'abord MLflow (run, experiment, params, metrics, artifacts, Model Registry,
aliases vs stages — décision D2) en français + derja.
Puis écris src/bankmlops/training/train.py :
- entraîne 3 modèles configurés dans params.yaml : LogisticRegression, RandomForest, XGBoost
  (pipeline = preprocessing + modèle) ;
- logge dans MLflow : params, PR-AUC, ROC-AUC, F1, recall, precision, matrice de confusion (PNG),
  courbe PR (PNG), le modèle avec signature et input_example ;
- écrit reports/metrics.json (lu par DVC et plus tard par CML) ;
- enregistre le meilleur modèle (selon PR-AUC) dans le Registry avec l'alias `champion`
  et exporte-le dans models/model.joblib (décision D3).
Vérifie la version de MLflow installée avant d'écrire le code. Ajoute le stage `train`
à dvc.yaml avec `metrics: reports/metrics.json`. Donne-moi les commandes pour lancer le serveur
MLflow et ce que je dois capturer pour les slides.
```

**Fini quand :** 3 runs visibles dans MLflow UI · modèle `champion` dans le Registry · `dvc metrics show` OK.
**Preuve slides :** capture MLflow (comparaison des runs) + capture du Registry.

---

## Phase 5 — Premier workflow CI (lint + tests) · B · branche `feature/ci`

```text
Phase 5. Explique GitHub Actions (workflow, job, step, runner, déclencheurs push/pull_request).
Crée .github/workflows/ci.yml : checkout, setup Python 3.11, cache, installation Poetry,
ruff + black --check, pytest avec couverture (rapport dans le log).
Les tests ne doivent pas dépendre des données réelles (fixtures factices).
Ajoute le badge CI dans le README. Dis-moi comment vérifier que la CI bloque un merge si elle échoue
(branch protection sur main).
```

**Fini quand :** CI verte sur une PR · badge dans le README · protection de `main` activée.
**Preuve slides :** capture GitHub Actions verte.

> ✅ **Ici : préparer la présentation de suivi** (demande à ton assistant de faire le .pptx à partir de
> `docs/PROGRESS.md` et des captures).

---

## Phase 6 — API FastAPI + Pydantic · B · branche `feature/fastapi-serving`

```text
Phase 6. Écris :
- api/schemas.py : modèles Pydantic v2 stricts pour un client (types, bornes, Literal pour les
  catégorielles avec les modalités réelles du dataset), réponse avec probabilité + décision.
- src/bankmlops/inference/predictor.py : charge models/model.joblib une seule fois.
- api/main.py : GET /health (statut + version du modèle), POST /predict (unitaire),
  POST /predict/batch (liste), gestion d'erreurs propre, docs Swagger.
Tests d'intégration avec TestClient (payload valide, payload invalide → 422, batch).
Donne-moi des exemples curl à utiliser pendant la démo.
```

**Fini quand :** Swagger accessible · tests API verts · exemples curl fonctionnels.

---

## Phase 7 — Docker multi-stage non-root + docker-compose · B · branche `feature/docker`

```text
Phase 7. Explique multi-stage, image slim, utilisateur non-root, HEALTHCHECK, .dockerignore.
Crée Dockerfile (builder + runtime python:3.11-slim, user non-root, HEALTHCHECK sur /health)
et docker-compose.yml (service api ; service mlflow optionnel). Exporte requirements.txt depuis
Poetry. Donne-moi les commandes pour mesurer la taille de l'image et vérifier que le process
ne tourne pas en root (docker exec ... whoami).
```

**Fini quand :** `docker compose up --build` → `/health` OK · `whoami` ≠ root · taille de l'image notée.

---

## Phase 8 — Tests complets (couverture > 75 %) + CML sur Pull Request · A + B · branche `feature/cml`

```text
Phase 8. 1) Complète la pyramide de tests jusqu'à > 75 % de couverture (unitaires, schéma,
inférence). Montre-moi le rapport de couverture.
2) Explique CML. Crée .github/workflows/cml.yml : sur pull_request, récupère les données
(selon la décision D1), lance `dvc repro`, puis publie en commentaire de PR : tableau de
`dvc metrics diff main`, matrice de confusion et courbe PR. Liste-moi les secrets GitHub à configurer.
```

**Fini quand :** couverture > 75 % · commentaire CML automatique visible sur une PR.

---

## Phase 9 — Détection de drift + simulateur · A · branche `feature/drift`

```text
Phase 9. Explique KS, χ² et PSI (formules, interprétation, seuils) en français + derja.
Écris :
- src/bankmlops/monitoring/drift_stats.py : KS (numériques), χ² (catégorielles), PSI (implémenté
  à la main avec binning sur la référence), résultat par feature + drift_share global ;
  seuils dans params.yaml (PSI ≥ 0.20, drift_share ≥ 0.30).
- src/bankmlops/monitoring/drift_simulator.py : génère des lots de production modifiés
  (décalage gaussien sur des numériques, changement de proportions de catégories), reproductible (seed).
- src/bankmlops/monitoring/evidently_report.py : rapport HTML Evidently reference vs production
  (vérifie l'API de la version installée d'Evidently).
Tests : distributions identiques → pas de drift ; décalage fort → drift détecté ; PSI connu sur un
exemple calculé à la main. Lance sur le drift naturel (production réelle) ET sur un lot simulé,
et donne-moi les vrais résultats.
```

**Fini quand :** rapport `reports/drift_report.html` généré · tests drift verts · résultats réels notés.

---

## Phase 10 — Orchestration Prefect 3.x · B · branche `feature/prefect`

```text
Phase 10. Explique Prefect 3 (task, flow, retries, deployment, work pool, worker, schedule CRON)
en français + derja. Vérifie la version installée.
Crée pipelines/training_flow.py (tasks atomiques : ingest → validate → prepare → train → register,
avec retries) et pipelines/monitoring_flow.py (charge un lot de production → calcule le drift →
si drift_share ≥ seuil : log d'alerte et appel du training_flow).
Crée prefect.yaml (déploiements déclaratifs) avec un work pool de type process et un schedule CRON.
Donne-moi les commandes pour lancer le serveur Prefect, le worker, et déclencher les flows pour la démo.
```

**Fini quand :** flows visibles dans l'UI Prefect · run planifié par CRON · retries démontrés.

---

## Phase 11 — Finalisation : README, rapport, démo, release · A + B

```text
Phase 11. 1) Finalise le README : badges, reproduction en 3 commandes (git clone, dvc pull, pytest),
schéma d'architecture Mermaid, captures. 2) Écris un script de démo pas-à-pas (docs/DEMO.md)
pour la séance 7 : CI, docker build/run, curl, MLflow UI, rapport de drift, Prefect.
3) Aide-moi à structurer le rapport PDF (6–8 pages) à partir des VRAIS résultats.
4) Prépare 20 questions techniques probables du jury avec réponses courtes.
Enfin : tag v1.0-release.
```

---

## Commandes slash disponibles (dossier `.claude/commands/`)

- `/explique <sujet>` — explication pédagogique français + derja + questions de jury.
- `/verifie-phase <n>` — vérifie la "Définition de fini" d'une phase et met à jour `docs/PROGRESS.md`.
- `/prepare-suivi` — rassemble l'état réel du projet pour préparer les 5 diapos de la séance de suivi.
