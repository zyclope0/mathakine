# Documentation des Tests - Mathakine

## Structure des Tests

Le projet utilise une architecture de tests en 4 niveaux, organisée dans le dossier `tests/` :

```
tests/
├── unit/                   # Tests unitaires
│   ├── test_models.py      # Tests des modèles de données
│   ├── test_services.py    # Tests des services métier
│   └── test_utils.py       # Tests des utilitaires
├── api/                    # Tests API
│   ├── test_base_endpoints.py     # Tests des endpoints de base
│   ├── test_exercise_endpoints.py # Tests des endpoints d'exercices
│   ├── test_user_endpoints.py     # Tests des endpoints utilisateurs 
│   └── test_challenge_endpoints.py # Tests des endpoints de défis logiques
├── integration/            # Tests d'intégration
│   └── test_user_exercise_flow.py  # Tests du flux utilisateur-exercice
├── functional/             # Tests fonctionnels
│   └── test_logic_challenge.py     # Tests des défis logiques
├── fixtures/               # Fixtures réutilisables
│   ├── model_fixtures.py   # Instances de modèles pour les tests
│   └── db_fixtures.py      # Sessions de base de données pour les tests
├── automation/             # Scripts d'automatisation
│   ├── run_tests.py        # Script principal unifié
│   └── run_tests.bat       # Script batch pour Windows
├── conftest.py             # Configuration centralisée de pytest
└── README.md               # Cette documentation
```

## Types de Tests

### 1. Tests Unitaires (`unit/`)
- Testent les composants individuels de manière isolée
- Vérifient le comportement des modèles, services et utilités
- Exemple : `test_models.py` teste la création et la validation des modèles

### 2. Tests API (`api/`)
- Testent les endpoints de l'API
- Vérifient les réponses HTTP et les formats de données
- Exemple : `test_base_endpoints.py` teste les endpoints de base

### 3. Tests d'Intégration (`integration/`)
- Testent l'interaction entre différents composants
- Vérifient les flux complets
- Exemple : `test_user_exercise_flow.py` teste le flux utilisateur-exercice

### 4. Tests Fonctionnels (`functional/`)
- Testent les fonctionnalités complètes
- Vérifient le comportement end-to-end
- Exemple : `test_logic_challenge.py` teste les défis logiques

### 5. Tests de suppression en cascade

Le projet inclut une série complète de tests pour valider le mécanisme de suppression en cascade :

1. **Tests unitaires** : `unit/test_cascade_relationships.py`
   - Vérifie que les relations avec cascade sont correctement configurées dans les modèles
   - Teste les relations entre User, Exercise, Attempt, LogicChallenge

2. **Tests d'intégration** : `integration/test_cascade_deletion.py`
   - Valide que la suppression d'une entité déclenche bien la suppression des entités dépendantes
   - Teste les suppressions en cascade pour Exercise, User et LogicChallenge

3. **Tests API** : `api/test_deletion_endpoints.py`
   - Vérifie que les endpoints de suppression gèrent correctement les suppressions en cascade
   - Teste les autorisations et les cas d'erreur

4. **Tests fonctionnels** : `functional/test_starlette_cascade_deletion.py`
   - Teste que le serveur Starlette gère correctement les suppressions en cascade
   - Valide le comportement end-to-end des suppressions

## Fixtures Réutilisables

Les fixtures sont centralisées dans le dossier `fixtures/` pour faciliter la réutilisation :

### 1. Modèles (`model_fixtures.py`)
- Fournit des instances préconfigurées des modèles de données
- Exemple : `test_user()`, `test_exercise()`, `test_logic_challenge()`

### 2. Base de Données (`db_fixtures.py`)
- Fournit des sessions de base de données pour les tests
- Supporte à la fois SQLite et PostgreSQL
- Exemple : `db_session()`, `populated_db_session()`

## Exécution des Tests

### Via le Script Unifié
```bash
# À la racine du projet
run_tests.bat --help              # Affiche l'aide
run_tests.bat --full              # Exécute une validation complète
run_tests.bat --basic             # Exécute une validation basique (tests unitaires et API)
run_tests.bat --unit              # Exécute uniquement les tests unitaires
run_tests.bat --api               # Exécute uniquement les tests d'API
run_tests.bat --integration       # Exécute uniquement les tests d'intégration
run_tests.bat --functional        # Exécute uniquement les tests fonctionnels
run_tests.bat --file FILE         # Exécute un fichier de test spécifique
run_tests.bat --verbose           # Mode verbeux
run_tests.bat --no-coverage       # Désactive la couverture de code
```

### Via Python Directement
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

## Rapports

Tous les rapports sont générés dans le dossier `test_results/` :

1. **Journal détaillé** : `auto_validation_TIMESTAMP.log`
2. **Rapport de compatibilité** : `compatibility_report_TIMESTAMP.txt`
3. **Rapport de validation** : `validation_TIMESTAMP.json`
4. **Rapport complet** : `rapport_complet_TIMESTAMP.md`
5. **Couverture de code** : `coverage/index.html`

Les formats des rapports ont été conservés pour assurer la compatibilité avec les processus existants.

## Base de données de test

Par défaut, les tests utilisent SQLite (`sqlite:///./test.db`), mais vous pouvez configurer une base de données PostgreSQL en définissant la variable d'environnement `TEST_DATABASE_URL` :

```bash
# Windows
set TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
run_tests.bat --full

# Linux/Mac
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db
./run_tests.sh --full
```

## Bonnes Pratiques

1. **Nommage des Tests**
   - Utiliser des noms descriptifs
   - Préfixer avec `test_`
   - Inclure le comportement attendu

2. **Organisation**
   - Un fichier de test par module
   - Tests indépendants
   - Nettoyage après chaque test

3. **Assertions**
   - Vérifier un comportement par test
   - Utiliser des messages d'erreur clairs
   - Tester les cas positifs et négatifs

4. **Fixtures**
   - Réutiliser les fixtures centralisées
   - Isoler les dépendances
   - Nettoyer les ressources

## Maintenance

1. **Ajout de Tests**
   - Créer un test pour chaque nouvelle fonctionnalité
   - Vérifier la couverture de code pour identifier les parties non testées
   - Ajouter des tests pour les cas limites ou scénarios d'erreur

2. **Mise à Jour**
   - Maintenir les fixtures à jour avec les modèles
   - Adapter les tests existants lors des modifications du code
   - Vérifier régulièrement la couverture globale

3. **Dépannage**
   - Consulter les logs dans `test_results/`
   - Exécuter les tests individuellement pour isoler les problèmes
   - Utiliser le mode verbose pour plus de détails

## Dépendances

- pytest
- pytest-cov
- fastapi
- sqlalchemy
- loguru

## Contribution

1. Écrire des tests pour les nouvelles fonctionnalités
2. Maintenir la couverture de code
3. Documenter les changements
4. Suivre les bonnes pratiques 

## Système d'Auto-Validation

Le projet Mathakine intègre un système complet d'auto-validation qui permet de vérifier l'intégrité et la compatibilité du projet à différents niveaux.

### Scripts de Validation

#### 1. Scripts Principaux

- **`auto_validation.py`** : Script principal qui exécute tous les tests (unitaires, API, intégration, fonctionnels) et vérifie la syntaxe Python.
- **`auto_validate.bat`** : Script batch pour exécuter `auto_validation.py` facilement sur Windows.
- **`auto_validator.bat`** : Exécute tous les outils de validation séquentiellement et génère un rapport complet.

#### 2. Scripts Alternatifs

Ces scripts ont été développés pour fonctionner même avec des problèmes de compatibilité (par exemple avec Python 3.13) :

- **`simple_validation.py`** : Vérifie la structure du projet sans dépendances complexes.
- **`simplified_validation.py`** : Version encore plus légère pour diagnostics rapides.
- **`db_check.py`** : Vérifie la configuration de la base de données sans dépendre de SQLAlchemy.
- **`api_check.py`** : Teste l'API sans dépendre de SQLAlchemy.
- **`basic_check.py`** : Détecte les problèmes de configuration élémentaires.
- **`compatibility_check.py`** : Vérifie la compatibilité avec Python 3.13+ et les dépendances.
- **`generate_report.py`** : Produit un rapport complet au format Markdown.

### Configuration de l'Environnement

Avant d'utiliser les scripts de validation, configurez l'environnement :

```bash
# En batch
tests/setup_validation.bat

# Directement en Python
python tests/setup_validation.py
```

Ce script installe toutes les dépendances nécessaires pour les validations et crée les dossiers requis.

### Utilisation Recommandée

#### 1. Validation Quotidienne

Lors du développement quotidien, utilisez la validation simplifiée pour des vérifications rapides :

```bash
python tests/simplified_validation.py
```

#### 2. Avant un Commit ou une Pull Request

Avant de soumettre des modifications au dépôt, exécutez la validation complète :

```bash
tests/auto_validate.bat
```

#### 3. Après une Mise à Jour de Dépendances

Après avoir mis à jour des dépendances, vérifiez la compatibilité :

```bash
python tests/compatibility_check.py
```

#### 4. Génération de Rapports pour l'Équipe

Pour produire des rapports détaillés à partager avec l'équipe :

```bash
python tests/generate_report.py
```

### Interprétation des Résultats

- **✅ SUCCESS** : Le test ou la vérification a réussi
- **⚠️ WARNING** : Problème non critique détecté
- **❌ ERROR** : Problème critique nécessitant une correction
- **ℹ️ INFO** : Information contextuelle

Les rapports complets sont générés dans le dossier `test_results/`.

### Dépannage Courant

| Problème | Cause Possible | Solution |
|----------|----------------|----------|
| Échec des tests SQLAlchemy | Incompatibilité avec Python 3.13 | Utiliser Python 3.11/3.12 ou SQLAlchemy 2.0.27+ |
| Erreur d'importation | Module manquant | Exécuter `setup_validation.py` |
| Problèmes de permissions | Droits insuffisants | Exécuter en tant qu'administrateur |
| Tests bloqués | Processus en arrière-plan | Redémarrer le terminal |

Pour plus d'informations sur le système d'auto-validation, consultez la documentation dans `docs/validation/README.md`. 