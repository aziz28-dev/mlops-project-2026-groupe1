# Kifech nabdew b Claude Code — guide de démarrage (binôme)

## 0. Prérequis (kol wa7ed 3al PC mte3ou)

| Outil | Lech | Vérif |
|---|---|---|
| Git | versioning | `git --version` |
| Python 3.11 | el projet | `python --version` |
| Poetry | gestion env | `poetry --version` |
| Docker Desktop | conteneurs | `docker --version` |
| VS Code + extension Claude Code | el assistant | — |
| Compte GitHub | dépôt public | — |

DVC tet7at ba3d b Poetry (phase 1), ma t7ottouhech global.

## 1. Installation du kit

1. Membre B ycréé el dépôt **public** fil GitHub : `mlops-project-2026-groupeX` (badel X b numéro el groupe).
2. Clone el dépôt fil PC, w **copie kol el contenu mta3 el kit** fih (m3a el dossiers cachés `.claude/`, `.github/`).
3. Kammel `SYNOPSIS.md` (esami w emails), w zid Membre A collaborateur fil GitHub (Settings → Collaborators).
4. Premier commit (chaque membre ycommiti b compte mte3ou) :
   ```bash
   git add .
   git commit -m "chore: initialisation du projet et synopsis"
   git push
   ```
5. Ab3thou el formulaire (wa7ed bark lel groupe) b lien el dépôt.

## 2. Kifech nesta3mlou Claude Code

1. Ftah el dossier fil VS Code → lancer Claude Code. Howa ya9ra `CLAUDE.md` wa7dou.
2. Ftah `docs/ROADMAP_PROMPTS.md`, 5ou el prompt mta3 el phase, w 7ottou fi Claude Code.
3. **Phase = branche = Pull Request.** Mathalan :
   ```bash
   git checkout -b feature/setup
   ```
4. Commandes spéciales elli 7adhertelkom :
   - `/explique DVC` → chra7 b français + derja + questions jury
   - `/verifie-phase 1` → yverifi el phase w ybaddel `docs/PROGRESS.md`
   - `/prepare-suivi` → yjama3 el contenu mta3 el 5 slides mta3 séance de suivi

## 3. Règles bech ma tet7ellouch fil soutenance

- **Kol wa7ed ycommiti b esmou**, b intizam. El prof bech ychouf `git log`.
- **Ma tcopiw kod ma fhemtouhch.** Ba3d kol phase, a3mlou `/explique <fichier>` w a9raw el questions jury.
- **Claude ma ycommitich blasetkom** (ktebnaha fil CLAUDE.md) — houwa y9tare7 message, intoma tcommitiw.
- **Ma t7ottou fil slides ken elli 5dem 7a9i9a**, b captures.
- Kol chay fih chak → `docs/reference/` (guide officiel).

## 4. Objectif 9bal séance de suivi

Phases **0 → 5** : dépôt + env, DVC, EDA, préparation, MLflow, CI lint+tests.
Ba3d `/prepare-suivi`, nraj3ou lel assistant bech ya3mel el .pptx m3a el captures el 7a9i9iyin.

## 5. Contenu du kit

```text
CLAUDE.md                     contexte + règles pour Claude Code
SYNOPSIS.md                   fiche de cadrage pré-remplie (zid esamikom)
params.yaml                   paramètres (split, modèles, seuils drift)
.pre-commit-config.yaml       ruff + black + contrôles
.gitignore                    data/models/mlruns hors Git
.claude/commands/             /explique, /verifie-phase, /prepare-suivi
docs/ROADMAP_PROMPTS.md       prompts phase par phase (0 → 11)
docs/ARCHITECTURE.md          schéma Mermaid
docs/PROGRESS.md              tableau de suivi + décisions + questions pour le prof
docs/reference/               guide officiel, template, les 2 mails
```
