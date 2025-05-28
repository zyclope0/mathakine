#!/usr/bin/env python3
"""
Test simple du système de badges - Test direct du service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import get_db
from app.services.badge_service import BadgeService
from app.models.user import User
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from sqlalchemy.orm import Session
from datetime import datetime, timezone

def test_badge_service():
    """Test direct du service de badges"""
    
    print("🧪 Test direct du service de badges")
    print("=" * 50)
    
    # Obtenir une session de base de données
    db = next(get_db())
    
    try:
        # 1. Trouver l'utilisateur ObiWan
        print("1. Recherche de l'utilisateur ObiWan...")
        user = db.query(User).filter(User.username == "ObiWan").first()
        if not user:
            print("❌ Utilisateur ObiWan non trouvé")
            return
        
        print(f"✅ Utilisateur trouvé: {user.username} (ID: {user.id})")
        
        # 2. Créer le service de badges
        badge_service = BadgeService(db)
        
        # 3. Vérifier l'état actuel des badges
        print("\n2. État actuel des badges...")
        user_badges = badge_service.get_user_badges(user.id)
        earned_badges = user_badges.get('earned_badges', [])
        user_stats = user_badges.get('user_stats', {})
        
        print(f"   Badges obtenus: {len(earned_badges)}")
        print(f"   Points: {user_stats.get('total_points', 0)}")
        print(f"   Niveau: {user_stats.get('current_level', 1)}")
        print(f"   Rang Jedi: {user_stats.get('jedi_rank', 'youngling')}")
        
        # 4. Compter les tentatives actuelles
        print("\n3. Statistiques des tentatives...")
        total_attempts = db.query(Attempt).filter(Attempt.user_id == user.id).count()
        correct_attempts = db.query(Attempt).filter(
            Attempt.user_id == user.id,
            Attempt.is_correct == True
        ).count()
        
        print(f"   Total tentatives: {total_attempts}")
        print(f"   Tentatives correctes: {correct_attempts}")
        
        # 5. Simuler une nouvelle tentative
        print("\n4. Simulation d'une nouvelle tentative...")
        attempt_data = {
            'is_correct': True,
            'time_spent': 3.2,
            'exercise_type': 'addition'
        }
        
        # Vérifier les badges avant
        badges_before = len(earned_badges)
        
        # Déclencher la vérification des badges
        new_badges = badge_service.check_and_award_badges(user.id, attempt_data)
        
        print(f"✅ Vérification terminée")
        print(f"   Nouveaux badges: {len(new_badges)}")
        
        if new_badges:
            print("🎖️ Badges obtenus:")
            for badge in new_badges:
                print(f"   - {badge['name']} (+{badge['points_reward']} pts)")
                print(f"     {badge['description']}")
        
        # 6. Vérifier l'état après
        print("\n5. État après vérification...")
        user_badges_after = badge_service.get_user_badges(user.id)
        earned_badges_after = user_badges_after.get('earned_badges', [])
        user_stats_after = user_badges_after.get('user_stats', {})
        
        print(f"   Badges obtenus: {len(earned_badges_after)}")
        print(f"   Points: {user_stats_after.get('total_points', 0)}")
        print(f"   Niveau: {user_stats_after.get('current_level', 1)}")
        print(f"   Rang Jedi: {user_stats_after.get('jedi_rank', 'youngling')}")
        
        # 7. Afficher tous les badges obtenus
        if earned_badges_after:
            print("\n6. Tous les badges obtenus:")
            for badge in earned_badges_after:
                print(f"   - {badge['name']} ({badge['star_wars_title']})")
                print(f"     {badge['description']}")
                print(f"     Difficulté: {badge['difficulty']} | Points: {badge['points_reward']}")
                earned_at = badge.get('earned_at', 'N/A')
                if earned_at != 'N/A':
                    try:
                        dt = datetime.fromisoformat(earned_at.replace('Z', '+00:00'))
                        earned_at = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                print(f"     Obtenu le: {earned_at}")
                print()
        
        # 8. Afficher les badges disponibles
        print("7. Badges disponibles:")
        available_badges = badge_service.get_available_badges()
        print(f"   Total: {len(available_badges)} badges")
        
        for badge in available_badges:
            is_earned = any(eb['id'] == badge['id'] for eb in earned_badges_after)
            status = "✅ OBTENU" if is_earned else "🔒 À débloquer"
            print(f"   {status} - {badge['name']} ({badge['difficulty']})")
            print(f"     {badge['description']}")
            print(f"     Récompense: {badge['points_reward']} points")
            print()
        
        print("=" * 50)
        print("🎯 Test terminé avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_badge_service() 