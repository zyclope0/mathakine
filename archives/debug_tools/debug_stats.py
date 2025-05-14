import sqlite3
import os

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_trainer.db")
print(f"Chemin de la base de données: {DB_PATH}")

# Se connecter à la base de données
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Afficher les données de la table user_stats
print("\n=== Contenu de la table user_stats ===")
cursor.execute("SELECT * FROM user_stats")
rows = cursor.fetchall()

if not rows:
    print("La table user_stats est vide!")
else:
    for row in rows:
        print(f"ID: {row['id']}, Type: {row['exercise_type']}, Difficulté: {row['difficulty']}")
        print(f"  Tentatives totales: {row['total_attempts']}, Tentatives correctes: {row['correct_attempts']}")
        print(f"  Dernière mise à jour: {row['last_updated']}")
        print("---")

# Afficher les totaux
print("\n=== Statistiques globales ===")
cursor.execute('''
SELECT 
    SUM(total_attempts) as total_completed,
    SUM(correct_attempts) as correct_answers
FROM user_stats
''')
overall_stats = cursor.fetchone()
print(f"Total des tentatives: {overall_stats['total_completed'] or 0}")
print(f"Total des réponses correctes: {overall_stats['correct_answers'] or 0}")

# Vérifier les entrées dans la table results
print("\n=== Dernières entrées dans la table results ===")
cursor.execute('''
SELECT 
    r.id,
    r.exercise_id,
    r.is_correct,
    r.time_spent,
    r.created_at,
    e.exercise_type,
    e.difficulty
FROM results r
JOIN exercises e ON r.exercise_id = e.id
ORDER BY r.created_at DESC
LIMIT 5
''')
results = cursor.fetchall()

if not results:
    print("La table results est vide!")
else:
    for result in results:
        print(f"ID: {result['id']}, Exercice: {result['exercise_id']}, Type: {result['exercise_type']}, Difficulté: {result['difficulty']}")
        print(f"  Correct: {'Oui' if result['is_correct'] else 'Non'}, Temps: {result['time_spent']:.2f}s")
        print(f"  Date: {result['created_at']}")
        print("---")

# Fermer la connexion
conn.close() 