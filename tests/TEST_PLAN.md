# Plan de Tests - Mathakine

Ce document détaille la stratégie de test complète pour le projet Mathakine, une application d'apprentissage des mathématiques avec une thématique Star Wars.

## Niveaux de Tests

L'application utilise plusieurs niveaux de tests pour assurer une qualité optimale:

1. **Tests Unitaires** - Tests isolés de composants individuels
2. **Tests API** - Tests pour valider les endpoints REST
3. **Tests d'Intégration** - Tests des composants en interaction
4. **Tests Fonctionnels** - Tests du système complet, basés sur les cas d'utilisation

## Ressources

### Équipe

| Rôle | Responsabilité |
|------|----------------|
| Développeur | Implémentation des tests unitaires et API |
| Testeur | Implémentation des tests d'intégration et fonctionnels |
| Lead Dev | Supervision de la qualité des tests |

### Environnements

| Environnement | Description |
|---------------|-------------|
| Développement | Tests développement local |
| Test | Pour tests d'intégration et validation |
| Production | Vérifications finales avant déploiement |

## Stratégie de Validation

### Configuration des Tests

Tous les tests peuvent être exécutés via pytest:

```bash
pytest -v
```

### Système d'Auto-Validation

Le projet intègre un système complet d'auto-validation pour faciliter la vérification de l'intégrité et la compatibilité du projet:

#### Scripts Principaux

| Script | Description |
|--------|-------------|
| `auto_validation.py` | Validation complète du projet (syntaxe, tests unitaires, API, intégration, fonctionnels) |
| `auto_validate.bat` | Script batch pour exécuter `auto_validation.py` facilement sur Windows |
| `simple_validation.py` | Vérification de la structure du projet sans dépendances complexes |
| `simplified_validation.py` | Version minimale pour diagnostics rapides |
| `compatibility_check.py` | Vérification de compatibilité Python 3.13+ et dépendances |
| `db_check.py` | Vérification de la configuration de la base de données |
| `api_check.py` | Test de l'API sans dépendre de SQLAlchemy |
| `basic_check.py` | Détection des problèmes de configuration élémentaires |
| `generate_report.py` | Génération d'un rapport complet au format Markdown |

#### Utilisation

```bash
# Configuration de l'environnement de validation
tests/setup_validation.bat

# Validation complète
tests/auto_validate.bat

# Vérification de compatibilité
python tests/compatibility_check.py

# Génération de rapport
python tests/generate_report.py
```

Pour plus de détails, consultez `docs/validation/README.md`.

## Plan d'Exécution

### Tests Unitaires

- Tests des modèles de données
- Tests des services métier
- Tests des utilitaires
- Tests des relations en cascade

### Tests API

- Tests des endpoints REST
- Vérification des réponses JSON
- Validation des codes de statut HTTP
- Tests des endpoints de suppression en cascade

### Tests d'Intégration

- Tests de l'interaction entre services
- Tests de la persistance des données
- Tests de l'authentification
- Tests de suppression en cascade entre modèles

### Tests Fonctionnels

- Tests des cas d'utilisation principal
- Tests des workflows utilisateur
- Tests de la UI (si applicable)
- Tests des suppressions en cascade sur le serveur Starlette

## Critères de Succès

1. Tous les tests unitaires et API doivent réussir avant toute fusion
2. La couverture de code doit être d'au moins 80%
3. Les tests d'intégration et fonctionnels doivent réussir avant un déploiement en production

## Outils

- **pytest** - Exécution des tests
- **pytest-cov** - Analyse de la couverture de code
- **Auto-validation** - Système complet de validation du projet
- **generate_report.py** - Génération de rapports de test

## Objectifs des Tests

1. **Qualité du Code**
   - Couverture de code > 80%
   - Tests automatisés pour toutes les fonctionnalités
   - Détection précoce des régressions

2. **Fiabilité**
   - Validation des fonctionnalités métier
   - Vérification des flux utilisateurs
   - Test des cas limites

3. **Performance**
   - Temps de réponse < 200ms
   - Gestion correcte des ressources
   - Scalabilité des opérations

## Types de Tests

### 1. Tests Unitaires

#### 1.1 Modèles de Données
- [x] Création et validation des modèles (types de tests vérifiés: UserRole.PADAWAN, ExerciseType.ADDITION, DifficultyLevel.INITIE)
- [x] Relations entre modèles
- [x] Contraintes de données
- [x] Validation des champs
- [x] Relations cascade (test_cascade_relationships.py)

#### 1.2 Services
- [ ] Génération d'exercices
- [ ] Validation des réponses
- [ ] Calcul des scores
- [ ] Gestion des utilisateurs

### 2. Tests API

#### 2.1 Endpoints de Base
- [x] Route racine (/)
- [x] Informations API (/api/info)
- [x] Debug (/debug)
- [x] Gestion des erreurs

#### 2.2 Endpoints Utilisateurs
- [x] Création de compte
- [x] Authentification
- [x] Gestion du profil
- [x] Progression

#### 2.3 Endpoints Exercices
- [x] Liste des exercices
- [x] Détails d'un exercice
- [x] Soumission de réponse
- [x] Historique des tentatives
- [x] Suppression en cascade (test_deletion_endpoints.py)

### 3. Tests d'Intégration

#### 3.1 Flux Utilisateur
- [x] Inscription → Authentification
- [x] Sélection d'exercice → Réponse
- [x] Progression → Niveau suivant
- [x] Historique → Statistiques

#### 3.2 Base de Données
- [x] Création des tables
- [x] Relations entre tables
- [x] Transactions
- [x] Migrations
- [x] Suppressions en cascade (test_cascade_deletion.py)

### 4. Tests Fonctionnels

#### 4.1 Défis Logiques
- [x] Liste des défis
- [x] Détails d'un défi
- [x] Soumission de réponse
- [x] Système d'indices

#### 4.2 Progression
- [x] Suivi des progrès
- [x] Niveaux de difficulté
- [x] Récompenses
- [x] Statistiques

#### 4.3 Suppressions en cascade
- [x] Serveur Starlette (test_starlette_cascade_deletion.py)
- [x] Intégrité référentielle
- [x] Comportement end-to-end

## Environnements de Test

### 1. Développement
- Base de données : SQLite
- Mode : Debug
- Logs : Détaillés

### 2. Test
- Base de données : PostgreSQL
- Mode : Test
- Logs : Résumés

### 3. Production
- Base de données : PostgreSQL
- Mode : Production
- Logs : Critiques

## Exécution des Tests

### 1. Local
```bash
# Tous les tests
tests/run_tests.bat --all

# Tests spécifiques
tests/run_tests.bat --unit
tests/run_tests.bat --api
tests/run_tests.bat --integration
tests/run_tests.bat --functional
```

### 2. CI/CD
```yaml
# GitHub Actions
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: python tests/run_tests.py
```

## Critères de Succès

### 1. Couverture
- Unitaires : > 90%
- API : > 85%
- Intégration : > 80%
- Fonctionnels : > 75%

### 2. Performance
- Temps de réponse < 200ms
- Utilisation CPU < 50%
- Utilisation mémoire < 500MB

### 3. Qualité
- Aucun test échoué
- Aucune vulnérabilité critique
- Documentation à jour

## Maintenance

### 1. Mise à Jour
- Ajout de tests pour nouvelles fonctionnalités
- Mise à jour des tests existants
- Vérification de la couverture

### 2. Documentation
- Mise à jour du plan de test
- Documentation des cas complexes
- Historique des changements

### 3. Revue
- Revue mensuelle des tests
- Analyse des échecs
- Optimisation des performances

## Responsabilités

### 1. Développeurs
- Écrire les tests unitaires
- Maintenir la couverture
- Corriger les échecs

### 2. QA
- Exécuter les tests fonctionnels
- Valider les scénarios
- Documenter les bugs

### 3. DevOps
- Configurer l'environnement
- Automatiser les tests
- Gérer les déploiements

## Historique des Versions

| Version | Date | Auteur | Description |
|---------|------|--------|-------------|
| 1.0 | 2025-03-07 | Claude | Version initiale |
| 1.1 | 2025-03-08 | Claude | Ajout des tests API |
| 1.2 | 2025-03-09 | Claude | Ajout des tests fonctionnels |
| 1.3 | 2025-05-12 | Claude | Ajout des tests de suppression en cascade | 