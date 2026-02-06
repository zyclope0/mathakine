#!/usr/bin/env python3
"""
Script de nettoyage des données de test de la base de données.
ATTENTION : Ce script supprime définitivement les données de test.
IMPORTANT : Les exercices sont considérés comme valides et ne sont PAS supprimés.
"""

import argparse
import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.base import engine
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def cleanup_test_data(dry_run=True, force=False):
    """
    Nettoie toutes les données de test de la base de données.
    IMPORTANT : Les exercices sont préservés car ils sont valides.
    
    Args:
        dry_run (bool): Si True, affiche seulement ce qui serait supprimé
        force (bool): Si True, force la suppression sans confirmation
    """
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("=== NETTOYAGE DES DONNÉES DE TEST ===\n")
        print("ℹ️  NOTE: Les exercices sont préservés car ils sont valides\n")
        
        if dry_run:
            print("🔍 MODE DRY-RUN : Aucune suppression ne sera effectuée\n")
        elif not force:
            print("⚠️  MODE SUPPRESSION RÉELLE")
            confirmation = input("Êtes-vous sûr de vouloir supprimer toutes les données de test ? (oui/non): ")
            if confirmation.lower() not in ['oui', 'yes', 'y']:
                print("❌ Opération annulée.")
                return
            print()
        
        # 1. Identifier les utilisateurs de test
        test_patterns = [
            'test_%', 'new_test_%', 'duplicate_%', '%_test_%', 
            'user_stats_%', 'rec_cascade_%', 'attempt_error_%',
            'nonexistent_%', 'record_%', 'starlette_%',
            'cascade_%', 'creator_%', 'malformed_%', 'disable_%',
            'flow_%', 'invalid_%', 'jedi_%'
        ]
        
        all_test_user_ids = set()
        for pattern in test_patterns:
            result = db.execute(text(f"SELECT id FROM users WHERE username LIKE '{pattern}' OR email LIKE '{pattern}'"))
            user_ids = [row[0] for row in result.fetchall()]
            all_test_user_ids.update(user_ids)
        
        print(f"🔍 Utilisateurs de test identifiés: {len(all_test_user_ids)}")
        
        if all_test_user_ids:
            # Afficher quelques exemples
            result = db.execute(text(f"SELECT username, email FROM users WHERE id IN ({','.join(map(str, list(all_test_user_ids)[:10]))})"))
            examples = result.fetchall()
            for username, email in examples:
                print(f"  - {username} ({email})")
            if len(all_test_user_ids) > 10:
                print(f"  ... et {len(all_test_user_ids) - 10} autres")
        
        # 2. Identifier SEULEMENT les défis logiques de test (pas les exercices)
        result = db.execute(text("""
            SELECT id, title FROM logic_challenges 
            WHERE title LIKE '%test%' 
            OR title LIKE '%Test%'
            OR title LIKE '%TEST%'
        """))
        test_challenges = result.fetchall()
        
        # Identifier aussi les défis logiques créés par des utilisateurs de test
        test_challenges_by_creator = []
        if all_test_user_ids:
            user_ids_str = ','.join(map(str, all_test_user_ids))
            result = db.execute(text(f"""
                SELECT id, title FROM logic_challenges 
                WHERE creator_id IN ({user_ids_str})
            """))
            test_challenges_by_creator = result.fetchall()
        
        # Combiner les deux listes et éliminer les doublons
        all_test_challenges = list(set(test_challenges + test_challenges_by_creator))
        
        print(f"\n🔍 Défis logiques de test identifiés: {len(all_test_challenges)}")
        for ch_id, title in all_test_challenges:
            print(f"  - ID {ch_id}: {title}")
        
        # Utiliser all_test_challenges au lieu de test_challenges dans le reste du code
        test_challenges = all_test_challenges
        
        # 3. Compter les données liées aux utilisateurs de test
        test_attempts = 0
        test_recommendations = 0
        test_progress = 0
        test_logic_attempts = 0
        
        if all_test_user_ids:
            user_ids_str = ','.join(map(str, all_test_user_ids))
            
            result = db.execute(text(f"SELECT COUNT(*) FROM attempts WHERE user_id IN ({user_ids_str})"))
            test_attempts = result.scalar()
            
            result = db.execute(text(f"SELECT COUNT(*) FROM recommendations WHERE user_id IN ({user_ids_str})"))
            test_recommendations = result.scalar()
            
            result = db.execute(text(f"SELECT COUNT(*) FROM progress WHERE user_id IN ({user_ids_str})"))
            test_progress = result.scalar()
            
            result = db.execute(text(f"SELECT COUNT(*) FROM logic_challenge_attempts WHERE user_id IN ({user_ids_str})"))
            test_logic_attempts = result.scalar()
            
            print(f"\n🔍 Données liées aux utilisateurs de test:")
            print(f"  - Tentatives: {test_attempts}")
            print(f"  - Tentatives de défis logiques: {test_logic_attempts}")
            print(f"  - Recommandations: {test_recommendations}")
            print(f"  - Progression: {test_progress}")
        
        # 4. Calculer l'impact (SANS les exercices)
        total_items = len(all_test_user_ids) + len(test_challenges)
        if all_test_user_ids:
            total_items += test_attempts + test_recommendations + test_progress + test_logic_attempts
        
        print(f"\n📊 RÉSUMÉ:")
        print(f"  - Utilisateurs de test: {len(all_test_user_ids)}")
        print(f"  - Défis logiques de test: {len(test_challenges)}")
        print(f"  - Données liées: {test_attempts + test_recommendations + test_progress + test_logic_attempts}")
        print(f"  - Total d'éléments à supprimer: {total_items}")
        print(f"  ✅ Exercices préservés (valides)")
        
        if dry_run:
            print(f"\n✅ DRY-RUN terminé. Utilisez --execute pour effectuer la suppression réelle.")
            return
        
        # 5. Effectuer les suppressions (ordre important pour les contraintes FK)
        print(f"\n🧹 DÉBUT DU NETTOYAGE...")
        
        deleted_count = 0
        
        # Supprimer les données liées aux utilisateurs de test en premier
        if all_test_user_ids:
            user_ids_str = ','.join(map(str, all_test_user_ids))
            
            # Tentatives de défis logiques liées aux utilisateurs de test (NOUVEAU)
            result = db.execute(text(f"DELETE FROM logic_challenge_attempts WHERE user_id IN ({user_ids_str})"))
            deleted_count += result.rowcount
            print(f"  ✅ Supprimé {result.rowcount} tentatives de défis logiques (utilisateurs)")
            
            # Tentatives
            result = db.execute(text(f"DELETE FROM attempts WHERE user_id IN ({user_ids_str})"))
            deleted_count += result.rowcount
            print(f"  ✅ Supprimé {result.rowcount} tentatives")
            
            # Recommandations
            result = db.execute(text(f"DELETE FROM recommendations WHERE user_id IN ({user_ids_str})"))
            deleted_count += result.rowcount
            print(f"  ✅ Supprimé {result.rowcount} recommandations")
            
            # Progression
            result = db.execute(text(f"DELETE FROM progress WHERE user_id IN ({user_ids_str})"))
            deleted_count += result.rowcount
            print(f"  ✅ Supprimé {result.rowcount} entrées de progression")
        
        # Supprimer les défis logiques de test
        if test_challenges:
            challenge_ids = [str(ch[0]) for ch in test_challenges]
            challenge_ids_str = ','.join(challenge_ids)
            
            # Tentatives de défis logiques
            result = db.execute(text(f"DELETE FROM logic_challenge_attempts WHERE challenge_id IN ({challenge_ids_str})"))
            deleted_count += result.rowcount
            print(f"  ✅ Supprimé {result.rowcount} tentatives de défis logiques")
            
            # Défis logiques
            result = db.execute(text(f"DELETE FROM logic_challenges WHERE id IN ({challenge_ids_str})"))
            deleted_count += result.rowcount
            print(f"  ✅ Supprimé {result.rowcount} défis logiques")
        
        # Supprimer les utilisateurs de test (en dernier)
        if all_test_user_ids:
            user_ids_str = ','.join(map(str, all_test_user_ids))
            result = db.execute(text(f"DELETE FROM users WHERE id IN ({user_ids_str})"))
            deleted_count += result.rowcount
            print(f"  ✅ Supprimé {result.rowcount} utilisateurs")
        
        # Commit toutes les suppressions
        db.commit()
        
        print(f"\n🎉 NETTOYAGE TERMINÉ!")
        print(f"  - Total d'éléments supprimés: {deleted_count}")
        
        # Vérification finale
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE username LIKE '%test%'"))
        remaining_users = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM logic_challenges WHERE title LIKE '%test%'"))
        remaining_challenges = result.scalar()
        
        result = db.execute(text("SELECT COUNT(*) FROM exercises"))
        total_exercises = result.scalar()
        
        print(f"\n📊 VÉRIFICATION FINALE:")
        print(f"  - Utilisateurs de test restants: {remaining_users}")
        print(f"  - Défis logiques de test restants: {remaining_challenges}")
        print(f"  - Exercices préservés: {total_exercises} ✅")
        
        if remaining_users == 0 and remaining_challenges == 0:
            print(f"  ✅ Base de données parfaitement nettoyée (exercices préservés)!")
        else:
            print(f"  ⚠️  Quelques éléments n'ont pas pu être supprimés (contraintes FK?)")
        
    except Exception as e:
        print(f"❌ Erreur pendant le nettoyage: {e}")
        db.rollback()
        logger.error(f"Erreur pendant le nettoyage: {e}")
        raise
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Nettoie les données de test de la base de données (préserve les exercices)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Mode dry-run (par défaut) - affiche seulement ce qui serait supprimé")
    parser.add_argument("--force", action="store_true",
                       help="Force la suppression réelle sans confirmation")
    parser.add_argument("--execute", action="store_true",
                       help="Exécute la suppression réelle (désactive dry-run)")
    
    args = parser.parse_args()
    
    # Si --execute est spécifié, désactiver dry-run
    if args.execute:
        args.dry_run = False
    
    try:
        cleanup_test_data(dry_run=args.dry_run, force=args.force)
    except KeyboardInterrupt:
        print("\n❌ Opération interrompue par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 