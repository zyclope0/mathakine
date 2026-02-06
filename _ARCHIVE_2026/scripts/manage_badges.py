"""
Script pour gérer les badges : vérification, nettoyage et peuplement
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from app.db.base import engine, SessionLocal
from app.models.achievement import Achievement, UserAchievement
from app.models.user import User
import json
from datetime import datetime, timezone

# Badges officiels à créer
OFFICIAL_BADGES = [
    {
        'code': 'first_steps',
        'name': 'Premiers Pas',
        'description': 'Réalise ta première tentative d\'exercice',
        'category': 'progression',
        'difficulty': 'bronze',
        'points_reward': 10,
        'star_wars_title': 'Éveil de la Force',
        'requirements': {'attempts_count': 1}
    },
    {
        'code': 'padawan_path',
        'name': 'Voie du Padawan',
        'description': 'Réalise 10 tentatives d\'exercices',
        'category': 'progression',
        'difficulty': 'silver',
        'points_reward': 50,
        'star_wars_title': 'Apprenti Jedi',
        'requirements': {'attempts_count': 10}
    },
    {
        'code': 'knight_trial',
        'name': 'Épreuve du Chevalier',
        'description': 'Réalise 50 tentatives d\'exercices',
        'category': 'progression',
        'difficulty': 'gold',
        'points_reward': 100,
        'star_wars_title': 'Chevalier Jedi',
        'requirements': {'attempts_count': 50}
    },
    {
        'code': 'addition_master',
        'name': 'Maître des Additions',
        'description': 'Réussis 20 additions consécutives',
        'category': 'mastery',
        'difficulty': 'gold',
        'points_reward': 100,
        'star_wars_title': 'Maître de l\'Harmonie',
        'requirements': {'exercise_type': 'addition', 'consecutive_correct': 20}
    },
    {
        'code': 'speed_demon',
        'name': 'Éclair de Vitesse',
        'description': 'Résous un exercice en moins de 5 secondes',
        'category': 'special',
        'difficulty': 'silver',
        'points_reward': 75,
        'star_wars_title': 'Réflexes de Jedi',
        'requirements': {'max_time': 5}
    },
    {
        'code': 'perfect_day',
        'name': 'Journée Parfaite',
        'description': 'Réussis tous les exercices d\'une journée',
        'category': 'special',
        'difficulty': 'gold',
        'points_reward': 150,
        'star_wars_title': 'Harmonie avec la Force',
        'requirements': {'daily_perfect': True}
    },
    # Badges de Progression supplémentaires
    {
        'code': 'jedi_master',
        'name': 'Maître Jedi',
        'description': 'Réalise 100 tentatives d\'exercices',
        'category': 'progression',
        'difficulty': 'gold',
        'points_reward': 200,
        'star_wars_title': 'Maître Jedi',
        'requirements': {'attempts_count': 100}
    },
    {
        'code': 'grand_master',
        'name': 'Grand Maître',
        'description': 'Réalise 200 tentatives d\'exercices',
        'category': 'progression',
        'difficulty': 'legendary',
        'points_reward': 300,
        'star_wars_title': 'Grand Maître Jedi',
        'requirements': {'attempts_count': 200}
    },
    # Badges de Maîtrise pour autres types
    {
        'code': 'subtraction_master',
        'name': 'Maître des Soustractions',
        'description': 'Réussis 15 soustractions consécutives',
        'category': 'mastery',
        'difficulty': 'gold',
        'points_reward': 100,
        'star_wars_title': 'Maître de la Précision',
        'requirements': {'exercise_type': 'soustraction', 'consecutive_correct': 15}
    },
    {
        'code': 'multiplication_master',
        'name': 'Maître des Multiplications',
        'description': 'Réussis 15 multiplications consécutives',
        'category': 'mastery',
        'difficulty': 'gold',
        'points_reward': 100,
        'star_wars_title': 'Maître de la Multiplication',
        'requirements': {'exercise_type': 'multiplication', 'consecutive_correct': 15}
    },
    {
        'code': 'division_master',
        'name': 'Maître des Divisions',
        'description': 'Réussis 15 divisions consécutives',
        'category': 'mastery',
        'difficulty': 'gold',
        'points_reward': 100,
        'star_wars_title': 'Maître de la Division',
        'requirements': {'exercise_type': 'division', 'consecutive_correct': 15}
    },
    # Badges de Performance
    {
        'code': 'expert',
        'name': 'Expert',
        'description': 'Atteins un taux de réussite de 80% sur 50 tentatives',
        'category': 'performance',
        'difficulty': 'gold',
        'points_reward': 150,
        'star_wars_title': 'Expert Jedi',
        'requirements': {'success_rate': 80, 'min_attempts': 50}
    },
    {
        'code': 'perfectionist',
        'name': 'Perfectionniste',
        'description': 'Atteins un taux de réussite de 95% sur 30 tentatives',
        'category': 'performance',
        'difficulty': 'legendary',
        'points_reward': 200,
        'star_wars_title': 'Perfection Jedi',
        'requirements': {'success_rate': 95, 'min_attempts': 30}
    },
    # Badges de Régularité
    {
        'code': 'perfect_week',
        'name': 'Semaine Parfaite',
        'description': 'Fais des exercices 7 jours consécutifs',
        'category': 'regularity',
        'difficulty': 'silver',
        'points_reward': 100,
        'star_wars_title': 'Détermination Jedi',
        'requirements': {'consecutive_days': 7}
    },
    {
        'code': 'perfect_month',
        'name': 'Mois Parfait',
        'description': 'Fais des exercices 30 jours consécutifs',
        'category': 'regularity',
        'difficulty': 'gold',
        'points_reward': 250,
        'star_wars_title': 'Dévotion Jedi',
        'requirements': {'consecutive_days': 30}
    },
    # Badges de Découverte
    {
        'code': 'explorer',
        'name': 'Explorateur',
        'description': 'Essaie tous les types d\'exercices disponibles',
        'category': 'discovery',
        'difficulty': 'silver',
        'points_reward': 100,
        'star_wars_title': 'Explorateur de la Force',
        'requirements': {'all_types': True}
    },
    {
        'code': 'versatile',
        'name': 'Polyvalent',
        'description': 'Réussis au moins 5 exercices de chaque type',
        'category': 'discovery',
        'difficulty': 'gold',
        'points_reward': 150,
        'star_wars_title': 'Maître Polyvalent',
        'requirements': {'min_per_type': 5}
    }
]


def check_badges_status(db):
    """Vérifier l'état actuel des badges"""
    print("\n" + "="*60)
    print("ETAT ACTUEL DES BADGES")
    print("="*60)
    
    # Compter les badges
    total_badges = db.query(Achievement).count()
    active_badges = db.query(Achievement).filter(Achievement.is_active == True).count()
    inactive_badges = total_badges - active_badges
    
    print(f"\n[OK] Badges totaux : {total_badges}")
    print(f"   - Actifs : {active_badges}")
    print(f"   - Inactifs : {inactive_badges}")
    
    # Lister les badges existants
    badges = db.query(Achievement).all()
    print(f"\nListe des badges existants :")
    for badge in badges:
        status = "[OK]" if badge.is_active else "[INACTIF]"
        print(f"   {status} [{badge.code}] {badge.name} ({badge.difficulty}) - {badge.points_reward} pts")
    
    # Compter les badges obtenus par utilisateur
    print(f"\nBadges obtenus par utilisateur :")
    user_badges = db.execute(text("""
        SELECT u.id, u.username, COUNT(ua.id) as badge_count
        FROM users u
        LEFT JOIN user_achievements ua ON u.id = ua.user_id
        GROUP BY u.id, u.username
        ORDER BY badge_count DESC
    """)).fetchall()
    
    for user_id, username, badge_count in user_badges:
        print(f"   - {username} (ID: {user_id}) : {badge_count} badge(s)")
    
    return badges, user_badges


def clean_test_badges(db):
    """Nettoyer les badges de test"""
    print("\n" + "="*60)
    print("NETTOYAGE DES BADGES DE TEST")
    print("="*60)
    
    # Identifier les badges de test (codes qui ne sont pas dans la liste officielle)
    official_codes = {badge['code'] for badge in OFFICIAL_BADGES}
    all_badges = db.query(Achievement).all()
    
    test_badges = []
    for badge in all_badges:
        if badge.code not in official_codes:
            test_badges.append(badge)
    
    if not test_badges:
        print("\n[OK] Aucun badge de test trouve")
        return 0
    
    print(f"\n[WARN] {len(test_badges)} badge(s) de test trouve(s) :")
    for badge in test_badges:
        print(f"   - [{badge.code}] {badge.name}")
    
    # Supprimer les badges de test et leurs attributions
    deleted_count = 0
    for badge in test_badges:
        # Supprimer les attributions utilisateur
        user_achievements = db.query(UserAchievement).filter(
            UserAchievement.achievement_id == badge.id
        ).all()
        
        for ua in user_achievements:
            db.delete(ua)
            deleted_count += 1
        
        # Supprimer le badge
        db.delete(badge)
        print(f"   [SUPPRIME] : [{badge.code}] {badge.name}")
    
    db.commit()
    print(f"\n[OK] {len(test_badges)} badge(s) de test supprime(s)")
    print(f"[OK] {deleted_count} attribution(s) utilisateur supprimee(s)")
    
    return len(test_badges)


def clean_test_user_badges(db, test_usernames=None):
    """Nettoyer les badges obtenus par les utilisateurs de test"""
    if test_usernames is None:
        test_usernames = ['test_user', 'ObiWan', 'test']
    
    print("\n" + "="*60)
    print("NETTOYAGE DES BADGES UTILISATEURS DE TEST")
    print("="*60)
    
    # Trouver les utilisateurs de test
    test_users = db.query(User).filter(
        User.username.in_(test_usernames)
    ).all()
    
    if not test_users:
        print("\n[OK] Aucun utilisateur de test trouve")
        return 0
    
    deleted_count = 0
    for user in test_users:
        user_badges = db.query(UserAchievement).filter(
            UserAchievement.user_id == user.id
        ).all()
        
        if user_badges:
            print(f"\nUtilisateur {user.username} (ID: {user.id}) :")
            for ua in user_badges:
                badge = db.query(Achievement).filter(Achievement.id == ua.achievement_id).first()
                if badge:
                    print(f"   - Suppression badge : [{badge.code}] {badge.name}")
                    db.delete(ua)
                    deleted_count += 1
            
            # Réinitialiser les stats de gamification
            db.execute(text("""
                UPDATE users 
                SET total_points = 0,
                    current_level = 1,
                    experience_points = 0,
                    jedi_rank = 'youngling'
                WHERE id = :user_id
            """), {"user_id": user.id})
            print(f"   [OK] Stats de gamification reinitialisees")
    
    db.commit()
    print(f"\n[OK] {deleted_count} attribution(s) badge(s) supprimee(s) pour les utilisateurs de test")
    
    return deleted_count


def populate_badges(db):
    """Peupler la base de données avec les badges officiels"""
    print("\n" + "="*60)
    print("PEUPLEMENT DES BADGES OFFICIELS")
    print("="*60)
    
    created_count = 0
    updated_count = 0
    
    for badge_data in OFFICIAL_BADGES:
        # Vérifier si le badge existe déjà
        existing = db.query(Achievement).filter(
            Achievement.code == badge_data['code']
        ).first()
        
        if existing:
            # Mettre à jour le badge existant
            existing.name = badge_data['name']
            existing.description = badge_data['description']
            existing.category = badge_data['category']
            existing.difficulty = badge_data['difficulty']
            existing.points_reward = badge_data['points_reward']
            existing.star_wars_title = badge_data['star_wars_title']
            existing.requirements = json.dumps(badge_data['requirements'])
            existing.is_active = True
            updated_count += 1
            print(f"   [MAJ] Mis a jour : [{badge_data['code']}] {badge_data['name']}")
        else:
            # Créer le nouveau badge
            new_badge = Achievement(
                code=badge_data['code'],
                name=badge_data['name'],
                description=badge_data['description'],
                category=badge_data['category'],
                difficulty=badge_data['difficulty'],
                points_reward=badge_data['points_reward'],
                star_wars_title=badge_data['star_wars_title'],
                requirements=json.dumps(badge_data['requirements']),
                is_active=True
            )
            db.add(new_badge)
            created_count += 1
            print(f"   [OK] Cree : [{badge_data['code']}] {badge_data['name']}")
    
    db.commit()
    print(f"\n[OK] {created_count} badge(s) cree(s)")
    print(f"[OK] {updated_count} badge(s) mis a jour")
    
    return created_count + updated_count


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("GESTION DES BADGES MATHAKINE")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # 1. Vérifier l'état actuel
        badges, user_badges = check_badges_status(db)
        
        # 2. Nettoyer les badges de test
        test_badges_deleted = clean_test_badges(db)
        
        # 3. Nettoyer les badges obtenus par les utilisateurs de test
        test_user_badges_deleted = clean_test_user_badges(db)
        
        # 4. Peupler avec les badges officiels
        badges_populated = populate_badges(db)
        
        # 5. État final
        print("\n" + "="*60)
        print("ETAT FINAL")
        print("="*60)
        check_badges_status(db)
        
        print("\n" + "="*60)
        print("OPERATIONS TERMINEES")
        print("="*60)
        print(f"   - Badges de test supprimes : {test_badges_deleted}")
        print(f"   - Attributions test supprimees : {test_user_badges_deleted}")
        print(f"   - Badges officiels crees/mis a jour : {badges_populated}")
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERREUR] Erreur : {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    main()

