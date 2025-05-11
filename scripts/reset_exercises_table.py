#!/usr/bin/env python
"""
Script pour réinitialiser la table exercises avec la structure corrigée
"""

import sys
import logging
from sqlalchemy import text
from datetime import datetime

from app.db.init_db import engine
from app.core.logging_config import get_logger

# Configuration du logger
logger = get_logger(__name__)



def reset_exercises_table():
    """
    Supprime et recrée la table exercises avec la bonne structure.
    Les données existantes seront perdues.
    """
    try:
        logger.info("Début de la réinitialisation de la table exercises")

        with engine.connect() as conn:
            # Utiliser une transaction pour que tout réussisse ou échoue ensemble
            with conn.begin():
                # Supprimer la table exercises si elle existe
                logger.info("Suppression de la table exercises existante")
                conn.execute(text("DROP TABLE IF EXISTS exercises CASCADE"))

                # Créer la table exercises avec la bonne structure
                logger.info("Création de la nouvelle table exercises")
                conn.execute(text("""
                CREATE TABLE exercises (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR NOT NULL,
                    creator_id INTEGER REFERENCES users(id),
                    exercise_type VARCHAR NOT NULL,
                    difficulty VARCHAR NOT NULL,
                    tags VARCHAR,
                    question TEXT NOT NULL,
                    correct_answer VARCHAR NOT NULL,
                    choices JSONB,
                    explanation TEXT,
                    hint TEXT,
                    image_url VARCHAR,
                    audio_url VARCHAR,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_archived BOOLEAN DEFAULT FALSE,
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """))

                # Créer des exemples d'exercices pour les tests
                logger.info("Création d'exercices d'exemple")

                # Exemple 1: Addition
                conn.execute(text("""
                INSERT INTO exercises (
                    title, creator_id, exercise_type, difficulty, question,
                    correct_answer, choices, explanation, hint, is_active
                ) VALUES (
                    'Addition simple', 1, 'addition', 'initie', 'Combien font 2+2?',
                    '4', '["2", "3", "4", "5"]', '2 + 2 = 4', 'Additionne les deux nombres', true
                )
                """))

                # Exemple 2: Multiplication
                conn.execute(text("""
                INSERT INTO exercises (
                    title, creator_id, exercise_type, difficulty, question,
                    correct_answer, choices, explanation, hint, is_active
                ) VALUES (
                    'Multiplication simple', 1, 'multiplication', 'padawan', 'Combien font 3×5?',
                    '15', '["10", "15", "18", "20"]', '3 × 5 = 15', 'Multiplie les deux nombres'\
                        , true
                )
                """))

                # Exemple 3: Soustraction
                conn.execute(text("""
                INSERT INTO exercises (
                    title, creator_id, exercise_type, difficulty, question,
                    correct_answer, choices, explanation, hint, is_active
                ) VALUES (
                    'Soustraction simple', 1, 'soustraction', 'padawan', 'Combien font 10-3?',
                    '7', '["5", "6", "7", "8"]', '10 - 3 = 7', 'Soustrais le second nombre du premier'\
                        , true
                )
                """))

                # Exemple 4: Division
                conn.execute(text("""
                INSERT INTO exercises (
                    title, creator_id, exercise_type, difficulty, question,
                    correct_answer, choices, explanation, hint, is_active
                ) VALUES (
                    'Division simple', 1, 'division', 'chevalier', 'Combien font 15÷3?',
                    '5', '["3", "4", "5", "6"]', '15 ÷ 3 = 5', 'Divise le premier nombre par le second'\
                        , true
                )
                """))

        logger.success("La table exercises a été réinitialisée avec succès avec 4 exercices d'exemple")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation de la table exercises: {str(e)}")
        return False

if __name__ == "__main__":
    print("Script de réinitialisation de la table exercises")
    print("ATTENTION: Cette opération va supprimer toutes les données existantes!")

    # Exécution directe sans demande de confirmation
    print("Exécution de la réinitialisation...")

    if reset_exercises_table():
        print("Opération terminée avec succès!")
        sys.exit(0)
    else:
        print("L'opération a échoué. Consultez les logs pour plus de détails.")
        sys.exit(1)
