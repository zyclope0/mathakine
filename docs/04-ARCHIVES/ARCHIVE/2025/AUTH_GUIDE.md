# Guide d'Authentification - Mathakine

Ce document décrit le système d'authentification de Mathakine, basé sur les tokens JWT (JSON Web Tokens) et sur la gestion des rôles utilisateurs selon la thématique Star Wars.

## Vue d'ensemble

Le système d'authentification de Mathakine est surnommé "Les Cristaux d'Identité" dans la terminologie du projet. Il s'agit d'un système d'authentification moderne et sécurisé basé sur JWT, offrant :

- Inscription et création de compte
- Connexion et génération de tokens
- Gestion de sessions sans état via JWT
- Système de rôles utilisateurs hiérarchiques
- Middleware de sécurité pour protéger les routes

## Rôles utilisateurs

Mathakine utilise quatre rôles utilisateurs principaux, conformes à la thématique Star Wars :

1. **PADAWAN** : Utilisateur standard, accès de base à l'application
2. **MAÎTRE** : Enseignant ou créateur de contenu, peut créer des exercices
3. **GARDIEN** : Modérateur, avec des privilèges de gestion des utilisateurs et du contenu
4. **ARCHIVISTE** : Administrateur, accès complet à toutes les fonctionnalités

Ces rôles sont implémentés dans `app/models/user.py` en tant qu'énumération `UserRole`.

## Architecture technique

Le système d'authentification est réparti sur plusieurs fichiers :

- `app/core/security.py` : Utilitaires de sécurité (hachage de mots de passe, création de tokens)
- `app/services/auth_service.py` : Services d'authentification (vérification, création d'utilisateurs)
- `app/api/deps.py` : Dépendances FastAPI pour la vérification des tokens et des rôles
- `app/api/endpoints/auth.py` : Endpoints d'API pour l'authentification
- `app/api/endpoints/users.py` : Endpoints de gestion des utilisateurs
- `app/schemas/user.py` : Schémas Pydantic pour la validation des données utilisateur

## Configuration

Les paramètres de sécurité sont définis dans plusieurs endroits :

1. Dans `app/core/config.py` :
   ```python
   # JWT Security
   SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
   ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # 7 jours
   ```

2. Dans `app/core/constants.py` :
   ```python
   class SecurityConfig:
       TOKEN_EXPIRY_MINUTES = 60 * 24 * 7  # 7 jours
       ALGORITHM = "HS256"
       ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```

Il est recommandé de définir une clé secrète forte via la variable d'environnement `SECRET_KEY` en production.

## Fonctionnement du système JWT

### 1. Création d'un utilisateur

```python
POST /api/users/
{
    "username": "luke_skywalker",
    "email": "luke@jedi-temple.sw",
    "password": "StrongPassword123",
    "full_name": "Luke Skywalker",
    "role": "padawan"  # Optionnel, "padawan" par défaut
}
```

Le mot de passe est haché via bcrypt avant d'être stocké en base de données.

### 2. Authentification et obtention d'un token

```python
POST /api/auth/login
{
    "username": "luke_skywalker",
    "password": "StrongPassword123"
}
```

Réponse avec cookies HTTP-only :
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

Les cookies sont configurés avec :
- access_token : 1 heure de validité
- refresh_token : 30 jours de validité
- httponly=True
- secure=True
- samesite="lax"

### 3. Utilisation du token pour les requêtes authentifiées

Le middleware d'authentification vérifie automatiquement les tokens dans les cookies pour les routes protégées. Les routes publiques sont :
- /
- /login
- /register
- /api/auth/login
- /api/users/
- /static
- /exercises

### 4. Récupération de l'utilisateur actuel

```python
GET /api/auth/me
```

Retourne les informations de l'utilisateur connecté.

### 5. Rafraîchissement du token

```python
POST /api/auth/refresh
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Retourne un nouveau token d'accès si le refresh token est valide.

## Protection des routes et vérification des rôles

Pour protéger une route, utilisez les dépendances définies dans `app/api/deps.py` :

```python
# Route accessible à tout utilisateur connecté
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}!"}

# Route accessible uniquement aux Maîtres
@router.post("/exercises")
def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_maitre_user)
):
    # Créer un exercice...
    pass

# Route accessible uniquement aux Gardiens et Archivistes
@router.get("/users")
def list_users(
    current_user: User = Depends(get_current_gardien_or_archiviste)
):
    # Lister les utilisateurs...
    pass

# Route accessible uniquement aux Archivistes
@router.delete("/system/reset")
def reset_system(
    current_user: User = Depends(get_current_archiviste)
):
    # Réinitialiser le système...
    pass
```

## Structure des tokens JWT

Les tokens JWT contiennent les informations suivantes :

- **sub** : Nom d'utilisateur (sujet du token)
- **exp** : Date d'expiration du token
- **role** : Rôle de l'utilisateur

Ces informations sont encodées et signées avec la clé secrète, garantissant leur intégrité.

## Test de l'authentification

Vous pouvez tester l'authentification via Swagger UI (http://localhost:8000/api/docs) ou via un client HTTP comme cURL ou Postman.

### Exemple avec cURL

```bash
# Créer un utilisateur
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"jedi_test","email":"jedi@test.com","password":"Force123Test","full_name":"Test Jedi"}'

# Se connecter et obtenir un token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"jedi_test","password":"Force123Test"}'

# Utiliser le token pour accéder à des ressources protégées
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer VOTRE_TOKEN_JWT"
```

## Bonnes pratiques de sécurité

1. **En développement** :
   - Utilisez des mots de passe forts, même pour les comptes de test
   - Ne commitez jamais de clés secrètes dans le dépôt

2. **En production** :
   - Définissez une clé secrète forte via la variable d'environnement `SECRET_KEY`
   - Utilisez HTTPS pour toutes les communications
   - Définissez une durée de vie appropriée pour les tokens (7 jours par défaut)
   - Surveillez les journaux d'authentification pour détecter les activités suspectes

3. **Pour les développeurs** :
   - N'exposez jamais les mots de passe hachés dans les réponses API
   - Utilisez les dépendances FastAPI pour vérifier les autorisations
   - Testez les cas limites (token expiré, mauvais rôle, etc.)

## Déconnexion

La déconnexion est conceptuelle dans un système JWT pur, car les tokens sont sans état. L'endpoint de déconnexion est fourni pour compatibilité :

```
POST /api/auth/logout
```

Pour une déconnexion réelle, le client doit supprimer le token JWT de son stockage.

Pour une implémentation plus robuste avec invalidation de tokens, il faudrait mettre en place un système de liste noire de tokens ou utiliser des refresh tokens.

## Conclusion

L'authentification JWT de Mathakine offre un équilibre entre simplicité, sécurité et performances. Les "Cristaux d'Identité" garantissent que chaque utilisateur ne peut accéder qu'aux ressources correspondant à son rang dans l'Ordre Jedi des Mathématiques.

---

*Pour plus d'informations sur l'implémentation technique, consultez les fichiers mentionnés dans la section "Architecture technique".* 