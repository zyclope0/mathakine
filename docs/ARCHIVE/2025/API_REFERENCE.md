# Référence API Mathakine

Ce document détaille tous les endpoints API disponibles dans Mathakine, leur utilisation et leurs paramètres. Les API sont organisées par catégorie et sont toutes préfixées par `/api`.

## 📚 Documentation interactive

La documentation API interactive est disponible aux URLs suivantes :

- **Swagger UI** : `/api/docs` - Interface interactive avec possibilité de tester les endpoints
- **ReDoc** : `/api/redoc` - Documentation plus lisible et mieux organisée
- **OpenAPI JSON** : `/api/openapi.json` - Spécification OpenAPI au format JSON

## 🔑 Authentification

### Obtention d'un token

```
POST /api/auth/login
```

**Corps de la requête** :
```json
{
  "username": "string",
  "password": "string"
}
```

**Réponse** (200 OK) :
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### Utilisation du token

Pour les endpoints sécurisés, ajoutez un header `Authorization` avec la valeur `Bearer {token}`.

## 👤 Endpoints Utilisateurs

### Liste des utilisateurs

```
GET /api/users/
```
- **Accès** : Gardien, Archiviste
- **Paramètres de requête** :
  - `skip` (int, défaut: 0) : Nombre d'éléments à sauter
  - `limit` (int, défaut: 100) : Nombre maximum d'éléments à retourner

### Création d'un utilisateur

```
POST /api/users/
```
- **Accès** : Public (inscription)
- **Corps de la requête** :
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

### Informations sur l'utilisateur courant

```
GET /api/users/me
```
- **Accès** : Utilisateur authentifié
- **Réponse** : Détails de l'utilisateur connecté

### Détails d'un utilisateur 

```
GET /api/users/{user_id}
```
- **Accès** : Gardien, Archiviste
- **Paramètres de chemin** :
  - `user_id` (int) : ID de l'utilisateur

### Mise à jour de l'utilisateur courant

```
PUT /api/users/me
```
- **Accès** : Utilisateur authentifié
- **Corps de la requête** : Champs à mettre à jour

### Mise à jour d'un utilisateur

```
PUT /api/users/{user_id}
```
- **Accès** : Gardien, Archiviste
- **Paramètres de chemin** :
  - `user_id` (int) : ID de l'utilisateur
- **Corps de la requête** : Champs à mettre à jour

### Progression des défis logiques d'un utilisateur

```
GET /api/users/{user_id}/challenges/progress
```
- **Accès** : L'utilisateur lui-même ou Gardien/Archiviste
- **Paramètres de chemin** :
  - `user_id` (int) : ID de l'utilisateur

### Progression globale d'un utilisateur

```
GET /api/users/{user_id}/progress
```
- **Accès** : L'utilisateur lui-même ou Gardien/Archiviste
- **Paramètres de chemin** :
  - `user_id` (int) : ID de l'utilisateur

### Suppression d'un utilisateur

```
DELETE /api/users/{user_id}
```
- **Accès** : Archiviste uniquement
- **Paramètres de chemin** :
  - `user_id` (int) : ID de l'utilisateur
- **Comportement** : Supprime l'utilisateur et toutes ses données associées en cascade
- **Réponse** :
  - 204 No Content : Suppression réussie
  - 404 Not Found : Utilisateur non trouvé
  - 500 Internal Server Error : Erreur lors de la suppression

## 📝 Endpoints Exercices

### Liste des exercices

```
GET /api/exercises/
```
- **Accès** : Public
- **Paramètres de requête** :
  - `skip` (int, défaut: 0) : Nombre d'éléments à sauter
  - `limit` (int, défaut: 100) : Nombre maximum d'éléments à retourner
  - `exercise_type` (string, optionnel) : Type d'exercice (addition, multiplication, etc.)
  - `difficulty` (string, optionnel) : Niveau de difficulté (easy, medium, hard)

### Création d'un exercice

```
POST /api/exercises/
```
- **Accès** : Gardien, Archiviste
- **Corps de la requête** : Détails de l'exercice

### Détails d'un exercice

```
GET /api/exercises/{exercise_id}
```
- **Paramètres de chemin** :
  - `exercise_id` (int) : ID de l'exercice

### Mise à jour d'un exercice

```
PUT /api/exercises/{exercise_id}
```
- **Accès** : Gardien, Archiviste
- **Paramètres de chemin** :
  - `exercise_id` (int) : ID de l'exercice
- **Corps de la requête** : Champs à mettre à jour

### Soumettre une réponse

```
POST /api/exercises/{exercise_id}/submit
```
- **Accès** : Utilisateur authentifié
- **Paramètres de chemin** :
  - `exercise_id` (int) : ID de l'exercice
- **Corps de la requête** :
```json
{
  "answer": "string"
}
```

### Générer un exercice

```
GET /api/exercises/generate
```
- **Paramètres de requête** :
  - `exercise_type` (string, optionnel) : Type d'exercice
  - `difficulty` (string, optionnel) : Niveau de difficulté
  - `use_ai` (bool, défaut: false) : Utiliser l'IA pour la génération

### Suppression d'un exercice

```
DELETE /api/exercises/{exercise_id}
```
- **Accès** : Gardien, Archiviste
- **Paramètres de chemin** :
  - `exercise_id` (int) : ID de l'exercice
- **Comportement** : Supprime l'exercice et toutes les tentatives associées en cascade
- **Réponse** :
  - 204 No Content : Suppression réussie
  - 404 Not Found : Exercice non trouvé
  - 500 Internal Server Error : Erreur lors de la suppression

## 🧩 Endpoints Défis Logiques

### Liste des défis logiques

```
GET /api/challenges/
```
- **Paramètres de requête** :
  - `skip` (int, défaut: 0) : Nombre d'éléments à sauter
  - `limit` (int, défaut: 100) : Nombre maximum d'éléments à retourner
  - `challenge_type` (string, optionnel) : Type de défi
  - `age_group` (string, optionnel) : Groupe d'âge cible
  - `active_only` (bool, défaut: true) : Ne retourner que les défis actifs

### Création d'un défi logique

```
POST /api/challenges/
```
- **Accès** : Gardien, Archiviste
- **Corps de la requête** : Détails du défi logique

### Détails d'un défi logique

```
GET /api/challenges/{challenge_id}
```
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique

### Mise à jour d'un défi logique

```
PUT /api/challenges/{challenge_id}
```
- **Accès** : Gardien, Archiviste
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique
- **Corps de la requête** : Champs à mettre à jour

### Tenter de résoudre un défi

```
POST /api/challenges/{challenge_id}/attempt
```
- **Accès** : Utilisateur authentifié
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique
- **Corps de la requête** :
```json
{
  "answer": "string"
}
```

### Obtenir un indice

```
GET /api/challenges/{challenge_id}/hint
```
- **Accès** : Utilisateur authentifié
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique
- **Paramètres de requête** :
  - `level` (int, défaut: 1) : Niveau d'indice (1-3)

### Statistiques d'un défi

```
GET /api/challenges/{challenge_id}/stats
```
- **Accès** : Gardien, Archiviste
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique

### Suppression d'un défi logique

```
DELETE /api/challenges/{challenge_id}
```
- **Accès** : Gardien, Archiviste
- **Paramètres de chemin** :
  - `challenge_id` (int) : ID du défi logique
- **Comportement** : Supprime le défi logique et toutes les tentatives associées en cascade
- **Réponse** :
  - 204 No Content : Suppression réussie
  - 404 Not Found : Défi logique non trouvé
  - 500 Internal Server Error : Erreur lors de la suppression

## 📊 Rôles et autorisations

Le système d'API utilise plusieurs niveaux de permissions :

1. **Public** : Endpoints accessibles sans authentification
2. **Utilisateur** : Nécessite un compte utilisateur standard
3. **Gardien** : Rôle de modération avec accès à la gestion des exercices et défis
4. **Archiviste** : Rôle administratif avec accès à toutes les fonctionnalités

### Hiérarchie des rôles

```
Archiviste > Gardien > Utilisateur
```

Chaque rôle supérieur possède toutes les permissions des rôles inférieurs.

## 🔄 Pagination et filtrage

La plupart des endpoints de liste supportent :

- **Pagination** via les paramètres `skip` et `limit`
- **Filtrage** via des paramètres spécifiques (ex: `exercise_type`, `difficulty`)
- **Tri** via le paramètre `sort_by` (sur certains endpoints)

## 🚀 Utilisation des webhooks

Pour certaines intégrations, Mathakine offre des webhooks permettant de recevoir des notifications lors d'événements spécifiques.

Pour configurer un webhook, contactez l'administrateur du système.

## 📋 Codes d'erreur communs

- **400 Bad Request** : Paramètres invalides
- **401 Unauthorized** : Non authentifié
- **403 Forbidden** : Permissions insuffisantes
- **404 Not Found** : Ressource non trouvée
- **500 Internal Server Error** : Erreur du serveur

Pour plus de détails sur chaque erreur, consultez le corps de la réponse qui contient un message descriptif. 