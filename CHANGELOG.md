# Changelog

Toutes les modifications notables du projet sont documentees dans ce fichier.

Le projet suit Semantic Versioning avec suffixe `-alpha.N` pour les releases alpha.
Source de verite release produit:
- `CHANGELOG.md`
- `frontend/package.json`

## Jalons internes du refactor backend (hors release produit)

- iteration `exercise/auth/user` : cloturee
- iteration `challenge/admin/badge` : cloturee
- iteration `Runtime Truth` : cloturee
- iteration `Contracts / Hardening` : cloturee

Reference active:
- [`bilan runtime + contracts`](docs/03-PROJECT/BILAN_BACKEND_RUNTIME_CONTRACTS_2026-03-13.md)

## [Unreleased]

### Changed
- Documentation racine, architecture, guides de test et index projet realignes sur la cloture reelle des iterations `Runtime Truth` et `Contracts / Hardening`.
- Les details lot par lot `Runtime` et `Contracts` sont desormais archives; un recapitulatif unique sert de reference active.
- La CI backend documentee et le guide de test refletent maintenant l'etat reel:
  - coverage gate `62 %`
  - faux gate `tests/api/test_admin_auth_stability.py` exclu des gates standards
  - ilots mypy plus stricts sur badge, auth session/recovery, exercise generation/query et challenge query/stream

### Fixed
- Les documents actifs ne disent plus que `Contracts / Hardening` est seulement preparee.
- `docs/03-PROJECT/CICD_DEPLOY.md` et `docs/01-GUIDES/TESTING.md` sont realignes sur la CI effective et les gates actuelles.
- Les references vers les anciens masters/lots actifs Runtime et Contracts pointent maintenant vers le recapitulatif et vers les archives.

### Notes
- Aucun bump de release produit n'est documente ici.
- Les sujets restants sont maintenant explicitement classes comme hors scope ou a peaufiner dans le recapitulatif backend actif.

## [3.1.0-alpha.8] - 2026-03-11

### Changed
- Release de consolidation backend centree sur `challenge`, `admin` et `badge`, avec handlers aminci et facades applicatives explicites sur les boundaries HTTP du scope.
- Les endpoints admin de lecture, de mutation users/config, de contenu et les endpoints badge publics/utilisateur passent desormais par des services applicatifs dedies, sans changer les contrats HTTP publics.
- Les tests API de preuve ont ete completes sur les endpoints admin content et badge afin de verifier le wiring reel des routes mutate/public du scope.

### Fixed
- La collision entre fixtures auth/admin et cleanup global des tests a ete supprimee; les namespaces de fixtures reserves ne sont plus captures par le nettoyage generique.
- Les tests challenge qui dependaient d'une selection non deterministe de `challenges[0]` utilisent desormais une fixture stable avec `correct_answer` connu.
- La stabilite locale du tree a ete retablie en excluant `tests/api/test_admin_auth_stability.py` des gates standard tant qu'il lance `pytest` dans `pytest` avec couverture.

### Notes
- Cette release reste en `alpha` : l'iteration backend `challenge/admin/badge` est cloturee en interne, mais le produit continue d'evoluer et garde des hotspots structurels hors scope (`challenge_validator.py`, `badge_service.py`, `admin_content_service.py`, `admin_stats_service.py`).

## [3.1.0-alpha.7] - 2026-03-09

### Changed
- Release de fiabilisation backend centree sur `exercise`, `auth` et `user`, avec handlers aminci, services applicatifs clarifies et boundaries HTTP preserves.
- Gestion du compte plus robuste : profil, sessions, export RGPD et suppression de compte passent desormais derriere une boundary `user` plus propre.
- Authentification plus robuste : login, refresh, verification, forgot/reset et invalidation post-reset ou post-changement de mot de passe ont ete reindustrialises sans changer les contrats HTTP publics.

### Fixed
- Reset password : les anciens `access_token` et `refresh_token` emis avant la reinitialisation sont desormais rejetes.
- Reset password : les autres sessions actives de l'utilisateur sont revoquees, et un ancien onglet doit se reconnecter au prochain controle protege.
- Changement de mot de passe depuis le profil : alignement sur le meme mecanisme de revocation (`password_changed_at` + rejet des anciens tokens).
- `POST /api/auth/resend-verification` revient a une reponse generique compatible sur email mal forme, sans fuite d'information par validation.
- `GET /api/users/me/export` est recable sur le bon handler HTTP et couvre desormais explicitement par un test API.

### Notes
- Cette release reste en `alpha` : l'iteration backend `exercise/auth/user` est maintenant cloturee en interne, mais le produit continue d'evoluer vite et garde encore des reliquats UX et des chantiers backend pour l'iteration suivante.

## [3.1.0-alpha.6] - 2026-03-07

### Added
- F07 : timeline progression avec `GET /api/users/me/progress/timeline`
- F32 : session entrelacee avec `GET /api/exercises/interleaved-plan`
- F35 : redaction des secrets URL DB au demarrage

### Changed
- Dashboard progression et visualisations harmonises
- `POST /api/exercises/generate` supporte mieux la resolution adaptive de `age_group`

## [2.1.0] - 2026-02-06

### Added
- Ordre aleatoire et option masquer les reussis pour exercices et defis
- Refonte badges
- Chatbot IA
- Espace admin
- Monitoring Sentry / Prometheus
- Options d'accessibilite

### Security
- CSRF, rate limiting, CORS, secure headers, validation JWT

## [2.0.0] et anterieur

Historique condense : exercices adaptatifs, defis logiques, authentification, verification email, badges, tableau de bord de base.
