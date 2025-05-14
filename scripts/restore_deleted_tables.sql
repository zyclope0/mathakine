-- Script pour restaurer les tables supprimées
-- Créé à partir des informations de migration Alembic

-- Table 'user_stats'
CREATE TABLE IF NOT EXISTS user_stats (
    id SERIAL PRIMARY KEY,
    exercise_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    total_attempts INTEGER DEFAULT 0,
    correct_attempts INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 'statistics'
CREATE TABLE IF NOT EXISTS statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(255) NOT NULL,
    exercise_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    total_attempts INTEGER DEFAULT 0 NOT NULL,
    correct_attempts INTEGER DEFAULT 0 NOT NULL,
    avg_time REAL DEFAULT 0 NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 'results'
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    attempt_count INTEGER DEFAULT 1,
    time_spent REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table 'schema_version' (simple version tracking)
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

-- Insère la version initiale dans schema_version si elle n'existe pas déjà
INSERT INTO schema_version (version) 
SELECT 1 
WHERE NOT EXISTS (SELECT 1 FROM schema_version);

-- Informations sur la restauration
COMMENT ON TABLE user_stats IS 'Table restaurée après suppression accidentelle le 12 mai 2025';
COMMENT ON TABLE statistics IS 'Table restaurée après suppression accidentelle le 12 mai 2025';
COMMENT ON TABLE results IS 'Table restaurée après suppression accidentelle le 12 mai 2025';
COMMENT ON TABLE schema_version IS 'Table restaurée après suppression accidentelle le 12 mai 2025'; 