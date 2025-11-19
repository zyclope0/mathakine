# Guide Complet : Vérification d'Email

**Date** : 19 novembre 2025  
**Fonctionnalité** : Système complet de vérification d'email pour les nouveaux utilisateurs

---

## 📋 Vue d'Ensemble

Le système de vérification d'email permet de :
- ✅ Vérifier que l'adresse email fournie lors de l'inscription est valide
- ✅ Envoyer un email avec un lien de vérification sécurisé
- ✅ Activer le compte uniquement après vérification
- ✅ Renvoyer l'email de vérification si nécessaire
- ✅ Gérer l'expiration des tokens (24 heures)

---

## 🏗️ Architecture

### Composants Créés

1. **Modèle User** (`app/models/user.py`)
   - `is_email_verified` : Boolean (défaut: False)
   - `email_verification_token` : String (nullable, indexé)
   - `email_verification_sent_at` : DateTime (nullable)

2. **Service Email** (`app/services/email_service.py`)
   - Support SMTP (Gmail, Outlook, serveur custom)
   - Support SendGrid (optionnel, si API key configurée)
   - Templates HTML pour emails de vérification

3. **Utilitaires** (`app/utils/email_verification.py`)
   - Génération de tokens sécurisés
   - Vérification d'expiration (24h)
   - Création de liens de vérification

4. **Handlers Backend** (`server/handlers/auth_handlers.py`)
   - `verify_email()` : GET `/api/auth/verify-email?token=...`
   - `resend_verification_email()` : POST `/api/auth/resend-verification`

5. **Page Frontend** (`frontend/app/verify-email/page.tsx`)
   - Affichage du statut de vérification
   - Bouton pour renvoyer l'email
   - Redirection vers login après succès

6. **Migration Alembic** (`alembic/versions/add_email_verification_fields.py`)
   - Ajout des colonnes à la table `users`
   - Index sur `email_verification_token`

---

## ⚙️ Configuration

### Option 1 : SMTP (Gmail, Outlook, Infomaniak, Serveur Custom)

**Variables d'environnement à ajouter** :

#### Configuration Infomaniak (Recommandé si vous avez un hébergement mail Infomaniak)

```bash
# Configuration SMTP Infomaniak
SMTP_HOST=mail.infomaniak.com     # Serveur SMTP Infomaniak
SMTP_PORT=587                      # Port recommandé (587 + STARTTLS)
SMTP_USER=mathakine@supernovafit.app  # Votre adresse email complète
SMTP_PASSWORD=votre-mot-de-passe   # Mot de passe de l'adresse mail
SMTP_FROM_EMAIL=mathakine@supernovafit.app  # Adresse expéditrice (même que SMTP_USER)
SMTP_USE_TLS=true                  # Utiliser STARTTLS (obligatoire pour port 587)

# URL du frontend (pour les liens de vérification)
FRONTEND_URL=https://mathakine-frontend.onrender.com
```

**Note Infomaniak** : 
- Port `587` + STARTTLS est la méthode recommandée (norme officielle)
- Port `465` + SSL/TLS est toléré en alternative si nécessaire
- Le username doit être l'adresse email complète (`mathakine@supernovafit.app`)
- Authentification obligatoire

#### Configuration Gmail

```bash
# Configuration SMTP Gmail
SMTP_HOST=smtp.gmail.com          # Serveur SMTP
SMTP_PORT=587                      # Port (587 pour TLS, 465 pour SSL)
SMTP_USER=votre-email@gmail.com   # Votre adresse email
SMTP_PASSWORD=votre-mot-de-passe   # Mot de passe ou "App Password" pour Gmail
SMTP_FROM_EMAIL=noreply@mathakine.com  # Adresse expéditrice
SMTP_USE_TLS=true                  # Utiliser TLS (true pour port 587)

# URL du frontend (pour les liens de vérification)
FRONTEND_URL=https://mathakine-frontend.onrender.com
```

**Infomaniak** (Votre configuration) :
```bash
SMTP_HOST=mail.infomaniak.com
SMTP_PORT=587
SMTP_USER=mathakine@supernovafit.app
SMTP_PASSWORD=votre-mot-de-passe-infomaniak
SMTP_FROM_EMAIL=mathakine@supernovafit.app
SMTP_USE_TLS=true
```
📖 Documentation : [Infomaniak - Envoi authentifié SMTP](https://www.infomaniak.com/fr/support/faq/2023/utiliser-lenvoi-authentifie-de-mail-depuis-un-site-web)

**Gmail - App Password** :
1. Aller sur https://myaccount.google.com/apppasswords
2. Créer un "App Password" pour "Mail"
3. Utiliser ce mot de passe dans `SMTP_PASSWORD`

**Outlook/Hotmail** :
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=votre-email@outlook.com
SMTP_PASSWORD=votre-mot-de-passe
SMTP_USE_TLS=true
```

**Serveur SMTP Custom** :
```bash
SMTP_HOST=votre-serveur-smtp.com
SMTP_PORT=587
SMTP_USER=votre-utilisateur
SMTP_PASSWORD=votre-mot-de-passe
SMTP_FROM_EMAIL=noreply@votre-domaine.com
SMTP_USE_TLS=true
```

### Option 2 : SendGrid (Recommandé pour Production)

**Installation** :
```bash
pip install sendgrid
```

**Ajout à `requirements.txt`** :
```
sendgrid==6.11.0  # Service d'envoi d'email professionnel
```

**Variables d'environnement** :
```bash
# SendGrid API Key (obtenue sur https://app.sendgrid.com/settings/api_keys)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@mathakine.com  # Email vérifié dans SendGrid

# URL du frontend
FRONTEND_URL=https://mathakine-frontend.onrender.com
```

**Configuration SendGrid** :
1. Créer un compte sur https://sendgrid.com
2. Vérifier votre domaine ou utiliser l'email de test
3. Créer une API Key dans Settings > API Keys
4. Ajouter l'API Key dans les variables d'environnement

---

## 🔄 Flux d'Inscription avec Vérification

### 1. Inscription Utilisateur

```
POST /api/users/
{
  "username": "nouvel_utilisateur",
  "email": "user@example.com",
  "password": "MotDePasse123",
  "full_name": "Nom Complet" (optionnel)
}
```

**Actions backend** :
1. Création de l'utilisateur avec `is_email_verified = False`
2. Génération d'un token de vérification (32 caractères aléatoires)
3. Sauvegarde du token et de la date d'envoi
4. Envoi de l'email de vérification
5. Retour des données utilisateur (avec `is_email_verified: false`)

**Réponse** :
```json
{
  "id": 123,
  "username": "nouvel_utilisateur",
  "email": "user@example.com",
  "is_email_verified": false,
  ...
}
```

### 2. Email de Vérification Envoyé

**Contenu de l'email** :
- Sujet : "Vérifiez votre adresse email - Mathakine"
- Lien : `https://mathakine-frontend.onrender.com/verify-email?token=xxxxx`
- Expiration : 24 heures
- Design : HTML avec template Star Wars

### 3. Vérification Email

**Utilisateur clique sur le lien** :
```
GET /api/auth/verify-email?token=xxxxx
```

**Actions backend** :
1. Recherche utilisateur par token
2. Vérification expiration (24h)
3. Si valide : `is_email_verified = True`, token supprimé
4. Retour succès avec données utilisateur

**Réponse succès** :
```json
{
  "message": "Votre adresse email a été vérifiée avec succès !",
  "success": true,
  "user": {
    "id": 123,
    "username": "nouvel_utilisateur",
    "email": "user@example.com",
    "is_email_verified": true
  }
}
```

### 4. Renvoi Email (si nécessaire)

**Endpoint** :
```
POST /api/auth/resend-verification
{
  "email": "user@example.com"
}
```

**Actions backend** :
1. Recherche utilisateur par email
2. Vérification si déjà vérifié
3. Génération nouveau token
4. Envoi nouvel email
5. Retour confirmation

---

## 🎨 Frontend

### Page de Vérification (`/verify-email`)

**États** :
- **Loading** : Vérification en cours
- **Success** : Email vérifié ✅ → Bouton "Aller à la connexion"
- **Error/Expired** : Token invalide/expiré ❌ → Bouton "Renvoyer l'email"

**Fonctionnalités** :
- Affichage du statut avec icônes
- Bouton pour renvoyer l'email si expiré
- Redirection automatique vers login après succès

### Page de Login (`/login`)

**Message après inscription** :
- Si email envoyé : Message jaune avec instructions
- Si déjà vérifié : Message vert "Inscription réussie"

---

## 📊 Base de Données

### Migration Alembic

**Fichier** : `alembic/versions/add_email_verification_fields.py`

**Colonnes ajoutées** :
```sql
ALTER TABLE users ADD COLUMN is_email_verified BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN email_verification_sent_at TIMESTAMP WITH TIME ZONE;
CREATE INDEX ix_users_email_verification_token ON users(email_verification_token);
```

**Application** :
```bash
# En développement
python -m alembic upgrade head

# En production (Render)
# La migration s'appliquera automatiquement au prochain déploiement
```

---

## 🔒 Sécurité

### Tokens de Vérification

- **Génération** : `secrets.token_urlsafe(32)` → 32 caractères aléatoires
- **Expiration** : 24 heures après envoi
- **Usage unique** : Token supprimé après vérification
- **Index** : Recherche rapide par token

### Protection

- **Pas d'énumération** : Même message si email inexistant (renvoi)
- **Expiration** : Tokens expirés rejetés
- **HTTPS** : Liens sécurisés en production
- **Validation** : Vérification format email côté serveur

---

## 🧪 Tests

### Test 1 : Inscription Complète
```
1. POST /api/users/ avec données valides
2. Vérifier email reçu dans boîte de réception
3. Cliquer sur le lien de vérification
4. Vérifier is_email_verified = true dans BDD
5. Se connecter avec le compte
```

### Test 2 : Token Expiré
```
1. Modifier email_verification_sent_at à -25h dans BDD
2. Essayer de vérifier avec le token
3. Vérifier erreur "token expiré"
4. Utiliser "Renvoyer l'email"
```

### Test 3 : Renvoi Email
```
1. POST /api/auth/resend-verification avec email valide
2. Vérifier nouveau token généré
3. Vérifier email reçu
4. Vérifier avec nouveau token
```

### Test 4 : Email Déjà Vérifié
```
1. Vérifier email une première fois
2. Essayer de vérifier à nouveau avec le même token
3. Vérifier message "déjà vérifié"
```

---

## 🚀 Déploiement

### Étapes

1. **Ajouter variables d'environnement** (Render Dashboard)
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=votre-email@gmail.com
   SMTP_PASSWORD=votre-app-password
   SMTP_FROM_EMAIL=noreply@mathakine.com
   SMTP_USE_TLS=true
   FRONTEND_URL=https://mathakine-frontend.onrender.com
   ```

2. **Appliquer migration** (automatique sur Render ou manuel)
   ```bash
   python -m alembic upgrade head
   ```

3. **Tester envoi email**
   - Créer un compte test
   - Vérifier réception email
   - Cliquer sur le lien
   - Vérifier activation compte

### Vérification Post-Déploiement

- [ ] Email reçu lors de l'inscription
- [ ] Lien de vérification fonctionne
- [ ] Compte activé après vérification
- [ ] Renvoi email fonctionne
- [ ] Tokens expirés rejetés
- [ ] Page `/verify-email` affiche correctement les statuts

---

## 📝 Variables d'Environnement Requises

### Minimum (SMTP)
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe
SMTP_FROM_EMAIL=noreply@mathakine.com
SMTP_USE_TLS=true
FRONTEND_URL=https://mathakine-frontend.onrender.com
```

### Optionnel (SendGrid)
```bash
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@mathakine.com
FRONTEND_URL=https://mathakine-frontend.onrender.com
```

### Mode Développement
Si aucune configuration SMTP/SendGrid :
- Les emails sont **simulés** (loggés mais non envoyés)
- L'inscription fonctionne quand même
- Utile pour développement local

---

## 🐛 Dépannage

### Email non reçu

1. **Vérifier spam/courrier indésirable**
2. **Vérifier logs backend** :
   ```
   logger.info(f"Email envoyé via SMTP à {to_email}")
   ```
3. **Vérifier configuration SMTP** :
   - Gmail : Utiliser "App Password" (pas le mot de passe normal)
   - Vérifier `SMTP_USE_TLS=true` pour port 587
4. **Tester avec SendGrid** (plus fiable)

### Token invalide

1. **Vérifier expiration** : Token valide 24h seulement
2. **Vérifier token dans BDD** : `SELECT email_verification_token FROM users WHERE email = '...'`
3. **Utiliser renvoi email** : Génère un nouveau token

### Migration échoue

1. **Vérifier dernière migration** :
   ```sql
   SELECT * FROM alembic_version;
   ```
2. **Appliquer manuellement** :
   ```sql
   ALTER TABLE users ADD COLUMN is_email_verified BOOLEAN NOT NULL DEFAULT false;
   ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(255);
   ALTER TABLE users ADD COLUMN email_verification_sent_at TIMESTAMP WITH TIME ZONE;
   CREATE INDEX ix_users_email_verification_token ON users(email_verification_token);
   ```

---

## 📚 Fichiers Créés/Modifiés

### Backend
- ✅ `app/models/user.py` (ajout colonnes)
- ✅ `app/services/email_service.py` (nouveau)
- ✅ `app/utils/email_verification.py` (nouveau)
- ✅ `server/handlers/auth_handlers.py` (nouveau)
- ✅ `server/handlers/user_handlers.py` (mise à jour inscription)
- ✅ `server/routes.py` (ajout routes)
- ✅ `alembic/versions/add_email_verification_fields.py` (nouveau)

### Frontend
- ✅ `frontend/app/verify-email/page.tsx` (nouveau)
- ✅ `frontend/app/login/page.tsx` (message vérification)
- ✅ `frontend/app/register/page.tsx` (gestion état vérification)
- ✅ `frontend/hooks/useAuth.ts` (gestion is_email_verified)
- ✅ `frontend/messages/fr.json` (traductions)
- ✅ `frontend/messages/en.json` (traductions)

---

## ✅ Checklist Configuration

### Backend
- [ ] Variables d'environnement SMTP configurées
- [ ] Migration Alembic appliquée
- [ ] Test envoi email réussi
- [ ] Endpoints `/api/auth/verify-email` et `/api/auth/resend-verification` fonctionnels

### Frontend
- [ ] Page `/verify-email` accessible
- [ ] Traductions FR/EN complètes
- [ ] Message vérification affiché sur `/login`
- [ ] Redirection après vérification fonctionne

### Tests
- [ ] Inscription → Email reçu
- [ ] Clic lien → Compte vérifié
- [ ] Token expiré → Erreur affichée
- [ ] Renvoi email → Nouveau token généré

---

**Responsable** : Assistant IA  
**Documentation** : Guide complet avec exemples de configuration

