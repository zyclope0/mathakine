-- ============================================================================
-- SCHÉMA COMPLET DE LA BASE DE DONNÉES MATHAKINE
-- Exporté le: 2026-01-30 15:34:10
-- Source: dpg-d0gi5m3e5dus73adi0gg-a.frankfurt-postgres.render.com
-- ============================================================================

-- ============================================================================
-- TYPES ENUM
-- ============================================================================

CREATE TYPE agegroup AS ENUM (
    'GROUP_10_12',
    'GROUP_13_15',
    'ALL_AGES'
);

CREATE TYPE difficultylevel AS ENUM (
    'INITIE',
    'PADAWAN',
    'CHEVALIER',
    'MAITRE'
);

CREATE TYPE exercisetype AS ENUM (
    'ADDITION',
    'SOUSTRACTION',
    'MULTIPLICATION',
    'DIVISION',
    'FRACTIONS',
    'GEOMETRIE',
    'DIVERS'
);

CREATE TYPE logicchallengetype AS ENUM (
    'SEQUENCE',
    'PATTERN',
    'PUZZLE',
    'DEDUCTION',
    'SPATIAL',
    'PROBABILITY',
    'GRAPH',
    'CODING',
    'CHESS',
    'CUSTOM',
    'VISUAL',
    'RIDDLE'
);

CREATE TYPE userrole AS ENUM (
    'PADAWAN',
    'MAITRE',
    'GARDIEN',
    'ARCHIVISTE'
);

-- ============================================================================
-- TABLES
-- ============================================================================

-- Table: achievements
CREATE TABLE achievements (
    id INTEGER NOT NULL DEFAULT nextval('achievements_id_seq'::regclass),
    code VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    category VARCHAR(50),
    difficulty VARCHAR(50),
    points_reward INTEGER DEFAULT '0',
    is_secret BOOLEAN DEFAULT 'false',
    requirements JSON,
    star_wars_title VARCHAR(255),
    is_active BOOLEAN DEFAULT 'true',
    created_at TIMESTAMPTZ DEFAULT 'CURRENT_TIMESTAMP',
    name_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    description_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    star_wars_title_translations JSONB DEFAULT ''{"fr": null}'::jsonb'
);

COMMENT ON COLUMN achievements.name_translations IS 'Traductions du nom du badge';
COMMENT ON COLUMN achievements.description_translations IS 'Traductions de la description du badge';
COMMENT ON COLUMN achievements.star_wars_title_translations IS 'Traductions du titre Star Wars du badge';

-- Table: alembic_version
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL
);

-- Table: attempts
CREATE TABLE attempts (
    id INTEGER NOT NULL DEFAULT nextval('attempts_id_seq1'::regclass),
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    user_answer VARCHAR NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent DOUBLE PRECISION,
    attempt_number INTEGER,
    hints_used INTEGER,
    device_info VARCHAR,
    created_at TIMESTAMPTZ
);

-- Table: exercises
CREATE TABLE exercises (
    id INTEGER NOT NULL DEFAULT nextval('exercises_id_seq'::regclass),
    title VARCHAR NOT NULL,
    creator_id INTEGER,
    exercise_type VARCHAR NOT NULL,
    difficulty VARCHAR NOT NULL,
    tags VARCHAR,
    question TEXT NOT NULL,
    correct_answer VARCHAR NOT NULL,
    choices JSON,
    explanation TEXT,
    hint TEXT,
    image_url VARCHAR,
    audio_url VARCHAR,
    is_active BOOLEAN,
    is_archived BOOLEAN,
    view_count INTEGER,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    ai_generated BOOLEAN DEFAULT 'false',
    age_group VARCHAR(10),
    context_theme VARCHAR(255),
    complexity INTEGER,
    answer_type VARCHAR,
    text_metadata JSON,
    title_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    question_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    explanation_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    hint_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    choices_translations JSONB DEFAULT ''{"fr": null}'::jsonb'
);

COMMENT ON COLUMN exercises.ai_generated IS 'Indique si l'exercice a Ã©tÃ© gÃ©nÃ©rÃ© par IA';
COMMENT ON COLUMN exercises.title_translations IS 'Traductions du titre: {"fr": "Titre", "en": "Title"}';
COMMENT ON COLUMN exercises.question_translations IS 'Traductions de la question: {"fr": "Question", "en": "Question"}';
COMMENT ON COLUMN exercises.explanation_translations IS 'Traductions de l'explication: {"fr": "Explication", "en": "Explanation"}';
COMMENT ON COLUMN exercises.hint_translations IS 'Traductions de l'indice: {"fr": "Indice", "en": "Hint"}';
COMMENT ON COLUMN exercises.choices_translations IS 'Traductions des choix: {"fr": ["Choix 1", "Choix 2"], "en": ["Choice 1", "Choice 2"]}';

-- Table: logic_challenge_attempts
CREATE TABLE logic_challenge_attempts (
    id INTEGER NOT NULL DEFAULT nextval('logic_challenge_attempts_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    user_answer VARCHAR,
    is_correct BOOLEAN NOT NULL,
    time_spent DOUBLE PRECISION,
    hint_level1_used BOOLEAN,
    hint_level2_used BOOLEAN,
    hint_level3_used BOOLEAN,
    attempt_number INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ,
    user_solution VARCHAR(255),
    hints_used INTEGER
);

-- Table: logic_challenges
CREATE TABLE logic_challenges (
    id INTEGER NOT NULL DEFAULT nextval('logic_challenges_id_seq'::regclass),
    title VARCHAR NOT NULL,
    creator_id INTEGER,
    challenge_type logicchallengetype NOT NULL,
    age_group agegroup NOT NULL,
    description TEXT NOT NULL,
    visual_data JSON,
    correct_answer VARCHAR NOT NULL,
    solution_explanation TEXT NOT NULL,
    hint_level1 TEXT,
    hint_level2 TEXT,
    hint_level3 TEXT,
    difficulty_rating DOUBLE PRECISION,
    estimated_time_minutes INTEGER,
    success_rate DOUBLE PRECISION,
    image_url VARCHAR,
    source_reference VARCHAR,
    tags VARCHAR,
    is_template BOOLEAN,
    generation_parameters JSON,
    is_active BOOLEAN,
    is_archived BOOLEAN,
    view_count INTEGER,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    difficulty VARCHAR(50),
    content TEXT,
    question TEXT,
    solution TEXT,
    choices JSON,
    hints JSON,
    title_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    description_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    question_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    solution_explanation_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    hints_translations JSONB DEFAULT ''{"fr": null}'::jsonb',
    success_count INTEGER DEFAULT '0',
    attempt_count INTEGER DEFAULT '0'
);

COMMENT ON COLUMN logic_challenges.title_translations IS 'Traductions du titre du défi';
COMMENT ON COLUMN logic_challenges.description_translations IS 'Traductions de la description du défi';
COMMENT ON COLUMN logic_challenges.question_translations IS 'Traductions de la question du défi';
COMMENT ON COLUMN logic_challenges.solution_explanation_translations IS 'Traductions de l'explication de la solution';
COMMENT ON COLUMN logic_challenges.hints_translations IS 'Traductions des indices: {"fr": ["Indice 1", "Indice 2"], "en": ["Hint 1", "Hint 2"]}';

-- Table: progress
CREATE TABLE progress (
    id INTEGER NOT NULL DEFAULT nextval('progress_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    exercise_type VARCHAR NOT NULL,
    difficulty VARCHAR NOT NULL,
    total_attempts INTEGER,
    correct_attempts INTEGER,
    average_time DOUBLE PRECISION,
    completion_rate DOUBLE PRECISION,
    streak INTEGER,
    highest_streak INTEGER,
    mastery_level INTEGER,
    awards JSON,
    strengths VARCHAR,
    areas_to_improve VARCHAR,
    recommendations VARCHAR,
    last_updated TIMESTAMPTZ,
    concept_mastery JSON,
    learning_curve JSON,
    last_active_date TIMESTAMPTZ
);

-- Table: recommendations
CREATE TABLE recommendations (
    id INTEGER NOT NULL DEFAULT nextval('recommendations_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    exercise_id INTEGER,
    exercise_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT '5',
    reason TEXT,
    is_completed BOOLEAN DEFAULT 'false',
    shown_count INTEGER DEFAULT '0',
    clicked_count INTEGER DEFAULT '0',
    created_at TIMESTAMPTZ DEFAULT 'CURRENT_TIMESTAMP',
    updated_at TIMESTAMPTZ DEFAULT 'CURRENT_TIMESTAMP',
    last_clicked_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Table: results
CREATE TABLE results (
    id INTEGER NOT NULL DEFAULT nextval('results_id_seq'::regclass),
    exercise_id INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    attempt_count INTEGER DEFAULT '1',
    time_spent REAL,
    created_at TEXT DEFAULT 'CURRENT_TIMESTAMP'
);

-- Table: schema_version
CREATE TABLE schema_version (
    version INTEGER NOT NULL
);

-- Table: settings
CREATE TABLE settings (
    id INTEGER NOT NULL DEFAULT nextval('settings_id_seq'::regclass),
    key VARCHAR NOT NULL,
    value VARCHAR,
    value_json JSON,
    description VARCHAR,
    category VARCHAR,
    is_system BOOLEAN,
    is_public BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- Table: sqlite_sequence
CREATE TABLE sqlite_sequence (
    name TEXT,
    seq TEXT
);

-- Table: statistics
CREATE TABLE statistics (
    id INTEGER NOT NULL DEFAULT nextval('statistics_id_seq'::regclass),
    user_id INTEGER,
    session_id VARCHAR(255) NOT NULL,
    exercise_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    total_attempts INTEGER NOT NULL DEFAULT '0',
    correct_attempts INTEGER NOT NULL DEFAULT '0',
    avg_time REAL NOT NULL DEFAULT '0',
    last_updated TIMESTAMPTZ DEFAULT 'CURRENT_TIMESTAMP'
);

-- Table: user_achievements
CREATE TABLE user_achievements (
    id INTEGER NOT NULL DEFAULT nextval('user_achievements_id_seq'::regclass),
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    earned_at TIMESTAMPTZ DEFAULT 'CURRENT_TIMESTAMP',
    progress_data JSON,
    is_displayed BOOLEAN DEFAULT 'true'
);

-- Table: user_stats
CREATE TABLE user_stats (
    id INTEGER NOT NULL DEFAULT nextval('user_stats_id_seq'::regclass),
    exercise_type VARCHAR(50) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    total_attempts INTEGER DEFAULT '0',
    correct_attempts INTEGER DEFAULT '0',
    last_updated TIMESTAMPTZ DEFAULT 'CURRENT_TIMESTAMP'
);

-- Table: users
CREATE TABLE users (
    id INTEGER NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    role userrole,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    grade_level INTEGER,
    learning_style VARCHAR,
    preferred_difficulty VARCHAR,
    preferred_theme VARCHAR,
    accessibility_settings VARCHAR,
    total_points INTEGER DEFAULT '0',
    current_level INTEGER DEFAULT '1',
    experience_points INTEGER DEFAULT '0',
    jedi_rank VARCHAR(50) DEFAULT ''youngling'::character varying',
    avatar_url VARCHAR(255),
    is_email_verified BOOLEAN NOT NULL DEFAULT 'false',
    email_verification_token VARCHAR(255),
    email_verification_sent_at TIMESTAMPTZ
);

-- ============================================================================
-- CONTRAINTES DE CLÉ PRIMAIRE
-- ============================================================================

ALTER TABLE achievements ADD CONSTRAINT achievements_pkey PRIMARY KEY (id);
ALTER TABLE attempts ADD CONSTRAINT attempts_pkey PRIMARY KEY (id);
ALTER TABLE exercises ADD CONSTRAINT exercises_pkey PRIMARY KEY (id);
ALTER TABLE logic_challenge_attempts ADD CONSTRAINT logic_challenge_attempts_pkey PRIMARY KEY (id);
ALTER TABLE logic_challenges ADD CONSTRAINT logic_challenges_pkey PRIMARY KEY (id);
ALTER TABLE progress ADD CONSTRAINT progress_pkey PRIMARY KEY (id);
ALTER TABLE recommendations ADD CONSTRAINT recommendations_pkey PRIMARY KEY (id);
ALTER TABLE results ADD CONSTRAINT results_pkey PRIMARY KEY (id);
ALTER TABLE settings ADD CONSTRAINT settings_pkey PRIMARY KEY (id);
ALTER TABLE statistics ADD CONSTRAINT statistics_pkey PRIMARY KEY (id);
ALTER TABLE user_achievements ADD CONSTRAINT user_achievements_pkey PRIMARY KEY (id);
ALTER TABLE user_stats ADD CONSTRAINT user_stats_pkey PRIMARY KEY (id);
ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id);

-- ============================================================================
-- CONTRAINTES DE CLÉ ÉTRANGÈRE
-- ============================================================================

ALTER TABLE attempts ADD CONSTRAINT attempts_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE attempts ADD CONSTRAINT attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE exercises ADD CONSTRAINT exercises_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES users (id) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE logic_challenge_attempts ADD CONSTRAINT logic_challenge_attempts_challenge_id_fkey FOREIGN KEY (challenge_id) REFERENCES logic_challenges (id) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE logic_challenge_attempts ADD CONSTRAINT logic_challenge_attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE logic_challenges ADD CONSTRAINT logic_challenges_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES users (id) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE progress ADD CONSTRAINT progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE recommendations ADD CONSTRAINT recommendations_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON UPDATE NO ACTION ON DELETE SET NULL;
ALTER TABLE recommendations ADD CONSTRAINT recommendations_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE user_achievements ADD CONSTRAINT user_achievements_achievement_id_fkey FOREIGN KEY (achievement_id) REFERENCES achievements (id) ON UPDATE NO ACTION ON DELETE CASCADE;
ALTER TABLE user_achievements ADD CONSTRAINT user_achievements_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) ON UPDATE NO ACTION ON DELETE CASCADE;

-- ============================================================================
-- CONTRAINTES UNIQUE
-- ============================================================================

ALTER TABLE achievements ADD CONSTRAINT achievements_code_key UNIQUE (code);
ALTER TABLE user_achievements ADD CONSTRAINT user_achievements_user_id_achievement_id_key UNIQUE (user_id, achievement_id);

-- ============================================================================
-- INDEX
-- ============================================================================

CREATE UNIQUE INDEX achievements_code_key ON public.achievements USING btree (code);
CREATE INDEX idx_achievements_active ON public.achievements USING btree (is_active);
CREATE INDEX idx_achievements_category ON public.achievements USING btree (category);
CREATE INDEX idx_achievements_code ON public.achievements USING btree (code);
CREATE INDEX idx_achievements_name_translations ON public.achievements USING gin (name_translations);
CREATE INDEX ix_attempts_id ON public.attempts USING btree (id);
CREATE INDEX idx_exercises_active ON public.exercises USING btree (is_active, is_archived) WHERE (is_archived = false);
CREATE INDEX idx_exercises_age_group ON public.exercises USING btree (age_group);
CREATE INDEX idx_exercises_ai_generated ON public.exercises USING btree (ai_generated) WHERE (is_archived = false);
CREATE INDEX idx_exercises_context_theme ON public.exercises USING btree (context_theme);
CREATE INDEX idx_exercises_created_at ON public.exercises USING btree (created_at DESC) WHERE (is_archived = false);
CREATE INDEX idx_exercises_creator ON public.exercises USING btree (creator_id) WHERE (is_archived = false);
CREATE INDEX idx_exercises_question_translations ON public.exercises USING gin (question_translations);
CREATE INDEX idx_exercises_title_translations ON public.exercises USING gin (title_translations);
CREATE INDEX idx_exercises_type_difficulty ON public.exercises USING btree (exercise_type, difficulty) WHERE (is_archived = false);
CREATE INDEX idx_exercises_view_count ON public.exercises USING btree (view_count DESC) WHERE (is_archived = false);
CREATE INDEX ix_exercises_id ON public.exercises USING btree (id);
CREATE INDEX ix_logic_challenge_attempts_id ON public.logic_challenge_attempts USING btree (id);
CREATE INDEX idx_challenges_description_translations ON public.logic_challenges USING gin (description_translations);
CREATE INDEX idx_challenges_title_translations ON public.logic_challenges USING gin (title_translations);
CREATE INDEX ix_logic_challenges_difficulty ON public.logic_challenges USING btree (difficulty);
CREATE INDEX ix_logic_challenges_id ON public.logic_challenges USING btree (id);
CREATE INDEX idx_progress_last_active_date ON public.progress USING btree (last_active_date);
CREATE INDEX ix_progress_id ON public.progress USING btree (id);
CREATE INDEX idx_recommendations_exercise_id ON public.recommendations USING btree (exercise_id);
CREATE INDEX idx_recommendations_user_id ON public.recommendations USING btree (user_id);
CREATE INDEX ix_settings_id ON public.settings USING btree (id);
CREATE UNIQUE INDEX ix_settings_key ON public.settings USING btree (key);
CREATE INDEX idx_user_achievements_earned ON public.user_achievements USING btree (earned_at);
CREATE INDEX idx_user_achievements_user ON public.user_achievements USING btree (user_id);
CREATE UNIQUE INDEX user_achievements_user_id_achievement_id_key ON public.user_achievements USING btree (user_id, achievement_id);
CREATE INDEX idx_users_jedi_rank ON public.users USING btree (jedi_rank);
CREATE INDEX idx_users_total_points ON public.users USING btree (total_points);
CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);
CREATE INDEX ix_users_email_verification_token ON public.users USING btree (email_verification_token);
CREATE INDEX ix_users_id ON public.users USING btree (id);
CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);

-- ============================================================================
-- SÉQUENCES
-- ============================================================================

CREATE SEQUENCE achievements_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE attempts_id_seq AS bigint START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 NO CYCLE;
CREATE SEQUENCE attempts_id_seq1 AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE exercises_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE logic_challenge_attempts_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE logic_challenges_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE progress_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE recommendations_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE results_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE settings_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE statistics_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE user_achievements_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE user_stats_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;
CREATE SEQUENCE users_id_seq AS integer START WITH 1 INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 NO CYCLE;

-- ============================================================================
-- RÉSUMÉ
-- ============================================================================

-- Tables: 16
-- Types ENUM: 5
-- Clés primaires: 13
-- Clés étrangères: 11
-- Contraintes UNIQUE: 2
-- Index: 37
-- Séquences: 14
