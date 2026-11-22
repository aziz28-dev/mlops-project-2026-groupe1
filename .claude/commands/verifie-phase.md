---
description: Vérifie qu'une phase de la roadmap est réellement terminée et met à jour docs/PROGRESS.md
argument-hint: <numéro de phase>
---

Vérifie la phase $ARGUMENTS de docs/ROADMAP_PROMPTS.md.

1. Relis sa "Définition de fini".
2. Pour chaque critère, exécute la commande de vérification (pytest, pre-commit, dvc status,
   docker, etc.) et montre-moi la sortie réelle. Si tu ne peux pas exécuter quelque chose, dis-le.
3. Donne un verdict par critère : ✅ fait (avec preuve) / ❌ pas fait / ⚠️ partiel.
4. Mets à jour docs/PROGRESS.md (crée-le s'il n'existe pas) avec un tableau :
   | Tâche | Statut | Preuve | Responsable (A/B) | Prochaine action |
   Statuts autorisés : Non commencé, En cours, Terminé, Bloqué, En attente de validation.
   Ne marque "Terminé" que si la preuve existe.
5. Liste les captures d'écran à faire pour les slides.
