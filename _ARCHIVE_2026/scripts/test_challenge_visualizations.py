"""
Script pour tester les visualisations interactives des challenges.
Crée des challenges de test avec visual_data pour chaque type.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_connection
from loguru import logger

def create_test_challenges():
    """Crée des challenges de test avec visual_data pour chaque type"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Récupérer un utilisateur pour creator_id
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_row = cursor.fetchone()
        creator_id = user_row['id'] if user_row else None
        
        if not creator_id:
            print("[ERREUR] Aucun utilisateur trouve. Veuillez creer un utilisateur d'abord.")
            return
        
        # Vérifier les valeurs d'enum valides
        cursor.execute("""
            SELECT unnest(enum_range(NULL::logicchallengetype))::text as enum_value
        """)
        valid_types = [row['enum_value'] for row in cursor.fetchall()]
        print(f"Types de challenges valides: {valid_types}\n")
        
        # Vérifier les valeurs d'enum valides pour age_group
        cursor.execute("""
            SELECT unnest(enum_range(NULL::agegroup))::text as enum_value
        """)
        valid_age_groups = [row['enum_value'] for row in cursor.fetchall()]
        print(f"Groupes d'âge valides: {valid_age_groups}\n")
        
        # Normaliser les types (majuscules)
        type_map = {t.upper(): t for t in valid_types}
        
        # Challenges de test avec visual_data
        # Utiliser les valeurs d'enum réelles de la base de données
        test_challenges = [
            {
                'title': 'Test Sequence - Suite de nombres',
                'description': 'Trouvez le prochain nombre dans la sequence.',
                'challenge_type': type_map.get('SEQUENCE', valid_types[0] if valid_types else 'VISUAL'),
                'age_group': 'GROUP_10_12' if 'GROUP_10_12' in valid_age_groups else valid_age_groups[0] if valid_age_groups else '10-12',
                'correct_answer': '16',
                'solution_explanation': 'La séquence suit le pattern : +2, +3, +4, +5...',
                'visual_data': json.dumps({
                    'sequence': [2, 4, 7, 11],
                    'pattern': 'n + (index + 1)'
                }),
                'hints': json.dumps(['Regardez la différence entre les nombres', 'Les différences augmentent', 'La différence entre 11 et le suivant est 5']),
                'difficulty_rating': 2.5,
                'estimated_time_minutes': 5,
            },
            {
                'title': 'Test Pattern - Grille 3x3',
                'description': 'Identifiez le pattern dans la grille.',
                'challenge_type': type_map.get('PATTERN', valid_types[0] if valid_types else 'VISUAL'),
                'age_group': 'GROUP_10_12' if 'GROUP_10_12' in valid_age_groups else valid_age_groups[0] if valid_age_groups else '10-12',
                'correct_answer': 'diagonale',
                'solution_explanation': 'Les X forment une diagonale de haut gauche à bas droite.',
                'visual_data': json.dumps({
                    'grid': [
                        ['X', 'O', 'O'],
                        ['O', 'X', 'O'],
                        ['O', 'O', 'X']
                    ],
                    'size': 3
                }),
                'hints': json.dumps(['Regardez les positions des X', 'Y a-t-il une ligne commune ?']),
                'difficulty_rating': 3.0,
                'estimated_time_minutes': 7,
            },
            {
                'title': 'Test Visuel - Formes geometriques',
                'description': 'Analysez les formes et leur disposition.',
                'challenge_type': type_map.get('VISUAL', valid_types[0] if valid_types else 'VISUAL'),
                'age_group': 'GROUP_10_12' if 'GROUP_10_12' in valid_age_groups else valid_age_groups[0] if valid_age_groups else '10-12',
                'correct_answer': 'triangle',
                'solution_explanation': 'Les formes suivent un pattern de rotation.',
                'visual_data': json.dumps({
                    'shapes': [
                        {'label': 'A', 'type': 'square'},
                        {'label': 'B', 'type': 'circle'},
                        {'label': 'C', 'type': 'triangle'}
                    ],
                    'ascii': '''
    ┌─────┐
    │  A  │
    └─────┘
       │
    ┌──┴──┐
    │  B  │
    └─────┘
       │
    ┌──┴──┐
    │  C  │
    └─────┘
                    '''
                }),
                'hints': json.dumps(['Observez la disposition', 'Y a-t-il une rotation ?']),
                'difficulty_rating': 2.0,
                'estimated_time_minutes': 6,
            },
            {
                'title': 'Test Puzzle - Reorganiser les etapes',
                'description': 'Remettez les etapes dans le bon ordre.',
                'challenge_type': type_map.get('PUZZLE', valid_types[0] if valid_types else 'VISUAL'),
                'age_group': 'GROUP_10_12' if 'GROUP_10_12' in valid_age_groups else valid_age_groups[0] if valid_age_groups else '10-12',
                'correct_answer': 'Préparer,Mélanger,Cuire,Servir',
                'solution_explanation': 'L\'ordre logique est : Préparer, Mélanger, Cuire, Servir.',
                'visual_data': json.dumps({
                    'pieces': [
                        'Servir',
                        'Préparer',
                        'Cuire',
                        'Mélanger'
                    ]
                }),
                'hints': json.dumps(['Pensez à l\'ordre logique', 'Quelle étape vient en premier ?']),
                'difficulty_rating': 2.5,
                'estimated_time_minutes': 5,
            },
            {
                'title': 'Test Graphe - Reseau de connexions',
                'description': 'Analysez le graphe et trouvez le chemin le plus court.',
                'challenge_type': type_map.get('GRAPH', valid_types[0] if valid_types else 'VISUAL'),
                'age_group': 'GROUP_13_15' if 'GROUP_13_15' in valid_age_groups else valid_age_groups[0] if valid_age_groups else '13-15',
                'correct_answer': 'A-C-D',
                'solution_explanation': 'Le chemin A-C-D est le plus court avec 2 arêtes.',
                'visual_data': json.dumps({
                    'nodes': ['A', 'B', 'C', 'D'],
                    'edges': [
                        {'from': 0, 'to': 1},  # A -> B
                        {'from': 0, 'to': 2},  # A -> C
                        {'from': 2, 'to': 3},  # C -> D
                        {'from': 1, 'to': 3},  # B -> D
                    ]
                }),
                'hints': json.dumps(['Comptez les arêtes', 'Quel chemin a le moins d\'étapes ?']),
                'difficulty_rating': 3.5,
                'estimated_time_minutes': 10,
            },
        ]
        
        print(f"\n=== Création de {len(test_challenges)} challenges de test ===\n")
        
        created_count = 0
        for challenge_data in test_challenges:
            try:
                # Vérifier si un challenge similaire existe déjà
                cursor.execute(
                    "SELECT id FROM logic_challenges WHERE title = %s",
                    (challenge_data['title'],)
                )
                existing = cursor.fetchone()
                
                if existing:
                    print(f"[INFO] Challenge '{challenge_data['title']}' existe deja (ID: {existing['id']})")
                    continue
                
                # Insérer le challenge
                insert_query = """
                    INSERT INTO logic_challenges (
                        title, description, challenge_type, age_group,
                        correct_answer, solution_explanation,
                        visual_data, hints,
                        difficulty_rating, estimated_time_minutes,
                        creator_id, is_active, is_archived,
                        created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, false,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ) RETURNING id, title, challenge_type
                """
                
                cursor.execute(
                    insert_query,
                    (
                        challenge_data['title'],
                        challenge_data['description'],
                        challenge_data['challenge_type'],
                        challenge_data['age_group'],
                        challenge_data['correct_answer'],
                        challenge_data['solution_explanation'],
                        challenge_data['visual_data'],
                        challenge_data['hints'],
                        challenge_data['difficulty_rating'],
                        challenge_data['estimated_time_minutes'],
                        creator_id,
                    )
                )
                
                result = cursor.fetchone()
                conn.commit()
                
                print(f"[OK] Challenge cree: '{result['title']}' (ID: {result['id']}, Type: {result['challenge_type']})")
                created_count += 1
                
            except Exception as e:
                conn.rollback()
                print(f"[ERREUR] Erreur lors de la creation de '{challenge_data['title']}': {e}")
        
        print(f"\n=== Résumé : {created_count}/{len(test_challenges)} challenges créés ===\n")
        
        # Afficher les challenges créés avec visual_data
        cursor.execute("""
            SELECT id, title, challenge_type, visual_data IS NOT NULL as has_visual_data
            FROM logic_challenges
            WHERE visual_data IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 10
        """)
        challenges_with_visual = cursor.fetchall()
        
        if challenges_with_visual:
            print("=== Challenges avec visual_data disponibles ===\n")
            for ch in challenges_with_visual:
                print(f"  • ID {ch['id']}: {ch['title']} ({ch['challenge_type']})")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des challenges de test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_test_challenges()

