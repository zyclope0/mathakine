#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test pour le système de badges
"""

from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.auth_service import create_user
from app.models.user import UserRole

def create_test_user():
    """Créer un utilisateur de test"""
    print("👤 Création d'un utilisateur de test pour les badges...")
    
    db = EnhancedServerAdapter.get_db_session()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        from app.services.auth_service import get_user_by_username
        existing_user = get_user_by_username(db, "TestBadges")
        
        if existing_user:
            print(f"✅ L'utilisateur TestBadges existe déjà")
            print(f"   - ID: {existing_user.id}")
            print(f"   - Email: {existing_user.email}")
            print(f"   - Rang Jedi: {getattr(existing_user, 'jedi_rank', 'youngling')}")
            print(f"   - Points: {getattr(existing_user, 'total_points', 0)}")
            return existing_user
        
        # Créer l'utilisateur directement avec SQLAlchemy
        from app.models.user import User
        from app.core.security import get_password_hash
        from datetime import datetime, timezone
        
        new_user = User(
            username="TestBadges",
            email="test.badges@mathakine.com",
            hashed_password=get_password_hash("Test123!"),
            full_name="Utilisateur Test Badges",
            role=UserRole.PADAWAN,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            # Colonnes de gamification avec valeurs par défaut
            total_points=0,
            current_level=1,
            experience_points=0,
            jedi_rank='youngling'
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Utilisateur TestBadges créé avec succès")
        print(f"   - ID: {new_user.id}")
        print(f"   - Email: {new_user.email}")
        print(f"   - Mot de passe: Test123!")
        return new_user
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        EnhancedServerAdapter.close_db_session(db)

def test_user_badges():
    """Tester les badges pour l'utilisateur créé"""
    print("\n🎖️ Test du système de badges...")
    
    db = EnhancedServerAdapter.get_db_session()
    
    try:
        from app.services.auth_service import get_user_by_username
        from app.services.badge_service import BadgeService
        
        # Récupérer l'utilisateur
        user = get_user_by_username(db, "TestBadges")
        if not user:
            print("❌ Utilisateur de test non trouvé")
            return
        
        # Initialiser le service de badges
        badge_service = BadgeService(db)
        
        # Vérifier les badges disponibles
        available_badges = badge_service.get_available_badges()
        print(f"📋 {len(available_badges)} badges disponibles:")
        for badge in available_badges:
            print(f"   - {badge['name']}: {badge['description']} ({badge['points_reward']} pts)")
        
        # Vérifier les badges de l'utilisateur
        user_badges = badge_service.get_user_badges(user.id)
        earned_badges = user_badges.get('earned_badges', [])
        user_stats = user_badges.get('user_stats', {})
        
        print(f"\n👤 Statistiques de {user.username}:")
        print(f"   - Badges obtenus: {len(earned_badges)}")
        print(f"   - Points Force: {user_stats.get('total_points', 0)}")
        print(f"   - Niveau: {user_stats.get('current_level', 1)}")
        print(f"   - Rang Jedi: {user_stats.get('jedi_rank', 'youngling')}")
        
        # Forcer la vérification des badges
        print("\n🔍 Vérification forcée des badges...")
        new_badges = badge_service.check_and_award_badges(user.id)
        
        if new_badges:
            print(f"🎉 {len(new_badges)} nouveaux badges obtenus!")
            for badge in new_badges:
                print(f"   - {badge['name']}: {badge['star_wars_title']} ({badge['points_reward']} pts)")
        else:
            print("   - Aucun nouveau badge (conditions non remplies)")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        EnhancedServerAdapter.close_db_session(db)

def simulate_exercise_attempts():
    """Simuler quelques tentatives d'exercices pour déclencher des badges"""
    print("\n📝 Simulation de tentatives d'exercices...")
    
    db = EnhancedServerAdapter.get_db_session()
    
    try:
        from app.services.auth_service import get_user_by_username
        from app.services.badge_service import BadgeService
        
        # Récupérer l'utilisateur
        user = get_user_by_username(db, "TestBadges")
        if not user:
            print("❌ Utilisateur de test non trouvé")
            return
        
        # Simuler des tentatives d'exercices
        badge_service = BadgeService(db)
        
        # Créer quelques tentatives fictives dans la base de données
        from app.models.attempt import Attempt
        from app.models.exercise import Exercise
        from datetime import datetime, timezone
        
        # Récupérer un exercice existant
        exercise = db.query(Exercise).first()
        if not exercise:
            print("❌ Aucun exercice trouvé pour les tests")
            return
        
        print(f"📚 Utilisation de l'exercice: {exercise.title}")
        
        # Créer 3 tentatives réussies
        for i in range(3):
            attempt = Attempt(
                user_id=user.id,
                exercise_id=exercise.id,
                user_answer=exercise.correct_answer,
                is_correct=True,
                time_spent=5.0 + i,  # Temps variable
                created_at=datetime.now(timezone.utc)
            )
            db.add(attempt)
        
        db.commit()
        print("✅ 3 tentatives réussies ajoutées")
        
        # Vérifier les badges après les tentatives
        print("\n🎖️ Vérification des badges après les tentatives...")
        new_badges = badge_service.check_and_award_badges(user.id)
        
        if new_badges:
            print(f"🎉 {len(new_badges)} nouveaux badges obtenus!")
            for badge in new_badges:
                print(f"   - {badge['name']}: {badge['star_wars_title']} ({badge['points_reward']} pts)")
        else:
            print("   - Aucun nouveau badge cette fois")
        
        # Afficher les statistiques finales
        user_badges = badge_service.get_user_badges(user.id)
        user_stats = user_badges.get('user_stats', {})
        
        print(f"\n📊 Statistiques finales:")
        print(f"   - Points Force: {user_stats.get('total_points', 0)}")
        print(f"   - Niveau: {user_stats.get('current_level', 1)}")
        print(f"   - Rang Jedi: {user_stats.get('jedi_rank', 'youngling')}")
        print(f"   - Badges obtenus: {len(user_badges.get('earned_badges', []))}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        EnhancedServerAdapter.close_db_session(db)

def main():
    """Fonction principale"""
    print("🚀 Test complet du système de badges Mathakine")
    print("=" * 60)
    
    # Créer l'utilisateur de test
    user = create_test_user()
    if not user:
        print("❌ Impossible de continuer sans utilisateur")
        return
    
    # Tester le système de badges
    test_user_badges()
    
    # Simuler des exercices
    simulate_exercise_attempts()
    
    print("\n" + "=" * 60)
    print("🎯 Test terminé!")
    print(f"\n💡 Utilisateur de test créé:")
    print(f"   - Nom d'utilisateur: TestBadges")
    print(f"   - Mot de passe: Test123!")
    print(f"   - Vous pouvez maintenant tester manuellement sur http://localhost:8000")

if __name__ == "__main__":
    main() 