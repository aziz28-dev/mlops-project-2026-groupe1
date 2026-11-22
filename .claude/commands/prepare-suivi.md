---
description: Rassemble l'état réel du projet pour la présentation de suivi (5 diapos max)
---

Prépare le contenu de la présentation de suivi d'avancement (voir docs/reference/MAIL_2_SEANCE_SUIVI.txt).

1. Analyse l'état RÉEL du dépôt : git log (commits par auteur), docs/PROGRESS.md, dvc.yaml,
   reports/metrics.json, reports/figures/, workflows CI, tests (lance pytest --cov).
2. Produis docs/SUIVI_CONTENU.md avec, pour chacune des 5 diapos imposées, les points clés,
   les chiffres réels et la liste des captures à insérer :
   1) Équipe & projet  2) Dataset & formulation ML  3) Architecture  4) Réalisé  5) Planning & risques.
3. Sépare strictement **Réalisé (avec preuve)** et **Prévu**. N'invente aucun chiffre.
4. Ajoute un tableau de répartition des commits par membre (depuis git log).
5. Propose 8 questions probables de l'enseignant avec réponses courtes.

Ce fichier servira à générer le .pptx final.
