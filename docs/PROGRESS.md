# Suivi d'avancement

Mis à jour après chaque phase (commande `/verifie-phase <n>`).
Statuts : Non commencé · En cours · Terminé · Bloqué · En attente de validation.

**Organisation de démarrage :** A fait les phases 0 → 4 (la phase 0 était prévue pour B, réattribuée
à A car A démarre seul le premier soir). B prend la phase 5 (CI) puis commence la phase 6 (FastAPI).
Objectif : phases 0 → 5 terminées avant la séance de suivi notée.

## Plan avant la séance de suivi (mardi 24/11)

| Créneau | Qui | Contenu | Hors de ce créneau |
|---|---|---|---|
| Dim. 22/11 soir | A | Phase 0 puis phase 1, versions simples | — |
| Lun. 23/11 journée | B | Phase 5 (CI lint + tests) | A indisponible (travail) |
| Lun. 23/11 soir | A | Phase 2 courte : 2 figures (déséquilibre de `y`, drift macro dans le temps) | Reste de l'EDA |
| Lun. 23/11 soir | A | Phase 4 « baseline » : préparation minimale (suppression de `duration`, split temporel, one-hot) + LogReg et RandomForest loggés dans MLflow | Phase 3 complète, XGBoost |
| Après la séance | A | Phase 3 complète (`pdays=999`, `unknown`, `build.py`, tests), XGBoost | — |

Pour la séance : phase 3 = « partielle (préparation minimale dans la baseline) » et phase 4 =
« baseline » ; à présenter comme tel sur la diapo 4 (réalisé vs prévu).

**Points de vigilance (vérifiés le 22/11 au soir) :**
- **Poetry non installé** → bloquant pour la phase 0.
- Docker non installé → pas bloquant avant la phase 7.
- Dataset UCI : téléchargement OK depuis `https://archive.ics.uci.edu/static/public/222/bank+marketing.zip`
  (zip imbriqué : `bank-additional.zip` → `bank-additional/bank-additional-full.csv`, 5,8 Mo, et
  `bank-additional-names.txt`).
- La CI de B (phase 5) suppose que le dépôt GitHub existe et que la phase 0 y est poussée ; les tests
  doivent tourner sur des données factices (conftest), car le remote DVC (D1) n'est pas encore choisi.

| Phase | Tâche | Responsable | Statut | Preuve | Prochaine action |
|---|---|---|---|---|---|
| — | Formulaire groupe soumis | A + B | Non commencé | — | Un seul envoi par groupe |
| — | SYNOPSIS.md complété (noms, emails) | A + B | En cours | SYNOPSIS.md | Compléter les noms, pousser sur GitHub |
| 0 | Dépôt + environnement + pre-commit | A | En cours | Résumé du projet validé (pas encore de fichier produit) | Installer Poetry, choisir l'option Git, puis exécuter la phase 0 |
| 1 | Ingestion + validation + DVC | A | Non commencé | — | Dim. 22/11 soir, après la phase 0 |
| 2 | EDA (version courte : 2 figures) | A | Non commencé | — | Lun. 23/11 soir |
| 3 | Préparation + split temporel | A | Non commencé | — | Minimal dans la phase 4 baseline ; version complète après le 24/11 |
| 4 | Entraînement + MLflow (baseline LogReg + RF) | A | Non commencé | — | Lun. 23/11 soir ; XGBoost après le 24/11 |
| 5 | CI lint + tests | B | Non commencé | — | Lun. 23/11 (dépend du dépôt GitHub + phase 0 poussée) |
| 6 | API FastAPI | B | Non commencé | — | — |
| 7 | Docker | B | Non commencé | — | — |
| 8 | Couverture > 75 % + CML | A + B | Non commencé | — | — |
| 9 | Drift + simulateur | A | Non commencé | — | — |
| 10 | Prefect | B | Non commencé | — | — |
| 11 | README, rapport, démo, v1.0-release | A + B | Non commencé | — | — |

## Décisions
| ID | Sujet | Décision | Date |
|---|---|---|---|
| D1 | Remote DVC accessible en CI | À trancher | — |
| D2 | MLflow stages vs aliases | Aliases proposés (à confirmer) | — |
| D3 | Chargement du modèle par l'API | Artefact exporté proposé (à confirmer) | — |

## Questions pour l'enseignant
- Format de la soutenance finale : avec slides (guide) ou sans slides (mail 1) ?
- Les aliases MLflow (`@champion`) sont-ils acceptés à la place des stages Staging/Production ?
