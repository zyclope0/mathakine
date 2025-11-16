# Stratégie de Vérification Avant Déploiement

## 🎯 Objectif

Éviter les erreurs de build en production en vérifiant systématiquement le code avant chaque push/déploiement.

## ✅ Checklist Avant Déploiement

### 1. Vérification TypeScript Locale

**Avant chaque commit/push**, exécuter :

```bash
# Windows PowerShell
.\scripts\check_types_before_deploy.ps1

# Linux/Mac
./scripts/check_types_before_deploy.sh

# Ou manuellement
cd frontend
npm run build
```

**Critères de succès** :
- ✅ Build réussit sans erreur TypeScript
- ✅ Aucun warning critique
- ✅ Tous les types sont correctement définis

### 2. Vérification des Types Critiques

Vérifier que tous les composants utilisent correctement les types définis :

#### Types Principaux à Vérifier

1. **`UserStats`** (`frontend/lib/validations/dashboard.ts`)
   - Vérifier que toutes les propriétés utilisées existent dans le type
   - Vérifier les transformations de données nécessaires

2. **`User`** (`frontend/types/api.ts`)
   - Vérifier les champs utilisés dans Profile/Settings

3. **`Challenge`** et **`Exercise`** (`frontend/types/api.ts`)
   - Vérifier les propriétés utilisées dans les composants

#### Points de Vérification

- [ ] `frontend/app/dashboard/page.tsx` - Utilise `UserStats` correctement
- [ ] `frontend/app/profile/page.tsx` - Utilise `User` correctement
- [ ] `frontend/app/settings/page.tsx` - Utilise `User` correctement
- [ ] Tous les composants qui utilisent des données API

### 3. Vérification des Imports

```bash
# Vérifier les imports manquants
cd frontend
npm run build 2>&1 | grep "Module not found"
```

### 4. Vérification des Composants

Vérifier que tous les composants reçoivent les bonnes props :

- [ ] `LevelIndicator` - Reçoit `{ current, title, current_xp, next_level_xp }`
- [ ] `RecentActivity` - Reçoit `ActivityItem[]` avec `description` et `time`
- [ ] `PerformanceByType` - Reçoit le bon format de données
- [ ] `StatsCard` - Props optionnelles correctement gérées

## 🔧 Scripts Automatisés

### Script PowerShell (Windows)

```powershell
.\scripts\check_types_before_deploy.ps1
```

### Script Bash (Linux/Mac)

```bash
./scripts/check_types_before_deploy.sh
```

## 📋 Workflow Recommandé

1. **Avant chaque commit** :
   ```bash
   cd frontend
   npm run build
   ```

2. **Avant chaque push** :
   ```bash
   .\scripts\check_types_before_deploy.ps1  # Windows
   # ou
   ./scripts/check_types_before_deploy.sh   # Linux/Mac
   ```

3. **En cas d'erreur** :
   - Corriger l'erreur localement
   - Relancer la vérification
   - Ne push que si le build réussit

## 🚨 Erreurs Communes à Vérifier

### Erreurs TypeScript Fréquentes

1. **Propriété inexistante** :
   ```
   Property 'X' does not exist on type 'Y'
   ```
   → Vérifier le type dans `frontend/lib/validations/` ou `frontend/types/api.ts`

2. **Type incompatible** :
   ```
   Type 'A' is not assignable to type 'B'
   ```
   → Transformer les données ou adapter le type

3. **Module non trouvé** :
   ```
   Module not found: Can't resolve '@/lib/...'
   ```
   → Vérifier que le fichier existe et est commité

### Solutions Rapides

- **Propriété manquante** : Ajouter au type ou retirer l'utilisation
- **Format incompatible** : Transformer les données avant de passer au composant
- **Import manquant** : Vérifier `.gitignore` et commit le fichier

## 📝 Notes

- Toujours tester le build localement avant de push
- Les erreurs TypeScript bloquent le build sur Render
- Utiliser les scripts automatisés pour gagner du temps
- Documenter les transformations de données nécessaires

