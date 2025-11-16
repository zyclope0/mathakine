#!/usr/bin/env python3
"""
Script pour analyser la qualité des challenges générés par IA.
Vérifie les incohérences, erreurs logiques, et problèmes récurrents.
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

def analyze_ai_challenges():
    """Analyse la qualité des challenges générés par IA."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Récupérer tous les challenges générés par IA
        cursor.execute("""
            SELECT id, title, challenge_type, correct_answer, visual_data, 
                   solution_explanation, question, tags
            FROM logic_challenges 
            WHERE tags LIKE '%ai%' OR tags LIKE '%generated%'
            ORDER BY id DESC
        """)
        challenges = cursor.fetchall()
        
        print(f"[ANALYSE QUALITE] {len(challenges)} challenges IA trouves\n")
        
        issues = {
            'pattern_incoherence': [],
            'missing_visual_data': [],
            'invalid_answer': [],
            'explanation_mismatch': [],
            'empty_fields': []
        }
        
        for challenge in challenges:
            ch_id = challenge['id']
            ch_type = challenge['challenge_type']
            correct_answer = challenge['correct_answer']
            visual_data = challenge['visual_data']
            explanation = challenge['solution_explanation']
            
            # Parser visual_data si nécessaire
            if visual_data:
                if isinstance(visual_data, str):
                    try:
                        visual_data = json.loads(visual_data)
                    except:
                        visual_data = None
            
            # Vérification 1: Visual data manquant
            if not visual_data:
                issues['missing_visual_data'].append({
                    'id': ch_id,
                    'title': challenge['title'],
                    'type': ch_type
                })
            
            # Vérification 2: Pattern incohérent pour les challenges PATTERN
            if ch_type == 'PATTERN' and visual_data and 'grid' in visual_data:
                grid = visual_data.get('grid', [])
                if grid and len(grid) > 0:
                    # Vérifier la cohérence du pattern
                    last_row = grid[-1] if grid else []
                    if '?' in str(last_row):
                        # Analyser le pattern
                        pattern_ok = check_pattern_coherence(grid, correct_answer)
                        if not pattern_ok:
                            issues['pattern_incoherence'].append({
                                'id': ch_id,
                                'title': challenge['title'],
                                'grid': grid,
                                'answer': correct_answer,
                                'explanation': explanation
                            })
            
            # Vérification 3: Réponse vide ou invalide
            if not correct_answer or correct_answer.strip() == '':
                issues['invalid_answer'].append({
                    'id': ch_id,
                    'title': challenge['title']
                })
            
            # Vérification 4: Explication manquante ou vide
            if not explanation or explanation.strip() == '':
                issues['empty_fields'].append({
                    'id': ch_id,
                    'title': challenge['title'],
                    'field': 'solution_explanation'
                })
        
        # Afficher les résultats
        print("=" * 80)
        print("RAPPORT DE QUALITE DES CHALLENGES IA")
        print("=" * 80)
        
        print(f"\n[1] PATTERNS INCOHERENTS: {len(issues['pattern_incoherence'])}")
        if issues['pattern_incoherence']:
            print("   Challenges avec patterns logiquement incorrects:")
            for issue in issues['pattern_incoherence'][:5]:  # Limiter à 5 exemples
                print(f"   - ID {issue['id']}: {issue['title']}")
                print(f"     Grille: {issue['grid']}")
                print(f"     Reponse: '{issue['answer']}'")
                print(f"     Explication: {issue['explanation'][:100]}...")
        
        print(f"\n[2] VISUAL_DATA MANQUANT: {len(issues['missing_visual_data'])}")
        if issues['missing_visual_data']:
            print("   Challenges sans visual_data:")
            for issue in issues['missing_visual_data'][:5]:
                print(f"   - ID {issue['id']}: {issue['title']} (type: {issue['type']})")
        
        print(f"\n[3] REPONSES INVALIDES: {len(issues['invalid_answer'])}")
        if issues['invalid_answer']:
            print("   Challenges avec reponse vide:")
            for issue in issues['invalid_answer'][:5]:
                print(f"   - ID {issue['id']}: {issue['title']}")
        
        print(f"\n[4] EXPLICATIONS MANQUANTES: {len(issues['empty_fields'])}")
        if issues['empty_fields']:
            print("   Challenges sans explication:")
            for issue in issues['empty_fields'][:5]:
                print(f"   - ID {issue['id']}: {issue['title']}")
        
        # Statistiques globales
        total_issues = sum(len(v) for v in issues.values())
        quality_score = max(0, 100 - (total_issues / len(challenges) * 100)) if challenges else 0
        
        print("\n" + "=" * 80)
        print(f"SCORE DE QUALITE GLOBAL: {quality_score:.1f}%")
        print(f"Total de problemes detectes: {total_issues}/{len(challenges)}")
        print("=" * 80)
        
        # Recommandations
        print("\n[RECOMMANDATIONS]")
        if len(issues['pattern_incoherence']) > len(challenges) * 0.1:
            print("   [CRITIQUE] Plus de 10% des challenges ont des patterns incoherents")
            print("   -> Ameliorer le prompt systeme pour la validation logique")
            print("   -> Ajouter une verification post-generation")
        
        if len(issues['missing_visual_data']) > len(challenges) * 0.2:
            print("   [CRITIQUE] Plus de 20% des challenges n'ont pas de visual_data")
            print("   -> Rendre visual_data obligatoire dans le prompt")
            print("   -> Ajouter une validation avant sauvegarde")
        
        if quality_score < 70:
            print("   [ATTENTION] Score de qualite inferieur a 70%")
            print("   -> Considerer l'utilisation d'un modele plus recent (GPT-4o)")
            print("   -> Implementer un systeme de validation multi-etapes")
            print("   -> Ajouter des exemples few-shot plus precis dans le prompt")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


def check_pattern_coherence(grid, correct_answer):
    """
    Vérifie la cohérence logique d'un pattern dans une grille.
    Retourne True si le pattern est cohérent, False sinon.
    """
    if not grid or len(grid) == 0:
        return False
    
    # Trouver la position du '?'
    question_pos = None
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == '?' or (isinstance(cell, str) and '?' in cell):
                question_pos = (i, j)
                break
        if question_pos:
            break
    
    if not question_pos:
        return True  # Pas de '?' à compléter
    
    row_idx, col_idx = question_pos
    
    # Analyser le pattern horizontal (ligne)
    row = grid[row_idx]
    if len(row) >= 2:
        # Pattern X-O-X suggère X
        if row[0] == 'X' and row[1] == 'O' and col_idx == 2:
            expected = 'X'
            return correct_answer.upper() == expected.upper()
    
    # Analyser le pattern vertical (colonne)
    if len(grid) >= 2:
        col = [grid[i][col_idx] for i in range(len(grid))]
        if len(col) >= 2:
            if col[0] == 'X' and col[1] == 'O' and row_idx == 2:
                expected = 'X'
                return correct_answer.upper() == expected.upper()
    
    # Si on ne peut pas déterminer, considérer comme cohérent
    return True


if __name__ == "__main__":
    analyze_ai_challenges()

