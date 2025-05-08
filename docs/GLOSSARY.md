# Glossaire de Mathakine

Ce document contient tous les termes spécifiques utilisés dans le projet Mathakine, organisés par catégorie pour faciliter la compréhension des différents aspects du projet.

## Table des matières

1. [Terminologie générale du projet](#terminologie-générale-du-projet)
2. [Termes pédagogiques](#termes-pédagogiques)
3. [Métaphores Star Wars](#métaphores-star-wars)
4. [Termes techniques](#termes-techniques)
5. [Termes liés aux données](#termes-liés-aux-données)
6. [Termes de développement et déploiement](#termes-de-développement-et-déploiement)

---

## Terminologie générale du projet

| Terme | Description |
|-------|-------------|
| **Mathakine** | Nom du projet d'entraînement mathématique, anciennement Math Trainer. Inspiré de l'univers Star Wars. |
| **API Rebelle** | Nom de l'API REST qui constitue le backend du projet. |
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

## Niveaux de difficulté

| Terme | Équivalent technique | Description |
|-------|---------------------|-------------|
| **Initié** | easy | Niveau de difficulté facile pour les débutants. |
| **Padawan** | medium | Niveau de difficulté intermédiaire. |
| **Chevalier** | hard | Niveau de difficulté avancé. |
| **Maître** | expert | Niveau de difficulté expert (pas encore implémenté). |

## Types d'exercices

| Terme | Équivalent technique | Description |
|-------|---------------------|-------------|
| **Addition** | addition | Exercices d'addition de nombres. |
| **Soustraction** | subtraction | Exercices de soustraction de nombres. |
| **Multiplication** | multiplication | Exercices de multiplication de nombres. |
| **Division** | division | Exercices de division de nombres. |
| **Défis de logique** | logic_challenge | Problèmes de logique pour les 10-15 ans. |

## Métaphores Star Wars

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

## Termes techniques

| Terme | Description |
|-------|-------------|
| **API REST** | Interface de programmation permettant au frontend de communiquer avec le backend. |
| **SQLite** | Base de données légère utilisée en développement. |
| **PostgreSQL** | Base de données plus robuste prévue pour la production. |
| **FastAPI** | Framework Python utilisé pour développer l'API backend. |
| **SQLAlchemy** | ORM (Object-Relational Mapping) permettant d'interagir avec la base de données. |
| **Pydantic** | Bibliothèque de validation de données utilisée avec FastAPI. |
| **JWT** | JSON Web Token, méthode d'authentification sécurisée. |
| **Docker** | Technologie de conteneurisation pour le déploiement. |
| **Render** | Plateforme de déploiement cloud. |

## Termes liés aux données

| Terme | Description |
|-------|-------------|
| **Normalisation** | Processus d'uniformisation des données pour assurer la cohérence entre les tables. |
| **Type d'exercice** | Catégorie d'exercice (addition, soustraction, etc.) stockée dans la base de données. |
| **Niveau de difficulté** | Niveau de complexité d'un exercice (easy, medium, hard) stocké dans la base de données. |
| **Statistiques utilisateur** | Données de performance stockées dans la table `user_stats`. |
| **Cohérence des données** | État où les données sont uniformes et sans contradiction entre les tables. |
| **Doublons** | Entrées multiples pour la même combinaison type/difficulté dans `user_stats`. |
| **Mappage** | Processus de conversion des variantes de format vers un format standard. |

## Termes de développement et déploiement

| Terme | Description |
|-------|-------------|
| **CI/CD** | Intégration Continue/Déploiement Continu, pratiques d'automatisation. |
| **Tests automatisés** | Tests exécutés automatiquement pour vérifier la qualité du code. |
| **Environnement de développement** | Configuration locale pour le développement. |
| **Environnement de production** | Configuration pour l'application en ligne. |
| **Migration de base de données** | Processus de transfert des données vers un nouveau système. |
| **API Gateway** | Point d'entrée unique pour toutes les requêtes API. |
| **Rate limiting** | Limitation du nombre de requêtes API dans un intervalle donné. |
| **CORS** | Cross-Origin Resource Sharing, mécanisme de sécurité pour les requêtes web. |
| **Middleware** | Composant logiciel qui s'intercale entre différentes couches d'une application. |

---

*Ce glossaire est en constante évolution à mesure que le projet se développe.*

*Dernière mise à jour : 22/07/2024* 