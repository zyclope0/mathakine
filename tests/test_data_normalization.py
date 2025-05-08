"""Test de vérification de la normalisation des données dans la base de données."""
import os
import unittest
import sqlite3
import sys

class TestDataNormalization(unittest.TestCase):
    """Tests pour vérifier la normalisation correcte des données dans la base de données."""
    
    def setUp(self):
        """Prépare l'environnement de test."""
        # Chemin de la base de données
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "math_trainer.db")
        # Valeurs attendues
        self.valid_exercise_types = ['addition', 'subtraction', 'multiplication', 'division']
        self.valid_difficulties = ['easy', 'medium', 'hard']
        
        # Vérifier si la base de données existe
        if not os.path.exists(self.db_path):
            print(f"ATTENTION: Base de données non trouvée à {self.db_path}")
            print("Les tests seront ignorés.")
            self.skipTest("Base de données non trouvée")
    
    def test_exercise_types_normalized(self):
        """Vérifie que tous les types d'exercices sont correctement normalisés."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT exercise_type FROM exercises")
        exercise_types = [row['exercise_type'] for row in cursor.fetchall()]
        
        # Vérifier que tous les types sont en minuscules
        for ex_type in exercise_types:
            self.assertEqual(ex_type.lower(), ex_type, 
                f"Type d'exercice '{ex_type}' n'est pas en minuscules")
        
        # Vérifier que tous les types sont valides
        for ex_type in exercise_types:
            self.assertIn(ex_type, self.valid_exercise_types, 
                f"Type d'exercice '{ex_type}' n'est pas valide")
        
        conn.close()
    
    def test_difficulties_normalized(self):
        """Vérifie que toutes les difficultés sont correctement normalisées."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT difficulty FROM exercises")
        difficulties = [row['difficulty'] for row in cursor.fetchall()]
        
        # Vérifier que toutes les difficultés sont en minuscules
        for diff in difficulties:
            self.assertEqual(diff.lower(), diff, 
                f"Difficulté '{diff}' n'est pas en minuscules")
        
        # Vérifier que toutes les difficultés sont valides
        for diff in difficulties:
            self.assertIn(diff, self.valid_difficulties, 
                f"Difficulté '{diff}' n'est pas valide")
        
        conn.close()
    
    def test_user_stats_no_duplicates(self):
        """Vérifie qu'il n'y a pas de doublons dans la table user_stats."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT exercise_type, difficulty, COUNT(*) as count
        FROM user_stats
        GROUP BY exercise_type, difficulty
        HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        
        self.assertEqual(len(duplicates), 0, 
            f"Trouvé {len(duplicates)} combinaisons en double dans user_stats")
        
        conn.close()
    
    def test_user_stats_types_match_exercises(self):
        """Vérifie que les types d'exercices dans user_stats correspondent à ceux dans exercises."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupérer les types d'exercices uniques dans exercises
        cursor.execute("SELECT DISTINCT exercise_type FROM exercises")
        exercise_types = set([row['exercise_type'] for row in cursor.fetchall()])
        
        # Récupérer les types d'exercices uniques dans user_stats
        cursor.execute("SELECT DISTINCT exercise_type FROM user_stats")
        user_stats_types = set([row['exercise_type'] for row in cursor.fetchall()])
        
        # Vérifier que tous les types dans exercises sont dans user_stats
        missing_types = exercise_types - user_stats_types
        self.assertEqual(len(missing_types), 0,
            f"Types manquants dans user_stats: {missing_types}")
        
        # Vérifier que tous les types dans user_stats sont valides
        invalid_types = user_stats_types - set(self.valid_exercise_types)
        self.assertEqual(len(invalid_types), 0,
            f"Types invalides dans user_stats: {invalid_types}")
        
        conn.close()

if __name__ == '__main__':
    unittest.main() 