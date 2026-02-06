#!/usr/bin/env python3
"""
Script pour vérifier le challenge 2362 et analyser sa réponse.
"""
import sys
import json
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
from loguru import logger

def check_challenge_2362():
    """Vérifie le challenge 2362 et analyse le pattern."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT id, title, correct_answer, visual_data, solution_explanation
            FROM logic_challenges 
            WHERE id = 2362
        """)
        row = cursor.fetchone()
        
        if not row:
            print("[ERREUR] Challenge 2362 non trouve")
            return
        
        challenge = dict(row)
        print(f"[OK] Challenge trouve:")
        print(f"   ID: {challenge['id']}")
        print(f"   Titre: {challenge['title']}")
        print(f"   Réponse correcte: {challenge['correct_answer']}")
        print(f"   Explication: {challenge['solution_explanation']}")
        
        if challenge['visual_data']:
            if isinstance(challenge['visual_data'], str):
                visual_data = json.loads(challenge['visual_data'])
            else:
                visual_data = challenge['visual_data']
            
            print(f"\n[VISUAL DATA]")
            print(json.dumps(visual_data, indent=2, ensure_ascii=False))
            
            # Analyser le pattern
            if 'grid' in visual_data:
                grid = visual_data['grid']
                print(f"\n[ANALYSE DU PATTERN]")
                print(f"   Grille: {grid}")
                
                # Analyser les lignes
                print(f"\n   Analyse par lignes:")
                for i, line in enumerate(grid):
                    print(f"      Ligne {i+1}: {line}")
                
                # Analyser les colonnes
                print(f"\n   Analyse par colonnes:")
                for j in range(len(grid[0]) if grid else 0):
                    col = [grid[i][j] for i in range(len(grid))]
                    print(f"      Colonne {j+1}: {col}")
                
                # Vérifier la réponse
                if len(grid) == 3 and len(grid[0]) == 3:
                    # Dernière cellule devrait être ?
                    last_cell = grid[2][2]
                    print(f"\n   Dernière cellule (3,3): {last_cell}")
                    
                    # Pattern attendu selon l'explication
                    # Ligne 1: X, O, X
                    # Ligne 2: O, X, O
                    # Ligne 3: X, O, ?
                    
                    # Si on regarde la colonne 3: X, O, ?
                    # Pattern alterné: X -> O -> ?
                    # Donc ? devrait être X (pour continuer X-O-X)
                    
                    # Mais l'explication dit "après le X, il faut mettre un O"
                    # Cela suggère qu'on regarde la séquence horizontale: X-O-X-O-X-O...
                    # Dans ce cas, après X (position 3,1), on devrait avoir O (position 3,2) ✓
                    # Et après O (position 3,2), on devrait avoir X (position 3,3)
                    
                    # Attendez... Regardons mieux:
                    # Ligne 3: X (3,1), O (3,2), ? (3,3)
                    # Si le pattern est X-O-X, alors après O on devrait avoir X
                    # Mais l'explication dit "après le X, il faut mettre un O"
                    # Cela semble contradictoire...
                    
                    print(f"\n[ANALYSE DE LA REPONSE]")
                    print(f"   Reponse en BDD: '{challenge['correct_answer']}'")
                    print(f"   Explication: {challenge['solution_explanation']}")
                    
                    # Vérifier la logique selon différents patterns possibles
                    print(f"\n[VERIFICATION DES PATTERNS POSSIBLES]")
                    
                    # Pattern 1: Colonne 3 verticale X-O-X
                    col3 = [grid[i][2] for i in range(3)]
                    print(f"   Colonne 3 (verticale): {col3}")
                    if col3 == ['X', 'O', '?']:
                        expected_col = 'X'  # Pour compléter X-O-X
                        print(f"   -> Pattern X-O-X suggere: '{expected_col}'")
                    
                    # Pattern 2: Ligne 3 horizontale X-O-?
                    row3 = grid[2]
                    print(f"   Ligne 3 (horizontale): {row3}")
                    if row3[0] == 'X' and row3[1] == 'O':
                        expected_row = 'X'  # Pour compléter X-O-X
                        print(f"   -> Pattern X-O-X suggere: '{expected_row}'")
                    
                    # Pattern 3: Diagonale principale
                    diag = [grid[i][i] for i in range(3)]
                    print(f"   Diagonale principale: {diag}")
                    
                    # Pattern 4: Diagonale secondaire
                    diag2 = [grid[i][2-i] for i in range(3)]
                    print(f"   Diagonale secondaire: {diag2}")
                    
                    # Vérifier la réponse
                    correct_answer = challenge['correct_answer'].upper()
                    print(f"\n[CONCLUSION]")
                    print(f"   Reponse en BDD: '{correct_answer}'")
                    print(f"   Pattern colonne 3 (X-O-X) suggere: 'X'")
                    print(f"   Pattern ligne 3 (X-O-X) suggere: 'X'")
                    
                    if correct_answer == 'X':
                        print(f"   [OK] La reponse 'X' est coherente avec les patterns observes")
                    elif correct_answer == 'O':
                        print(f"   [ATTENTION] La reponse 'O' ne correspond pas aux patterns X-O-X observes")
                        print(f"   [SUGGESTION] La reponse devrait probablement etre 'X' pour completer le pattern X-O-X")
                    else:
                        print(f"   [INFO] Reponse inattendue: '{correct_answer}'")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_challenge_2362()

