import psycopg2
import random
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

def main():
    """
    Ce script modifie la structure de la table results puis ajoute des données de test
    pour afficher les données réelles sur le graphique du tableau de bord.
    """
    # Charger les variables d'environnement
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    print(f"Connexion à la base de données PostgreSQL...")
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    # 1. Recréer la table results avec un ID auto-incrémenté
    print("Tentative de suppression et recréation de la table results...")
    try:
        # Vérifier si la table results existe déjà
        cursor.execute("SELECT COUNT(*) FROM results")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"La table results existe déjà avec {count} enregistrements.")
            user_input = input("Voulez-vous supprimer et recréer la table? (y/n): ")
            if user_input.lower() != 'y':
                print("Opération annulée.")
                conn.close()
                return
        
        # Supprimer la table et toutes les contraintes
        cursor.execute("DROP TABLE IF EXISTS results CASCADE")
        conn.commit()
        print("Table results supprimée.")
        
        # Recréer la table avec la bonne structure
        cursor.execute("""
        CREATE TABLE results (
            id SERIAL PRIMARY KEY,
            exercise_id INTEGER NOT NULL,
            is_correct BOOLEAN NOT NULL,
            time_spent REAL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        print("Table results recréée avec succès.")
        
    except Exception as e:
        print(f"Erreur lors de la création de la table: {e}")
        conn.rollback()
        conn.close()
        return

    # 2. Ajouter des données de test
    print("Ajout de données de test...")
    
    # Récupérer la liste des IDs d'exercices existants
    cursor.execute("SELECT id FROM exercises ORDER BY id")
    exercise_ids = [row[0] for row in cursor.fetchall()]
    
    if not exercise_ids:
        print("Aucun exercice trouvé dans la base de données. Impossible d'ajouter des données de test.")
        conn.close()
        return
    
    print(f"Nombre d'exercices disponibles: {len(exercise_ids)}")
    
    # Générer des données pour les 30 derniers jours
    current_date = datetime.now()
    
    # Calculer la répartition des données sur les jours
    # Plus de données pour les jours récents, moins pour les jours anciens
    day_counts = []
    total_entries = 150  # Nombre total d'entrées à créer
    base_count = total_entries // 30  # Nombre moyen par jour
    
    # Distribution gaussienne simple pour avoir plus d'entrées récentes
    for i in range(30):
        factor = max(0.5, (30 - i) / 30)  # Plus élevé pour les jours récents
        count = int(base_count * factor * random.uniform(0.8, 1.2))
        day_counts.append(count)
    
    # Assurer que le nombre total d'entrées est respecté
    while sum(day_counts) > total_entries:
        idx = random.randint(0, len(day_counts) - 1)
        if day_counts[idx] > 1:
            day_counts[idx] -= 1
    
    # Répartition des exercices par jour
    entries_created = 0
    days_with_data = 0
    
    for i, count in enumerate(day_counts):
        if count == 0:
            continue
            
        days_with_data += 1
        day_date = current_date - timedelta(days=i)
        
        print(f"Ajout de {count} entrées pour le {day_date.strftime('%Y-%m-%d')}...")
        
        for j in range(count):
            # Sélectionner un exercice aléatoire
            exercise_id = random.choice(exercise_ids)
            
            # 70% de chances que l'exercice soit correct
            is_correct = random.random() < 0.7
            
            # Temps passé entre 10 et 60 secondes
            time_spent = random.uniform(10, 60)
            
            # Calculer un timestamp aléatoire dans la journée
            hour = random.randint(8, 22)  # Entre 8h et 22h
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            timestamp = day_date.replace(hour=hour, minute=minute, second=second)
            
            # Insérer dans la base de données
            try:
                cursor.execute("""
                INSERT INTO results (exercise_id, is_correct, time_spent, created_at)
                VALUES (%s, %s, %s, %s)
                """, (exercise_id, is_correct, time_spent, timestamp))
                entries_created += 1
            except Exception as e:
                print(f"Erreur lors de l'insertion: {e}")
                continue
    
    conn.commit()
    print(f"Données de test ajoutées avec succès: {entries_created} entrées sur {days_with_data} jours.")
    
    # 3. Vérifier les données
    cursor.execute("SELECT COUNT(*) FROM results")
    count = cursor.fetchone()[0]
    print(f"Nombre total d'enregistrements dans la table results: {count}")
    
    # Afficher la répartition par jour
    cursor.execute("""
    SELECT DATE(created_at) as day, COUNT(*) as count
    FROM results
    GROUP BY DATE(created_at)
    ORDER BY day DESC
    LIMIT 10
    """)
    
    print("\nRépartition des données par jour:")
    print("-" * 40)
    print(f"{'Date':<12} | {'Nombre d''enregistrements'}")
    print("-" * 40)
    
    for row in cursor.fetchall():
        print(f"{row[0]} | {row[1]}")
    
    conn.close()
    print("Opération terminée.")

if __name__ == "__main__":
    main() 