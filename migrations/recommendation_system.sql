-- Script de migration pour le système de recommandations personnalisées Mathakine
-- Date: 2025-06-15

-- 1. Ajout des nouvelles colonnes à la table exercises
-- Note: ai_generated existe déjà, on n'ajoute que les nouvelles colonnes
ALTER TABLE exercises 
ADD COLUMN IF NOT EXISTS age_group VARCHAR(10),
ADD COLUMN IF NOT EXISTS context_theme VARCHAR(255),
ADD COLUMN IF NOT EXISTS complexity INTEGER;

-- 2. Ajout des nouvelles colonnes à la table progress
ALTER TABLE progress
ADD COLUMN IF NOT EXISTS concept_mastery JSON,
ADD COLUMN IF NOT EXISTS learning_curve JSON,
ADD COLUMN IF NOT EXISTS last_active_date TIMESTAMP WITH TIME ZONE;

-- 3. Création de la table recommendations
CREATE TABLE IF NOT EXISTS recommendations (
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

-- 4. Création des index pour améliorer les performances (seulement s'ils n'existent pas)
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_exercise_id ON recommendations(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercises_age_group ON exercises(age_group);
CREATE INDEX IF NOT EXISTS idx_exercises_context_theme ON exercises(context_theme);
CREATE INDEX IF NOT EXISTS idx_progress_last_active_date ON progress(last_active_date); 