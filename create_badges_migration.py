#!/usr/bin/env python3
"""
Migration pour créer les tables du système de badges et achievements
"""

from server.database import get_db_connection
import logging

def create_badges_tables():
    """Créer les tables achievements et user_achievements"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🎖️ Création des tables du système de badges...")
        
        # 1. Table achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id SERIAL PRIMARY KEY,
                code VARCHAR(100) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                icon_url VARCHAR(255),
                category VARCHAR(50),
                difficulty VARCHAR(50),
                points_reward INTEGER DEFAULT 0,
                is_secret BOOLEAN DEFAULT FALSE,
                requirements JSON,
                star_wars_title VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Index pour performances
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_achievements_code ON achievements(code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_achievements_category ON achievements(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_achievements_active ON achievements(is_active);")
        
        # 2. Table user_achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                achievement_id INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
                earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                progress_data JSON,
                is_displayed BOOLEAN DEFAULT TRUE,
                UNIQUE(user_id, achievement_id)
            );
        """)
        
        # Index pour performances
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_achievements_user ON user_achievements(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_achievements_earned ON user_achievements(earned_at);")
        
        print("✅ Tables achievements et user_achievements créées")
        
        # 3. Ajouter colonnes gamification à users
        gamification_columns = [
            ("total_points", "INTEGER DEFAULT 0"),
            ("current_level", "INTEGER DEFAULT 1"),
            ("experience_points", "INTEGER DEFAULT 0"),
            ("jedi_rank", "VARCHAR(50) DEFAULT 'youngling'"),
            ("avatar_url", "VARCHAR(255)")
        ]
        
        for col_name, col_def in gamification_columns:
            try:
                cursor.execute(f"""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS {col_name} {col_def};
                """)
                print(f"✅ Colonne {col_name} ajoutée à users")
            except Exception as e:
                print(f"⚠️ Colonne {col_name} existe déjà ou erreur: {e}")
        
        # Index pour performances gamification
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_jedi_rank ON users(jedi_rank);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_total_points ON users(total_points);")
        
        conn.commit()
        print("🎉 Migration badges terminée avec succès!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur migration: {e}")
        raise
    finally:
        conn.close()

def insert_initial_badges():
    """Insérer les badges de base Star Wars"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🌟 Insertion des badges Star Wars initiaux...")
        
        initial_badges = [
            # BADGES DE PROGRESSION
            {
                'code': 'first_steps',
                'name': 'Premiers Pas',
                'description': 'Résoudre votre premier exercice',
                'category': 'progression',
                'difficulty': 'bronze',
                'points_reward': 10,
                'star_wars_title': 'Youngling Prometteur',
                'requirements': '{"attempts_count": 1}'
            },
            {
                'code': 'padawan_path',
                'name': 'Voie du Padawan',
                'description': 'Résoudre 10 exercices',
                'category': 'progression',
                'difficulty': 'silver',
                'points_reward': 50,
                'star_wars_title': 'Padawan Déterminé',
                'requirements': '{"attempts_count": 10}'
            },
            {
                'code': 'knight_trial',
                'name': 'Épreuve du Chevalier',
                'description': 'Résoudre 50 exercices',
                'category': 'progression',
                'difficulty': 'gold',
                'points_reward': 200,
                'star_wars_title': 'Chevalier Jedi',
                'requirements': '{"attempts_count": 50}'
            },
            
            # BADGES DE MAÎTRISE
            {
                'code': 'addition_master',
                'name': 'Maître des Additions',
                'description': 'Réussir 20 additions consécutives',
                'category': 'mastery',
                'difficulty': 'gold',
                'points_reward': 100,
                'star_wars_title': 'Calculateur de la Force',
                'requirements': '{"exercise_type": "addition", "streak": 20}'
            },
            {
                'code': 'speed_demon',
                'name': 'Éclair de Vitesse',
                'description': 'Résoudre un exercice en moins de 5 secondes',
                'category': 'special',
                'difficulty': 'silver',
                'points_reward': 75,
                'star_wars_title': 'Réflexes de Jedi',
                'requirements': '{"max_time": 5}'
            },
            {
                'code': 'perfect_day',
                'name': 'Journée Parfaite',
                'description': 'Réussir tous les exercices d\'une journée',
                'category': 'special',
                'difficulty': 'gold',
                'points_reward': 150,
                'star_wars_title': 'Harmonie avec la Force',
                'requirements': '{"daily_perfect": true}'
            }
        ]
        
        for badge in initial_badges:
            cursor.execute("""
                INSERT INTO achievements 
                (code, name, description, category, difficulty, points_reward, 
                 star_wars_title, requirements, is_active)
                VALUES (%(code)s, %(name)s, %(description)s, %(category)s, 
                       %(difficulty)s, %(points_reward)s, %(star_wars_title)s, 
                       %(requirements)s, TRUE)
                ON CONFLICT (code) DO NOTHING;
            """, badge)
        
        conn.commit()
        print(f"✅ {len(initial_badges)} badges initiaux insérés")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur insertion badges: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_badges_tables()
    insert_initial_badges()
    print("🎖️ Système de badges prêt !") 