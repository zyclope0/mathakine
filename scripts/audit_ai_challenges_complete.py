#!/usr/bin/env python3
"""
Audit complet de la génération IA des challenges.
Vérifie : type, groupe d'âge, difficulté, visual_data, cohérence.
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

def audit_ai_challenges():
    """Audit complet des challenges générés par IA."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT id, title, challenge_type, age_group, difficulty_rating, 
                   visual_data, tags, correct_answer, question
            FROM logic_challenges 
            WHERE tags LIKE '%ai%' OR tags LIKE '%generated%'
            ORDER BY id DESC
        """)
        challenges = cursor.fetchall()
        
        print(f"[AUDIT COMPLET] {len(challenges)} challenges IA trouves\n")
        print("=" * 80)
        
        issues = {
            'age_group_mismatch': [],
            'difficulty_inappropriate': [],
            'graph_visual_data_incomplete': [],
            'visual_data_malformed': [],
            'type_correct': []
        }
        
        # Mapping des groupes d'âge attendus
        age_group_difficulty_map = {
            'GROUP_10_12': {'min': 1.0, 'max': 3.0, 'ideal': 2.0},
            'GROUP_13_15': {'min': 2.0, 'max': 4.5, 'ideal': 3.5},
            'ALL_AGES': {'min': 1.0, 'max': 5.0, 'ideal': 3.0}
        }
        
        for challenge in challenges:
            ch_id = challenge['id']
            ch_type = challenge['challenge_type']
            age_group = challenge['age_group']
            difficulty = challenge['difficulty_rating']
            visual_data = challenge['visual_data']
            
            # Parser visual_data
            if visual_data:
                if isinstance(visual_data, str):
                    try:
                        visual_data = json.loads(visual_data)
                    except:
                        visual_data = None
            
            # Vérification 1: Type de défi (semble correct selon l'utilisateur)
            issues['type_correct'].append({
                'id': ch_id,
                'type': ch_type
            })
            
            # Vérification 2: Groupe d'âge (vérifier si normalisé correctement)
            if age_group not in ['GROUP_10_12', 'GROUP_13_15', 'ALL_AGES']:
                issues['age_group_mismatch'].append({
                    'id': ch_id,
                    'title': challenge['title'],
                    'age_group': age_group,
                    'expected': 'GROUP_10_12, GROUP_13_15, or ALL_AGES'
                })
            
            # Vérification 3: Difficulté adaptée au groupe d'âge
            if age_group in age_group_difficulty_map:
                expected_range = age_group_difficulty_map[age_group]
                if difficulty < expected_range['min'] or difficulty > expected_range['max']:
                    issues['difficulty_inappropriate'].append({
                        'id': ch_id,
                        'title': challenge['title'],
                        'age_group': age_group,
                        'difficulty': difficulty,
                        'expected_min': expected_range['min'],
                        'expected_max': expected_range['max'],
                        'ideal': expected_range['ideal']
                    })
            
            # Vérification 4: Visual_data pour GRAPH
            if ch_type == 'GRAPH' and visual_data:
                nodes = visual_data.get('nodes', [])
                edges = visual_data.get('edges', [])
                
                if not nodes or len(nodes) == 0:
                    issues['graph_visual_data_incomplete'].append({
                        'id': ch_id,
                        'title': challenge['title'],
                        'issue': 'Pas de nodes'
                    })
                elif not edges or len(edges) == 0:
                    issues['graph_visual_data_incomplete'].append({
                        'id': ch_id,
                        'title': challenge['title'],
                        'issue': 'Pas de edges'
                    })
                else:
                    # Vérifier que tous les nœuds dans edges existent dans nodes
                    node_set = set(str(n).upper() for n in nodes)
                    missing_nodes = []
                    
                    for edge in edges:
                        if isinstance(edge, list) and len(edge) >= 2:
                            from_node = str(edge[0]).upper()
                            to_node = str(edge[1]).upper()
                            
                            if from_node not in node_set:
                                missing_nodes.append(from_node)
                            if to_node not in node_set:
                                missing_nodes.append(to_node)
                    
                    if missing_nodes:
                        issues['graph_visual_data_incomplete'].append({
                            'id': ch_id,
                            'title': challenge['title'],
                            'issue': f'Nodes manquants dans edges: {set(missing_nodes)}',
                            'nodes': nodes,
                            'edges': edges
                        })
            
            # Vérification 5: Visual_data malformé
            if visual_data and isinstance(visual_data, dict):
                # Vérifier les structures communes malformées
                if 'arrangement' in visual_data:
                    arrangement = visual_data['arrangement']
                    if isinstance(arrangement, str) and arrangement in ['[', ']', ',', ' ']:
                        issues['visual_data_malformed'].append({
                            'id': ch_id,
                            'title': challenge['title'],
                            'issue': f'arrangement invalide: "{arrangement}"',
                            'visual_data': visual_data
                        })
        
        # Afficher les résultats
        print("\n[1] GROUPES D'AGE INCOHERENTS")
        print(f"   Total: {len(issues['age_group_mismatch'])}")
        for issue in issues['age_group_mismatch'][:5]:
            print(f"   - ID {issue['id']}: {issue['title']}")
            print(f"     Age group: '{issue['age_group']}' (attendu: {issue['expected']})")
        
        print("\n[2] DIFFICULTE INAPPROPRIEE")
        print(f"   Total: {len(issues['difficulty_inappropriate'])}")
        for issue in issues['difficulty_inappropriate'][:5]:
            print(f"   - ID {issue['id']}: {issue['title']}")
            print(f"     Age: {issue['age_group']}, Difficulty: {issue['difficulty']}")
            print(f"     Attendu: {issue['expected_min']}-{issue['expected_max']} (ideal: {issue['ideal']})")
        
        print("\n[3] GRAPH VISUAL_DATA INCOMPLET")
        print(f"   Total: {len(issues['graph_visual_data_incomplete'])}")
        for issue in issues['graph_visual_data_incomplete'][:5]:
            print(f"   - ID {issue['id']}: {issue['title']}")
            print(f"     Probleme: {issue['issue']}")
            if 'nodes' in issue:
                print(f"     Nodes: {issue['nodes']}")
                print(f"     Edges: {issue['edges']}")
        
        print("\n[4] VISUAL_DATA MALFORME")
        print(f"   Total: {len(issues['visual_data_malformed'])}")
        for issue in issues['visual_data_malformed'][:5]:
            print(f"   - ID {issue['id']}: {issue['title']}")
            print(f"     Probleme: {issue['issue']}")
        
        print("\n[5] TYPES DE DEFIS")
        print(f"   Total: {len(issues['type_correct'])}")
        type_counts = {}
        for item in issues['type_correct']:
            t = item['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, count in sorted(type_counts.items()):
            print(f"   - {t}: {count}")
        
        # Score global
        total_issues = (
            len(issues['age_group_mismatch']) +
            len(issues['difficulty_inappropriate']) +
            len(issues['graph_visual_data_incomplete']) +
            len(issues['visual_data_malformed'])
        )
        quality_score = max(0, 100 - (total_issues / len(challenges) * 100)) if challenges else 0
        
        print("\n" + "=" * 80)
        print(f"SCORE DE QUALITE: {quality_score:.1f}%")
        print(f"Total de problemes: {total_issues}/{len(challenges)}")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    audit_ai_challenges()

