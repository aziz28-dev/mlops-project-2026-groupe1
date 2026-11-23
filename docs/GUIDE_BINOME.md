# Guide de démarrage lel binôme (Membre B)

> Men : Membre A (GitHub `aziz28-dev`) · Mis à jour : thnin 23/11/2026 3achiya.
> Document temporaire : tnajjem tfas5ou ba3d ma trakkeb el projet.

## 1. El projet fi safha wa7da

Projet fin de module MLOps (prof : Haythem Ghazouani). Mouch ken modèle : **el système el kemel** elli
dayer bih (DVC, MLflow, API, Docker, CI, Prefect, drift).

| 7aja | Tafsil |
|---|---|
| Poids | Projet = 40 % mel module. Séance de suivi = 30 % mel note mta3 el projet |
| Séance de suivi | **Thletha 24/11** : 5 slides (équipe, dataset, architecture, réalisé, planning) |
| El prof ychouf | `git log` : kol wa7ed ycommiti b compte mte3ou |
| Règle d'or | `git clone` → `dvc pull` → `pytest` |

## 2. El sujet

Banque portugaise t3ayyet lel clients bech tbi3 **dépôt à terme**. El modèle y9ollek, l kol client,
9adech 3andou chance yechri. Dataset : UCI Bank Marketing (`bank-additional-full.csv`), 41 188 ligne,
cible `y` (yes/no), **11,27 % « yes »** → métriques PR-AUC, F1, ROC-AUC, recall (mouch accuracy).

3 règles :
- **`duration` mfas5a** : ma tet3refech ken ba3d el appel (data leakage).
- **Ma n5altouch el lignes** : el fichier mratteb bel date. 70 % el 9dom = référence (train/test
  stratifié), 30 % el jdod = « production » (bech nchoufou el drift).
- **`"unknown"`** = modalité, mouch NaN. **`pdays = 999`** = 3omrou ma t3ayytlou.

## 3. Chnoua t3mal (Membre A)

| Phase | Contenu | PR |
|---|---|---|
| 0 | Poetry, pre-commit (ruff + black), structure `src/`, `config.py` | #1 |
| 1 | `ingest.py`, `validate.py`, pipeline DVC `ingest → validate` | #2 |
| 2 | `notebooks/01_eda.ipynb` + 2 figures fi `reports/figures/` | #4 |
| 4 (baseline) | `prepare.py`, `build.py`, `metrics.py`, `plots.py`, `train.py` ; LogReg + RandomForest fi MLflow ; champion fil Registry (`@champion`) ; `models/model.joblib` | `feature/mlflow` |

**Les chiffres el 7a9i9iyin :**
- EDA : taux de yes 5,6 % (référence) → 24,6 % (production) ; euribor3m 4,69 → 1,14 ; contact cellular
  52 % → 90 %. Ya3ni drift 9wi.
- Baseline (test) : RF PR-AUC 0,164, LogReg 0,163 (el hasard ≈ 0,056). Fil production, ROC-AUC RF
  0,543 vs LogReg 0,633 : el drift y5arrab el modèle.
- **33 test**, couverture 87 %, w **7atta test ma ya7tej internet walla el data el 7a9i9iya**.

## 4. L'installation 3al PC mte3ek

| Outil | Verifi | Ken mouch mawjoud |
|---|---|---|
| Git | `git --version` | git-scm.com |
| Python **3.11** | `py -3.11 --version` | python.org (cochi « Add to PATH ») |
| VS Code + Claude Code | — | code.visualstudio.com |
| Docker Desktop | `docker --version` | mouch urgent (phase 7) |

**Poetry** (PowerShell) :

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -3.11 -
```

Zid `C:\Users\<enti>\AppData\Roaming\Python\Scripts` fil PATH, sakker VS Code w 7allou, w verifi
`poetry --version` (version 2.x).

**L'invitation + identité Git** : 9bal l'invitation mta3 `aziz28-dev` fil GitHub, ba3d :

```powershell
git config --global user.name "pseudo-github-mte3ek"
git config --global user.email "email-github-mte3ek@exemple.com"
```

**Clone w installation** :

```powershell
cd $HOME\Desktop
git clone https://github.com/aziz28-dev/mlops-project-2026-groupeB.git
cd mlops-project-2026-groupeB
poetry install
poetry run pre-commit install
poetry run pytest
```

Lazem tchouf **33 passed**. Ba3d 7ell el dossier fi VS Code w 5ayyer l'interpréteur `.venv`.

**El data (ken t7eb)** : `dvc pull` ma yemchich 3andek (el remote 3al PC mta3 A, décision D1). A3mel :

```powershell
poetry run dvc repro
```

Yhabbet el zip, yvalidih, yaccédi lel préparation w yt3allem el modèles (~1 minute).

## 5. El mission mte3ek

### Phase 5 — CI (el priorité, 9bal el thletha)

```powershell
git checkout main
git pull
git checkout -b feature/ci
```

7ell Claude Code (y9ra `CLAUDE.md` wa7dou) w colli el prompt « Phase 5 » men `docs/ROADMAP_PROMPTS.md`.

Kamlet ki : **CI 5adhra 3la PR** · **badge fil README** · **protection mta3 `main`**. Ma lazemhech
`dvc pull` fil CI. Preuve lel slides : capture GitHub Actions 5adhra.

### Phase 6 — API FastAPI (ba3d el phase 5)

Branche `feature/fastapi-serving`, prompt « Phase 6 ». Ma3loumet mouhemma :
- El API t7ammel `models/model.joblib` : `Pipeline` sklearn kemel (prétraitement + modèle) →
  `predict_proba(df)[:, 1]`.
- El entrée = **19 colonne** (`feature_columns(["duration"])` fi `src/bankmlops/features/build.py`).
  Fama asami fihom point (`emp.var.rate`, `cons.price.idx`, `cons.conf.idx`, `nr.employed`) → alias
  Pydantic.
- El seuil fi `params.yaml` → `train.decision_threshold`.
- 7atta nt7asmou D1, testi el API b modèle factice sghir ta3mlou fil tests.

## 6. El 9wa3ed

- Phase = branche `feature/...` = Pull Request. 3omrek ma tcommiti direct 3la `main`.
- Merge b **« Create a merge commit »** (mouch Squash).
- Claude **ma ycommitich** : y9tare7 el message, w enti tcommiti.
- Messages Conventional Commits : `feat:`, `fix:`, `docs:`, `build:`, `ci:`, `test:`.
- 9bal kol commit : `poetry run pytest` w `poetry run pre-commit run --all-files` 5odhr.
- Ba3d kol phase : baddel `docs/PROGRESS.md` (statut + preuve).
- 3omrek ma t5ammem chiffre fil slides.

## 7. El décisions

| ID | Mawdhou3 | Wad3iya |
|---|---|---|
| D1 | Remote DVC partagé | **Lazem nt7asmouha m3a b3adhna** (DagsHub mo9tara7). Bla biha ma tnajjamch tjib `model.joblib` |
| D2 | MLflow aliases (`@champion`) | Mo9tara7, nt2akdou m3a el prof |
| D3 | API t7ammel `models/model.joblib` | ✅ T7asmet (23/11) |
| D4 | Python 3.11, `numpy<2.5`, `xgboost<3.3` | ✅ T7asmet (22/11) |

## 8. Ghaltat tla9inehom (w el 7all)

| Chnoua tchouf | El 7all |
|---|---|
| `poetry` mouch ma3rouf | Sakker VS Code w 7allou, walla `& "$env:APPDATA\Python\Scripts\poetry.exe"` |
| `Your pre-commit configuration is unstaged` | Commiti `.pre-commit-config.yaml` lowel |
| Hook « Failed » + « files were modified » | 3awed `git add <fichier>` w nafs el `git commit` |
| ruff/black « Skipped » | Normal 9bal `git add` |
| Warnings LF/CRLF | Ma fihom chay (`.gitattributes`) |
| `Your local changes would be overwritten by checkout` | `git stash` → baddel branche → `git stash pop` |
| Message ghalet 3la commit mazel ma tpushach | `git reset --soft <commit>` w 3awed (3omrek ba3d push) |
| « requires Python >=3.12 » | 7added el version, ma tbaddelch Python |
| Timeout ki `poetry add` | `$env:POETRY_REQUESTS_TIMEOUT = "180"` w 3awed |
