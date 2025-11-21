# Gestion unifiée des suppressions en cascade

Ce document décrit l'implémentation des mécanismes de suppression en cascade dans le projet Mathakine, permettant de maintenir l'intégrité des données tout en simplifiant les opérations de nettoyage et maintenance.

## Principe et avantages

Les suppressions en cascade permettent, lorsqu'une entité parente est supprimée, de supprimer automatiquement toutes les entités enfants qui en dépendent. Cette approche offre plusieurs avantages :

1. **Intégrité des données** : Évite les références orphelines dans la base de données
2. **Simplification du code** : Réduit la complexité des opérations de suppression
3. **Performance** : Exécute les suppressions dans une seule transaction
4. **Maintenance** : Facilite le nettoyage des données obsolètes
5. **Cohérence** : Garantit une approche uniforme dans toute l'application

## Implémentation technique

### 1. Relations SQLAlchemy avec option cascade

Nous utilisons l'API SQLAlchemy pour définir les relations entre les modèles avec l'option `cascade="all, delete-orphan"` :

```python
# Exemple dans le modèle User
class User(Base):
    # ... autres attributs ...
    
    # Relation vers les exercices créés
    created_exercises = relationship(
        "Exercise",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    
    # Relation vers les tentatives
    attempts = relationship(
        "Attempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )
```

### 2. Gestionnaire de transactions unifié

Nous avons implémenté un gestionnaire de transactions centralisé qui assure la cohérence des opérations de base de données :

```python
with TransactionManager.transaction(db) as session:
    # Effectuer des opérations
    session.delete(user)
    # La transaction est automatiquement validée ou annulée
```

Ce gestionnaire s'occupe de :
- Commiter les transactions réussies
- Faire un rollback en cas d'erreur
- Journaliser les opérations
- Gérer les cas spécifiques comme l'archivage

### 3. Service d'adaptation pour les opérations de base de données

Un adaptateur de base de données (`DatabaseAdapter`) fournit une interface unifiée pour toutes les opérations :

```python
# Suppression physique
DatabaseAdapter.delete(db, object)

# Archivage logique
DatabaseAdapter.archive(db, object)
```

### 4. Services métier spécialisés

Des services métier dédiés utilisent le gestionnaire de transactions et l'adaptateur :

```python
# Exemple de suppression d'un utilisateur
UserService.delete_user(db, user_id)

# Exemple d'archivage d'un exercice
ExerciseService.archive_exercise(db, exercise_id)
```

## Choix entre suppression physique et archivage logique

Deux approches sont possibles pour "supprimer" des données :

### Suppression physique

- **Avantage** : Libère de l'espace de stockage
- **Avantage** : Respecte le droit à l'oubli (RGPD)
- **Inconvénient** : Irréversible

### Archivage logique

- **Avantage** : Permet de récupérer les données si nécessaire
- **Avantage** : Maintient l'historique
- **Inconvénient** : Consomme plus d'espace

La décision entre ces deux approches dépend du contexte :
- Les exercices sont généralement archivés (`is_archived = true`)
- Les utilisateurs peuvent être physiquement supprimés (droits RGPD)
- Les données sensibles doivent pouvoir être physiquement supprimées

## Tests de validation

Des tests unitaires vérifient automatiquement que :
1. Les relations cascade sont correctement configurées
2. Les suppressions en cascade fonctionnent comme prévu
3. Les deux modes de suppression (physique et logique) fonctionnent correctement

## Bonnes pratiques

1. **Toujours utiliser les services** plutôt que de manipuler directement les modèles
2. **Préférer l'archivage** pour les données qui pourraient être utiles plus tard
3. **Documenter clairement** le comportement attendu pour chaque entité
4. **Tester soigneusement** les suppressions en cascade pour éviter les surprises

## Relations en cascade par modèle

### Modèle User

Les entités supprimées automatiquement lors de la suppression d'un utilisateur :
- Tous les exercices créés par l'utilisateur
- Toutes les tentatives de résolution d'exercices
- Toutes les tentatives de défis logiques
- Statistiques et progression

### Modèle Exercise

Les entités supprimées automatiquement lors de la suppression d'un exercice :
- Toutes les tentatives de résolution
- Statistiques associées

### Modèle LogicChallenge

Les entités supprimées automatiquement lors de la suppression d'un défi logique :
- Toutes les tentatives de résolution
- Statistiques associées

## Endpoints de suppression

### 1. Suppression d'utilisateur

```
DELETE /api/users/{user_id}
```
- **Autorisations requises** : Rôle Archiviste
- **Comportement** : Supprime l'utilisateur et toutes ses données associées
- **Implémentation** : `app/api/endpoints/users.py`

### 2. Suppression d'exercice

```
DELETE /api/exercises/{exercise_id}
```
- **Autorisations requises** : Rôle Gardien ou Archiviste
- **Comportement** : Supprime l'exercice et toutes les tentatives associées
- **Implémentation** : `app/api/endpoints/exercises.py`

### 3. Suppression de défi logique

```
DELETE /api/challenges/{challenge_id}
```
- **Autorisations requises** : Rôle Gardien ou Archiviste
- **Comportement** : Supprime le défi logique et toutes les tentatives associées
- **Implémentation** : `app/api/endpoints/challenges.py`

## Résumé

L'implémentation des suppressions en cascade dans Mathakine permet de maintenir l'intégrité des données tout en simplifiant le code. Cette approche uniforme garantit que les opérations de suppression sont cohérentes dans toute l'application et prévient les références orphelines dans la base de données. 

## Tests implémentés

Des tests complets ont été implémentés pour valider le mécanisme de suppression en cascade à tous les niveaux :

- Tests unitaires : `tests/unit/test_cascade_relationships.py`
- Tests d'intégration : `tests/integration/test_cascade_deletion.py`
- Tests API : `tests/api/test_deletion_endpoints.py`
- Tests fonctionnels : `tests/functional/test_starlette_cascade_deletion.py`

Pour plus de détails sur l'exécution de ces tests, consultez [la documentation des tests](../tests/README.md). 