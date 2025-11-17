#!/usr/bin/env python3
"""Ajoute visual_data aux challenges pour affichage visuel"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def main():
    print("=== AJOUT VISUAL_DATA AUX CHALLENGES ===\n")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    from app.models.logic_challenge import LogicChallenge, LogicChallengeType
    import os
    import json
    
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("[1/1] Mise a jour des challenges avec visual_data...\n")
        
        # Récupérer tous les challenges
        challenges = db.query(LogicChallenge).all()
        updated = 0
        
        for challenge in challenges:
            visual_data = None
            
            # Extraire les valeurs de la question pour créer les visual_data
            question = challenge.question or ""
            
            # SEQUENCES
            if challenge.challenge_type == LogicChallengeType.SEQUENCE:
                # Parser la question pour extraire la séquence
                # Format attendu: "2, 4, 6, 8, ?"
                if "?" in question:
                    # Extraire la partie de la séquence
                    parts = [p.strip() for p in question.split(":")]
                    sequence_str = parts[-1] if len(parts) > 1 else question
                    
                    # Parser les nombres/lettres
                    items = [item.strip() for item in sequence_str.replace(",", " ").split() if item.strip()]
                    
                    visual_data = {
                        "sequence": items,
                        "type": "numeric" if any(c.isdigit() for c in sequence_str) else "alphabetic"
                    }
            
            # PATTERNS
            elif challenge.challenge_type == LogicChallengeType.PATTERN:
                # Parser la question pour extraire le pattern
                # Format: "A, B, A, B, ?"
                if "?" in question:
                    parts = [p.strip() for p in question.split(":")]
                    pattern_str = parts[-1] if len(parts) > 1 else question
                    
                    items = [item.strip() for item in pattern_str.replace(",", " ").split() if item.strip()]
                    
                    # Créer une grille 1D pour le pattern
                    visual_data = {
                        "pattern": items,
                        "grid": items,
                        "size": len(items)
                    }
            
            # SPATIAL
            elif challenge.challenge_type == LogicChallengeType.SPATIAL:
                # Créer des données visuelles basiques pour spatial
                if "cube" in question.lower():
                    visual_data = {
                        "shapes": ["cube"],
                        "type": "3d",
                        "ascii": """
   +-----+
  /     /|
 +-----+ |
 |     | +
 |     |/
 +-----+
                        """.strip()
                    }
                elif "miroir" in question.lower() or "symetrie" in question.lower():
                    visual_data = {
                        "type": "symmetry",
                        "symmetry_line": "vertical",
                        "content": "b → d"
                    }
                else:
                    visual_data = {
                        "shapes": ["square", "circle", "triangle"],
                        "type": "2d"
                    }
            
            # PUZZLE
            elif challenge.challenge_type == LogicChallengeType.PUZZLE:
                # Créer des pièces de puzzle
                if challenge.choices:
                    try:
                        choices = json.loads(challenge.choices) if isinstance(challenge.choices, str) else challenge.choices
                        visual_data = {
                            "pieces": [{"id": i, "content": choice, "position": i} for i, choice in enumerate(choices)],
                            "type": "reorder"
                        }
                    except:
                        pass
            
            # VISUAL (comme SPATIAL)
            elif challenge.challenge_type == LogicChallengeType.VISUAL:
                visual_data = {
                    "shapes": ["circle", "square", "triangle"],
                    "type": "shape_recognition"
                }
            
            # GRAPH
            elif challenge.challenge_type == LogicChallengeType.GRAPH:
                visual_data = {
                    "nodes": [
                        {"id": "A", "x": 100, "y": 100},
                        {"id": "B", "x": 300, "y": 100},
                        {"id": "C", "x": 200, "y": 250}
                    ],
                    "edges": [
                        {"from": "A", "to": "B"},
                        {"from": "B", "to": "C"},
                        {"from": "C", "to": "A"}
                    ]
                }
            
            # Mettre à jour si visual_data a été créé
            if visual_data:
                challenge.visual_data = visual_data
                updated += 1
        
        db.commit()
        print(f"  OK: {updated} challenges mis a jour avec visual_data\n")
        
        # Vérification
        print("[VERIFICATION]")
        total = db.query(LogicChallenge).count()
        with_visual = db.query(LogicChallenge).filter(LogicChallenge.visual_data.isnot(None)).count()
        print(f"  Total challenges: {total}")
        print(f"  Avec visual_data: {with_visual}")
        
        print("\n[SUCCES] Mise a jour terminee!")
        return 0
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    sys.exit(main())

