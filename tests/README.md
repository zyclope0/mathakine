# Tests Mathakine (API Rebelle)

Ce répertoire contient la structure des tests pour le projet Mathakine (anciennement Math Trainer), organisés selon une logique claire pour assurer la qualité et la fiabilité de l'application.

## Structure des Tests

Les tests sont organisés en quatre catégories principales :

```
math-trainer-backend/tests/
├── unit/           # Tests unitaires (composants individuels)
├── integration/    # Tests d'intégration (interactions entre composants)
├── api/            # Tests API (points d'accès de l'API Rebelle)
├── functional/     # Tests fonctionnels (fonctionnalités complètes)
├── TEST_PLAN.md    # Plan de test détaillé
└── run_tests.py    # Script d'exécution des tests
```

### Types de Tests

1. **Tests Unitaires** (unit)
   - Tests des énumérations et constantes
   - Tests des modèles de données
   - Tests de validation des schémas
   - Tests de génération d'exercices mathématiques

2. **Tests d'Intégration** (integration)
   - Tests des interactions entre composants
   - Tests du flux complet utilisateur-exercice
   - Tests de la base de données et des requêtes

3. **Tests API** (api)
   - Tests des points d'accès de base
   - Tests des points d'accès des exercices
   - Tests des points d'accès utilisateurs
   - Tests d'authentification

4. **Tests Fonctionnels** (functional)
   - Tests des fonctionnalités métier complètes
   - Tests des scénarios utilisateurs

## Exécution des Tests

### En utilisant les scripts fournis

#### Windows (PowerShell)

```powershell
# Exécuter tous les tests
.\Run-Tests.ps1

# Exécuter uniquement les tests unitaires
.\Run-Tests.ps1 -Type unit

# Exécuter avec plus de détails
.\Run-Tests.ps1 -Verbose
```

#### Windows (Batch)

```batch
# Exécuter tous les tests
run_tests.bat

# Exécuter uniquement les tests API
run_tests.bat --api

# Exécuter avec plus de détails
run_tests.bat --verbose
```

#### Directement avec Python

```bash
# Exécuter tous les tests
python math-trainer-backend/tests/run_tests.py

# Exécuter uniquement les tests d'intégration
python math-trainer-backend/tests/run_tests.py --type integration

# Exécuter avec plus de détails
python math-trainer-backend/tests/run_tests.py --verbose
```

## Conventions de Nommage

- Tous les fichiers de test commencent par `test_`
- Les classes de test commencent par `Test`
- Les méthodes de test commencent par `test_`
- Les commentaires des tests sont en français

## Plan de Test Complet

Pour une documentation exhaustive de tous les scénarios de test, consultez le fichier [TEST_PLAN.md](TEST_PLAN.md) qui contient :

- La matrice de couverture des tests
- Les objectifs détaillés de chaque test
- Les procédures de test manuel
- Les critères de validation
- La gestion des défauts

## Thème Star Wars

Conformément au thème du projet, les tests utilisent la terminologie Star Wars :
- **Padawan** : Utilisateur apprenant
- **Maître** : Enseignant
- **Gardien** : Parent/Tuteur
- **Archiviste** : Administrateur
- **API Rebelle** : L'API REST Mathakine
- **Épreuves du Conseil Jedi** : Défis logiques 