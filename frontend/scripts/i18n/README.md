# 🌐 Scripts i18n - Vérification Automatique

Scripts pour industrialiser la gestion des traductions dans Mathakine.

---

## 📋 **Scripts Disponibles**

### **1. `check-translations.js`**

Vérifie la cohérence entre les fichiers de traduction FR et EN.

**Utilisation** :
```bash
npm run i18n:check
```

**Vérifications** :
- ✅ Toutes les clés FR existent en EN
- ✅ Toutes les clés EN existent en FR
- ✅ Structure identique entre les deux fichiers
- ✅ Détection des clés orphelines

**Exemple de sortie** :
```
🔍 Vérification des traductions...

📊 Statistiques:
   - Clés FR: 281
   - Clés EN: 281

✅ Toutes les traductions sont cohérentes !
   - 281 clés vérifiées
   - Structure identique entre FR et EN
```

---

### **2. `extract-hardcoded.js`**

Détecte les textes français hardcodés dans le code.

**Utilisation** :
```bash
npm run i18n:extract
```

**Fonctionnalités** :
- 🔍 Scan des fichiers `.tsx`, `.ts`, `.jsx`, `.js`
- 📝 Détection des textes français (accents, mots courants)
- 💡 Suggestion de namespace approprié
- 📄 Génération d'un rapport JSON

**Exemple de sortie** :
```
🔍 Extraction des textes hardcodés...

📁 Scan de app/...
📁 Scan de components/...

📊 Résultats:
   - 15 textes hardcodés détectés

📝 Textes hardcodés détectés:

📄 app/login/page.tsx
   Namespace suggéré: auth
   Ligne 48: "Connexion"
   Contexte: <CardTitle>Connexion</CardTitle>
   ...
```

**Rapport généré** : `hardcoded-texts-report.json`

---

### **3. `validate-structure.js`**

Valide la structure et la syntaxe des fichiers de traduction.

**Utilisation** :
```bash
npm run i18n:validate
```

**Vérifications** :
- ✅ Syntaxe JSON valide
- ✅ Profondeur maximale
- ✅ Nombre de clés
- ✅ Valeurs vides
- ✅ Comparaison FR/EN

**Exemple de sortie** :
```
🔍 Validation de la structure des traductions...

📄 Validation de fr.json...
   ✅ Syntaxe JSON valide
   📊 Profondeur maximale: 3
   📊 Nombre de clés: 281

📄 Validation de en.json...
   ✅ Syntaxe JSON valide
   📊 Profondeur maximale: 3
   📊 Nombre de clés: 281

🔍 Comparaison des structures...
   ✅ Profondeurs identiques: 3
   ✅ Nombre de clés identique: 281

✅ Structure valide et cohérente !
```

---

## 🚀 **Utilisation Combinée**

Exécuter tous les scripts en une seule commande :

```bash
npm run i18n:all
```

Cette commande exécute dans l'ordre :
1. `validate-structure.js` - Valide la structure
2. `check-translations.js` - Vérifie la cohérence
3. `extract-hardcoded.js` - Détecte les textes hardcodés

---

## 📝 **Workflow Recommandé**

### **Avant d'ajouter des traductions** :

1. Valider la structure actuelle :
   ```bash
   npm run i18n:validate
   ```

2. Vérifier la cohérence :
   ```bash
   npm run i18n:check
   ```

### **Après avoir ajouté des traductions** :

1. Valider la nouvelle structure :
   ```bash
   npm run i18n:validate
   ```

2. Vérifier la cohérence :
   ```bash
   npm run i18n:check
   ```

3. Vérifier qu'il n'y a plus de textes hardcodés :
   ```bash
   npm run i18n:extract
   ```

### **Avant un commit** :

```bash
npm run i18n:all
```

Assurez-vous que tous les scripts passent avant de committer.

---

## 🔧 **Intégration CI/CD**

Ces scripts peuvent être intégrés dans votre pipeline CI/CD :

```yaml
# Exemple GitHub Actions
- name: Check translations
  run: npm run i18n:all
```

---

## 📚 **Documentation**

- **Guide i18n** : `docs/development/I18N_GUIDE.md`
- **Workflow i18n** : `docs/development/I18N_WORKFLOW.md`

---

## 🐛 **Dépannage**

### **Erreur : "Cannot find module"**

Assurez-vous d'exécuter les scripts depuis le dossier `frontend/` :
```bash
cd frontend
npm run i18n:check
```

### **Erreur : "SyntaxError: Unexpected token"**

Vérifiez que les fichiers JSON sont valides :
```bash
npm run i18n:validate
```

---

**Dernière mise à jour** : Janvier 2025

