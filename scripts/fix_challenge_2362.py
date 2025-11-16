#!/usr/bin/env python3
"""
Script pour corriger le challenge 2362 avec un pattern incohérent.
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
from loguru import logger
import json

def fix_challenge_2362():
    """Corrige le challenge 2362 avec le pattern incohérent."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Récupérer le challenge
        cursor.execute("""
            SELECT id, title, correct_answer, visual_data, solution_explanation,
                   title_translations, solution_explanation_translations
            FROM logic_challenges 
            WHERE id = 2362
        """)
        challenge = cursor.fetchone()
        
        if not challenge:
            print("[ERREUR] Challenge 2362 non trouve")
            return
        
        print(f"[OK] Challenge trouve: {challenge['title']}")
        print(f"   Reponse actuelle: '{challenge['correct_answer']}'")
        
        # Parser visual_data
        visual_data = challenge['visual_data']
        if isinstance(visual_data, str):
            visual_data = json.loads(visual_data)
        
        grid = visual_data.get('grid', [])
        print(f"   Grille: {grid}")
        
        # Analyser le pattern
        # Colonne 3: X, O, ? → Pattern X-O-X → ? = X
        # Ligne 3: X, O, ? → Pattern X-O-X → ? = X
        correct_answer = "X"
        
        # Nouvelle explication cohérente
        new_explanation = (
            "En observant la grille, on peut identifier le pattern X-O-X qui se répète. "
            "Dans la colonne de droite (colonne 3), on observe : X, O, ?. "
            "Dans la ligne du bas (ligne 3), on observe également : X, O, ?. "
            "Le pattern X-O-X se répète dans les deux directions, donc la réponse manquante est 'X' pour compléter le pattern."
        )
        
        print(f"\n[Correction]")
        print(f"   Nouvelle reponse: '{correct_answer}'")
        print(f"   Nouvelle explication: {new_explanation[:100]}...")
        
        # Mettre à jour dans la base de données
        cursor.execute("""
            UPDATE logic_challenges
            SET correct_answer = %s,
                solution_explanation = %s,
                updated_at = NOW()
            WHERE id = 2362
        """, (correct_answer, new_explanation))
        
        # Mettre à jour les traductions si elles existent
        if challenge.get('solution_explanation_translations'):
            translations = challenge['solution_explanation_translations']
            if isinstance(translations, str):
                translations = json.loads(translations)
            
            translations['fr'] = new_explanation
            
            cursor.execute("""
                UPDATE logic_challenges
                SET solution_explanation_translations = %s
                WHERE id = 2362
            """, (json.dumps(translations),))
        
        conn.commit()
        
        print(f"\n[OK] Challenge 2362 corrige avec succes")
        print(f"   Reponse: '{correct_answer}'")
        print(f"   Explication mise a jour")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_challenge_2362()

