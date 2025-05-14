# Glossaire Mathakine

Ce glossaire définit tous les termes spécifiques utilisés dans le projet Mathakine, organisés par catégories pour faciliter la compréhension du projet.

## Table des matières

1. [Terminologie du projet](#terminologie-du-projet)
2. [Termes pédagogiques](#termes-pédagogiques)
   - [Niveaux de difficulté](#niveaux-de-difficulté)
   - [Types d'exercices](#types-dexercices)
3. [Thème Star Wars](#thème-star-wars)
4. [Terminologie technique](#terminologie-technique)
   - [Architecture et composants](#architecture-et-composants)
   - [Base de données](#base-de-données)
   - [Interface utilisateur](#interface-utilisateur)
5. [Développement et déploiement](#développement-et-déploiement)

---

## Terminologie du projet

| Terme | Description |
|-------|-------------|
| **Mathakine** | Nom du projet d'entraînement mathématique, anciennement "Math Trainer". Inspiré de l'univers Star Wars. |
| **API Rebelle** | Nom de l'API REST qui constitue le backend du projet (Itération 3). |
| **Frontend Académie** | L'interface utilisateur que les enfants utilisent pour interagir avec l'application. |
| **Backend Temple** | Le serveur et les services backend qui gèrent la logique métier. |
| **Archives** | La base de données du projet. |
| **Textes Anciens** | La documentation du projet. |

## Termes pédagogiques

| Terme | Description |
|-------|-------------|
| **Exercice** (Épreuve) | Un problème mathématique à résoudre par l'utilisateur. |
| **Force des nombres** | Les compétences mathématiques que l'utilisateur développe. |
| **Padawan** | Un utilisateur apprenant les mathématiques. |
| **Parcours d'apprentissage** | La séquence d'exercices recommandée pour l'utilisateur. |
| **Célébration de réussite** | Animation affichée après la réussite d'un exercice. |
| **Défis de logique** | Problèmes de logique mathématique pour les 10-15 ans. |
| **Interface holographique** | Style visuel des exercices inspiré des hologrammes de Star Wars. |

### Niveaux de difficulté

| Terme | Code technique | Description |
|-------|----------------|-------------|
| **Initié** | `easy` | Niveau de difficulté facile pour les débutants. Opérations avec les nombres 1-10. |
| **Padawan** | `medium` | Niveau de difficulté intermédiaire. Opérations avec les nombres 10-50. |
| **Chevalier** | `hard` | Niveau de difficulté avancé. Opérations avec les nombres 50-100. |
| **Maître** | `expert` | Niveau de difficulté expert. Opérations avec les nombres 100-500. |

### Types d'exercices

| Terme | Code technique | Description |
|-------|----------------|-------------|
| **Addition** | `addition` | Exercices d'addition de nombres. |
| **Soustraction** | `subtraction` | Exercices de soustraction de nombres. |
| **Multiplication** | `multiplication` | Exercices de multiplication de nombres. |
| **Division** | `division` | Exercices de division de nombres. |
| **Fractions** | `fractions` | Exercices sur les opérations avec fractions. |
| **Géométrie** | `geometry` | Exercices sur les figures géométriques et leurs propriétés. |
| **Divers (Problèmes)** | `mixed` | Exercices variés sous forme de problèmes à résoudre. |
| **Défis de logique** | `logic_challenge` | Problèmes de logique adaptés aux 10-15 ans. |

## Thème Star Wars

| Terme | Signification technique |
|-------|------------------------|
| **Épreuves d'Initié** | Tests unitaires |
| **Épreuves de Chevalier** | Tests d'intégration |
| **Épreuves de Maître** | Tests de performance |
| **Épreuves du Conseil Jedi** | Défis logiques pour les 10-15 ans |
| **Cristaux d'Identité** | Système d'authentification JWT |
| **Boucliers Déflecteurs** | Middleware de sécurité |
| **Holocrons** | Documentation API (Swagger/OpenAPI) |
| **Côté Lumineux** | Mode d'interface claire |
| **Côté Obscur** | Mode d'interface sombre |
| **Sabre lumineux** | Barre de progression |
| **Mémoire Hyperespace** | Système de cache Redis |
| **Senseurs Longue Portée** | Monitoring et alerting |
| **Modules d'Expansion** | Conteneurs Docker |
| **Vitesse Hyperdrive** | Performance optimale de l'API |
| **Protocole d'Harmonie** | Système de normalisation des données |
| **Ordre Jedi des Mathématiques** | Système de médailles et récompenses (prévu pour l'itération 4) |

## Terminologie technique

### Architecture et composants

| Terme | Description |
|-------|-------------|
| **API REST** | Interface de programmation permettant au frontend de communiquer avec le backend. |
| **FastAPI** | Framework Python utilisé pour développer l'API backend. |
| **Starlette** | Framework sous-jacent à FastAPI, utilisé dans `enhanced_server.py`. |
| **CLI** | Interface en ligne de commande (`mathakine_cli.py`). |
| **Pydantic** | Bibliothèque de validation de données utilisée avec FastAPI. |
| **JWT** | JSON Web Token, méthode d'authentification sécurisée. |
| **Jinja2** | Moteur de templates HTML utilisé par Starlette pour le rendu des pages. |
| **Middleware** | Composant logiciel qui s'intercale entre différentes couches d'une application. |
| **API Gateway** | Point d'entrée unique pour toutes les requêtes API. |
| **Rate limiting** | Limitation du nombre de requêtes API dans un intervalle donné. |
| **CORS** | Cross-Origin Resource Sharing, mécanisme de sécurité pour les requêtes web. |

### Base de données

| Terme | Description |
|-------|-------------|
| **SQLite** | Base de données légère utilisée en développement. |
| **PostgreSQL** | Base de données robuste utilisée en production. |
| **SQLAlchemy** | ORM (Object-Relational Mapping) permettant d'interagir avec la base de données. |
| **Alembic** | Outil de migration de base de données utilisé avec SQLAlchemy. |
| **Normalisation** | Processus d'uniformisation des données pour assurer la cohérence entre les tables. |
| **Statistiques utilisateur** | Données de performance stockées dans la table `user_stats`. |
| **Résultats** | Données sur les tentatives de réponses stockées dans la table `results`. |
| **Doublons** | Entrées multiples pour la même combinaison type/difficulté dans `user_stats`. |
| **Mappage** | Processus de conversion des variantes de format vers un format standard. |
| **Cascade de suppression** | Mécanisme permettant de supprimer automatiquement les enregistrements liés. |
| **Intégrité référentielle** | Principe garantissant que les relations entre tables restent valides. |

### Interface utilisateur

| Terme | Description |
|-------|-------------|
| **Hero section** | Section principale de la page d'accueil présentant l'application. |
| **Badges de type** | Indicateurs visuels du type d'exercice avec code couleur. |
| **Badges de difficulté** | Indicateurs visuels du niveau de difficulté avec code couleur. |
| **Badge IA** | Indicateur des exercices générés par IA avec une icône de robot. |
| **Card UI** | Interface basée sur des cartes pour présenter les exercices. |
| **Vue grille** | Affichage des exercices en format grille (par défaut). |
| **Vue liste** | Affichage des exercices en format liste (alternatif). |
| **Modalité** | Fenêtre qui s'affiche par-dessus le contenu pour des interactions spécifiques. |
| **CSS utilitaires** | Classes CSS réutilisables pour la mise en page (mt-3, d-flex, etc.). |
| **Thème spatial** | Style visuel inspiré de l'espace et de Star Wars. |

## Développement et déploiement

| Terme | Description |
|-------|-------------|
| **CI/CD** | Intégration Continue/Déploiement Continu, pratiques d'automatisation. |
| **Tests automatisés** | Tests exécutés automatiquement pour vérifier la qualité du code. |
| **Environnement de développement** | Configuration locale pour le développement. |
| **Environnement de production** | Configuration pour l'application en ligne. |
| **Docker** | Technologie de conteneurisation pour le déploiement. |
| **Render** | Plateforme de déploiement cloud recommandée pour le projet. |
| **Heroku** | Plateforme de déploiement alternative. |
| **Fly.io** | Option de déploiement basée sur Docker. |
| **Migration de base de données** | Processus de transfert des données vers un nouveau système. |
| **Profil de configuration** | Ensemble de paramètres adaptés à un environnement spécifique. |
| **Centralized Logging** | Système de journalisation centralisé avec rotation des logs. |

---

*Ce glossaire est maintenu à jour à mesure que le projet évolue. Pour toute question ou suggestion d'ajout, consultez l'équipe de documentation.*

*Dernière mise à jour : 12 juin 2025* 