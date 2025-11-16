#!/usr/bin/env python3
"""
Script pour corriger le visual_data du challenge 2363 (symétrie spatiale).
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

def fix_challenge_2363():
    """Corrige le visual_data du challenge 2363 pour la symétrie spatiale."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Récupérer le challenge
        cursor.execute("""
            SELECT id, title, correct_answer, visual_data, question, description
            FROM logic_challenges 
            WHERE id = 2363
        """)
        challenge = cursor.fetchone()
        
        if not challenge:
            print("[ERREUR] Challenge 2363 non trouve")
            return
        
        print(f"[OK] Challenge trouve: {challenge['title']}")
        print(f"   Question: {challenge['question']}")
        print(f"   Reponse correcte: {challenge['correct_answer']}")
        
        # Visual_data actuel (malformé)
        old_visual_data = challenge['visual_data']
        if isinstance(old_visual_data, str):
            old_visual_data = json.loads(old_visual_data)
        
        print(f"\n[Visual Data Actuel (malforme)]")
        print(json.dumps(old_visual_data, indent=2, ensure_ascii=False))
        
        # Nouveau visual_data structuré pour la symétrie
        # D'après la question : "Quelle forme doit être placée à la position '?' pour que la symétrie soit respectée par rapport à la ligne de symétrie ?"
        # Et la réponse correcte est "cercle"
        # On suppose une symétrie horizontale avec triangle, rectangle, ?, cercle
        
        new_visual_data = {
            "type": "symmetry",
            "symmetry_line": "vertical",  # Ligne de symétrie verticale au milieu
            "layout": [
                {"position": 0, "shape": "triangle", "side": "left"},
                {"position": 1, "shape": "rectangle", "side": "left"},
                {"position": 2, "shape": "?", "side": "right", "question": True},
                {"position": 3, "shape": "cercle", "side": "right"}
            ],
            "shapes": ["triangle", "rectangle", "?", "cercle"],
            "arrangement": "horizontal",
            "description": "Ligne de symétrie verticale au centre. Les formes à gauche doivent être symétriques à celles de droite."
        }
        
        print(f"\n[Nouveau Visual Data]")
        print(json.dumps(new_visual_data, indent=2, ensure_ascii=False))
        
        # Mettre à jour dans la base de données
        cursor.execute("""
            UPDATE logic_challenges
            SET visual_data = %s,
                updated_at = NOW()
            WHERE id = 2363
        """, (json.dumps(new_visual_data),))
        
        conn.commit()
        
        print(f"\n[OK] Challenge 2363 corrige avec succes")
        print(f"   Visual_data mis a jour avec structure de symetrie")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_challenge_2363()

