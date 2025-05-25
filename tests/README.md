# Guide des tests pour Mathakine (Mai 2025)

## 🎯 **État actuel**
- **296 tests passent**, 51 échecs, 2 ignorés
- **Couverture : 73%** (+26% depuis corrections)
- **Tests fonctionnels : 6/6 passent** ✅
- **Statut : Stable pour fonctionnalités critiques**

## 🚀 **Exécution rapide**

### **Commandes essentielles :**
```bash
# Tous les tests avec rapport complet
python tests/unified_test_runner.py --all --verbose

# Tests fonctionnels défis logiques (validation état stable)
python -m pytest tests/functional/test_logic_challenge_isolated.py -v

# Tests spécifiques par catégorie
python tests/unified_test_runner.py --unit    # Tests unitaires
python tests/unified_test_runner.py --api     # Tests API
```

### **Options principales :**
| Option | Description |
|--------|-------------|
| `--all` | Exécuter tous les tests |
| `--unit`, `--api`, `--integration`, `--functional` | Tests par catégorie |
| `--fix-enums` | Corriger problèmes énumérations automatiquement |
| `--verbose` | Affichage détaillé pour debug |
| `--specific PATH` | Test d'un fichier spécifique |

## 📁 **Structure des tests**

```
tests/
├── unit/                 # Tests unitaires (95% des tests critiques passent)
├── api/                  # Tests API REST  
├── integration/          # Tests d'intégration entre composants
├── functional/           # Tests fonctionnels (6/6 passent ✅)
├── archives/             # Fichiers obsolètes (ne pas utiliser)
├── unified_test_runner.py # Script principal d'exécution
└── DOCUMENTATION_TESTS_CONSOLIDEE.md # Documentation complète
```

## 📚 **Documentation complète**

Pour une documentation détaillée, consultez :

### **📖 Documents principaux :**
- **[DOCUMENTATION_TESTS_CONSOLIDEE.md](DOCUMENTATION_TESTS_CONSOLIDEE.md)** - Documentation complète mise à jour
- **[CORRECTION_PLAN.md](CORRECTION_PLAN.md)** - Plan de correction avec progrès détaillés

### **🔍 Ce que vous y trouverez :**
- Analyse détaillée des 51 échecs restants par catégorie
- Plan de correction Phase D avec priorités
- Métriques de qualité et évolution de la couverture
- Commandes de debug spécifiques par problème
- Bonnes pratiques et erreurs à éviter

## 🎉 **Progrès accomplis**

### **Corrections majeures (Mai 2025) :**
- ✅ **Mapping énumérations PostgreSQL** : Ordre paramètres corrigé
- ✅ **Format JSON PostgreSQL** : Conversion automatique listes
- ✅ **Tests fonctionnels** : 6/6 défis logiques passent
- ✅ **Couverture** : 47% → 73% (+26%)
- ✅ **Tests corrigés** : 83 échecs → 51 échecs (-32)

### **État stable atteint :**
Le projet est maintenant **production-ready** pour les fonctionnalités critiques avec une base de tests solide et un processus de debug systématique documenté.

---

> **Note :** Les anciens scripts et documentation ont été archivés dans `archives/`. 
> Utilisez uniquement `unified_test_runner.py` et la documentation consolidée. 