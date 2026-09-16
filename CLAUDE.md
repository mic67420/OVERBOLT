# Instructions pour Claude Code — projet OVERBOLT | NO BS

Ce dossier est l'unique dossier de travail du projet (app + documentation +
dépôt Git). Voir [HANDOFF_claude_code.md](HANDOFF_claude_code.md) pour le
contexte complet (architecture, fonctionnalités, historique des tentatives
en cours).

`index.html` EST l'application (fichier unique HTML/CSS/JS autonome, déployé
tel quel via GitHub Pages). Il n'y a plus de fichier séparé du type
`OVERBOLT_vX.Y.html` à maintenir en parallèle — toute modification se fait
directement dans `index.html`.

## Workflow Git automatique

Après chaque modification significative du projet (nouvelle fonctionnalité,
correction de bug, changement de version), effectue automatiquement, sans
attendre que l'utilisateur le demande explicitement :

1. `git add` des fichiers modifiés
2. `git commit` avec un message descriptif de ce qui a changé
3. `git push origin main` vers GitHub

Confirme simplement à l'utilisateur ce qui a été poussé une fois fait —
pas besoin de redemander la permission à chaque fois, c'est le comportement
attendu par défaut pour ce projet.

## Conventions du projet

- Numéro de version affiché dans l'app (en-tête + `<title>`) : à incrémenter
  à CHAQUE modification, format `vX.Y`.
- `sw.js` : incrémenter `CACHE_NAME` (v2, v3...) à chaque changement de
  fichiers pour forcer le rafraîchissement du cache PWA.
- Toujours vérifier la syntaxe avant de pousser.
- Le client (propriétaire du projet) n'est pas très technique : toute
  instruction manuelle qu'il doit exécuter lui-même doit être détaillée
  pas à pas.
