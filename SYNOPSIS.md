# FICHE DE CADRAGE : SYNOPSIS DU PROJET MLOPS (SESSION 2026–2027)

> Fiche déposée à la racine du dépôt pour validation par l'enseignant (Jalon 1).

---

## 1. Informations Générales & Équipe

* **Titre du Projet :** Plateforme MLOps de ciblage des campagnes de télémarketing bancaire
* **Taille du groupe :** 2 étudiants (binôme)
* **Membres de l'équipe :**
  1. **Étudiant 1 (Lead Data, DVC, Modeling & MLflow, Drift) :** NOM Prénom — Email : `...`
  2. **Étudiant 2 (Lead Serving, CI/CD, CML & Prefect) :** NOM Prénom — Email : `...`
* **Lien vers le Dépôt GitHub :** `https://github.com/<compte>/mlops-project-2026-groupeX`

---

## 2. Problématique Métier & Cas d'Usage

* **Contexte Business :** Une banque portugaise mène des campagnes de télémarketing pour vendre des dépôts à terme. La grande majorité des appels n'aboutit pas à une souscription : les conseillers passent beaucoup de temps sur des clients peu susceptibles d'accepter.
* **Décision assistée :** Pour chaque client de la liste d'appel, le modèle estime la probabilité de souscription. Les conseillers appellent en priorité les clients dont la probabilité dépasse un seuil configurable.
* **Objectif métier quantifié (KPI) :** En appelant seulement les clients les mieux classés par le modèle, retrouver une part nettement plus importante des souscripteurs qu'en appelant au hasard *(KPI chiffré à fixer après l'analyse exploratoire et la baseline)*.

---

## 3. Formulation Machine Learning & Choix du Dataset

* **Type de problème ML :** Classification binaire (classes déséquilibrées)
* **Variable Cible (`Target`) :** `y` — `yes` = le client a souscrit un dépôt à terme, `no` = il n'a pas souscrit
* **Source du Dataset :** UCI Machine Learning Repository — Bank Marketing — https://archive.ics.uci.edu/dataset/222/bank+marketing (fichier `bank-additional-full.csv`, licence CC BY 4.0)
* **Volume et dimensions :** 41 188 lignes, 20 variables explicatives + 1 cible ; données collectées de mai 2008 à novembre 2010
* **Variables prédictives clés :**
  * *Variables numériques :* `age`, `campaign`, `pdays`, `previous`, `emp.var.rate`, `cons.price.idx`, `cons.conf.idx`, `euribor3m`, `nr.employed`
  * *Variables catégorielles :* `job`, `marital`, `education`, `default`, `housing`, `loan`, `contact`, `month`, `day_of_week`, `poutcome`
  * *Variable exclue :* `duration` (durée de l'appel, connue seulement après l'appel → fuite de données)
* **Métriques ML cibles :** PR-AUC et F1 sur la classe positive comme métriques principales, ROC-AUC en complément, latence d'inférence de l'API < 150 ms *(seuils chiffrés fixés après la baseline)*

---

## 4. Architecture MLOps Prévisionnelle

| Composant MLOps | Outil & Configuration retenue |
|---|---|
| **Qualité du code** | Package `src/`, Poetry, pre-commit (Ruff + Black), typage et docstrings |
| **Versioning Données** | DVC (`dvc.yaml` : ingest → validate → prepare → train) avec remote storage |
| **Tracking & Registry** | MLflow Tracking Server local (`http://127.0.0.1:5000`) & Model Registry (alias `champion`) |
| **Microservice Inférence** | API REST FastAPI (`/health`, `/predict`, `/predict/batch`) avec Swagger |
| **Validation des données** | Schémas Pydantic stricts pour les payloads + contrôles de schéma à l'ingestion |
| **Packaging & Isolation** | Image Docker multi-stage `python:3.11-slim`, utilisateur non-root, `docker-compose.yml` |
| **Intégration Continue (CI)** | GitHub Actions : lint (Ruff, Black) + Pytest (couverture > 75 %) |
| **Rapports CML** | Métriques et courbes publiées automatiquement en commentaire de Pull Request |
| **Orchestration** | Prefect 3.x (tasks atomiques avec retries, flow d'entraînement, Work Pool, CRON) |
| **Déploiement Continu** | Hors périmètre binôme (Blue/Green ou Canary en bonus si le temps le permet) |
| **Surveillance de Dérive** | KS (numériques), χ² (catégorielles), PSI calculé formellement + rapport HTML Evidently AI |
| **Export Métriques** | Hors périmètre binôme (Prometheus en bonus) |
| **Boucle de Rétroaction** | Flow Prefect de monitoring : si `drift_share >= 0.30`, alerte et déclenchement du flow de réentraînement |

---

## 5. Scénario de Dérive de Données (Data Drift)

* **Quelles variables vont dériver en production ?**
  * *Drift naturel :* les données étant ordonnées dans le temps (2008 → 2010, crise financière), les indicateurs macro-économiques (`euribor3m`, `emp.var.rate`, `nr.employed`…) et la proportion de souscriptions évoluent entre la période de référence et la période « production ».
  * *Drift simulé :* modification de l'âge et du nombre de contacts, bascule du canal `contact` et changement de répartition de `job`.
* **Méthode d'injection de la dérive :** split temporel référence / production (sans mélange) + module `DriftSimulator` (décalage gaussien sur les numériques, modification des proportions des catégories, graine fixe).
* **Seuil d'alerte :** PSI ≥ 0.20 sur une feature clé ou proportion de features en dérive (`drift_share`) ≥ 30 %.
* **Comportement du système :** génération du rapport de dérive HTML, alerte journalisée et appel du flow Prefect de réentraînement, avec enregistrement du nouveau modèle dans le Model Registry.

---

## 6. Planning Prévisionnel & Validation Enseignant

* [ ] **Jalon 1 (S2) :** Dépôt initialisé, Synopsis validé, Dataset importé sous DVC
* [ ] **Jalon 2 (S4) :** Pipeline DVC + MLflow fonctionnels, 1ers tests Pytest
* [ ] **Jalon 3 (S5) :** API FastAPI opérationnelle, Dockerfile validé, Workflow CI actif
* [ ] **Jalon 4 (S6) :** Flow Prefect orchestré, Détection de drift
* [ ] **Jalon Final :** Tag `v1.0-release`, Rapport PDF et Soutenance

> **Avis de l'Enseignant :** `[  ] VALIDÉ  /  [  ] À REVOIR`
> **Commentaires :**
