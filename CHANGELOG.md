# Changelog

Toutes les modifications notables du projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/), et le projet adhère au [Semantic Versioning](https://semver.org/lang/fr/) avec suffixe `-alpha.N` pour les versions alpha.

## [2.2.0-alpha.1] - 2026-02-22

### Added

- Pages À propos, Contact, Politique de confidentialité (RGPD)
- Bouton de signalement (FeedbackFab) : exercices, défis, bugs — icône drapeau rouge
- Filtre par groupe d'âge sur le classement
- Widget temps moyen par session sur le tableau de bord
- Recommandations : exclusion des exercices et défis déjà réussis

### Fixed

- Chevauchement footer / chatbot / FeedbackFab (z-index)

### Changed

- Footer : nouveaux liens rapides (À propos, Contact, Politique de confidentialité)

---

## [2.1.0] - 2026-02-06

### Added

- Ordre aléatoire et option « Masquer les réussis » pour exercices et défis
- Refonte badges : onglets En cours / À débloquer, rareté, épinglage
- Défis : parsing tolérant, types VISUAL multi-position
- Thèmes : Dune, Forêt, Lumière, Dinosaures
- Classement (leaderboard)
- Export PDF/Excel des données
- Assistant mathématique (chatbot IA)
- Espace admin : contenu, modération, paramètres globaux, audit
- Monitoring Sentry, Prometheus
- Options d'accessibilité (contraste, texte, animations, mode Focus TSA/TDAH)

### Security

- CSRF, rate limiting, CORS, SecureHeaders
- Validation JWT (type=access)

---

## [2.0.0] et antérieur

Historique condensé : exercices adaptatifs, défis logiques, authentification, vérification email, badges, tableau de bord de base.

---

## Convention de versioning (alpha)

- **Format** : `MAJOR.MINOR.PATCH-alpha.N` (ex. `2.2.0-alpha.1`)
- **Alpha** : fonctionnalités instables, changements fréquents
- **Incrément** : `alpha.N` à chaque release alpha significative
- **Sortie alpha** : retirer le suffixe (ex. `2.2.0`)
