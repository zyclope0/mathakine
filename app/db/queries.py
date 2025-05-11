"""
Requêtes SQL centralisées pour l'application Mathakine
Ce fichier contient toutes les requêtes SQL utilisées dans l'application.
"""

# Requêtes pour la table 'exercises'
class ExerciseQueries:
    # Création et modification
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS exercises (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        creator_id INTEGER REFERENCES users(id),
        exercise_type VARCHAR(50) NOT NULL,
        difficulty VARCHAR(50) NOT NULL,
        tags VARCHAR(255),
        question TEXT NOT NULL,
        correct_answer VARCHAR(255) NOT NULL,
        choices JSONB,
        explanation TEXT,
        hint TEXT,
        image_url VARCHAR(255),
        audio_url VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        is_archived BOOLEAN DEFAULT FALSE,
        ai_generated BOOLEAN DEFAULT FALSE,
        view_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Sélection
    GET_ALL = """
    SELECT * FROM exercises 
    WHERE is_archived = false
    ORDER BY id DESC
    """
    
    GET_BY_ID = """
    SELECT * FROM exercises 
    WHERE id = %s AND is_archived = false
    """
    
    GET_BY_TYPE = """
    SELECT * FROM exercises 
    WHERE exercise_type = %s AND is_archived = false
    ORDER BY id DESC
    """
    
    GET_BY_DIFFICULTY = """
    SELECT * FROM exercises 
    WHERE difficulty = %s AND is_archived = false
    ORDER BY id DESC
    """
    
    GET_BY_TYPE_AND_DIFFICULTY = """
    SELECT * FROM exercises 
    WHERE exercise_type = %s AND difficulty = %s AND is_archived = false
    ORDER BY id DESC
    """
    
    GET_RANDOM = """
    SELECT * FROM exercises 
    WHERE is_archived = false
    ORDER BY RANDOM() 
    LIMIT 1
    """
    
    GET_RANDOM_BY_TYPE = """
    SELECT * FROM exercises 
    WHERE exercise_type = %s AND is_archived = false
    ORDER BY RANDOM() 
    LIMIT 1
    """
    
    GET_RANDOM_BY_DIFFICULTY = """
    SELECT * FROM exercises 
    WHERE difficulty = %s AND is_archived = false
    ORDER BY RANDOM() 
    LIMIT 1
    """
    
    GET_RANDOM_BY_TYPE_AND_DIFFICULTY = """
    SELECT * FROM exercises 
    WHERE exercise_type = %s AND difficulty = %s AND is_archived = false
    ORDER BY RANDOM() 
    LIMIT 1
    """
    
    # Insertion
    INSERT = """
    INSERT INTO exercises 
    (title, creator_id, exercise_type, difficulty, tags, question, correct_answer, 
    choices, explanation, hint, image_url, audio_url, ai_generated) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    # Mise à jour
    UPDATE = """
    UPDATE exercises 
    SET title = %s, exercise_type = %s, difficulty = %s, tags = %s, question = %s, 
    correct_answer = %s, choices = %s, explanation = %s, hint = %s, image_url = %s, 
    audio_url = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    """
    
    ARCHIVE = """
    UPDATE exercises 
    SET is_archived = true, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    """
    
    ACTIVATE = """
    UPDATE exercises 
    SET is_active = true, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    """
    
    DEACTIVATE = """
    UPDATE exercises 
    SET is_active = false, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    """
    
    # Suppression
    DELETE = """
    DELETE FROM exercises 
    WHERE id = %s
    """

# Requêtes pour la table 'results'
class ResultQueries:
    # Création et modification
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS results (
        id SERIAL PRIMARY KEY,
        exercise_id INTEGER NOT NULL,
        is_correct BOOLEAN NOT NULL,
        attempt_count INTEGER,
        time_spent REAL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Sélection
    GET_BY_USER = """
    SELECT * FROM results 
    WHERE user_id = %s
    ORDER BY created_at DESC
    """
    
    GET_BY_EXERCISE = """
    SELECT * FROM results 
    WHERE exercise_id = %s
    ORDER BY created_at DESC
    """
    
    GET_BY_USER_AND_EXERCISE = """
    SELECT * FROM results 
    WHERE user_id = %s AND exercise_id = %s
    ORDER BY created_at DESC
    """
    
    # Insertion
    INSERT = """
    INSERT INTO results 
    (exercise_id, is_correct, attempt_count, time_spent) 
    VALUES (%s, %s, %s, %s)
    RETURNING id
    """

# Requêtes pour les statistiques
class UserStatsQueries:
    # Statistiques globales par utilisateur
    GET_USER_STATS = """
    SELECT 
        COUNT(*) as total_exercises,
        SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_answers,
        AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100 as success_rate,
        AVG(time_taken) as avg_time_taken
    FROM results 
    WHERE user_id = %s
    """
    
    # Statistiques par type d'exercice
    GET_USER_STATS_BY_TYPE = """
    SELECT 
        e.exercise_type,
        COUNT(*) as total_exercises,
        SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) as correct_answers,
        AVG(CASE WHEN r.is_correct THEN 1 ELSE 0 END) * 100 as success_rate,
        AVG(r.time_taken) as avg_time_taken
    FROM results r
    JOIN exercises e ON r.exercise_id = e.id
    WHERE r.user_id = %s
    GROUP BY e.exercise_type
    """
    
    # Statistiques par niveau de difficulté
    GET_USER_STATS_BY_DIFFICULTY = """
    SELECT 
        e.difficulty,
        COUNT(*) as total_exercises,
        SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) as correct_answers,
        AVG(CASE WHEN r.is_correct THEN 1 ELSE 0 END) * 100 as success_rate,
        AVG(r.time_taken) as avg_time_taken
    FROM results r
    JOIN exercises e ON r.exercise_id = e.id
    WHERE r.user_id = %s
    GROUP BY e.difficulty
    """
    
    # Progression dans le temps (par jour)
    GET_USER_PROGRESS_BY_DAY = """
    SELECT 
        DATE(r.created_at) as exercise_date,
        COUNT(*) as total_exercises,
        SUM(CASE WHEN r.is_correct THEN 1 ELSE 0 END) as correct_answers,
        AVG(CASE WHEN r.is_correct THEN 1 ELSE 0 END) * 100 as success_rate
    FROM results r
    WHERE r.user_id = %s
    GROUP BY DATE(r.created_at)
    ORDER BY DATE(r.created_at)
    """

    # Exercices par jour sur les 30 derniers jours (global, tous utilisateurs)
    GET_EXERCISES_BY_DAY = """
    SELECT 
        DATE(created_at) as exercise_date,
        COUNT(*) as count
    FROM results
    GROUP BY DATE(created_at)
    ORDER BY exercise_date DESC
    LIMIT 30
    """

# Requêtes pour la table 'users'
class UserQueries:
    # Création et modification
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        full_name VARCHAR(100),
        hashed_password VARCHAR(100) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Sélection
    GET_ALL = """
    SELECT id, username, email, full_name, is_active, is_admin, created_at
    FROM users
    ORDER BY id
    """
    
    GET_BY_ID = """
    SELECT id, username, email, full_name, is_active, is_admin, created_at
    FROM users
    WHERE id = %s
    """
    
    GET_BY_USERNAME = """
    SELECT id, username, email, full_name, is_active, is_admin, created_at, hashed_password
    FROM users
    WHERE username = %s
    """
    
    GET_BY_EMAIL = """
    SELECT id, username, email, full_name, is_active, is_admin, created_at, hashed_password
    FROM users
    WHERE email = %s
    """
    
    # Insertion
    INSERT = """
    INSERT INTO users 
    (username, email, full_name, hashed_password, is_active, is_admin) 
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    # Mise à jour
    UPDATE = """
    UPDATE users 
    SET username = %s, email = %s, full_name = %s, is_active = %s
    WHERE id = %s
    """
    
    UPDATE_PASSWORD = """
    UPDATE users 
    SET hashed_password = %s
    WHERE id = %s
    """
    
    # Suppression
    DELETE = """
    DELETE FROM users 
    WHERE id = %s
    """

# Requêtes pour la table 'settings'
class SettingQueries:
    # Création et modification
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        key VARCHAR(100) UNIQUE NOT NULL,
        value TEXT NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # Sélection
    GET_ALL = """
    SELECT * FROM settings
    WHERE is_active = true
    ORDER BY key
    """
    
    GET_BY_KEY = """
    SELECT * FROM settings
    WHERE key = %s AND is_active = true
    """
    
    # Insertion
    INSERT = """
    INSERT INTO settings 
    (key, value, description, is_active) 
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (key) 
    DO UPDATE SET value = EXCLUDED.value, 
                 description = EXCLUDED.description,
                 updated_at = CURRENT_TIMESTAMP
    RETURNING id
    """
    
    # Mise à jour
    UPDATE = """
    UPDATE settings 
    SET value = %s, description = %s, updated_at = CURRENT_TIMESTAMP
    WHERE key = %s
    """
    
    # Suppression
    DELETE = """
    DELETE FROM settings 
    WHERE key = %s
    """ 