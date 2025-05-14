# Système unifié de transaction et gestion des données

Ce document décrit le système complet de gestion des transactions, suppressions en cascade et adaptation pour le serveur Starlette dans le projet Mathakine.

## 1. Vue d'ensemble du système de transaction

Le projet Mathakine implémente un système robuste et unifié pour gérer les transactions de base de données, assurant l'intégrité des données et simplifiant le développement.

### Architecture générale

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  TransactionManager  ───►  DatabaseAdapter  ◄────►  Services Métier   │
│                   │     │                   │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
          ▲                         ▲                        ▲
          │                         │                        │
          └─────────────────────────┼────────────────────────┘
                                    │
                          ┌───────────────────┐
                          │                   │
                          │ EnhancedServerAdapter │
                          │                   │
                          └───────────────────┘
                                    ▲
                                    │
                          ┌───────────────────┐
                          │                   │
                          │  enhanced_server.py  │
                          │                   │
                          └───────────────────┘
```

### Composants principaux

1. **TransactionManager** - Gestionnaire de contexte pour les transactions
2. **DatabaseAdapter** - Interface unifiée pour les opérations CRUD
3. **Services métier** - Logique métier spécifique à chaque domaine
4. **EnhancedServerAdapter** - Adaptateur pour le serveur Starlette

## 2. Le gestionnaire de transactions (TransactionManager)

Le `TransactionManager` est un utilitaire qui fournit un contexte pour exécuter des opérations dans une transaction, gérant automatiquement le commit et le rollback.

### Fonctionnalités principales

- **Gestionnaire de contexte** pour encapsuler les transactions
- **Commit et rollback automatiques** selon le résultat de l'opération
- **Gestion des erreurs** avec journalisation détaillée
- **Méthodes spécialisées** pour les opérations courantes (suppression, archivage)

### Exemples d'utilisation

```python
# Utilisation comme gestionnaire de contexte
with TransactionManager.transaction(db) as session:
    user = User(username="nouveau_utilisateur", email="user@example.com")
    session.add(user)
    # Commit automatique à la fin du bloc si aucune exception n'est levée

# Suppression sécurisée avec cascade
TransactionManager.safe_delete(db, user)

# Archivage d'un objet
TransactionManager.safe_archive(db, exercise)
```

## 3. Système de suppression en cascade

Le système de suppression en cascade assure que lorsqu'une entité est supprimée, toutes ses dépendances sont automatiquement traitées. Cette approche garantit l'intégrité des données et simplifie la maintenance.

### Implémentation technique

#### Relations SQLAlchemy avec cascade

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

#### Suppression physique vs archivage logique

Deux approches sont disponibles pour "supprimer" des données :

1. **Suppression physique** - Supprime définitivement les données de la base
   ```python
   DatabaseAdapter.delete(db, object)
   ```

2. **Archivage logique** - Marque les données comme archivées sans les supprimer
   ```python
   DatabaseAdapter.archive(db, object)
   ```

#### Relations en cascade par modèle

| Modèle | Entités supprimées en cascade |
|--------|------------------------------|
| User | Exercices créés, tentatives, statistiques |
| Exercise | Tentatives, statistiques |
| LogicChallenge | Tentatives, statistiques |

## 4. L'adaptateur pour le serveur Starlette (EnhancedServerAdapter)

L'adaptateur `EnhancedServerAdapter` permet d'intégrer le système de transaction unifié avec le serveur Starlette existant (`enhanced_server.py`) qui utilisait des requêtes SQL directes.

### Fonctionnement de l'adaptateur

- **Conversion** des opérations SQL directes en appels aux services métier
- **Gestion cohérente** des sessions SQLAlchemy
- **Transformation** des résultats entre formats SQLAlchemy et dictionnaires
- **Migration progressive** sans réécriture complète du code existant

### Utilisation de l'adaptateur

```python
# Obtenir une session
db = EnhancedServerAdapter.get_db_session()
try:
    # Récupérer l'exercice
    exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
    if not exercise:
        return JSONResponse({"error": "Exercice introuvable"}, status_code=404)
    
    # Utiliser l'exercice...
    
finally:
    # Fermer la session
    EnhancedServerAdapter.close_db_session(db)
```

### Fonctions disponibles

| Catégorie | Fonctions |
|-----------|-----------|
| Sessions | `get_db_session()`, `close_db_session(db)` |
| Exercices | `get_exercise_by_id()`, `list_exercises()`, `create_exercise()`, `update_exercise()`, `archive_exercise()` |
| Tentatives | `record_attempt()` |
| Utilisateurs | `get_user_stats()` |
| Générique | `execute_raw_query()` |

## 5. Bonnes pratiques

1. **Toujours utiliser les services métier** plutôt que les modèles directement
2. **Utiliser le gestionnaire de contexte** pour les transactions
3. **Préférer l'archivage logique** pour les données potentiellement utiles plus tard
4. **Documenter le comportement attendu** pour chaque entité
5. **Fermer les sessions avec try/finally** dans le code utilisant l'adaptateur

## 6. Tests et validation

Le système est couvert par une suite complète de tests :

- Tests unitaires : `tests/unit/test_transaction_manager.py`, `tests/unit/test_cascade_relationships.py`
- Tests d'intégration : `tests/integration/test_cascade_deletion.py` 
- Tests API : `tests/api/test_deletion_endpoints.py`
- Tests fonctionnels : `tests/functional/test_starlette_cascade_deletion.py`

## 7. Avantages du système unifié

1. **Cohérence** - Une seule approche pour toutes les opérations de données
2. **Robustesse** - Gestion automatique des erreurs et rollback
3. **Simplicité** - Les développeurs n'ont pas à gérer manuellement les transactions
4. **Traçabilité** - Journalisation détaillée des opérations
5. **Migration progressive** - Transition en douceur entre l'ancien et le nouveau système

## 8. Endpoints affectés

Les endpoints suivants ont été modifiés pour utiliser l'adaptateur :

| Endpoint | Fonction | Description |
|----------|----------|-------------|
| `/delete_exercise` | `delete_exercise` | Archive les exercices |
| `/submit_answer` | `submit_answer` | Enregistre les tentatives |
| `/get_exercises_list` | `get_exercises_list` | Liste les exercices |
| `/get_user_stats` | `get_user_stats` | Récupère les statistiques utilisateur |

---

*Ce document consolide les informations de TRANSACTION_MANAGEMENT.md, CASCADE_DELETION.md et ADAPTATEUR.md*