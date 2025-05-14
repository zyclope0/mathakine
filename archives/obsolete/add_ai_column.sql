-- Ajouter la colonne ai_generated à la table exercises
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE;

-- Mettre à jour les exercices existants qui contiennent "TEST-ZAXXON" dans leur titre ou question
UPDATE exercises 
SET ai_generated = TRUE 
WHERE title LIKE '%TEST-ZAXXON%' OR question LIKE '%TEST-ZAXXON%'; 