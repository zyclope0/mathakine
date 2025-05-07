# Tests Mathakine (API Rebelle)

Ce répertoire contient la structure des tests pour le projet Mathakine, organisés selon une logique claire pour assurer la qualité et la fiabilité de l'application.

## Structure des Tests

Les tests sont organisés en quatre catégories principales :

```
math-trainer-backend/tests/
├── unit/           # Tests unitaires (composants individuels)
├── integration/    # Tests d'intégration (interactions entre composants)
├── api/            # Tests API (points d'accès de l'API Rebelle)
├── functional/     # Tests fonctionnels (fonctionnalités complètes)
├── TEST_PLAN.md    # Plan de test détaillé
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

#### Windows (Batch)

```batch
# Exécuter tous les tests
scripts/tests/run_tests.bat
```

#### Windows (PowerShell)

```powershell
# Exécuter tous les tests
scripts/tests/Run-Tests.ps1
```

#### Directement avec Python

```bash
# Exécuter tous les tests
python math-trainer-backend/tests/run_tests.py
```

## Conventions de Nommage

- Tous les fichiers de test commencent par `test_`
- Les classes de test commencent par `Test`
- Les méthodes de test commencent par `test_`
- Les commentaires des tests sont en français

## Plan de Test Complet

Pour une documentation exhaustive de tous les scénarios de test, consultez le fichier [TEST_PLAN.md](TEST_PLAN.md).

## Thème Star Wars

Conformément au thème du projet, les tests utilisent la terminologie Star Wars :
- **Padawan** : Utilisateur apprenant
- **Maître** : Enseignant
- **Gardien** : Parent/Tuteur
- **Archiviste** : Administrateur
- **API Rebelle** : L'API REST Mathakine
- **Épreuves du Conseil Jedi** : Défis logiques 