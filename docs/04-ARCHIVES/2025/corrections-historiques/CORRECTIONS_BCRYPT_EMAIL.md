# Corrections : Erreur bcrypt et Email non reçu

**Date** : 19 novembre 2025  
**Problèmes** : 
1. `AttributeError: module 'bcrypt' has no attribute '__about__'`
2. Email de vérification non reçu

---

## 🔍 Diagnostic

### Problème 1 : Erreur bcrypt

**Erreur** :
```
AttributeError: module 'bcrypt' has no attribute '__about__'
File "/opt/render/project/src/.venv/lib/python3.11/site-packages/passlib/handlers/bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
```

**Cause** : Incompatibilité entre `bcrypt==4.3.0` et `passlib==1.7.4`

**Solution** : Downgrader `bcrypt` à `4.0.1` (version compatible)

### Problème 2 : Email non reçu

**Symptômes** :
- Utilisateur créé avec succès (201 Created)
- Aucun log d'envoi d'email dans la console
- Email non reçu dans la boîte mail

**Causes possibles** :
1. Variables SMTP non configurées dans Render
2. Erreur bcrypt interrompt le flux avant l'envoi d'email
3. Erreur silencieuse dans l'envoi SMTP

---

## ✅ Solutions Appliquées

### 1. Correction Version bcrypt

**Fichier** : `requirements.txt`

**Changement** :
```diff
- bcrypt==4.3.0  # Compatible avec passlib 1.7.4
+ bcrypt==4.0.1  # Version compatible avec passlib 1.7.4 (4.3.0 cause AttributeError)
```

**Action requise** :
- Redémarrer le service backend sur Render pour réinstaller les dépendances

### 2. Amélioration Logging Email

**Fichier** : `app/services/email_service.py`

**Améliorations** :
- ✅ Log détaillé de la configuration SMTP (host, port, user)
- ✅ Log avant tentative d'envoi
- ✅ Logs étape par étape (connexion, TLS, authentification, envoi)
- ✅ Gestion spécifique des erreurs SMTP (AuthenticationError, SMTPException)
- ✅ Traceback complet en cas d'erreur

**Nouveaux logs** :
```python
logger.info(f"Tentative d'envoi email SMTP à {to_email} via {smtp_host}:{smtp_port}")
logger.debug(f"Connexion SMTP à {smtp_host}:{smtp_port}")
logger.debug(f"Authentification avec {smtp_user}")
logger.info(f"✅ Email envoyé via SMTP à {to_email}")
logger.error(f"❌ Erreur d'authentification SMTP: {e}")
```

**Fichier** : `server/handlers/user_handlers.py`

**Améliorations** :
- ✅ Log avant préparation de l'email
- ✅ Log du frontend URL et token (masqué)
- ✅ Logs de succès/échec détaillés
- ✅ Traceback en cas d'exception

### 3. Vérification Configuration SMTP

**Variables requises dans Render** :
```bash
SMTP_HOST=mail.infomaniak.com
SMTP_PORT=587
SMTP_USER=mathakine@supernovafit.app
SMTP_PASSWORD=champion0%0
SMTP_FROM_EMAIL=mathakine@supernovafit.app
SMTP_USE_TLS=true
FRONTEND_URL=https://mathakine-frontend.onrender.com
```

**Logs de diagnostic** :
- Si SMTP non configuré : `SMTP_USER=MANQUANT` ou `SMTP_PASSWORD=MANQUANT`
- Si erreur d'authentification : `❌ Erreur d'authentification SMTP`

---

## 🧪 Tests à Effectuer

### Test 1 : Vérifier Configuration SMTP

**Dans Render Dashboard** :
1. Aller dans **Environment Variables**
2. Vérifier que toutes les variables SMTP sont présentes :
   - ✅ `SMTP_HOST=mail.infomaniak.com`
   - ✅ `SMTP_PORT=587`
   - ✅ `SMTP_USER=mathakine@supernovafit.app`
   - ✅ `SMTP_PASSWORD=champion0%0`
   - ✅ `SMTP_FROM_EMAIL=mathakine@supernovafit.app`
   - ✅ `SMTP_USE_TLS=true`
   - ✅ `FRONTEND_URL=https://mathakine-frontend.onrender.com`

### Test 2 : Redémarrer Backend

**Action** :
1. Dans Render Dashboard → Service Backend
2. Cliquer sur **Manual Deploy** → **Deploy latest commit**
3. Attendre le redémarrage (~2-3 minutes)

**Vérifier** :
- ✅ Build réussi (pas d'erreur bcrypt)
- ✅ Service démarré correctement

### Test 3 : Créer Nouveau Compte

**Action** :
1. Aller sur `/register`
2. Créer un compte test avec email valide
3. Observer les logs dans Render

**Logs attendus** :
```
INFO: Nouvel utilisateur créé: testuser (ID: 9463)
INFO: Préparation envoi email de vérification à test@example.com
INFO: Tentative d'envoi email SMTP à test@example.com via mail.infomaniak.com:587
DEBUG: Connexion SMTP à mail.infomaniak.com:587
DEBUG: Authentification avec mathakine@supernovafit.app
INFO: ✅ Email envoyé via SMTP à test@example.com depuis mathakine@supernovafit.app
INFO: ✅ Email de vérification envoyé avec succès à test@example.com
```

**Si erreur** :
```
WARNING: SMTP_USER=MANQUANT, SMTP_PASSWORD=MANQUANT
```
→ Vérifier variables d'environnement

```
ERROR: ❌ Erreur d'authentification SMTP: ...
```
→ Vérifier mot de passe Infomaniak

### Test 4 : Vérifier Réception Email

**Action** :
1. Vérifier boîte mail `mathakine@supernovafit.app`
2. Vérifier dossier spam/courrier indésirable
3. Cliquer sur le lien de vérification

---

## 🐛 Dépannage

### Erreur bcrypt persiste

**Solution** :
1. Vérifier que `requirements.txt` contient `bcrypt==4.0.1`
2. Redémarrer le service backend
3. Vérifier les logs de build pour confirmer l'installation

### Email toujours non reçu

**Vérifications** :

1. **Variables d'environnement** :
   ```bash
   # Dans Render Dashboard → Environment Variables
   # Vérifier que toutes les variables sont présentes et correctes
   ```

2. **Logs backend** :
   - Chercher `SMTP_USER=MANQUANT` → Variables manquantes
   - Chercher `❌ Erreur d'authentification SMTP` → Mot de passe incorrect
   - Chercher `❌ Erreur SMTP` → Problème de connexion

3. **Mot de passe Infomaniak** :
   - Le caractère `%` peut nécessiter un encodage
   - Essayer `champion0%250` si `champion0%0` ne fonctionne pas

4. **Port SMTP** :
   - Port `587` avec `SMTP_USE_TLS=true` (recommandé)
   - Alternative : Port `465` avec `SMTP_USE_TLS=false`

5. **Dossier spam** :
   - Vérifier le dossier spam/courrier indésirable
   - Ajouter `mathakine@supernovafit.app` aux contacts

---

## 📝 Checklist Post-Correction

- [ ] `requirements.txt` mis à jour avec `bcrypt==4.0.1`
- [ ] Variables SMTP configurées dans Render
- [ ] Service backend redémarré
- [ ] Test création compte effectué
- [ ] Logs vérifiés (pas d'erreur bcrypt)
- [ ] Logs email vérifiés (tentative d'envoi visible)
- [ ] Email reçu dans boîte mail
- [ ] Lien de vérification fonctionne

---

## 🚀 Déploiement

**Fichiers modifiés** :
- ✅ `requirements.txt` (bcrypt 4.0.1)
- ✅ `app/services/email_service.py` (logging amélioré)
- ✅ `server/handlers/user_handlers.py` (logging amélioré)

**Action requise** :
1. Commit et push les changements
2. Render redémarre automatiquement
3. Vérifier les logs après redémarrage

---

**Résultat attendu** : 
- ✅ Plus d'erreur bcrypt
- ✅ Logs détaillés pour diagnostic email
- ✅ Email envoyé avec succès via Infomaniak

