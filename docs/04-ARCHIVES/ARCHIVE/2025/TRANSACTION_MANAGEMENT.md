# Gestion unifiée des transactions dans Mathakine

Ce document décrit le système de gestion de transactions implémenté dans le projet Mathakine pour assurer la cohérence des opérations sur la base de données.

## Introduction

Un système de gestion de transactions robuste est essentiel pour assurer l'intégrité des données dans une application. Pour Mathakine, nous avons mis en place une approche unifiée qui encapsule les meilleures pratiques et simplifie la gestion des transactions pour tous les développeurs.

## Composants du système

Le système de gestion de transactions se compose de trois éléments principaux :

1. **TransactionManager** : Un gestionnaire de contexte qui encapsule les opérations de transaction
2. **DatabaseAdapter** : Un adaptateur qui fournit une interface unifiée pour les opérations de base de données
3. **Services métier** : Des classes qui utilisent le gestionnaire et l'adaptateur pour les opérations spécifiques

## 1. TransactionManager

Le `TransactionManager` est un utilitaire qui fournit un contexte pour exécuter des opérations dans une transaction. Il s'occupe automatiquement du commit en cas de succès et du rollback en cas d'erreur.

### Principales fonctionnalités

- Gestionnaire de contexte `transaction` pour des blocs de code transactionnels
- Méthodes utilitaires `commit` et `rollback` pour un contrôle manuel
- Méthodes spécialisées `safe_delete` et `safe_archive` pour les opérations courantes
- Journalisation détaillée des opérations pour faciliter le débogage

### Exemples d'utilisation

```python
# Utilisation comme gestionnaire de contexte
with TransactionManager.transaction(db) as session:
    user = User(username="nouveau_utilisateur", email="user@example.com")
    session.add(user)
    # Commit automatique à la fin du bloc si aucune exception n'est levée

# Utilisation manuelle pour des cas spécifiques
try:
    db.add(entity)
    TransactionManager.commit(db)
except Exception as e:
    TransactionManager.rollback(db)
    logger.error(f"Erreur: {e}")

# Suppression sécurisée avec cascade
TransactionManager.safe_delete(db, user)

# Archivage d'un objet
TransactionManager.safe_archive(db, exercise)
```

## 2. DatabaseAdapter

Le `DatabaseAdapter` fournit une interface cohérente pour les opérations courantes sur la base de données, que ce soit via SQLAlchemy ou des requêtes SQL directes.

### Principales fonctionnalités

- Opérations CRUD standard (`get_by_id`, `list_active`, `create`, `update`, `delete`, etc.)
- Filtre automatique par `is_archived` pour les modèles qui ont cet attribut
- Gestion des erreurs robuste et journalisation
- Méthode `execute_query` pour les requêtes SQL personnalisées

### Exemples d'utilisation

```python
# Récupérer un objet par son ID
user = DatabaseAdapter.get_by_id(db, User, user_id)

# Lister les objets actifs
exercises = DatabaseAdapter.list_active(db, Exercise)

# Créer un nouvel objet
new_exercise = DatabaseAdapter.create(db, Exercise, exercise_data)

# Mettre à jour un objet
DatabaseAdapter.update(db, exercise, {"title": "Nouveau titre"})

# Archiver un objet
DatabaseAdapter.archive(db, exercise)

# Exécuter une requête personnalisée
results = DatabaseAdapter.execute_query(
    db,
    "SELECT * FROM exercises WHERE difficulty = :difficulty AND is_archived = false",
    {"difficulty": "padawan"}
)
```

## 3. Services métier

Les services métier encapsulent la logique métier spécifique à chaque entité et utilisent le `TransactionManager` et le `DatabaseAdapter` pour interagir avec la base de données.

### Services disponibles

- **ExerciseService** : Gestion des exercices et des tentatives
- **LogicChallengeService** : Gestion des défis logiques
- **UserService** : Gestion des utilisateurs et statistiques

### Exemples d'utilisation

```python
# Récupérer un exercice
exercise = ExerciseService.get_exercise(db, exercise_id)

# Lister les exercices d'un certain type et niveau
exercises = ExerciseService.list_exercises(
    db,
    exercise_type="addition",
    difficulty="padawan"
)

# Créer un utilisateur
user = UserService.create_user(db, user_data)

# Supprimer un défi logique
LogicChallengeService.delete_challenge(db, challenge_id)

# Obtenir les statistiques d'un utilisateur
stats = UserService.get_user_stats(db, user_id)
```

## Avantages de cette approche

1. **Cohérence** : Une seule façon de gérer les transactions dans toute l'application
2. **Simplicité** : Les développeurs n'ont pas à gérer manuellement les commits et rollbacks
3. **Robustesse** : Gestion automatique des erreurs avec journalisation
4. **Traçabilité** : Journalisation détaillée des opérations pour faciliter le débogage
5. **Adaptabilité** : Support pour différents types de bases de données (PostgreSQL, SQLite)

## Bonnes pratiques

1. **Toujours utiliser les services métier** plutôt que de manipuler directement les modèles
2. **Préférer le gestionnaire de contexte** pour les blocs de code transactionnels
3. **Utiliser des transactions courtes** pour limiter les risques de conflits
4. **Journaliser toutes les opérations critiques** pour faciliter le débogage
5. **Tester les cas d'erreur** pour s'assurer que le rollback fonctionne correctement

## Tests

Le système est couvert par une suite de tests unitaires qui vérifient :

1. Le fonctionnement correct du gestionnaire de contexte
2. Le commit et le rollback automatiques
3. Les suppressions en cascade
4. L'intégration avec les services métier

Pour exécuter les tests :

```bash
pytest tests/unit/test_transaction_manager.py -v
```

## Conclusion

Le système de gestion de transactions unifié de Mathakine offre une approche robuste et cohérente pour interagir avec la base de données. En centralisant la logique de transaction, nous réduisons les risques d'erreurs et simplifions le développement et la maintenance de l'application. 