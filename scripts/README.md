# Scripts de Correction et Maintenance

Ce dossier contient plusieurs scripts utilitaires pour corriger des problèmes courants et maintenir la compatibilité du code dans le projet Mathakine.

## Scripts unifiés

### `fix_all_issues.py` (recommandé)

Script tout-en-un qui combine les fonctionnalités de plusieurs scripts de correction.

```bash
# Exécuter toutes les corrections
python scripts/fix_all_issues.py

# Mode simulation (n'applique pas les modifications)
python scripts/fix_all_issues.py --dry-run

# Mode verbose 
python scripts/fix_all_issues.py --verbose

# Uniquement les tests
python scripts/fix_all_issues.py --tests-only

# Corriger seulement les énumérations
python scripts/fix_all_issues.py --enum

# Corriger seulement les méthodes Pydantic
python scripts/fix_all_issues.py --pydantic

# Corriger seulement les méthodes Response
python scripts/fix_all_issues.py --response

# Traiter un fichier spécifique
python scripts/fix_all_issues.py --file app/models/user.py
```

## Scripts spécialisés

### 1. Correction des énumérations

#### `fix_enum_names.py`
Corrige les noms d'énumérations incorrects comme `UserRole.PADAWA` → `UserRole.PADAWAN`.

```bash
python scripts/fix_enum_names.py [--dry-run] [--verbose] [--tests-only]
```

#### `fix_malformed_enums.py`
Corrige les énumérations malformées comme `UserRole.PADAWA.value` → `UserRole.PADAWAN.value`.

```bash
python scripts/fix_malformed_enums.py [--dry-run] [--verbose] [--tests-only]
```

### 2. Corrections liées à Pydantic v2

#### `fix_pydantic_methods.py`
Remplace les méthodes obsolètes de Pydantic v1 par leurs équivalents v2 :
- `.json()` → `.model_dump_json()`
- `.dict()` → `.model_dump()`
- `.parse_obj()` → `.model_validate()`

```bash
python scripts/fix_pydantic_methods.py [--dry-run] [--verbose] [--tests-only]
```

### 3. Corrections pour les objets Response

#### `fix_response_methods.py`
Remplace les appels incorrects comme `response.model_dump_json()` par `response.json()` sur les objets Response FastAPI.

```bash
python scripts/fix_response_methods.py [--dry-run] [--verbose]
```

### 4. Vérification de compatibilité

#### `check_compatibility.py`
Script complet qui vérifie plusieurs aspects de compatibilité et peut appliquer des corrections.

```bash
# Vérifier sans corriger
python scripts/check_compatibility.py

# Corriger les problèmes liés aux énumérations
python scripts/check_compatibility.py --fix-enums

# Corriger les problèmes liés à Pydantic v2
python scripts/check_compatibility.py --fix-pydantic

# Mode verbeux
python scripts/check_compatibility.py --verbose
```

## Procédure recommandée

Pour une approche systématique, suivez cette procédure :

1. **Vérification initiale** : Exécutez d'abord en mode simulation pour voir les problèmes
   ```bash
   python scripts/fix_all_issues.py --dry-run --verbose
   ```

2. **Correction** : Appliquez les corrections en fonction des résultats
   ```bash
   python scripts/fix_all_issues.py
   ```

3. **Vérification finale** : Exécutez à nouveau pour vous assurer que tous les problèmes ont été résolus
   ```bash
   python scripts/fix_all_issues.py --dry-run
   ```

4. **Tests** : Exécutez les tests pour confirmer que les corrections n'ont pas introduit de régressions
   ```bash
   python -m pytest tests/
   ``` 