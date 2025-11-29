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
   - **Database** : `mathakine_test`
   - **Region** : `Frankfurt` (même région que votre base de production)
   - **Plan** : `Free` (suffisant pour les tests)
4. Cliquez sur **"Create Database"**

### **Étape 2 : Récupérer l'URL de Connexion**

1. Une fois la base créée, cliquez dessus
2. Dans l'onglet **"Connections"**, copiez **"Internal Database URL"**
3. Elle ressemble à : `postgresql://user:password@host:5432/mathakine_test`

### **Étape 3 : Initialiser le Schéma**

Utilisez le script Python pour initialiser la base :

```bash
# Définir temporairement DATABASE_URL vers la nouvelle base
export DATABASE_URL="postgresql://user:password@host:5432/mathakine_test"

# Initialiser le schéma
python -c "from app.db.init_db import create_tables_with_test_data; create_tables_with_test_data()"
```

### **Étape 4 : Configurer les Variables d'Environnement**

Dans le dashboard Render, pour votre service backend (`mathakine-alpha`) :

1. Allez dans **"Environment"**
2. Ajoutez la variable :
   ```
   TEST_DATABASE_URL=postgresql://user:password@host:5432/mathakine_test
   ```
3. **Important** : Gardez `DATABASE_URL` pointant vers la base de production
4. Sauvegardez et redéployez

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

# 4. Initialiser le schéma
export DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine_test"
python -c "from app.db.init_db import create_tables_with_test_data; create_tables_with_test_data()"

# 5. Restaurer DATABASE_URL
export DATABASE_URL="postgresql://postgres:postgres@localhost/mathakine"
```

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
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost/mathakine_test
```

---

## 🆘 **Dépannage**

### **Erreur : "Database does not exist"**

La base de test n'existe pas encore. Créez-la avec le script ou manuellement.

### **Erreur : "Permission denied"**

Vérifiez que l'utilisateur PostgreSQL a les droits de création de base de données.

### **Erreur : "Connection refused"**

Vérifiez que PostgreSQL est démarré et que `DATABASE_URL` est correcte.

---

## 📚 **Références**

- [Documentation PostgreSQL - CREATE DATABASE](https://www.postgresql.org/docs/current/sql-createdatabase.html)
- [Render.com - PostgreSQL](https://render.com/docs/databases)

