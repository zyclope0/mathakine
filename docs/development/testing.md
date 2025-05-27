# Guide complet du système de tests - Mathakine

Ce document décrit l'architecture de test complète du projet Mathakine, incluant la structure, les types de tests, l'exécution, le système CI/CD intégré et les bonnes pratiques.

## 1. Vue d'ensemble du système de tests

Le projet Mathakine implémente une architecture de tests en 4 niveaux avec un système CI/CD intégré pour assurer la qualité et la fiabilité du code. Cette approche permet de tester l'application sous différents angles, de l'unité individuelle jusqu'au système complet.

### Niveaux de tests

1. **Tests Unitaires** - Tests isolés de composants individuels
2. **Tests API** - Tests pour valider les endpoints REST
3. **Tests d'Intégration** - Tests des composants en interaction
4. **Tests Fonctionnels** - Tests du système complet, basés sur les cas d'utilisation

### Système CI/CD avec Classification Intelligente

Le projet utilise un système de classification des tests en 3 niveaux de criticité :

#### 🔴 Tests Critiques (BLOQUANTS)
- **Impact** : Bloquent le commit et le déploiement
- **Timeout** : 3 minutes maximum
- **Échecs max** : 1 seul échec autorisé
- **Contenu** : Tests fonctionnels, services core, authentification

#### 🟡 Tests Importants (NON-BLOQUANTS)  
- **Impact** : Avertissement, commit autorisé
- **Timeout** : 2 minutes maximum
- **Échecs max** : 5 échecs autorisés
- **Contenu** : Tests d'intégration, modèles, adaptateurs

#### 🟢 Tests Complémentaires (INFORMATIFS)
- **Impact** : Information seulement
- **Timeout** : 1 minute maximum
- **Échecs max** : 10 échecs autorisés
- **Contenu** : CLI, initialisation, fonctionnalités secondaires

### Installation du Système CI/CD

```bash
# Installation des hooks Git
python scripts/setup_git_hooks.py

# Vérification manuelle
python scripts/pre_commit_check.py

# Tests par catégorie
python -m pytest tests/functional/ -v      # Critiques
python -m pytest tests/integration/ -v     # Importants
python -m pytest tests/unit/test_cli.py -v # Complémentaires
```

### Pipeline GitHub Actions

Le pipeline CI/CD s'exécute automatiquement et comprend :
1. **Tests Critiques** en parallèle (fail-fast)
2. **Tests Importants** si critiques passent
3. **Tests Complémentaires** informatifs
4. **Analyse de couverture** de code
5. **Vérifications qualité** (Black, Flake8, Bandit)
6. **Génération de rapports** et artifacts

Pour plus de détails, consultez le [Guide CI/CD complet](../CI_CD_GUIDE.md).

### Structure des fichiers

```
tests/
├── unit/                   # Tests unitaires
│   ├── test_models.py      # Tests des modèles de données
│   ├── test_services.py    # Tests des services métier
│   ├── test_cascade_relationships.py  # Test des relations en cascade
│   └── test_utils.py       # Tests des utilitaires
├── api/                    # Tests API
│   ├── test_base_endpoints.py     # Tests des endpoints de base
│   ├── test_exercise_endpoints.py # Tests des endpoints d'exercices
│   ├── test_user_endpoints.py     # Tests des endpoints utilisateurs 
│   ├── test_deletion_endpoints.py  # Tests des endpoints de suppression
│   └── test_challenge_endpoints.py # Tests des endpoints de défis logiques
├── integration/            # Tests d'intégration
│   ├── test_user_exercise_flow.py  # Tests du flux utilisateur-exercice
│   └── test_cascade_deletion.py    # Tests de suppression en cascade
├── functional/             # Tests fonctionnels
│   ├── test_logic_challenge.py     # Tests des défis logiques
│   ├── test_enhanced_server.py     # Tests du serveur
│   └── test_starlette_cascade_deletion.py  # Tests de suppression via Starlette
├── fixtures/               # Fixtures réutilisables
│   ├── model_fixtures.py   # Instances de modèles pour les tests
│   └── db_fixtures.py      # Sessions de base de données pour les tests
├── conftest.py             # Configuration centralisée de pytest
├── run_tests.py            # Script principal d'exécution
├── run_tests.bat           # Script batch pour Windows
├── README.md               # Documentation des tests
└── TEST_PLAN.md            # Plan de test détaillé
```

## 2. Types de tests

### 2.1 Tests Unitaires (`unit/`)

Les tests unitaires vérifient le comportement des composants individuels en isolation.

#### Composants testés
- **Modèles de données** - création, validation, contraintes
- **Services métier** - logique d'affaires
- **Utilitaires** - fonctions auxiliaires
- **Relations en cascade** - configuration des relations

#### Exemples implémentés
- `test_models.py` - Teste les modèles User, Exercise, Attempt, etc.
- `test_cascade_relationships.py` - Vérifie les relations avec cascade="all, delete-orphan"
- `test_services.py` - Teste les services ExerciseService, UserService, etc.
- `test_enhanced_server_adapter.py` - Teste l'adaptateur pour le serveur Starlette

### 2.2 Tests API (`api/`)

Les tests API vérifient le comportement des endpoints REST, incluant les réponses, les codes d'état et la validation des données.

#### Endpoints testés
- **Endpoints de base** - racine, info, debug
- **Endpoints d'utilisateurs** - création, authentification, profil
- **Endpoints d'exercices** - liste, détail, soumission, suppression
- **Endpoints de défis logiques** - liste, détail, résolution

#### Exemples implémentés
- `test_base_endpoints.py` - Teste les endpoints de base
- `test_exercise_endpoints.py` - Teste les endpoints d'exercices
- `test_deletion_endpoints.py` - Teste les suppressions en cascade via API

### 2.3 Tests d'Intégration (`integration/`)

Les tests d'intégration vérifient l'interaction entre plusieurs composants de l'application.

#### Flux testés
- **Flux utilisateur-exercice** - Inscription → Exercice → Réponse → Statistiques
- **Suppression en cascade** - Vérification de l'intégrité référentielle
- **Transactions** - Comportement des transactions sur plusieurs tables

#### Exemples implémentés
- `test_user_exercise_flow.py` - Teste le flux complet utilisateur-exercice
- `test_cascade_deletion.py` - Teste la suppression en cascade entre modèles

### 2.4 Tests Fonctionnels (`functional/`)

Les tests fonctionnels vérifient le comportement de l'application complète du point de vue de l'utilisateur.

#### Fonctionnalités testées
- **Défis logiques** - Workflow complet des défis
- **Démarrage du serveur** - Vérification du démarrage correct
- **Suppressions en cascade** - Comportement end-to-end dans Starlette

#### Exemples implémentés
- `test_logic_challenge.py` - Teste les défis logiques
- `test_enhanced_server.py` - Teste le démarrage du serveur
- `test_starlette_cascade_deletion.py` - Teste les suppressions dans le serveur

## 3. Focus sur les tests de suppression en cascade

Un ensemble spécifique de tests a été mis en place pour valider le mécanisme de suppression en cascade, essentiel à l'intégrité des données.

### 3.1 Tests unitaires
- Vérifient la configuration des relations avec `cascade="all, delete-orphan"`
- Test des relations entre User, Exercise, Attempt, LogicChallenge

### 3.2 Tests d'intégration
- Valident que la suppression d'une entité déclenche la suppression des entités dépendantes
- Testent les suppressions pour User → Exercise → Attempt

### 3.3 Tests API
- Vérifient les endpoints de suppression (DELETE /api/exercises/{id}, etc.)
- Testent les autorisations et les cas d'erreur

### 3.4 Tests fonctionnels
- Testent le comportement end-to-end dans le serveur Starlette
- Vérifient l'intégrité référentielle complète

### Exemple de test de suppression en cascade

```python
def test_exercise_cascade_deletion(db_session):
    """Test that deleting an exercise cascades to attempts"""
    # Créer un utilisateur
    user = User(username="cascade_test", email="cascade@test.com", 
                hashed_password="hashed_pass")
    db_session.add(user)
    db_session.commit()
    
    # Créer un exercice
    exercise = Exercise(title="Cascade Test", creator_id=user.id,
                       exercise_type=ExerciseType.ADDITION,
                       difficulty=DifficultyLevel.INITIE,
                       question="1+1=?", correct_answer="2")
    db_session.add(exercise)
    db_session.commit()
    
    # Créer des tentatives
    attempt = Attempt(user_id=user.id, exercise_id=exercise.id,
                     user_answer="2", is_correct=True)
    db_session.add(attempt)
    db_session.commit()
    
    # Vérifier que la tentative existe
    assert db_session.query(Attempt).filter_by(id=attempt.id).first() is not None
    
    # Supprimer l'exercice
    db_session.delete(exercise)
    db_session.commit()
    
    # Vérifier que la tentative a été supprimée en cascade
    assert db_session.query(Attempt).filter_by(id=attempt.id).first() is None
```

## 4. Fixtures et configuration des tests

### 4.1 Fixtures réutilisables

Les fixtures sont centralisées dans le dossier `fixtures/` pour faciliter la réutilisation :

#### Modèles (`model_fixtures.py`)
- Fournit des instances préconfigurées des modèles
- Exemples : `test_user()`, `test_exercise()`, `test_logic_challenge()`

#### Base de données (`db_fixtures.py`)
- Fournit des sessions de base de données pour les tests
- Supporte SQLite et PostgreSQL
- Exemples : `db_session()`, `populated_db_session()`

### 4.2 Configuration centralisée

Le fichier `conftest.py` centralise la configuration de pytest :

- **Configuration de session** - Initialisation et nettoyage
- **Fixtures d'authentification** - Pour les tests nécessitant un utilisateur connecté
- **Base de données temporaire** - Configuration automatique de la base de test

## 5. Exécution des tests

### 5.1 Script unifié

Le script `run_tests.bat` (Windows) ou `run_tests.py` (multiplateforme) permet d'exécuter les tests facilement :

```bash
# Exécuter tous les tests
tests/run_tests.bat --all

# Exécuter par catégorie
tests/run_tests.bat --unit      # Tests unitaires
tests/run_tests.bat --api       # Tests API
tests/run_tests.bat --integration # Tests d'intégration
tests/run_tests.bat --functional # Tests fonctionnels

# Options additionnelles
tests/run_tests.bat --file FILE  # Tester un fichier spécifique
tests/run_tests.bat --verbose    # Mode verbeux
tests/run_tests.bat --no-coverage # Désactiver la couverture
```

### 5.2 Via Python directement

Vous pouvez également exécuter les tests directement avec pytest :

```bash
# Tous les tests
python -m pytest tests/

# Tests par dossier
python -m pytest tests/unit/
python -m pytest tests/api/
python -m pytest tests/integration/
python -m pytest tests/functional/

# Couverture de code
python -m pytest --cov=app --cov-report=html:test_results/coverage tests/
```

### 5.3 Base de données de test

Par défaut, les tests utilisent SQLite, mais vous pouvez configurer PostgreSQL :

```bash
# Windows
set TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
run_tests.bat --all

# Linux/Mac
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
./run_tests.sh --all
```

## 6. Système d'auto-validation

Le projet intègre un système complet d'auto-validation pour vérifier l'intégrité et la compatibilité.

### 6.1 Scripts principaux

| Script | Description |
|--------|-------------|
| `auto_validation.py` | Validation complète du projet |
| `auto_validate.bat` | Script batch pour Windows |
| `simple_validation.py` | Vérification simplifiée |
| `compatibility_check.py` | Vérification de compatibilité |
| `generate_report.py` | Génération de rapport |

### 6.2 Utilisation recommandée

#### Validation quotidienne
```bash
python tests/simplified_validation.py
```

#### Avant un commit
```bash
tests/auto_validate.bat
```

#### Après mise à jour des dépendances
```bash
python tests/compatibility_check.py
```

## 7. Rapports et résultats

Tous les rapports sont générés dans le dossier `test_results/` :

1. **Journal détaillé** - `auto_validation_TIMESTAMP.log`
2. **Rapport de couverture** - `coverage/index.html`
3. **Rapport JUnit XML** - `junit.xml`
4. **Rapport complet** - `rapport_complet_TIMESTAMP.md`

### Résultats actuels (mai 2025)

- **58 tests réussis**
- **1 test ignoré** (PostgreSQL spécifique)
- **0 échecs**
- **Couverture de code: 64%**
- **Temps d'exécution moyen: ~25 secondes**

## 8. Bonnes pratiques

### 8.1 Nommage des tests
- Utiliser des noms descriptifs (`test_user_deletion_cascades_to_exercises`)
- Préfixer avec `test_`
- Inclure le comportement attendu

### 8.2 Organisation
- Un fichier de test par module
- Tests indépendants
- Nettoyage après chaque test

### 8.3 Assertions
- Vérifier un comportement par test
- Utiliser des messages d'erreur clairs
- Tester les cas positifs et négatifs

### 8.4 Fixtures
- Réutiliser les fixtures centralisées
- Isoler les dépendances
- Nettoyer les ressources

## 9. Plan d'amélioration des tests

### 9.1 Couverture à améliorer
- Services métier (génération d'exercices, validation des réponses)
- Cas d'erreur et cas limites
- Nouveaux endpoints

### 9.2 Tests à ajouter
- Tests de performance
- Tests d'interface utilisateur
- Tests de déploiement

### 9.3 Tests asynchrones
- Support amélioré pour les fonctions asynchrones
- Tests de concurrence

## 10. Critères de succès

Pour valider la qualité des tests, nous nous basons sur les critères suivants :

### 10.1 Couverture
- Unitaires : > 90%
- API : > 85%
- Intégration : > 80%
- Fonctionnels : > 75%

### 10.2 Performance
- Temps de réponse < 200ms
- Utilisation CPU < 50%
- Utilisation mémoire < 500MB

### 10.3 Qualité
- Aucun test échoué
- Aucune vulnérabilité critique
- Documentation à jour

## 11. Responsabilités

| Rôle | Responsabilité |
|------|----------------|
| Développeur | Tests unitaires et API |
| Testeur | Tests d'intégration et fonctionnels |
| Lead Dev | Supervision de la qualité |
| DevOps | Configuration de l'environnement |

## 12. Dépannage courant

| Problème | Cause possible | Solution |
|----------|----------------|----------|
| Échec SQLAlchemy avec Python 3.13 | Incompatibilité | Utiliser Python 3.11/3.12 ou SQLAlchemy 2.0.27+ |
| Erreur d'importation | Module manquant | Exécuter `setup_validation.py` |
| Problèmes de permissions | Droits insuffisants | Exécuter en administrateur |
| Tests bloqués | Processus en arrière-plan | Redémarrer le terminal |

---

*Ce document consolide les informations de tests/README.md, tests/TEST_PLAN.md et docs/TESTS.md* 