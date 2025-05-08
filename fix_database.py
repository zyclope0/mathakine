import sqlite3
import os
import sys

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_trainer.db")
print(f"Chemin de la base de données: {DB_PATH}")

# Analyser les types d'exercices et difficultés existants
def analyze_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Analyser les exercices
    print("\n=== Types d'exercices dans la table exercises ===")
    cursor.execute("SELECT DISTINCT exercise_type FROM exercises")
    types = cursor.fetchall()
    for t in types:
        print(f"- {t['exercise_type']}")
    
    print("\n=== Difficultés dans la table exercises ===")
    cursor.execute("SELECT DISTINCT difficulty FROM exercises")
    difficulties = cursor.fetchall()
    for d in difficulties:
        print(f"- {d['difficulty']}")
    
    # Analyser les statistiques
    print("\n=== Types d'exercices dans la table user_stats ===")
    cursor.execute("SELECT DISTINCT exercise_type FROM user_stats")
    stats_types = cursor.fetchall()
    for t in stats_types:
        print(f"- {t['exercise_type']}")
    
    print("\n=== Difficultés dans la table user_stats ===")
    cursor.execute("SELECT DISTINCT difficulty FROM user_stats")
    stats_diff = cursor.fetchall()
    for d in stats_diff:
        print(f"- {d['difficulty']}")
        
    # Analyser les données de résultats
    print("\n=== Données dans la table results ===")
    cursor.execute("SELECT COUNT(*) as count FROM results")
    result_count = cursor.fetchone()['count']
    print(f"Nombre total de résultats: {result_count}")
    
    conn.close()
    
    return types, difficulties, stats_types, stats_diff

# Normaliser un type d'exercice
def normalize_exercise_type(exercise_type):
    exercise_type = exercise_type.lower()
    
    # Mapper les différentes variantes aux types standard
    mappings = {
        'addition': 'addition',
        'add': 'addition',
        'somme': 'addition',
        'plus': 'addition',
        'subtraction': 'subtraction',
        'sub': 'subtraction',
        'soustraction': 'subtraction',
        'minus': 'subtraction',
        'multiplication': 'multiplication',
        'mult': 'multiplication',
        'produit': 'multiplication',
        'times': 'multiplication',
        'division': 'division',
        'div': 'division',
    }
    
    # Vérifier les correspondances exactes
    if exercise_type in mappings:
        return mappings[exercise_type]
    
    # Vérifier les correspondances partielles
    for key, value in mappings.items():
        if key in exercise_type:
            return value
    
    # Si c'est tout en majuscules, convertir en minuscules
    if exercise_type.upper() == exercise_type:
        lowercase = exercise_type.lower()
        if lowercase in mappings:
            return mappings[lowercase]
    
    # Par défaut, retourner addition
    print(f"ATTENTION: Type d'exercice inconnu: {exercise_type}, conversion par défaut en 'addition'")
    return 'addition'

# Normaliser une difficulté
def normalize_difficulty(difficulty):
    difficulty = difficulty.lower()
    
    # Mapper les différentes variantes aux difficultés standard
    mappings = {
        'easy': 'easy',
        'facile': 'easy',
        'débutant': 'easy',
        'initie': 'easy',
        'initié': 'easy',
        'medium': 'medium',
        'moyen': 'medium',
        'intermédiaire': 'medium',
        'padawan': 'medium',
        'hard': 'hard',
        'difficile': 'hard',
        'avancé': 'hard',
        'chevalier': 'hard',
    }
    
    # Vérifier les correspondances exactes
    if difficulty in mappings:
        return mappings[difficulty]
    
    # Vérifier les correspondances partielles
    for key, value in mappings.items():
        if key in difficulty:
            return value
    
    # Si c'est tout en majuscules, convertir en minuscules
    if difficulty.upper() == difficulty:
        lowercase = difficulty.lower()
        if lowercase in mappings:
            return mappings[lowercase]
    
    # Par défaut, retourner easy
    print(f"ATTENTION: Difficulté inconnue: {difficulty}, conversion par défaut en 'easy'")
    return 'easy'

# Corriger les doublons dans la table user_stats
def fix_duplicates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Identifier les combinaisons uniques de type et difficulté
    cursor.execute("""
    SELECT exercise_type, difficulty, COUNT(*) as count
    FROM user_stats
    GROUP BY exercise_type, difficulty
    HAVING COUNT(*) > 1
    """)
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print("\n=== Doublons détectés dans user_stats ===")
        for dup in duplicates:
            ex_type, diff, count = dup
            print(f"Type: {ex_type}, Difficulté: {diff}, Nombre: {count}")
            
            # Récupérer toutes les entrées pour ce type et cette difficulté
            cursor.execute("""
            SELECT id, total_attempts, correct_attempts
            FROM user_stats
            WHERE exercise_type = ? AND difficulty = ?
            ORDER BY id
            """, (ex_type, diff))
            
            entries = cursor.fetchall()
            
            # Garder la première entrée et fusionner les statistiques
            keep_id = entries[0][0]
            total_attempts = sum(entry[1] for entry in entries)
            correct_attempts = sum(entry[2] for entry in entries)
            
            print(f"  Fusion vers ID {keep_id}: {total_attempts} tentatives, {correct_attempts} correctes")
            
            # Mettre à jour l'entrée à conserver
            cursor.execute("""
            UPDATE user_stats
            SET total_attempts = ?, correct_attempts = ?, last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (total_attempts, correct_attempts, keep_id))
            
            # Supprimer les autres entrées
            for entry in entries[1:]:
                cursor.execute("DELETE FROM user_stats WHERE id = ?", (entry[0],))
                print(f"  Suppression de l'entrée ID {entry[0]}")
    
    else:
        print("\nAucun doublon détecté dans user_stats.")
    
    conn.commit()
    conn.close()

# Corriger la base de données
def fix_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Corriger les types d'exercices dans la table exercises
    cursor.execute("SELECT id, exercise_type FROM exercises")
    exercises = cursor.fetchall()
    
    for ex in exercises:
        ex_id, ex_type = ex
        normalized_type = normalize_exercise_type(ex_type)
        if normalized_type != ex_type:
            print(f"Correction du type d'exercice: {ex_type} -> {normalized_type} (ID: {ex_id})")
            cursor.execute("UPDATE exercises SET exercise_type = ? WHERE id = ?", (normalized_type, ex_id))
    
    # 2. Corriger les difficultés dans la table exercises
    cursor.execute("SELECT id, difficulty FROM exercises")
    exercises = cursor.fetchall()
    
    for ex in exercises:
        ex_id, ex_diff = ex
        normalized_diff = normalize_difficulty(ex_diff)
        if normalized_diff != ex_diff:
            print(f"Correction de la difficulté: {ex_diff} -> {normalized_diff} (ID: {ex_id})")
            cursor.execute("UPDATE exercises SET difficulty = ? WHERE id = ?", (normalized_diff, ex_id))
    
    # 3. S'assurer que les valeurs standard existent dans user_stats
    for exercise_type in ['addition', 'subtraction', 'multiplication', 'division']:
        for difficulty in ['easy', 'medium', 'hard']:
            cursor.execute("""
            INSERT OR IGNORE INTO user_stats (exercise_type, difficulty, total_attempts, correct_attempts, last_updated)
            VALUES (?, ?, 0, 0, CURRENT_TIMESTAMP)
            """, (exercise_type, difficulty))
    
    conn.commit()
    
    # Vérifier que des lignes user_stats n'ont pas de types standards
    cursor.execute("""
    SELECT id, exercise_type, difficulty 
    FROM user_stats 
    WHERE exercise_type NOT IN ('addition', 'subtraction', 'multiplication', 'division')
    OR difficulty NOT IN ('easy', 'medium', 'hard')
    """)
    
    non_standard = cursor.fetchall()
    if non_standard:
        print("\n=== Lignes user_stats non standard ===")
        for row in non_standard:
            print(f"ID: {row[0]}, Type: {row[1]}, Difficulté: {row[2]}")
            
            # Récupérer les stats de cette ligne
            cursor.execute("""
            SELECT total_attempts, correct_attempts 
            FROM user_stats 
            WHERE id = ?
            """, (row[0],))
            stats = cursor.fetchone()
            
            if stats and (stats[0] > 0 or stats[1] > 0):
                # Normaliser les valeurs
                norm_type = normalize_exercise_type(row[1])
                norm_diff = normalize_difficulty(row[2])
                
                # Mettre à jour les statistiques standard correspondantes
                print(f"  Transfert des statistiques vers {norm_type}/{norm_diff}")
                cursor.execute("""
                UPDATE user_stats
                SET 
                    total_attempts = total_attempts + ?,
                    correct_attempts = correct_attempts + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE exercise_type = ? AND difficulty = ?
                """, (stats[0], stats[1], norm_type, norm_diff))
                
                # Supprimer l'entrée non standard (optionnel)
                cursor.execute("DELETE FROM user_stats WHERE id = ?", (row[0],))
    
    conn.commit()
    conn.close()

# Fonction principale
if __name__ == "__main__":
    print("=== Analyse de la base de données ===")
    analyze_database()
    
    answer = input("\nVoulez-vous corriger la base de données ? (y/n): ")
    if answer.lower() == 'y':
        print("\n=== Correction de la base de données ===")
        fix_database()
        
        print("\n=== Correction des doublons ===")
        fix_duplicates()
        
        print("\n=== Analyse après correction ===")
        analyze_database()
    else:
        print("Opération annulée.") 