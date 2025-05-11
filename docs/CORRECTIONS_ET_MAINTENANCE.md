# Corrections et maintenance - Mathakine

Ce document unifié regroupe les corrections majeures apportées au projet Mathakine, ainsi que des guides pour résoudre les problèmes courants. Il sert de référence pour comprendre les défis techniques et leurs solutions.

## 1. Corrections majeures

### Problème d'affichage des exercices

> **Note**: Ce problème est documenté en détail dans [CENTRALISATION_ET_REFACTORING.md](CENTRALISATION_ET_REFACTORING.md#problème-majeur-affichage-des-exercices).

#### Résumé du problème
Suite au refactoring de centralisation, les exercices n'apparaissaient plus dans l'interface utilisateur bien qu'ils soient correctement générés et stockés dans la base de données.

#### Cause
Les requêtes SQL centralisées dans `app/db/queries.py` incluaient toutes un filtre `WHERE is_archived = false`, mais le champ `is_archived` n'était pas correctement initialisé lors de la création des exercices.

#### Solution implémentée
Modification de la fonction `exercises_page` dans `enhanced_server.py` pour utiliser des requêtes SQL personnalisées sans le filtre sur `is_archived`.

### Problème d'insertion dans la table results

#### Résumé du problème
Les réponses aux exercices étaient correctement validées visuellement dans l'interface utilisateur, mais aucune donnée n'était insérée dans la base de données (table `results`). Cela empêchait la mise à jour des statistiques et du tableau de bord.

#### Cause
Dans la fonction `submit_answer` de `enhanced_server.py`, il y avait un problème de gestion des transactions et des erreurs:
1. Le code continuait son exécution après une erreur d'insertion sans interrompre la transaction
2. Le `conn.commit()` était effectué après plusieurs opérations, ce qui pouvait entraîner la perte de certaines insertions en cas d'erreur
3. Les erreurs n'étaient pas correctement journalisées ni signalées à l'utilisateur

#### Solution implémentée
1. Division du processus en deux transactions distinctes (insertion du résultat et mise à jour des statistiques)
2. Ajout d'un commit immédiat après l'insertion réussie dans la table `results`
3. Gestion appropriée des erreurs avec rollback en cas d'échec
4. Ajout de journalisation détaillée pour faciliter le débogage
5. Retour d'une réponse d'erreur plus informative à l'utilisateur en cas de problème

#### Code de la correction
```python
async def submit_answer(request):
    """Traite la soumission d'une réponse à un exercice"""
    try:
        # [Code existant pour récupérer les données et l'exercice...]
        
        # Enregistrer le résultat dans la table results
        try:
            print("Tentative d'insertion dans la table results...")
            cursor.execute(ResultQueries.INSERT, (
                exercise_id,     # exercise_id
                is_correct,      # is_correct
                1,               # attempt_count (par défaut 1 pour la première tentative)
                time_spent       # time_spent
            ))
            print("Insertion réussie dans la table results")
            
            # Commit immédiatement après l'insertion réussie
            conn.commit()
            print("Transaction validée (commit) pour l'insertion de résultat")
        except Exception as e:
            print(f"ERREUR lors de l'insertion dans results: {e}")
            conn.rollback()
            print("Transaction annulée (rollback) suite à l'erreur")
            # Renvoyer une réponse avec l'erreur mais continuer pour l'affichage côté client
            return JSONResponse({
                "is_correct": is_correct,
                "correct_answer": exercise['correct_answer'],
                "explanation": exercise.get('explanation', ""),
                "error": f"Erreur lors de l'enregistrement du résultat: {str(e)}"
            }, status_code=500)

        # Transaction distincte pour mettre à jour les statistiques
        try:
            # [Code existant pour mettre à jour user_stats...]
            conn.commit()
            print("Transaction validée (commit) pour les statistiques")
        except Exception as stats_error:
            print(f"ERREUR lors de la mise à jour des statistiques: {stats_error}")
            conn.rollback()
            # On continue malgré l'erreur car les résultats sont déjà enregistrés
        
        # [Reste du code...]
```

### Problème du tableau de bord

#### Résumé du problème
Le tableau de bord (`templates/dashboard.html`) ne fonctionnait pas correctement car il tentait d'accéder à un endpoint API qui n'existait pas : `/api/users/stats`.

#### Cause
1. Le script dans `dashboard.html` essayait de charger les données de statistiques via `fetch('/api/users/stats')`
2. L'endpoint `/api/users/stats` n'était pas défini dans le serveur
3. Sans cet endpoint, les statistiques comme le nombre d'exercices résolus, le taux de réussite et l'activité récente ne s'affichaient pas

#### Solution implémentée
Ajout de deux éléments au fichier `enhanced_server.py` :

1. **Fonction `get_user_stats`**:
   - Interrogation de la base de données pour obtenir les statistiques globales
   - Calcul du taux de réussite global
   - Récupération des statistiques par type d'exercice
   - Récupération de l'activité récente (les 10 derniers exercices effectués)
   - Retour des données au format JSON compatible avec le tableau de bord

2. **Route `/api/users/stats`**: 
   - Ajout de cette route à la configuration de l'application Starlette

#### Format des données retournées
```json
{
  "total_exercises": 15,
  "correct_answers": 12,
  "success_rate": 80,
  "experience_points": 150,
  "performance_by_type": {
    "addition": { "completed": 5, "correct": 4, "success_rate": 80 },
    "soustraction": { "completed": 4, "correct": 3, "success_rate": 75 },
    "multiplication": { "completed": 3, "correct": 3, "success_rate": 100 },
    "division": { "completed": 3, "correct": 2, "success_rate": 67 }
  },
  "recent_activity": [...],
  "level": { "current": 1, "title": "Débutant Stellaire", "current_xp": 25, "next_level_xp": 100 },
  "progress_over_time": { ... }
}
```

## 2. Guide de résolution des problèmes courants

### Problèmes de base de données

#### Erreur "Unknown PG numeric type: 25"

**Symptôme:** Erreur 500 lors de la suppression d'un exercice avec le message "Unknown PG numeric type: 25".

**Cause:** Incompatibilité entre le driver PostgreSQL et les types de données TEXT/VARCHAR (type 25) lors de l'utilisation de SQLAlchemy ORM pour des opérations complexes.

**Solution:**
1. Utiliser des requêtes SQL directes au lieu de l'ORM pour les opérations critiques
2. Implémenter avec des requêtes paramétrées pour éviter les injections SQL:

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

#### Erreur "A transaction is already begun on this Session"

**Symptôme:** Erreur 500 lors de la suppression d'un exercice avec le message "A transaction is already begun on this Session".

**Cause:** Tentative de démarrer une transaction explicite alors qu'une transaction implicite est déjà en cours.

**Solution:**
1. Ne pas appeler `db.begin()` si vous utilisez un contexte de requête où SQLAlchemy démarre déjà une transaction implicite
2. Comprendre le cycle de vie des transactions dans SQLAlchemy:
   - Les opérations de lecture démarrent implicitement une transaction
   - Les transactions explicites ne sont nécessaires que dans des cas spécifiques

#### Erreur de violation de contrainte de clé étrangère

**Symptôme:** Erreur 500 lors de la suppression d'un exercice avec un message concernant une violation de contrainte de clé étrangère.

**Cause:** Tentative de supprimer un exercice qui a des tentatives associées sans supprimer d'abord ces tentatives.

**Solution:**
1. Définir la relation avec l'option `cascade="all, delete-orphan"`:
```python
attempts = relationship("Attempt", back_populates="exercise", cascade="all, delete-orphan")
```

2. Ou supprimer explicitement les entités liées avant l'entité principale:
```python
# Supprimer d'abord les tentatives
db.query(AttemptModel).filter(AttemptModel.exercise_id == exercise_id).delete()
# Puis supprimer l'exercice
db.delete(exercise)
db.commit()
```

### Problèmes d'API

#### Redirection en boucle lors de la génération d'exercices

**Symptôme:** Redirection en boucle infinie lors de l'accès à `/api/exercises/generate`.

**Cause:** Redirection incorrecte qui renvoie vers le même endpoint.

**Solution:**
1. Vérifier que les redirections pointent vers les bons endpoints
2. S'assurer que les endpoints de génération redirigent vers des pages différentes
3. Utiliser des codes de statut appropriés (303 See Other pour les redirections POST → GET)

### Problèmes liés à l'interface utilisateur

#### Boutons de suppression ne fonctionnant pas

**Symptôme:** Cliquer sur le bouton de suppression d'un exercice n'a aucun effet ou provoque des erreurs.

**Cause:** Problèmes dans le gestionnaire d'événements JavaScript ou mauvaise configuration de l'endpoint API.

**Solution:**
1. Vérifier les écouteurs d'événements dans le JavaScript
2. S'assurer que l'URL de l'API est correcte
3. Ajouter des logs dans la console pour déboguer:
```javascript
console.log(`Tentative de suppression de l'exercice ${exerciseId}`);
```

#### Erreurs non affichées à l'utilisateur

**Symptôme:** Les opérations échouent silencieusement sans feedback pour l'utilisateur.

**Cause:** Manque de gestion des erreurs côté client.

**Solution:**
1. Implémenter des gestionnaires d'erreurs pour les appels d'API:
```javascript
.catch(error => {
    console.error('Erreur détaillée:', error);
    alert(`Erreur: ${error.message}`);
});
```

2. Ajouter des alertes ou notifications pour les opérations réussies/échouées

### Problèmes de performance

#### Requêtes lentes sur la liste des exercices

**Symptôme:** Temps de chargement lent pour la page d'exercices.

**Cause:** Requêtes inefficaces ou manque d'indexation.

**Solution:**
1. Ajouter des index aux colonnes fréquemment consultées
2. Implémenter la pagination pour limiter le nombre d'exercices chargés
3. Optimiser les requêtes en sélectionnant seulement les colonnes nécessaires

### Problèmes de déploiement

#### Échec de déploiement sur Render

**Symptôme:** Échec du déploiement avec des erreurs liées à la base de données.

**Cause:** Différences entre l'environnement de développement et de production.

**Solution:**
1. Vérifier les variables d'environnement sur Render
2. S'assurer que la chaîne de connexion PostgreSQL est correcte
3. Exécuter les migrations de base de données avant le déploiement

## 3. Ressources supplémentaires

- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Tutoriel sur les transactions SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)

---

*Ce document consolidé remplace les anciens documents FIXES.md, TROUBLESHOOTING.md et DASHBOARD_FIX_REPORT.md.*  
*Dernière mise à jour : 11 Mai 2025* 