# Guide de résolution des problèmes - Mathakine

Ce document fournit des solutions aux problèmes courants rencontrés lors du développement et de l'utilisation de l'application Mathakine.

## Problèmes de base de données

### Erreur "Unknown PG numeric type: 25"

**Symptôme :** Erreur 500 lors de la suppression d'un exercice avec le message "Unknown PG numeric type: 25".

**Cause :** Incompatibilité entre le driver PostgreSQL et les types de données TEXT/VARCHAR (type 25) lors de l'utilisation de SQLAlchemy ORM pour des opérations complexes.

**Solution :**
1. Utiliser des requêtes SQL directes au lieu de l'ORM pour les opérations critiques
2. Implémenter avec des requêtes paramétrées pour éviter les injections SQL :

```python
from sqlalchemy import text

# Supprimer les tentatives associées
db.execute(text("DELETE FROM attempts WHERE exercise_id = :exercise_id"), 
           {"exercise_id": exercise_id})

# Supprimer l'exercice
db.execute(text("DELETE FROM exercises WHERE id = :exercise_id"), 
           {"exercise_id": exercise_id})

# Valider la transaction
db.commit()
```

### Erreur "A transaction is already begun on this Session"

**Symptôme :** Erreur 500 lors de la suppression d'un exercice avec le message "A transaction is already begun on this Session".

**Cause :** Tentative de démarrer une transaction explicite alors qu'une transaction implicite est déjà en cours.

**Solution :**
1. Ne pas appeler `db.begin()` si vous utilisez un contexte de requête où SQLAlchemy démarre déjà une transaction implicite
2. Comprendre le cycle de vie des transactions dans SQLAlchemy :
   - Les opérations de lecture démarrent implicitement une transaction
   - Les transactions explicites ne sont nécessaires que dans des cas spécifiques

### Erreur de violation de contrainte de clé étrangère

**Symptôme :** Erreur 500 lors de la suppression d'un exercice avec un message concernant une violation de contrainte de clé étrangère.

**Cause :** Tentative de supprimer un exercice qui a des tentatives associées sans supprimer d'abord ces tentatives.

**Solution :**
1. Définir la relation avec l'option `cascade="all, delete-orphan"` :
```python
attempts = relationship("Attempt", back_populates="exercise", cascade="all, delete-orphan")
```

2. Ou supprimer explicitement les entités liées avant l'entité principale :
```python
# Supprimer d'abord les tentatives
db.query(AttemptModel).filter(AttemptModel.exercise_id == exercise_id).delete()
# Puis supprimer l'exercice
db.delete(exercise)
db.commit()
```

## Problèmes d'API

### Redirection en boucle lors de la génération d'exercices

**Symptôme :** Redirection en boucle infinie lors de l'accès à `/api/exercises/generate`.

**Cause :** Redirection incorrecte qui renvoie vers le même endpoint.

**Solution :**
1. Vérifier que les redirections pointent vers les bons endpoints
2. S'assurer que les endpoints de génération redirigent vers des pages différentes
3. Utiliser des codes de statut appropriés (303 See Other pour les redirections POST → GET)

## Problèmes liés à l'interface utilisateur

### Boutons de suppression ne fonctionnant pas

**Symptôme :** Cliquer sur le bouton de suppression d'un exercice n'a aucun effet ou provoque des erreurs.

**Cause :** Problèmes dans le gestionnaire d'événements JavaScript ou mauvaise configuration de l'endpoint API.

**Solution :**
1. Vérifier les écouteurs d'événements dans le JavaScript
2. S'assurer que l'URL de l'API est correcte
3. Ajouter des logs dans la console pour déboguer :
```javascript
console.log(`Tentative de suppression de l'exercice ${exerciseId}`);
```

### Erreurs non affichées à l'utilisateur

**Symptôme :** Les opérations échouent silencieusement sans feedback pour l'utilisateur.

**Cause :** Manque de gestion des erreurs côté client.

**Solution :**
1. Implémenter des gestionnaires d'erreurs pour les appels d'API :
```javascript
.catch(error => {
    console.error('Erreur détaillée:', error);
    alert(`Erreur: ${error.message}`);
});
```

2. Ajouter des alertes ou notifications pour les opérations réussies/échouées

## Problèmes de performance

### Requêtes lentes sur la liste des exercices

**Symptôme :** Temps de chargement lent pour la page d'exercices.

**Cause :** Requêtes inefficaces ou manque d'indexation.

**Solution :**
1. Ajouter des index aux colonnes fréquemment consultées
2. Implémenter la pagination pour limiter le nombre d'exercices chargés
3. Optimiser les requêtes en sélectionnant seulement les colonnes nécessaires

## Problèmes de déploiement

### Échec de déploiement sur Render

**Symptôme :** Échec du déploiement avec des erreurs liées à la base de données.

**Cause :** Différences entre l'environnement de développement et de production.

**Solution :**
1. Vérifier les variables d'environnement sur Render
2. S'assurer que la chaîne de connexion PostgreSQL est correcte
3. Exécuter les migrations de base de données avant le déploiement

## Ressources supplémentaires

- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Tutoriel sur les transactions SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)

---

*Si vous rencontrez un problème qui n'est pas listé ici, veuillez ouvrir une issue sur GitHub.*

*Dernière mise à jour : 08/05/2025* 