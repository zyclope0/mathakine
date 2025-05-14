# Documentation des Tests Mathakine

## Structure des Tests

Le projet Mathakine comprend une suite de tests complète organisée en quatre niveaux, conformément aux bonnes pratiques du développement logiciel. Cette approche permet de tester l'application sous différents angles, assurant ainsi sa robustesse et sa fiabilité.

### Niveaux de Tests

1. **Tests Unitaires** (`tests/unit/`)
   - Validation des composants individuels
   - Vérifient que chaque unité de code fonctionne comme prévu en isolation
   - Focus sur les modèles, services et utilitaires

2. **Tests d'API** (`tests/api/`)
   - Validation des endpoints API Rest
   - Vérifient que les réponses HTTP, codes d'état et formats sont corrects
   - Chaque endpoint est testé indépendamment

3. **Tests d'Intégration** (`tests/integration/`)
   - Validation de l'interaction entre composants
   - Vérifient que les différentes parties de l'application fonctionnent correctement ensemble
   - Incluent des flux complets (par exemple, création utilisateur → création exercice → tentative)

4. **Tests Fonctionnels** (`tests/functional/`)
   - Validation du comportement de l'application entière
   - Vérifient les fonctionnalités du point de vue de l'utilisateur
   - Tests de l'interface Starlette et des fonctionnalités serveur complètes

### Organisation des Fichiers

```
tests/
├── api/                   # Tests des endpoints API
│   ├── test_base_endpoints.py
│   ├── test_challenge_endpoints.py
│   ├── test_deletion_endpoints.py
│   └── test_exercise_endpoints.py
├── fixtures/              # Données de test partagées
│   ├── db_fixtures.py
│   └── model_fixtures.py
├── functional/            # Tests fonctionnels
│   ├── test_enhanced_server.py
│   ├── test_logic_challenge.py
│   └── test_starlette_cascade_deletion.py
├── integration/           # Tests d'intégration
│   ├── test_cascade_deletion.py
│   └── test_user_exercise_flow.py
├── unit/                  # Tests unitaires
│   ├── test_cascade_relationships.py
│   ├── test_cli.py
│   ├── test_db_init_service.py
│   ├── test_models.py
│   └── test_services.py
├── conftest.py            # Configuration centralisée pour pytest
├── run_tests.py           # Script Python pour exécuter les tests
├── run_tests.bat          # Script batch pour exécuter les tests sous Windows
├── README.md              # Documentation des tests
└── TEST_PLAN.md           # Plan de test détaillé
```

## Exécution des Tests

### Commandes d'Exécution

Pour exécuter les tests, utilisez les commandes suivantes:

```bash
# Exécuter tous les tests
tests/run_tests.bat --all

# Exécuter par catégorie
tests/run_tests.bat --unit
tests/run_tests.bat --api
tests/run_tests.bat --integration
tests/run_tests.bat --functional

# Exécuter les tests avec coverage
tests/run_tests.bat --all --cov
```

### Rapports Générés

Les rapports suivants sont générés automatiquement dans le dossier `tests/test_results/`:

- **Journaux détaillés**: Fichiers log avec timestamp
- **Rapports de couverture HTML**: Détails de la couverture du code dans `coverage/`
- **Rapports JUnit XML**: Compatible avec les systèmes CI/CD dans `junit.xml`
- **Rapports par catégorie**: Fichiers XML séparés pour chaque type de test

## Tests de Suppression en Cascade

Une attention particulière a été portée aux tests de suppression en cascade, qui sont essentiels pour maintenir l'intégrité des données dans l'application.

### Objectif

Vérifier que lors de la suppression d'une entité parente (comme un utilisateur), toutes les entités enfants associées (exercices, tentatives, etc.) sont automatiquement supprimées.

### Tests Implémentés

1. **Tests Unitaires**
   - `test_cascade_relationships.py`: Vérifie la configuration correcte des relations avec `cascade="all, delete-orphan"`
   
2. **Tests d'API**
   - `test_deletion_endpoints.py`: Vérifie que les endpoints de suppression suppriment correctement les données associées

3. **Tests d'Intégration**
   - `test_cascade_deletion.py`: Vérifie le comportement en cascade à travers plusieurs modèles

4. **Tests Fonctionnels**
   - `test_starlette_cascade_deletion.py`: Vérifie le comportement de suppression en cascade dans le serveur Starlette

### Exemple de Test de Suppression en Cascade

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

## Récentes Améliorations (Mai 2025)

### Corrections et Améliorations

1. **Correction de l'Authentification dans les Tests**
   - Ajout d'une fixture `auth_client` dans `conftest.py` pour faciliter les tests nécessitant l'authentification
   - Correction des tests de défis logiques pour utiliser cette authentification

2. **Amélioration de la Gestion des Transactions**
   - Correction des avertissements "transaction already deassociated" dans les tests
   - Meilleure gestion des sessions SQLAlchemy dans les tests

3. **Support des Tests Asynchrones**
   - Ajout de `pytest-asyncio` pour les tests de fonctions asynchrones
   - Adaptation du test `test_starlette_cascade_deletion.py` pour supporter les fonctions `async`

4. **Correction des Tests du Serveur**
   - Nouveau test `test_enhanced_server.py` pour vérifier le démarrage du serveur
   - Meilleure gestion des erreurs et timeout dans les tests de serveur

5. **Mise à Jour des API**
   - Nouveaux endpoints `/attempt` pour les exercices
   - Endpoint de statistiques utilisateur amélioré avec support des défis logiques

### Résultats Actuels

- **58 tests passent** avec succès
- **1 test ignoré** (nécessitant une base de données PostgreSQL)
- **64% de couverture de code** globale
- Temps d'exécution moyen: ~25 secondes pour la suite complète

## Recommandations pour les Tests Futurs

1. **Amélioration de la Couverture**
   - Augmenter la couverture des modules `exercises.py` (21%) et `users.py` (47%)
   - Ajouter des tests pour les chemins d'erreur et cas limites

2. **Tests de Performance**
   - Ajouter des tests de benchmark pour les endpoints critiques
   - Vérifier les performances avec de grands volumes de données

3. **Tests de l'Interface Utilisateur**
   - Ajouter des tests Selenium pour l'interface web
   - Vérifier les interactions utilisateur complètes

4. **Tests de Déploiement**
   - Ajouter des tests vérifiant la compatibilité avec l'environnement de production
   - Automatiser les tests post-déploiement

5. **Rotation des Rapports**
   - Implémenter un système de nettoyage des anciens rapports
   - Conserver uniquement les N rapports les plus récents 