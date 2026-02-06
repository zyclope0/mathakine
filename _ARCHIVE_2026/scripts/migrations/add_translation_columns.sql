-- Migration pour ajouter les colonnes de traduction aux tables
-- Date: 2025-01-XX
-- Description: Ajoute des colonnes JSONB pour stocker les traductions des données

-- ============================================
-- TABLE: exercises
-- ============================================

-- Ajouter colonnes de traduction
ALTER TABLE exercises 
  ADD COLUMN IF NOT EXISTS title_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS question_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS explanation_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS hint_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS choices_translations JSONB DEFAULT '{"fr": null}'::jsonb;

-- Migrer les données existantes vers les colonnes de traduction
UPDATE exercises SET
  title_translations = jsonb_build_object('fr', title)
WHERE title_translations IS NULL OR title_translations = '{"fr": null}'::jsonb;

UPDATE exercises SET
  question_translations = jsonb_build_object('fr', question)
WHERE question_translations IS NULL OR question_translations = '{"fr": null}'::jsonb;

UPDATE exercises SET
  explanation_translations = jsonb_build_object('fr', COALESCE(explanation, ''))
WHERE (explanation IS NOT NULL AND explanation != '') 
  AND (explanation_translations IS NULL OR explanation_translations = '{"fr": null}'::jsonb);

UPDATE exercises SET
  hint_translations = jsonb_build_object('fr', COALESCE(hint, ''))
WHERE (hint IS NOT NULL AND hint != '') 
  AND (hint_translations IS NULL OR hint_translations = '{"fr": null}'::jsonb);

UPDATE exercises SET
  choices_translations = jsonb_build_object('fr', choices)
WHERE choices IS NOT NULL 
  AND (choices_translations IS NULL OR choices_translations = '{"fr": null}'::jsonb);

-- Créer des index GIN pour les recherches dans les traductions
CREATE INDEX IF NOT EXISTS idx_exercises_title_translations 
  ON exercises USING GIN (title_translations);

CREATE INDEX IF NOT EXISTS idx_exercises_question_translations 
  ON exercises USING GIN (question_translations);

-- ============================================
-- TABLE: logic_challenges
-- ============================================

-- Ajouter colonnes de traduction
ALTER TABLE logic_challenges
  ADD COLUMN IF NOT EXISTS title_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS description_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS question_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS solution_explanation_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS hints_translations JSONB DEFAULT '{"fr": null}'::jsonb;

-- Migrer les données existantes
UPDATE logic_challenges SET
  title_translations = jsonb_build_object('fr', title)
WHERE title_translations IS NULL OR title_translations = '{"fr": null}'::jsonb;

UPDATE logic_challenges SET
  description_translations = jsonb_build_object('fr', description)
WHERE description_translations IS NULL OR description_translations = '{"fr": null}'::jsonb;

UPDATE logic_challenges SET
  question_translations = jsonb_build_object('fr', COALESCE(question, ''))
WHERE (question IS NOT NULL AND question != '') 
  AND (question_translations IS NULL OR question_translations = '{"fr": null}'::jsonb);

UPDATE logic_challenges SET
  solution_explanation_translations = jsonb_build_object('fr', COALESCE(solution_explanation, ''))
WHERE (solution_explanation IS NOT NULL AND solution_explanation != '') 
  AND (solution_explanation_translations IS NULL OR solution_explanation_translations = '{"fr": null}'::jsonb);

UPDATE logic_challenges SET
  hints_translations = jsonb_build_object('fr', hints)
WHERE hints IS NOT NULL 
  AND (hints_translations IS NULL OR hints_translations = '{"fr": null}'::jsonb);

-- Créer des index GIN
CREATE INDEX IF NOT EXISTS idx_challenges_title_translations 
  ON logic_challenges USING GIN (title_translations);

CREATE INDEX IF NOT EXISTS idx_challenges_description_translations 
  ON logic_challenges USING GIN (description_translations);

-- ============================================
-- TABLE: achievements
-- ============================================

-- Ajouter colonnes de traduction
ALTER TABLE achievements
  ADD COLUMN IF NOT EXISTS name_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS description_translations JSONB DEFAULT '{"fr": null}'::jsonb,
  ADD COLUMN IF NOT EXISTS star_wars_title_translations JSONB DEFAULT '{"fr": null}'::jsonb;

-- Migrer les données existantes
UPDATE achievements SET
  name_translations = jsonb_build_object('fr', name)
WHERE name_translations IS NULL OR name_translations = '{"fr": null}'::jsonb;

UPDATE achievements SET
  description_translations = jsonb_build_object('fr', COALESCE(description, ''))
WHERE (description IS NOT NULL AND description != '') 
  AND (description_translations IS NULL OR description_translations = '{"fr": null}'::jsonb);

UPDATE achievements SET
  star_wars_title_translations = jsonb_build_object('fr', COALESCE(star_wars_title, ''))
WHERE (star_wars_title IS NOT NULL AND star_wars_title != '') 
  AND (star_wars_title_translations IS NULL OR star_wars_title_translations = '{"fr": null}'::jsonb);

-- Créer des index GIN
CREATE INDEX IF NOT EXISTS idx_achievements_name_translations 
  ON achievements USING GIN (name_translations);

-- ============================================
-- COMMENTAIRES
-- ============================================

COMMENT ON COLUMN exercises.title_translations IS 'Traductions du titre: {"fr": "Titre", "en": "Title"}';
COMMENT ON COLUMN exercises.question_translations IS 'Traductions de la question: {"fr": "Question", "en": "Question"}';
COMMENT ON COLUMN exercises.explanation_translations IS 'Traductions de l''explication: {"fr": "Explication", "en": "Explanation"}';
COMMENT ON COLUMN exercises.hint_translations IS 'Traductions de l''indice: {"fr": "Indice", "en": "Hint"}';
COMMENT ON COLUMN exercises.choices_translations IS 'Traductions des choix: {"fr": ["Choix 1", "Choix 2"], "en": ["Choice 1", "Choice 2"]}';

COMMENT ON COLUMN logic_challenges.title_translations IS 'Traductions du titre du défi';
COMMENT ON COLUMN logic_challenges.description_translations IS 'Traductions de la description du défi';
COMMENT ON COLUMN logic_challenges.question_translations IS 'Traductions de la question du défi';
COMMENT ON COLUMN logic_challenges.solution_explanation_translations IS 'Traductions de l''explication de la solution';
COMMENT ON COLUMN logic_challenges.hints_translations IS 'Traductions des indices: {"fr": ["Indice 1", "Indice 2"], "en": ["Hint 1", "Hint 2"]}';

COMMENT ON COLUMN achievements.name_translations IS 'Traductions du nom du badge';
COMMENT ON COLUMN achievements.description_translations IS 'Traductions de la description du badge';
COMMENT ON COLUMN achievements.star_wars_title_translations IS 'Traductions du titre Star Wars du badge';

