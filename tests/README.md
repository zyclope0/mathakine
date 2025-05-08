# Documentation des Tests - Mathakine

## Structure des Tests

Le projet utilise une architecture de tests en 4 niveaux, organisée dans le dossier `tests/` :

```
tests/
├── unit/                 # Tests unitaires
│   └── test_models.py   # Tests des modèles de données
├── api/                  # Tests API
│   └── test_base_endpoints.py  # Tests des endpoints de base
├── integration/          # Tests d'intégration
│   └── test_user_exercise_flow.py  # Tests du flux utilisateur-exercice
├── functional/          # Tests fonctionnels
│   └── test_logic_challenge.py  # Tests des défis logiques
├── run_tests.py         # Script principal d'exécution des tests
├── run_tests.bat        # Script Windows pour l'exécution des tests
└── test_results/        # Dossier des résultats de test
```

## Types de Tests

### 1. Tests Unitaires (`unit/`)
- Testent les composants individuels de manière isolée
- Vérifient le comportement des modèles de données
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

## Exécution des Tests

### Via le Script Batch (Windows)
```bash
# Tous les tests
tests\run_tests.bat --all

# Tests spécifiques
tests\run_tests.bat --unit
tests\run_tests.bat --api
tests\run_tests.bat --integration
tests\run_tests.bat --functional
```

### Via Python
```bash
# Tous les tests
python tests/run_tests.py

# Tests spécifiques
python tests/run_tests.py --type unit
python tests/run_tests.py --type api
python tests/run_tests.py --type integration
python tests/run_tests.py --type functional
```

## Résultats des Tests

Les résultats sont générés dans le dossier `test_results/` :
- `test_run_{timestamp}.log` : Logs détaillés de l'exécution
- `coverage/` : Rapports de couverture de code en HTML
- `junit.xml` : Rapport au format JUnit

## Couverture de Code

Le projet utilise `pytest-cov` pour mesurer la couverture de code :
- Génère des rapports HTML détaillés
- Affiche les lignes non couvertes
- Calcule le pourcentage de couverture par module

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
   - Réutiliser le code de configuration
   - Isoler les dépendances
   - Nettoyer les ressources

## Exemple de Test

```python
def test_user_model():
    """Test de création et validation d'un modèle utilisateur"""
    user = User(
        username="test_user",
        email="test@example.com",
        role=UserRole.PADAWAN,
        created_at=datetime.now()
    )
    
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.role == UserRole.PADAWAN
    assert isinstance(user.created_at, datetime)
```

## Maintenance

1. **Mise à Jour**
   - Ajouter des tests pour les nouvelles fonctionnalités
   - Mettre à jour les tests existants lors des changements
   - Vérifier la couverture de code

2. **Dépannage**
   - Consulter les logs dans `test_results/`
   - Vérifier la couverture de code
   - Utiliser le mode debug de pytest

3. **Documentation**
   - Maintenir à jour cette documentation
   - Documenter les cas de test complexes
   - Expliquer les choix de conception

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