# Migration SQL Directe - Vérification Email

**URGENT** : La migration sera appliquée automatiquement au prochain redémarrage, mais vous pouvez l'appliquer **MAINTENANT** via SQL direct.

---

## 🚀 Application Immédiate via Render Dashboard

### Option 1 : Via Render PostgreSQL Dashboard (Le Plus Simple)

1. **Dans Render Dashboard** → **Database** → **mathakine-db**
2. Cliquez sur **"Connect"** ou **"psql"**
3. **Copiez-collez ce SQL** :

```sql
-- Ajouter les colonnes de vérification email
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_email_verified BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_sent_at TIMESTAMP WITH TIME ZONE;

-- Créer l'index
CREATE INDEX IF NOT EXISTS ix_users_email_verification_token ON users(email_verification_token);

-- Vérifier que les colonnes existent
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('is_email_verified', 'email_verification_token', 'email_verification_sent_at');
```

4. **Exécutez** → Vous devriez voir les 3 colonnes listées

---

### Option 2 : Via Script Python (Render Shell)

1. **Dans Render Dashboard** → **Service Backend** → **Shell**
2. **Exécutez** :
   ```bash
   cd /opt/render/project/src
   python scripts/apply_email_verification_migration.py
   ```

---

## ✅ Vérification

Après application, testez la création d'un compte. L'erreur `column users.is_email_verified does not exist` devrait disparaître.

---

## 🔄 Migration Automatique

**Note** : La migration sera appliquée automatiquement au prochain redémarrage du backend grâce aux modifications dans :
- `server/app.py` (fonction `startup()`)
- `scripts/start_render.sh` (exécution avant démarrage)

Mais pour que ça fonctionne **MAINTENANT**, appliquez la migration SQL directement via l'Option 1 ci-dessus.

