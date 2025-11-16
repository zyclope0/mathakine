"""
Requêtes SQL avec support des traductions JSONB pour PostgreSQL.

Ces requêtes utilisent des fonctions PostgreSQL pour extraire les traductions
depuis les colonnes JSONB selon la locale demandée.
"""
import json
from typing import Optional, Dict, Any, List


def build_translation_select(field_name: str, translations_field: str, locale_param: str = "%s") -> str:
    """
    Construit une expression SQL pour extraire une traduction depuis JSONB.
    
    Args:
        field_name: Nom du champ original (pour fallback)
        translations_field: Nom du champ JSONB de traductions
        locale_param: Paramètre SQL pour la locale (%s)
    
    Returns:
        Expression SQL pour SELECT
    
    Example:
        build_translation_select('title', 'title_translations', '%s')
        -> "COALESCE(title_translations->%s, title_translations->'fr', to_jsonb(title))::text"
    """
    return f"""
    COALESCE(
        {translations_field}->{locale_param},
        {translations_field}->'fr',
        to_jsonb({field_name})
    )::text
    """


def build_translation_array_select(field_name: str, translations_field: str, locale_param: str = "%s") -> str:
    """
    Construit une expression SQL pour extraire un array traduit depuis JSONB.
    
    Args:
        field_name: Nom du champ original (pour fallback)
        translations_field: Nom du champ JSONB de traductions
        locale_param: Paramètre SQL pour la locale
    
    Returns:
        Expression SQL pour SELECT
    """
    return f"""
    COALESCE(
        {translations_field}->{locale_param},
        {translations_field}->'fr',
        {field_name}
    )
    """


class ExerciseQueriesWithTranslations:
    """Requêtes SQL pour les exercices avec support des traductions"""
    
    @staticmethod
    def get_by_id(locale: str = "fr") -> tuple[str, tuple]:
        """
        Récupère un exercice par ID avec traductions.
        
        Args:
            locale: Locale demandée (fr, en, etc.)
        
        Returns:
            Tuple (query, params) pour cursor.execute()
        """
        query = """
        SELECT 
            id,
            COALESCE(
                title_translations->>%s,
                title_translations->>'fr',
                COALESCE(title, '')
            ) as title,
            COALESCE(
                question_translations->>%s,
                question_translations->>'fr',
                COALESCE(question, '')
            ) as question,
            COALESCE(
                explanation_translations->>%s,
                explanation_translations->>'fr',
                COALESCE(explanation, '')
            ) as explanation,
            COALESCE(
                hint_translations->>%s,
                hint_translations->>'fr',
                COALESCE(hint, '')
            ) as hint,
            CASE 
                WHEN choices_translations->%s IS NOT NULL THEN (choices_translations->%s)::jsonb
                WHEN choices_translations->'fr' IS NOT NULL THEN (choices_translations->'fr')::jsonb
                ELSE COALESCE(choices::jsonb, '[]'::jsonb)
            END::jsonb as choices,
            exercise_type,
            difficulty,
            correct_answer,
            tags,
            image_url,
            audio_url,
            is_active,
            is_archived,
            ai_generated,
            view_count,
            creator_id,
            created_at,
            updated_at
        FROM exercises 
        WHERE id = %s AND is_archived = false
        """
        
        # Paramètres: title(1), question(1), explanation(1), hint(1), choices(2 pour CASE: WHEN et THEN), exercise_id(1) = 7 total
        # Dans le CASE: WHEN choices_translations->%s (5ème) THEN choices_translations->%s (6ème)
        params = (locale, locale, locale, locale, locale, locale, None)  # Le dernier None sera remplacé par exercise_id
        return query, params
    
    @staticmethod
    def list_exercises(
        locale: str = "fr",
        exercise_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> tuple[str, tuple]:
        """
        Liste les exercices avec traductions et filtres optionnels.
        
        Args:
            locale: Locale demandée
            exercise_type: Type d'exercice à filtrer
            difficulty: Difficulté à filtrer
            search: Terme de recherche (recherche dans title et question)
            limit: Nombre maximum de résultats
            offset: Décalage pour pagination
        
        Returns:
            Tuple (query, params) pour cursor.execute()
        """
        query = """
        SELECT 
            id,
            COALESCE(
                title_translations->>%s,
                title_translations->>'fr',
                COALESCE(title, '')
            ) as title,
            COALESCE(
                question_translations->>%s,
                question_translations->>'fr',
                COALESCE(question, '')
            ) as question,
            COALESCE(
                explanation_translations->>%s,
                explanation_translations->>'fr',
                COALESCE(explanation, '')
            ) as explanation,
            COALESCE(
                hint_translations->>%s,
                hint_translations->>'fr',
                COALESCE(hint, '')
            ) as hint,
            CASE 
                WHEN choices_translations->%s IS NOT NULL THEN (choices_translations->%s)::jsonb
                WHEN choices_translations->'fr' IS NOT NULL THEN (choices_translations->'fr')::jsonb
                ELSE COALESCE(choices::jsonb, '[]'::jsonb)
            END::jsonb as choices,
            exercise_type,
            difficulty,
            correct_answer,
            tags,
            image_url,
            audio_url,
            is_active,
            ai_generated,
            view_count,
            created_at,
            updated_at
        FROM exercises 
        WHERE is_archived = false AND is_active = true
        """
        
        # Paramètres: title(1), question(1), explanation(1), hint(1), choices(2 pour CASE: WHEN et THEN) = 6 total
        # Dans le CASE: WHEN choices_translations->%s (5ème) THEN choices_translations->%s (6ème)
        params = [locale, locale, locale, locale, locale, locale]
        
        # Ajouter les filtres
        if exercise_type:
            query += " AND exercise_type = %s"
            params.append(exercise_type)
        
        if difficulty:
            query += " AND difficulty = %s"
            params.append(difficulty)
        
        # Ajouter la recherche (dans title et question traduits)
        if search:
            search_pattern = f"%{search}%"
            query += """ AND (
                COALESCE(title_translations->>%s, title_translations->>'fr', title) ILIKE %s
                OR COALESCE(question_translations->>%s, question_translations->>'fr', question) ILIKE %s
            )"""
            params.extend([locale, search_pattern, locale, search_pattern])
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        if offset:
            query += " OFFSET %s"
            params.append(offset)
        
        return query, tuple(params)
    
    @staticmethod
    def count_exercises(
        locale: str = "fr",
        exercise_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[str, tuple]:
        """
        Compte le nombre total d'exercices avec les mêmes filtres que list_exercises.
        
        Args:
            locale: Locale demandée (pour recherche)
            exercise_type: Type d'exercice à filtrer
            difficulty: Difficulté à filtrer
            search: Terme de recherche
        
        Returns:
            Tuple (query, params) pour cursor.execute()
        """
        query = """
        SELECT COUNT(*) as total
        FROM exercises 
        WHERE is_archived = false AND is_active = true
        """
        
        params = []
        
        # Ajouter les filtres
        if exercise_type:
            query += " AND exercise_type = %s"
            params.append(exercise_type)
        
        if difficulty:
            query += " AND difficulty = %s"
            params.append(difficulty)
        
        # Ajouter la recherche (dans title et question traduits)
        if search:
            search_pattern = f"%{search}%"
            query += """ AND (
                COALESCE(title_translations->>%s, title_translations->>'fr', title) ILIKE %s
                OR COALESCE(question_translations->>%s, question_translations->>'fr', question) ILIKE %s
            )"""
            params.extend([locale, search_pattern, locale, search_pattern])
        
        return query, tuple(params)


class ChallengeQueriesWithTranslations:
    """Requêtes SQL pour les défis logiques avec support des traductions"""
    
    @staticmethod
    def get_by_id(locale: str = "fr") -> tuple[str, tuple]:
        """Récupère un défi par ID avec traductions"""
        query = """
        SELECT 
            id,
            COALESCE(
                NULLIF(NULLIF(title_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(title_translations->>'fr', 'null'), ''),
                title
            ) as title,
            COALESCE(
                NULLIF(NULLIF(description_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(description_translations->>'fr', 'null'), ''),
                description
            ) as description,
            COALESCE(
                NULLIF(NULLIF(question_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(question_translations->>'fr', 'null'), ''),
                question,
                ''
            ) as question,
            COALESCE(
                NULLIF(NULLIF(solution_explanation_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(solution_explanation_translations->>'fr', 'null'), ''),
                solution_explanation,
                ''
            ) as solution_explanation,
            CASE 
                WHEN hints_translations->%s IS NOT NULL THEN (hints_translations->%s)::jsonb
                WHEN hints_translations->'fr' IS NOT NULL THEN (hints_translations->'fr')::jsonb
                ELSE COALESCE(hints::jsonb, '[]'::jsonb)
            END::jsonb as hints,
            challenge_type,
            age_group,
            difficulty,
            correct_answer,
            choices,
            visual_data,
            difficulty_rating,
            estimated_time_minutes,
            success_rate,
            image_url,
            tags,
            is_active,
            is_archived,
            view_count,
            created_at,
            updated_at
        FROM logic_challenges 
        WHERE id = %s AND is_archived = false
        """
        
        # Paramètres: title(1), description(1), question(1), solution_explanation(1), hints(2 pour CASE), challenge_id(1) = 7 total
        params = (locale, locale, locale, locale, locale, locale, None)
        return query, params
    
    @staticmethod
    def list_challenges(
        locale: str = "fr",
        challenge_type: Optional[str] = None,
        age_group: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> tuple[str, tuple]:
        """
        Liste les défis logiques avec traductions et filtres optionnels.
        
        Args:
            locale: Locale demandée
            challenge_type: Type de défi à filtrer
            age_group: Groupe d'âge à filtrer
            search: Terme de recherche (recherche dans title et description)
            limit: Nombre maximum de résultats
            offset: Décalage pour pagination
        
        Returns:
            Tuple (query, params) pour cursor.execute()
        """
        query = """
        SELECT 
            id,
            COALESCE(
                NULLIF(NULLIF(title_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(title_translations->>'fr', 'null'), ''),
                title,
                ''
            ) as title,
            COALESCE(
                NULLIF(NULLIF(description_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(description_translations->>'fr', 'null'), ''),
                description,
                ''
            ) as description,
            COALESCE(
                NULLIF(NULLIF(question_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(question_translations->>'fr', 'null'), ''),
                question,
                ''
            ) as question,
            COALESCE(
                NULLIF(NULLIF(solution_explanation_translations->>%s, 'null'), ''),
                NULLIF(NULLIF(solution_explanation_translations->>'fr', 'null'), ''),
                solution_explanation,
                ''
            ) as solution_explanation,
            CASE 
                WHEN hints_translations->%s IS NOT NULL THEN (hints_translations->%s)::jsonb
                WHEN hints_translations->'fr' IS NOT NULL THEN (hints_translations->'fr')::jsonb
                ELSE COALESCE(hints::jsonb, '[]'::jsonb)
            END::jsonb as hints,
            challenge_type,
            age_group,
            difficulty,
            correct_answer,
            choices,
            visual_data,
            difficulty_rating,
            estimated_time_minutes,
            success_rate,
            image_url,
            tags,
            is_active,
            is_archived,
            view_count,
            created_at,
            updated_at
        FROM logic_challenges 
        WHERE is_archived = false AND is_active = true
        """
        
        # Paramètres: title(1), description(1), question(1), solution_explanation(1), hints(2 pour CASE) = 6 total
        params = [locale, locale, locale, locale, locale, locale]
        
        # Ajouter les filtres
        if challenge_type:
            query += " AND challenge_type = %s"
            params.append(challenge_type)
        
        if age_group:
            query += " AND age_group = %s"
            params.append(age_group)
        
        # Ajouter la recherche (dans title et description traduits)
        if search:
            search_pattern = f"%{search}%"
            query += """ AND (
                COALESCE(title_translations->>%s, title_translations->>'fr', title) ILIKE %s
                OR COALESCE(description_translations->>%s, description_translations->>'fr', description) ILIKE %s
            )"""
            params.extend([locale, search_pattern, locale, search_pattern])
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        if offset:
            query += " OFFSET %s"
            params.append(offset)
        
        return query, tuple(params)
    
    @staticmethod
    def count_challenges(
        locale: str = "fr",
        challenge_type: Optional[str] = None,
        age_group: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[str, tuple]:
        """
        Compte le nombre total de défis avec les mêmes filtres que list_challenges.
        
        Args:
            locale: Locale demandée (pour recherche)
            challenge_type: Type de défi à filtrer
            age_group: Groupe d'âge à filtrer
            search: Terme de recherche
        
        Returns:
            Tuple (query, params) pour cursor.execute()
        """
        query = """
        SELECT COUNT(*) as total
        FROM logic_challenges 
        WHERE is_archived = false AND is_active = true
        """
        
        params = []
        
        # Ajouter les filtres
        if challenge_type:
            query += " AND challenge_type = %s"
            params.append(challenge_type)
        
        if age_group:
            query += " AND age_group = %s"
            params.append(age_group)
        
        # Ajouter la recherche (dans title et description traduits)
        if search:
            search_pattern = f"%{search}%"
            query += """ AND (
                COALESCE(title_translations->>%s, title_translations->>'fr', title) ILIKE %s
                OR COALESCE(description_translations->>%s, description_translations->>'fr', description) ILIKE %s
            )"""
            params.extend([locale, search_pattern, locale, search_pattern])
        
        return query, tuple(params)


class AchievementQueriesWithTranslations:
    """Requêtes SQL pour les badges avec support des traductions"""
    
    @staticmethod
    def get_by_id(locale: str = "fr") -> tuple[str, tuple]:
        """Récupère un badge par ID avec traductions"""
        query = """
        SELECT 
            id,
            code,
            NULLIF(
                COALESCE(
                    NULLIF(name_translations->>%s, 'null'),
                    NULLIF(name_translations->>'fr', 'null'),
                    name
                ),
                'null'
            ) as name,
            NULLIF(
                COALESCE(
                    NULLIF(description_translations->>%s, 'null'),
                    NULLIF(description_translations->>'fr', 'null'),
                    description
                ),
                'null'
            ) as description,
            NULLIF(
                COALESCE(
                    NULLIF(star_wars_title_translations->>%s, 'null'),
                    NULLIF(star_wars_title_translations->>'fr', 'null'),
                    star_wars_title
                ),
                'null'
            ) as star_wars_title,
            icon_url,
            category,
            difficulty,
            points_reward,
            is_secret,
            requirements,
            is_active,
            created_at
        FROM achievements 
        WHERE id = %s AND is_active = true
        """
        
        # Les paramètres doivent être dans l'ordre : locale (x3 pour name, description, star_wars_title), puis achievement_id
        # Mais on doit construire le tuple correctement
        params = (locale, locale, locale)  # Les 3 locales pour les traductions
        # Le %s pour l'ID sera ajouté dans badge_service_translations.py
        return query, params
    
    @staticmethod
    def list_all(locale: str = "fr") -> tuple[str, tuple]:
        """Liste tous les badges avec traductions"""
        query = """
        SELECT 
            id,
            code,
            NULLIF(
                COALESCE(
                    NULLIF(name_translations->>%s, 'null'),
                    NULLIF(name_translations->>'fr', 'null'),
                    name
                ),
                'null'
            ) as name,
            NULLIF(
                COALESCE(
                    NULLIF(description_translations->>%s, 'null'),
                    NULLIF(description_translations->>'fr', 'null'),
                    description
                ),
                'null'
            ) as description,
            NULLIF(
                COALESCE(
                    NULLIF(star_wars_title_translations->>%s, 'null'),
                    NULLIF(star_wars_title_translations->>'fr', 'null'),
                    star_wars_title
                ),
                'null'
            ) as star_wars_title,
            icon_url,
            category,
            difficulty,
            points_reward,
            is_secret,
            requirements,
            is_active,
            created_at
        FROM achievements 
        WHERE is_active = true
        ORDER BY category, points_reward DESC
        """
        
        params = (locale, locale, locale)
        return query, params

