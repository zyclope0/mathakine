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

### 2. Endpoints de suppression uniformisés

Tous les endpoints de suppression suivent désormais la même structure :

```python
@router.delete("/{item_id}", status_code=204)
def delete_item(
    *,
    db: Session = Depends(get_db_session),
    item_id: int,
    current_user: User = Depends(get_current_user_with_permission)
) -> None:
    try:
        # Vérification de l'existence
        item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item non trouvé")
            
        # Suppression (cascade automatique)
        db.delete(item)
        db.commit()
        
        return None
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Erreur SQL: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de base de données")
```

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

## Bonnes pratiques

1. **Toujours définir les cascades dans les modèles** : Utilisez les relations SQLAlchemy avec l'option cascade appropriée
2. **Valider les suppressions** : Vérifiez que les entités sont bien supprimées en cascade
3. **Journaliser les suppressions** : Enregistrez les suppressions pour la traçabilité
4. **Gérer les erreurs** : Utilisez try/except et rollback en cas d'erreur
5. **Limiter les autorisations** : Restreignez les suppressions aux rôles appropriés

## Tests

Pour valider le comportement des suppressions en cascade :

```python
# Test de suppression en cascade pour les utilisateurs
def test_delete_user_cascade():
    user = create_test_user()
    exercise = create_test_exercise(creator_id=user.id)
    attempt = create_test_attempt(user_id=user.id, exercise_id=exercise.id)
    
    # Supprimer l'utilisateur
    db.delete(user)
    db.commit()
    
    # Vérifier que tout a été supprimé
    assert db.query(Exercise).filter_by(id=exercise.id).first() is None
    assert db.query(Attempt).filter_by(id=attempt.id).first() is None
```

## Résumé

L'implémentation des suppressions en cascade dans Mathakine permet de maintenir l'intégrité des données tout en simplifiant le code. Cette approche uniforme garantit que les opérations de suppression sont cohérentes dans toute l'application et prévient les références orphelines dans la base de données. 

## Tests implémentés

Des tests complets ont été implémentés pour valider le mécanisme de suppression en cascade à tous les niveaux :

- Tests unitaires : `tests/unit/test_cascade_relationships.py`
- Tests d'intégration : `tests/integration/test_cascade_deletion.py`
- Tests API : `tests/api/test_deletion_endpoints.py`
- Tests fonctionnels : `tests/functional/test_starlette_cascade_deletion.py`

Pour plus de détails sur l'exécution de ces tests, consultez [la documentation des tests](../tests/README.md). 