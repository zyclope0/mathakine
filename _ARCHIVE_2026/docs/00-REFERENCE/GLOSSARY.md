# 📖 GLOSSAIRE - MATHAKINE

**Version** : 2.0.0  
**Date** : 20 novembre 2025

---

## A

### API (Application Programming Interface)
Interface de programmation permettant la communication entre le frontend et le backend via HTTP/REST.

### Alembic
Outil de migration de base de données pour SQLAlchemy. Utilisé pour gérer les changements de schéma.

### App Router
Nouveau système de routing de Next.js basé sur le système de fichiers dans le dossier `app/`.

---

## B

### Badge
Récompense virtuelle attribuée à un utilisateur lors de la réalisation d'objectifs spécifiques.

### Backend
Serveur Starlette exposant 37 routes API JSON. Port 8000.

---

## C

### Challenge
Défi logique ou mathématique plus complexe qu'un exercice simple. Types : SEQUENCE, PATTERN, PUZZLE, CALCULATION, CHESS.

### CORS (Cross-Origin Resource Sharing)
Mécanisme de sécurité permettant au frontend (3000) d'accéder au backend (8000).

### Coverage
Pourcentage de code couvert par les tests automatisés. Cible : 60%+.

---

## D

### DRY (Don't Repeat Yourself)
Principe éliminant la duplication de code. Appliqué en Phase 3 avec centralisation des constantes.

---

## E

### Exercise
Exercice mathématique simple (addition, soustraction, multiplication, division).

### Enum (Enumeration)
Type Python définissant un ensemble fixe de valeurs. Ex : `ExerciseTypes`, `DifficultyLevels`.

---

## F

### FastAPI
Framework Python pour APIs. Utilisé pour les docs OpenAPI, mais routes principales via Starlette.

### Frontend
Application Next.js servie sur le port 3000. Interface utilisateur complète.

---

## G

### Gamification
Système de points, niveaux, badges pour motiver l'apprentissage.

---

## H

### Handlers
Fonctions Python traitant les requêtes HTTP dans `server/handlers/`.

### HTTP-only Cookie
Cookie non accessible via JavaScript (protection XSS). Utilisé pour stocker JWT.

---

## I

### i18n (Internationalization)
Système de traduction (FR/EN) via next-intl.

---

## J

### JWT (JSON Web Token)
Token d'authentification signé, stocké dans cookie HTTP-only. Expiration : 30 min.

---

## L

### Loguru
Bibliothèque Python de logging avancé avec couleurs et formatage.

---

## M

### Migration
Changement de schéma de base de données géré par Alembic.

---

## N

### Next.js
Framework React pour le frontend. Version 16 (App Router).

### Normalization
Conversion de valeurs vers un format standardisé. Ex : `"sequence"` → `"SEQUENCE"`.

---

## O

### ORM (Object-Relational Mapping)
SQLAlchemy 2.0. Mapping Python ↔ SQL.

---

## P

### Phase
Étape du projet de refactoring. Phases 1-6 complétées.

### PostgreSQL
Base de données production. Version 15+.

### PWA (Progressive Web App)
Application web installable avec service worker.

---

## R

### REST (Representational State Transfer)
Style d'architecture API avec HTTP methods (GET, POST, PUT, DELETE).

### Render
Plateforme de déploiement cloud. Hosting frontend + backend + PostgreSQL.

---

## S

### SQLAlchemy
ORM Python. Version 2.0 utilisée exclusivement (post-Phase 4).

### SSE (Server-Sent Events)
Streaming unidirectionnel serveur → client. Utilisé pour génération IA.

### Starlette
Framework Python ASGI léger. Backend API Mathakine (37 routes JSON).

---

## T

### TanStack Query
Bibliothèque React pour gestion état serveur (anciennement React Query).

### TypeScript
Superset de JavaScript avec typage statique. Utilisé en mode strict.

---

## Z

### Zustand
Bibliothèque React pour state management global léger.

---

## 🔤 ACRONYMES COURANTS

| Acronyme | Signification | Usage |
|----------|---------------|-------|
| **API** | Application Programming Interface | Backend JSON |
| **CORS** | Cross-Origin Resource Sharing | Sécurité |
| **DRY** | Don't Repeat Yourself | Principe |
| **JWT** | JSON Web Token | Auth |
| **ORM** | Object-Relational Mapping | SQLAlchemy |
| **PWA** | Progressive Web App | Frontend |
| **REST** | Representational State Transfer | API |
| **SSE** | Server-Sent Events | Streaming |

---

## 📚 TERMES MÉTIER

### Age Group
Tranche d'âge cible : `GROUP_6_8`, `GROUP_10_12`, `GROUP_13_15`.

### Challenge Type
Type de défi : `SEQUENCE`, `PATTERN`, `PUZZLE`, `CALCULATION`, `CHESS`.

### Difficulty
Niveau de difficulté : `EASY`, `MEDIUM`, `HARD`.

### Exercise Type
Type d'exercice : `ADDITION`, `SUBTRACTION`, `MULTIPLICATION`, `DIVISION`.

### Hint Level
Niveau d'indice pour challenges : `level_1`, `level_2`, `level_3`.

### Role
Rôle utilisateur : `student`, `teacher`, `admin`.

---

## 🏗️ ARCHITECTURE

### Dual Backend (obsolète)
Ancienne architecture avec FastAPI (API) + Starlette (web). **Remplacée** en Phase 2 par backend Starlette API pur.

### Service Layer
Couche métier entre handlers et base de données. Contient logique ORM.

### Constants Centralization
Principe de la Phase 3 : Une source unique de vérité pour constantes dans `app/core/constants.py`.

---

## 📝 CONVENTIONS

### Naming
- **Files** : `snake_case.py`
- **Classes** : `PascalCase`
- **Functions** : `snake_case()`
- **Constants** : `UPPER_SNAKE_CASE`
- **Variables** : `snake_case`

### Database
- **Tables** : `snake_case` (pluriel)
- **Columns** : `snake_case`
- **Enums** : `UPPER_SNAKE_CASE`

### API
- **Routes** : `/api/resource` (pluriel)
- **Methods** : GET, POST, PUT, DELETE
- **Responses** : JSON camelCase

---

## 🔗 RÉFÉRENCES

- **Architecture** : [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **API** : [`API.md`](API.md)
- **Getting Started** : [`GETTING_STARTED.md`](GETTING_STARTED.md)

---

**Glossaire maintenu à jour avec la terminologie du projet.**

