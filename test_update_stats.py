import sqlite3
import os
import requests
import json

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_trainer.db")
print(f"Chemin de la base de données: {DB_PATH}")

# Imprimer l'état initial des statistiques
def print_user_stats():
    print("\n=== Contenu de la table user_stats ===")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_stats")
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"ID: {row['id']}, Type: {row['exercise_type']}, Difficulté: {row['difficulty']}")
        print(f"  Tentatives totales: {row['total_attempts']}, Tentatives correctes: {row['correct_attempts']}")
        print(f"  Dernière mise à jour: {row['last_updated']}")
        print("---")
    
    conn.close()

# Obtenir un exercice existant
def get_exercise():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM exercises LIMIT 1")
    exercise = cursor.fetchone()
    
    result = None
    if exercise:
        result = dict(exercise)
    
    conn.close()
    return result

# Simuler l'envoi d'une réponse directement via la base de données
def simulate_answer_via_db(exercise_id, is_correct=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Récupérer l'exercice
    cursor.execute("SELECT * FROM exercises WHERE id = ?", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not exercise:
        print(f"Exercice {exercise_id} non trouvé.")
        conn.close()
        return
    
    exercise_type = exercise[6].lower()  # Indice 6 est exercise_type
    difficulty = exercise[7].lower()     # Indice 7 est difficulty
    
    # Normaliser comme dans le code corrigé
    if exercise_type not in ['addition', 'subtraction', 'multiplication', 'division']:
        if exercise_type == 'addition':
            exercise_type = 'addition'
        elif exercise_type == 'subtraction':
            exercise_type = 'subtraction'
        elif exercise_type == 'multiplication':
            exercise_type = 'multiplication'
        elif exercise_type == 'division':
            exercise_type = 'division'
    
    if difficulty not in ['easy', 'medium', 'hard']:
        if difficulty == 'initie':
            difficulty = 'easy'
        elif difficulty == 'padawan':
            difficulty = 'medium'
        elif difficulty == 'chevalier':
            difficulty = 'hard'
    
    # Insérer un résultat
    cursor.execute('''
    INSERT INTO results (exercise_id, is_correct, time_spent)
    VALUES (?, ?, ?)
    ''', (exercise_id, is_correct, 1.5))
    
    # Mettre à jour les statistiques
    cursor.execute('''
    UPDATE user_stats
    SET 
        total_attempts = total_attempts + 1,
        correct_attempts = correct_attempts + CASE WHEN ? THEN 1 ELSE 0 END,
        last_updated = CURRENT_TIMESTAMP
    WHERE exercise_type = ? AND difficulty = ?
    ''', (is_correct, exercise_type, difficulty))
    
    # Vérifier si la mise à jour a affecté des lignes
    if cursor.rowcount == 0:
        print(f"Avertissement: Aucune ligne mise à jour dans user_stats pour exercise_type={exercise_type}, difficulty={difficulty}")
        cursor.execute('''
        INSERT OR IGNORE INTO user_stats (exercise_type, difficulty, total_attempts, correct_attempts, last_updated)
        VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
        ''', (exercise_type, difficulty, 1 if is_correct else 0))
    
    conn.commit()
    conn.close()
    print(f"Simulation d'une réponse {'correcte' if is_correct else 'incorrecte'} pour l'exercice {exercise_id} (type: {exercise_type}, difficulté: {difficulty}).")

# Simuler l'envoi d'une réponse via l'API
def simulate_answer_via_api(exercise_id, selected_answer="42"):
    try:
        # Vérifier que le serveur est en cours d'exécution
        response = requests.post(
            'http://localhost:8000/api/submit-answer',
            json={
                'exercise_id': exercise_id,
                'selected_answer': selected_answer,
                'time_spent': 2.5
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"Simulation d'une réponse via API pour l'exercice {exercise_id}.")
            print(f"Résultat: {'Correct' if result['is_correct'] else 'Incorrect'}")
            return True
        else:
            print(f"Erreur lors de l'envoi de la réponse via API: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception lors de l'envoi de la réponse via API: {e}")
        return False

# Test principal
if __name__ == "__main__":
    print("=== Test de la mise à jour des statistiques ===")
    print_user_stats()
    
    exercise = get_exercise()
    if exercise:
        print(f"\nExercice trouvé: ID={exercise['id']}, Type={exercise['exercise_type']}, Difficulté={exercise['difficulty']}")
        
        # Tester via la base de données
        print("\n=== Test via la base de données ===")
        simulate_answer_via_db(exercise['id'], True)
        
        print("\n=== Statistiques après la simulation via DB ===")
        print_user_stats()
        
        # Si le serveur est lancé, tester aussi via l'API
        print("\n=== Test via l'API (ignoré si le serveur n'est pas en cours d'exécution) ===")
        try:
            if simulate_answer_via_api(exercise['id'], exercise['correct_answer']):
                print("\n=== Statistiques après la simulation via API ===")
                print_user_stats()
        except:
            print("Serveur non disponible, test API ignoré.")
    else:
        print("Aucun exercice trouvé dans la base de données.") 