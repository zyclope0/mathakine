# Application Migration Email Verification

**Problème** : `column users.is_email_verified does not exist`

La migration Alembic n'a pas été appliquée à la base de données PostgreSQL sur Render.

---

## Solution 1 : Script Python (Recommandé)

J'ai créé un script `scripts/apply_email_verification_migration.py` qui applique la migration automatiquement.

### Sur Render (via SSH ou Console)

1. **Connectez-vous au service backend** via SSH ou utilisez la console Render
2. **Exécutez le script** :
   ```bash
   cd /opt/render/project/src
   python scripts/apply_email_verification_migration.py
   ```

### En Local (pour tester)

```bash
python scripts/apply_email_verification_migration.py
```

---

## Solution 2 : SQL Direct (Alternative)

Si vous avez accès à la base de données PostgreSQL directement :

```sql
-- Ajouter les colonnes de vérification email
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_email_verified BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_sent_at TIMESTAMP WITH TIME ZONE;

-- Créer l'index
CREATE INDEX IF NOT EXISTS ix_users_email_verification_token ON users(email_verification_token);
```

---

## Solution 3 : Via Alembic (Si configuré)

Si Alembic est configuré sur Render :

```bash
cd /opt/render/project/src
alembic upgrade head
```

---

## Vérification

Après application de la migration, vérifiez que les colonnes existent :

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('is_email_verified', 'email_verification_token', 'email_verification_sent_at');
```

Vous devriez voir :
- `is_email_verified` (boolean)
- `email_verification_token` (varchar)
- `email_verification_sent_at` (timestamp with time zone)

---

## Note Importante

**Le script est idempotent** : il vérifie si les colonnes existent avant de les créer, donc vous pouvez l'exécuter plusieurs fois sans problème.

