# 🗄️ Créer une Base de Données de Test

Ce guide explique comment créer une base de données de test séparée pour éviter que les tests utilisent la base de production.

---

## 🎯 **Pourquoi une Base de Test ?**

Les tests peuvent supprimer ou modifier des données. Pour éviter d'affecter la production, il faut une base de données séparée.

---

## 🚀 **Option 1 : Sur Render.com (Production)**

### **Étape 1 : Créer une Nouvelle Base PostgreSQL**

1. Connectez-vous au [dashboard Render](https://dashboard.render.com)
2. Cliquez sur **"New +"** → **"PostgreSQL"**
3. Configurez la nouvelle base :
   - **Name** : `mathakine-test` (ou `mathakine_test`)
   - **Database** : `mathakine_test` (ou un nom similaire)
   - **Region** : `Frankfurt` (même région que votre base de production)
   - **Plan** : `Free` (suffisant pour les tests)
4. Cliquez sur **"Create Database"**

### **Étape 2 : Récupérer l'URL de Connexion**

1. Une fois la base créée, cliquez dessus
2. Dans l'onglet **"Connections"**, copiez **"Internal Database URL"**
3. Elle ressemble à : `postgresql://user:password@host:5432/mathakine_test`

**Exemple réel** (base de test créée le 29/11/2025) :
- **Database** : `mathakine_test_jk25`
- **Username** : `mathakine_test_jk25_user`
- **Host** : `dpg-d4lj1n9r0fns73fc6ncg-a.frankfurt-postgres.render.com`
- **URL** : `postgresql://mathakine_test_jk25_user:password@dpg-d4lj1n9r0fns73fc6ncg-a/mathakine_test_jk25`

### **Étape 3 : Initialiser le Schéma**

Utilisez le script Python pour initialiser la base :

```bash
# Option A : Via le script dédié (recommandé)
python scripts/init_test_database_render.py

# Option B : Manuellement
# Définir temporairement DATABASE_URL vers la nouvelle base
export DATABASE_URL="postgresql://user:password@host:5432/mathakine_test"
export TESTING=true

# Initialiser le schéma
python -c "from app.db.init_db import create_tables_with_test_data; create_tables_with_test_data()"
```

### **Étape 4 : Configurer les Variables d'Environnement**

Dans le dashboard Render, pour votre service backend (`mathakine-alpha`) :

1. Allez dans **"Environment"**
2. Ajoutez la variable :
   ```
   Key: TEST_DATABASE_URL
   Value: postgresql://user:password@host:5432/mathakine_test
   ```
3. **IMPORTANT** : Vérifiez que `DATABASE_URL` pointe toujours vers la base de **production** (`mathakine`)
4. Cliquez sur **"Save Changes"** (Render redéploiera automatiquement)

---

## 🖥️ **Option 2 : Localement (Développement)**

### **Méthode Automatique (Recommandée)**

Utilisez le script fourni :

```bash
# Assurez-vous que DATABASE_URL pointe vers votre PostgreSQL local
export DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine"

# Exécuter le script
python scripts/create_test_database.py
```

Le script va :
1. Créer automatiquement `mathakine_test` à partir de `mathakine`
2. Initialiser le schéma
3. Vous donner l'URL à utiliser

### **Méthode Manuelle**

```bash
# 1. Se connecter à PostgreSQL
psql -U postgres

# 2. Créer la base de test
CREATE DATABASE mathakine_test;

# 3. Quitter psql
\q

# 4. Appliquer les migrations sur la base de test
# (alembic utilise TEST_DATABASE_URL quand TESTING=true)
$env:TESTING="true"; $env:TEST_DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine_test"; alembic upgrade head

# Linux/Mac :
# TESTING=true TEST_DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine_test" alembic upgrade head

# 5. Restaurer DATABASE_URL
export DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine"
```

---

## ⚠️ **Avant de lancer les tests**

Après avoir créé ou réinitialisé la base de test, le schéma doit être à jour.

**Option A — Migrations Alembic** (base vide ou cohérente) :

```powershell
# Windows PowerShell
$env:TESTING="true"; alembic upgrade head
```

```bash
# Linux / Mac
TESTING=true alembic upgrade head
```

**Option B — Base partiellement initialisée** (ex. créée par `create_all` ou script d’init) :

Si `alembic upgrade head` échoue (tables déjà existantes), exécutez le script de rattrapage :

```powershell
# Windows PowerShell
$env:TESTING="true"; python scripts/fix_recommendations_schema_for_tests.py
```

Cela ajoute les colonnes manquantes (`challenge_id`, `recommendation_type`) à la table `recommendations`.

---

## ✅ **Vérification**

### **Vérifier que les Tests Utilisent la Bonne Base**

```bash
# Exécuter les tests avec les logs de debug
TESTING=true TEST_DATABASE_URL="postgresql://..." pytest tests/ -v -s

# Vérifier dans les logs que la bonne base est utilisée
```

### **Vérifier la Configuration**

Le code vérifie automatiquement que :
- `TEST_DATABASE_URL` est défini
- `TEST_DATABASE_URL` ≠ `DATABASE_URL`
- Le nom de la base contient "test" (sauf si localhost)

Si ces conditions ne sont pas remplies, les tests **refuseront de s'exécuter** pour protéger la production.

---

## 🔒 **Sécurité**

### **Protections Implémentées**

1. ✅ Les tests ne peuvent plus utiliser `DATABASE_URL` comme fallback
2. ✅ Vérification que `TEST_DATABASE_URL` ≠ `DATABASE_URL`
3. ✅ Blocage si le nom de la base ne contient pas "test" (sauf localhost)
4. ✅ Scripts de nettoyage bloqués en production

### **En Cas d'Erreur**

Si vous voyez cette erreur :
```
🚨 SÉCURITÉ: TEST_DATABASE_URL pointe vers la même base que DATABASE_URL!
```

**Solution** : Définir `TEST_DATABASE_URL` vers une base séparée.

---

## 📝 **Variables d'Environnement Requises**

### **Production (Render)**

```bash
# Base de production (NE PAS MODIFIER)
DATABASE_URL=postgresql://.../mathakine

# Base de test (NOUVELLE)
TEST_DATABASE_URL=postgresql://.../mathakine_test
```

### **Développement Local**

```bash
# Base de développement
DATABASE_URL=postgresql://postgres:postgres@localhost/mathakine

# Base de test
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost/test_mathakine
```

---

## 🐳 **Option 3 : Docker (PostgreSQL localhost:5432)**

**Note :** La BDD de dev local tourne souvent via Docker (conteneur Postgres sur localhost:5432). Pour le backup, utiliser `docker exec` — voir [PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md](../03-PROJECT/PLAN_PREPARATION_MIGRATION_ALEMBIC_DDL.md) § 1.2b.

Si PostgreSQL tourne dans un conteneur Docker exposé sur `localhost:5432` :

### **Étape 1 : Créer la base de test**

```bash
# Se connecter au conteneur PostgreSQL (remplacer postgres par votre image si besoin)
docker exec -it <nom_conteneur_postgres> psql -U postgres -c "CREATE DATABASE test_mathakine;"

# Ou via psql depuis l'hôte si le port 5432 est mappé :
psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE test_mathakine;"
```

### **Étape 2 : Appliquer le schéma**

**Option A – via create_tables (recommandé pour Docker)**  
Le `.env` peut écraser `DATABASE_URL`. Utiliser `TESTING` + `TEST_DATABASE_URL` :

```powershell
# PowerShell
$env:TESTING="true"
$env:TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_mathakine"
python -c "from app.services.db_init_service import create_tables; create_tables()"
```

**Option B – via Alembic**  
Alembic lit `DATABASE_URL`. Lancez en pointant vers la base de test :

```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_mathakine"
alembic upgrade head
```

### **Étape 3 : Variables dans .env**

```bash
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_mathakine
```

*Note : Le port 5432 est optionnel si c’est le défaut PostgreSQL.*

### **Étape 4 : Lancer les tests**

Avec `TEST_DATABASE_URL` dans le `.env`, pytest utilise automatiquement la base de test (conftest définit `TESTING=true`). Aucune variable à passer manuellement :

```bash
python -m pytest tests/api/test_auth_flow.py -v
```

Les logs doivent afficher :  
`Mode test détecté, utilisation de l'URL de base de données: .../test_mathakine`

---

## 🔄 **Comportement automatique (pytest)**

1. **conftest.py** définit `TESTING=true` avant tout import.
2. **load_dotenv** charge le `.env` → `TEST_DATABASE_URL` est lu.
3. **config** utilise `TEST_DATABASE_URL` quand `TESTING` est true.
4. **Important** : ne pas définir `TESTING=false` dans le `.env`, sinon les tests utiliseraient `DATABASE_URL` (base dev/prod).

---

## 🆘 **Dépannage**

### **Erreur : "Database does not exist"**

La base de test n'existe pas encore. Créez-la avec le script ou manuellement.

### **Erreur : "relation \"users\" does not exist"**

Le schéma (tables) n’a pas été appliqué. Réexécutez l’étape 2 (Option Docker) : `create_tables` ou `alembic upgrade head`.

### **Erreur : "Permission denied"**

Vérifiez que l'utilisateur PostgreSQL a les droits de création de base de données.

### **Erreur : "Connection refused"**

Vérifiez que PostgreSQL est démarré et que `DATABASE_URL` est correcte.

### **"Veuillez vérifier votre adresse email" ou "Utilisateur non trouvé"**

Les utilisateurs créés par `create_tables_with_test_data()` ont désormais `is_email_verified=True`. Si ObiWan manque ou n'est pas vérifié :

```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_mathakine"
python scripts/ensure_dev_users.py
```

---

## 📚 **Références**

- [Documentation PostgreSQL - CREATE DATABASE](https://www.postgresql.org/docs/current/sql-createdatabase.html)
- [Render.com - PostgreSQL](https://render.com/docs/databases)

