# Système de Recommandations Personnalisées (Les Conseils du Conseil Jedi)

*Dernière mise à jour: 16/05/2025*

## Vue d'ensemble

Le système de recommandations personnalisées (alias "Les Conseils du Conseil Jedi" dans la métaphore Star Wars) permet à Mathakine de suggérer aux utilisateurs des exercices adaptés à leur niveau, leurs forces et leurs besoins d'amélioration.

Cette fonctionnalité offre une expérience d'apprentissage personnalisée qui aide les jeunes Padawans à progresser efficacement dans leur maîtrise des mathématiques.

## Architecture technique

### Base de données

#### Nouvelle table: `recommendations`

```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id INTEGER REFERENCES exercises(id) ON DELETE SET NULL,
    exercise_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5,
    reason TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    shown_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### Extensions à la table `exercises`

```sql
ALTER TABLE exercises 
ADD COLUMN age_group VARCHAR(10),
ADD COLUMN context_theme VARCHAR(255),
ADD COLUMN complexity INTEGER;
```

#### Extensions à la table `progress`

```sql
ALTER TABLE progress
ADD COLUMN concept_mastery JSON,
ADD COLUMN learning_curve JSON,
ADD COLUMN last_active_date TIMESTAMP WITH TIME ZONE;
```

#### Index pour les performances

```sql
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_exercise_id ON recommendations(exercise_id);
CREATE INDEX idx_exercises_age_group ON exercises(age_group);
CREATE INDEX idx_exercises_context_theme ON exercises(context_theme);
CREATE INDEX idx_progress_last_active_date ON progress(last_active_date);
```

### Migrations Alembic

Les modifications de schéma ont été appliquées via un script SQL puis documentées dans une migration Alembic (91fb5e67f95d) pour maintenir la cohérence du système de migration.

## Fonctionnement du système

### Algorithme de recommandation

Le système de recommandations utilise plusieurs facteurs pour déterminer les exercices à suggérer:

1. **Analyse des performances passées**:
   - Taux de réussite par type d'exercice et niveau
   - Temps moyen de résolution
   - Progression récente (learning_curve)

2. **Identification des lacunes**:
   - Concepts mathématiques nécessitant plus de pratique
   - Types d'exercices avec des taux de réussite inférieurs

3. **Personnalisation**:
   - Préférence de difficulté de l'utilisateur
   - Groupe d'âge approprié
   - Thèmes contextuels préférés (ex: vaisseaux spatiaux, planètes)

4. **Équilibrage**:
   - Mélange de renforcement des forces et amélioration des faiblesses
   - Progression graduelle de la difficulté
   - Variété des types d'exercices pour maintenir l'engagement

### Champs JSON complexes

#### `concept_mastery`

Ce champ JSON stocke la maîtrise fine des concepts mathématiques:

```json
{
  "addition": {
    "single_digit": 0.95,
    "double_digit": 0.78,
    "with_carrying": 0.65
  },
  "subtraction": {
    "single_digit": 0.88,
    "double_digit": 0.72,
    "with_borrowing": 0.58
  }
}
```

#### `learning_curve`

Ce champ JSON enregistre l'évolution des performances au fil du temps:

```json
{
  "addition": [
    {"date": "2025-04-01", "score": 0.65},
    {"date": "2025-04-15", "score": 0.72},
    {"date": "2025-05-01", "score": 0.78}
  ],
  "subtraction": [
    {"date": "2025-04-01", "score": 0.55},
    {"date": "2025-04-15", "score": 0.60},
    {"date": "2025-05-01", "score": 0.72}
  ]
}
```

## Interface utilisateur

### Tableau de bord

Un nouveau panneau "Conseils du Conseil Jedi" apparaît sur le tableau de bord de l'utilisateur, affichant:
- 3-5 exercices recommandés avec leur type et niveau
- Une brève explication de la raison de la recommandation
- Un indicateur visuel de priorité (cristal Kyber de différentes couleurs)

### Page d'exercices

La liste des exercices inclut maintenant un filtre "Recommandés pour vous" qui:
- Met en évidence les exercices recommandés avec un halo bleu
- Permet de trier les exercices par priorité de recommandation
- Affiche une infobulle expliquant pourquoi un exercice est recommandé

## Flux de données

1. **Collecte des données**: Chaque tentative d'exercice est enregistrée et analysée
2. **Calcul des recommandations**: Exécuté périodiquement (quotidien) ou après des sessions significatives
3. **Stockage**: Les recommandations sont stockées dans la table `recommendations`
4. **Présentation**: L'interface utilisateur récupère et affiche les recommandations actives
5. **Feedback**: Les interactions utilisateur avec les recommandations sont enregistrées pour affiner l'algorithme

## Considérations spéciales pour les enfants autistes

Le système de recommandations inclut des adaptations spécifiques:

- **Progression plus granulaire**: Augmentation plus progressive de la difficulté
- **Reconnaissance des patterns préférés**: Identification et suggestion d'exercices suivant les patterns appréciés
- **Prédictibilité**: Maintien d'une structure cohérente dans les types d'exercices recommandés
- **Thèmes d'intérêt spécial**: Prise en compte des thèmes préférés pour augmenter l'engagement

## États et développement futur

### MVP (Version actuelle)
- ✅ Schéma de base de données implémenté
- ✅ Migrations appliquées
- ✅ Structure backend en place

### Version 1.0 (Prévue pour Juillet 2025)
- ⏳ Services d'algorithme de recommandation
- ⏳ API pour récupérer les recommandations
- ⏳ Interface utilisateur de base

### Version 2.0 (Prévue pour Septembre 2025)
- ⏳ Algorithme avancé avec apprentissage automatique
- ⏳ Analyse prédictive des performances futures
- ⏳ Tableau de bord amélioré pour les enseignants

## Documentation technique associée

- [API Endpoints](../Tech/API_REFERENCE.md) - Détails des endpoints API pour les recommandations
- [Schéma de Base de Données](../Tech/DATABASE_GUIDE.md) - Vue d'ensemble complète du schéma
- [Migrations](../Tech/DATABASE_GUIDE.md#3-gestion-des-migrations-avec-alembic) - Documentation sur les migrations Alembic 