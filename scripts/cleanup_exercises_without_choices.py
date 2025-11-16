"""
Script pour nettoyer les exercices sans choix valides dans la base de données.

Ce script identifie et supprime les exercices qui n'ont pas de choix multiples valides,
car ils ne sont pas compatibles avec la nouvelle interface utilisateur.
"""
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au path Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.exercise import Exercise
from loguru import logger

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Construire depuis les variables individuelles si DATABASE_URL n'est pas défini
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "mathakine")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

logger.info(f"Connexion à la base de données: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}")

# Créer l'engine et la session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def check_exercise_choices(exercise: Exercise) -> bool:
    """
    Vérifie si un exercice a des choix valides.
    
    Returns:
        True si l'exercice a des choix valides (liste non vide), False sinon
    """
    if exercise.choices is None:
        return False
    
    # Si c'est une string, essayer de la parser en JSON
    if isinstance(exercise.choices, str):
        try:
            import json
            parsed = json.loads(exercise.choices)
            if isinstance(parsed, list) and len(parsed) > 0:
                return True
            return False
        except (json.JSONDecodeError, TypeError):
            return False
    
    # Si c'est une liste
    if isinstance(exercise.choices, list):
        return len(exercise.choices) > 0
    
    return False


def cleanup_exercises_without_choices(dry_run: bool = True):
    """
    Nettoie les exercices sans choix valides.
    
    Args:
        dry_run: Si True, affiche seulement les exercices qui seraient supprimés sans les supprimer
    """
    db = SessionLocal()
    
    try:
        # Récupérer tous les exercices
        all_exercises = db.query(Exercise).all()
        
        logger.info(f"Total d'exercices dans la base de données: {len(all_exercises)}")
        
        # Identifier les exercices sans choix valides
        exercises_without_choices = []
        exercises_with_choices = []
        
        for exercise in all_exercises:
            if check_exercise_choices(exercise):
                exercises_with_choices.append(exercise)
            else:
                exercises_without_choices.append(exercise)
        
        logger.info(f"✅ Exercices avec choix valides: {len(exercises_with_choices)}")
        logger.info(f"❌ Exercices sans choix valides: {len(exercises_without_choices)}")
        
        if len(exercises_without_choices) == 0:
            logger.info("🎉 Aucun exercice à nettoyer !")
            return
        
        # Afficher les détails des exercices à supprimer
        logger.info("\n" + "="*80)
        logger.info("EXERCICES SANS CHOIX VALIDES (à supprimer):")
        logger.info("="*80)
        
        for exercise in exercises_without_choices:
            logger.info(
                f"  ID: {exercise.id:5d} | "
                f"Type: {exercise.exercise_type.value:15s} | "
                f"Difficulté: {exercise.difficulty.value:10s} | "
                f"Titre: {exercise.title[:40]:40s} | "
                f"Choices: {exercise.choices}"
            )
        
        if dry_run:
            logger.info("\n" + "="*80)
            logger.info("🔍 MODE DRY-RUN : Aucune suppression effectuée")
            logger.info("Pour supprimer ces exercices, relancez le script avec --execute")
            logger.info("="*80)
            return
        
        # Supprimer les exercices sans choix valides
        logger.info("\n" + "="*80)
        logger.info("🗑️  SUPPRESSION DES EXERCICES SANS CHOIX VALIDES...")
        logger.info("="*80)
        
        deleted_count = 0
        for exercise in exercises_without_choices:
            try:
                exercise_id = exercise.id
                exercise_title = exercise.title
                db.delete(exercise)
                deleted_count += 1
                logger.info(f"  ✅ Supprimé: ID {exercise_id} - {exercise_title}")
            except Exception as e:
                logger.error(f"  ❌ Erreur lors de la suppression de l'exercice {exercise.id}: {e}")
        
        # Commit les changements
        db.commit()
        
        logger.info("\n" + "="*80)
        logger.info(f"🎉 NETTOYAGE TERMINÉ : {deleted_count} exercice(s) supprimé(s)")
        logger.info(f"📊 Exercices restants: {len(exercises_with_choices)}")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Nettoie les exercices sans choix valides dans la base de données"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Exécute réellement la suppression (par défaut, mode dry-run)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirme automatiquement la suppression (bypass la confirmation interactive)"
    )
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        logger.info("🔍 MODE DRY-RUN activé (aucune modification)")
    else:
        logger.warning("⚠️  MODE EXÉCUTION : Les exercices seront réellement supprimés !")
        if not args.yes:
            try:
                response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ")
                if response.lower() not in ['oui', 'yes', 'o', 'y']:
                    logger.info("Opération annulée.")
                    sys.exit(0)
            except (EOFError, KeyboardInterrupt):
                logger.error("Opération annulée (pas de confirmation interactive disponible)")
                logger.info("Utilisez --yes pour bypasser la confirmation")
                sys.exit(1)
    
    cleanup_exercises_without_choices(dry_run=dry_run)

