# Pilotage Cursor - Iteration backend challenge admin badge - 2026-03-10

## Resume
- Strategie: `domaines restants a fort risque`.
- Perimetre: `challenge`, `admin`, `badge`.
- Objectif: fermer les boundaries HTTP restantes les plus critiques apres cloture de `exercise/auth/user`.
- Cible architecture: handlers minces, services applicatifs clairs, acces data isoles quand le ROI justifie un repository.
- Aucun changement volontaire de contrat HTTP public.
- Ordre d'execution strict, pas de travail en parallele entre lots.

## Pourquoi cette iteration est plus risquee
- `challenge_validator.py`, `challenge_ai_service.py`, `badge_service.py`, `admin_content_service.py` et `admin_stats_service.py` restent des hotspots majeurs.
- `challenge_handlers.py`, `admin_handlers.py` et `badge_handlers.py` ouvrent encore directement la DB et portent encore de l'orchestration metier.
- `admin` est heterogene: lecture, config, users, contenu, export, analytics.
- Cette iteration doit donc reduire le risque par couches, pas chercher un grand refactor global.

## Versioning interne recommande
- Point de depart: `0.1.0`
- Lot 1 valide -> `0.1.0`
- Lot 2 valide -> `0.2.0`
- Lot 3 valide -> `0.3.0`
- Lot 4 valide -> `0.4.0`
- Lot 5 valide -> `0.5.0`
- Lot 6 valide -> `0.6.0`
- Lot 7 valide -> `0.7.0`
- Iteration cloturee et gates vertes -> `1.0.0`

## Lots de l'iteration
1. `LOT 1` - Challenge query boundary
2. `LOT 2` - Challenge attempt boundary
3. `LOT 3` - Challenge AI stream boundary
4. `LOT 4` - Admin read boundary
5. `LOT 5` - Admin user and config mutation boundary
6. `LOT 6` - Admin content boundary
7. `LOT 7` - Badge boundary

## Regles globales
- un lot = un objectif = une preuve = une sortie
- aucun refactor opportuniste
- aucun changement frontend
- aucun changement volontaire de route, status code ou payload public
- toute nouvelle entree HTTP doit passer par un schema quand c'est raisonnable
- tout bug produit decouvert doit etre remonte factuellement, pas masque par un patch large
- si un lot deborde sur plusieurs domaines, stop et sous-lot recommande

## Gates minimales
- apres chaque lot: tests cibles + `black app/ server/ tests/ --check`
- apres les lots 3, 6 et 7: `pytest -q --maxfail=20`
- aucun handler du scope du lot ne doit encore ouvrir directement `db_session` a la fin du lot, sauf exception explicitement documentee dans le document du lot

## Hotspots a ne pas surinterpreter
- `challenge_validator.py` reste un monolithe a risque, mais cette iteration ne doit pas partir sur un grand redesign sans seam prouvee
- `AdminService` existe deja comme facade; le bon prochain pas est une couche applicative qui absorbe `db_session` et les branchements handler, pas une re-ecriture des sous-services admin
- `BadgeService` reste riche; le bon premier mouvement est de sortir les handlers et le wiring HTTP, pas de refaire tout le moteur de badges

## Criteres de cloture de l'iteration
- handlers `challenge`, `admin`, `badge` sensiblement aminci sur le scope traite
- aucune regression critique sur la suite backend
- docs de pilotage et versioning internes mises a jour
- delta restant explicite pour les hotspots non traites (`challenge_validator`, `badge_service`, `admin_content_service` si encore partiellement massifs)
