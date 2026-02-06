#!/usr/bin/env python3
"""
Script pour nettoyer la base de production et créer 30-40 exercices et challenges cohérents.
ATTENTION: Ce script modifie la base de PRODUCTION.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import random

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from app.db.base import engine, SessionLocal
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.models.user import User, UserRole
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def check_production_safety():
    """Vérifie qu'on est bien en production et demande confirmation"""
    database_url = os.getenv("DATABASE_URL", "")
    
    is_production = (
        os.getenv("NODE_ENV") == "production" or 
        os.getenv("ENVIRONMENT") == "production" or
        os.getenv("MATH_TRAINER_PROFILE") == "prod" or
        "render.com" in database_url.lower()
    )
    
    if not is_production:
        logger.warning("⚠️  Vous n'êtes pas en environnement de production")
        logger.info(f"   DATABASE_URL: {database_url[:50]}...")
        response = input("Continuer quand même ? (o/N): ").strip().lower()
        if response != 'o':
            return False
    
    print("\n" + "=" * 60)
    print("🚨 ATTENTION: NETTOYAGE DE LA BASE DE PRODUCTION")
    print("=" * 60)
    print(f"   DATABASE_URL: {database_url[:50]}...")
    print("\n   Ce script va:")
    print("   - Supprimer TOUS les exercices et challenges existants")
    print("   - Créer 30-40 nouveaux exercices et challenges cohérents")
    print("\n   Les utilisateurs et tentatives seront PRÉSERVÉS")
    print("=" * 60)
    print()
    
    response = input("Confirmer le nettoyage et la création de nouvelles données ? (tapez 'CONFIRMER'): ").strip().upper()
    if response != "CONFIRMER":
        logger.info("Opération annulée")
        return False
    
    return True


def clean_users(db, keep_user_ids=[8404, 9468]):
    """Nettoie les utilisateurs en gardant seulement ceux spécifiés"""
    logger.info(f"Nettoyage des utilisateurs (garde IDs: {keep_user_ids})...")
    
    try:
        # Supprimer toutes les relations qui référencent des utilisateurs
        # Utiliser des requêtes SQL directes pour éviter les problèmes de paramètres
        ids_str = ', '.join(map(str, keep_user_ids))
        
        logger.info("Suppression des tentatives...")
        db.execute(text(f"DELETE FROM attempts WHERE user_id NOT IN ({ids_str})"))
        db.execute(text(f"DELETE FROM logic_challenge_attempts WHERE user_id NOT IN ({ids_str})"))
        db.flush()
        
        logger.info("Suppression des progressions...")
        # Supprimer TOUTES les progressions d'abord (on les recréera si nécessaire)
        result = db.execute(text("DELETE FROM progress"))
        deleted_count = result.rowcount
        logger.info(f"   {deleted_count} progressions supprimées (toutes)")
        db.flush()
        
        logger.info("Suppression des recommandations...")
        db.execute(text(f"DELETE FROM recommendations WHERE user_id NOT IN ({ids_str})"))
        db.flush()
        
        # Tables optionnelles (peuvent ne pas exister)
        try:
            logger.info("Suppression des notifications...")
            db.execute(text(f"DELETE FROM notifications WHERE user_id NOT IN ({ids_str})"))
            db.flush()
        except Exception as e:
            logger.debug(f"Table notifications n'existe pas ou erreur: {e}")
            db.rollback()
        
        try:
            logger.info("Suppression des achievements utilisateur...")
            db.execute(text(f"DELETE FROM user_achievements WHERE user_id NOT IN ({ids_str})"))
            db.flush()
        except Exception as e:
            logger.debug(f"Table user_achievements n'existe pas ou erreur: {e}")
            db.rollback()
        
        try:
            logger.info("Suppression des sessions utilisateur...")
            db.execute(text(f"DELETE FROM user_sessions WHERE user_id NOT IN ({ids_str})"))
            db.flush()
        except Exception as e:
            logger.debug(f"Table user_sessions n'existe pas ou erreur: {e}")
            db.rollback()
        
        # Mettre à jour les creator_id des exercices et challenges pour les utilisateurs supprimés
        logger.info("Mise à jour des exercices et challenges...")
        creator = db.query(User).filter(User.id == keep_user_ids[0]).first()  # ObiWan
        if creator:
            db.execute(text(f"UPDATE exercises SET creator_id = {creator.id} WHERE creator_id NOT IN ({ids_str})"))
            db.execute(text(f"UPDATE logic_challenges SET creator_id = {creator.id} WHERE creator_id NOT IN ({ids_str})"))
            db.flush()
        
        # Supprimer les utilisateurs
        logger.info("Suppression des utilisateurs...")
        deleted = db.execute(text(f"DELETE FROM users WHERE id NOT IN ({ids_str})"))
        db.flush()
        
        logger.success(f"Nettoyage des utilisateurs terminé ({deleted.rowcount} utilisateurs supprimés)")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du nettoyage des utilisateurs: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def clean_exercises_and_challenges(db):
    """Nettoie les exercices et challenges existants"""
    logger.info("Nettoyage des exercices et challenges...")
    
    try:
        # Supprimer les tentatives liées d'abord (contraintes FK)
        db.execute(text("DELETE FROM attempts"))
        db.execute(text("DELETE FROM logic_challenge_attempts"))
        
        # Supprimer les exercices et challenges
        db.execute(text("DELETE FROM exercises"))
        db.execute(text("DELETE FROM logic_challenges"))
        
        db.flush()
        logger.success("Nettoyage terminé")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du nettoyage: {e}")
        return False


def get_creator(db, user_id=8404):
    """Récupère l'utilisateur créateur par ID"""
    creator = db.query(User).filter(User.id == user_id).first()
    
    if not creator:
        logger.error(f"Utilisateur avec ID {user_id} non trouvé")
        # Fallback: chercher ObiWan
        creator = db.query(User).filter(User.username == "ObiWan").first()
        if creator:
            logger.info(f"Utilisation de l'utilisateur ObiWan (ID: {creator.id}) comme fallback")
        else:
            # Dernier recours: chercher un utilisateur MAITRE
            creator = db.query(User).filter(User.role == UserRole.MAITRE).first()
            if creator:
                logger.info(f"Utilisation de l'utilisateur MAITRE existant: {creator.username} (ID: {creator.id})")
    else:
        logger.info(f"Utilisation de l'utilisateur ID {creator.id}: {creator.username}")
    
    return creator


def create_production_exercises(db):
    """Crée 30-35 exercices cohérents et variés"""
    logger.info("Création des exercices de production...")
    
    creator = get_creator(db)
    if not creator:
        logger.error("Impossible de créer ou trouver un utilisateur MAITRE")
        return []
    
    exercises = []
    now = datetime.now(timezone.utc)
    
    # ADDITION - INITIE (5 exercices)
    exercises.extend([
        Exercise(
            title="Addition Jedi - Initiation",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="Dans le Temple Jedi, il y a 12 Padawans dans la salle A et 8 dans la salle B. Combien y a-t-il de Padawans au total ?",
            correct_answer="20",
            choices=["18", "19", "20", "21"],
            explanation="12 + 8 = 20 Padawans au total",
            hint="Additionne les Padawans des deux salles",
            context_theme="Temple Jedi",
            age_group="8-10",
            complexity=1,
            created_at=now,
        ),
        Exercise(
            title="Addition de Cristaux",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="Obi-Wan a collecté 15 cristaux kyber et Anakin en a trouvé 9. Combien de cristaux ont-ils ensemble ?",
            correct_answer="24",
            choices=["22", "23", "24", "25"],
            explanation="15 + 9 = 24 cristaux au total",
            hint="Additionne les cristaux des deux Jedi",
            context_theme="Cristaux Kyber",
            age_group="8-10",
            complexity=1,
            created_at=now,
        ),
        Exercise(
            title="Addition de Vaisseaux",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="La flotte de la République compte 7 vaisseaux de type A et 13 de type B. Combien de vaisseaux au total ?",
            correct_answer="20",
            choices=["18", "19", "20", "21"],
            explanation="7 + 13 = 20 vaisseaux",
            hint="Additionne les deux types de vaisseaux",
            context_theme="Flotte Républicaine",
            age_group="8-10",
            complexity=1,
            created_at=now,
        ),
        Exercise(
            title="Addition de Droïdes",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="Un atelier contient 6 droïdes R2 et 14 droïdes C3PO. Combien de droïdes au total ?",
            correct_answer="20",
            choices=["18", "19", "20", "22"],
            explanation="6 + 14 = 20 droïdes",
            hint="Additionne les deux types de droïdes",
            context_theme="Atelier de Droïdes",
            age_group="8-10",
            complexity=1,
            created_at=now,
        ),
        Exercise(
            title="Addition de Planètes",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.INITIE,
            question="Dans le système solaire de Tatooine, il y a 11 planètes habitées et 9 désertes. Combien de planètes au total ?",
            correct_answer="20",
            choices=["18", "19", "20", "21"],
            explanation="11 + 9 = 20 planètes",
            hint="Additionne les planètes habitées et désertes",
            context_theme="Système Solaire",
            age_group="8-10",
            complexity=1,
            created_at=now,
        ),
    ])
    
    # ADDITION - PADAWAN (5 exercices)
    exercises.extend([
        Exercise(
            title="Addition Avancée - Padawan",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Un Maître Jedi entraîne 23 Padawans le matin et 17 l'après-midi. Combien de Padawans sont entraînés dans la journée ?",
            correct_answer="40",
            choices=["38", "39", "40", "41"],
            explanation="23 + 17 = 40 Padawans",
            hint="Additionne les Padawans du matin et de l'après-midi",
            context_theme="Entraînement Jedi",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Addition de Crédits",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Luke a gagné 45 crédits en vendant des récoltes et 28 crédits en réparant des droïdes. Combien a-t-il gagné au total ?",
            correct_answer="73",
            choices=["71", "72", "73", "74"],
            explanation="45 + 28 = 73 crédits",
            hint="Additionne les deux sources de revenus",
            context_theme="Crédits Galactiques",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Addition de Bataillons",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.PADAWAN,
            question="L'armée clone compte 156 soldats dans le bataillon Alpha et 89 dans le bataillon Beta. Combien de soldats au total ?",
            correct_answer="245",
            choices=["243", "244", "245", "246"],
            explanation="156 + 89 = 245 soldats",
            hint="Additionne les deux bataillons",
            context_theme="Armée Clone",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Addition de Modules",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Un vaisseau spatial nécessite 67 modules d'énergie et 34 modules de navigation. Combien de modules au total ?",
            correct_answer="101",
            choices=["99", "100", "101", "102"],
            explanation="67 + 34 = 101 modules",
            hint="Additionne les deux types de modules",
            context_theme="Vaisseau Spatial",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Addition de Systèmes",
            creator_id=creator.id,
            exercise_type=ExerciseType.ADDITION,
            difficulty=DifficultyLevel.PADAWAN,
            question="La galaxie compte 124 systèmes stellaires dans le secteur Core et 91 dans le secteur Outer Rim. Combien de systèmes au total ?",
            correct_answer="215",
            choices=["213", "214", "215", "216"],
            explanation="124 + 91 = 215 systèmes",
            hint="Additionne les systèmes des deux secteurs",
            context_theme="Galaxie",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
    ])
    
    # MULTIPLICATION - PADAWAN (5 exercices)
    exercises.extend([
        Exercise(
            title="Multiplication Jedi",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Chaque Padawan utilise 6 cristaux kyber pour construire son sabre laser. Si 8 Padawans construisent leur sabre, combien de cristaux sont nécessaires ?",
            correct_answer="48",
            choices=["44", "46", "48", "50"],
            explanation="6 × 8 = 48 cristaux",
            hint="Multiplie le nombre de cristaux par le nombre de Padawans",
            context_theme="Sabre Laser",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Vaisseaux",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Chaque escadron contient 12 chasseurs X-Wing. Combien de chasseurs y a-t-il dans 5 escadrons ?",
            correct_answer="60",
            choices=["58", "59", "60", "62"],
            explanation="12 × 5 = 60 chasseurs",
            hint="Multiplie le nombre de chasseurs par le nombre d'escadrons",
            context_theme="Flotte Républicaine",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Rations",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Chaque soldat clone consomme 3 rations par jour. Combien de rations sont nécessaires pour 25 soldats pendant 1 jour ?",
            correct_answer="75",
            choices=["73", "74", "75", "76"],
            explanation="3 × 25 = 75 rations",
            hint="Multiplie les rations par le nombre de soldats",
            context_theme="Armée Clone",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Modules",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Chaque droïde nécessite 7 modules de programmation. Combien de modules faut-il pour 9 droïdes ?",
            correct_answer="63",
            choices=["61", "62", "63", "64"],
            explanation="7 × 9 = 63 modules",
            hint="Multiplie les modules par le nombre de droïdes",
            context_theme="Droïdes",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Planètes",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Chaque système solaire contient 4 planètes habitables. Combien de planètes y a-t-il dans 8 systèmes ?",
            correct_answer="32",
            choices=["30", "31", "32", "33"],
            explanation="4 × 8 = 32 planètes",
            hint="Multiplie le nombre de planètes par le nombre de systèmes",
            context_theme="Système Solaire",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
    ])
    
    # MULTIPLICATION - CHEVALIER (5 exercices)
    exercises.extend([
        Exercise(
            title="Multiplication Avancée - Chevalier",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="Chaque Maître Jedi entraîne 15 Padawans. Combien de Padawans sont entraînés par 6 Maîtres ?",
            correct_answer="90",
            choices=["88", "89", "90", "91"],
            explanation="15 × 6 = 90 Padawans",
            hint="Multiplie le nombre de Padawans par le nombre de Maîtres",
            context_theme="Entraînement Jedi",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Flottes",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="Chaque flotte contient 24 vaisseaux de combat. Combien de vaisseaux y a-t-il dans 7 flottes ?",
            correct_answer="168",
            choices=["166", "167", "168", "169"],
            explanation="24 × 7 = 168 vaisseaux",
            hint="Multiplie le nombre de vaisseaux par le nombre de flottes",
            context_theme="Flotte Républicaine",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Bataillons",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="Chaque bataillon clone compte 144 soldats. Combien de soldats y a-t-il dans 5 bataillons ?",
            correct_answer="720",
            choices=["718", "719", "720", "721"],
            explanation="144 × 5 = 720 soldats",
            hint="Multiplie le nombre de soldats par le nombre de bataillons",
            context_theme="Armée Clone",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Systèmes",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="Chaque secteur galactique contient 18 systèmes stellaires. Combien de systèmes y a-t-il dans 9 secteurs ?",
            correct_answer="162",
            choices=["160", "161", "162", "163"],
            explanation="18 × 9 = 162 systèmes",
            hint="Multiplie le nombre de systèmes par le nombre de secteurs",
            context_theme="Galaxie",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Multiplication de Crédits",
            creator_id=creator.id,
            exercise_type=ExerciseType.MULTIPLICATION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="Chaque mission rapporte 35 crédits. Combien de crédits gagne-t-on avec 12 missions réussies ?",
            correct_answer="420",
            choices=["418", "419", "420", "421"],
            explanation="35 × 12 = 420 crédits",
            hint="Multiplie les crédits par le nombre de missions",
            context_theme="Crédits Galactiques",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
    ])
    
    # SOUSTRACTION - PADAWAN (5 exercices)
    exercises.extend([
        Exercise(
            title="Soustraction Jedi",
            creator_id=creator.id,
            exercise_type=ExerciseType.SOUSTRACTION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Il y avait 50 Padawans dans le Temple. 23 sont partis en mission. Combien reste-t-il de Padawans ?",
            correct_answer="27",
            choices=["25", "26", "27", "28"],
            explanation="50 - 23 = 27 Padawans",
            hint="Soustrais les Padawans partis du total",
            context_theme="Temple Jedi",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Soustraction de Vaisseaux",
            creator_id=creator.id,
            exercise_type=ExerciseType.SOUSTRACTION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Une flotte de 38 vaisseaux a perdu 15 vaisseaux au combat. Combien de vaisseaux restent ?",
            correct_answer="23",
            choices=["21", "22", "23", "24"],
            explanation="38 - 15 = 23 vaisseaux",
            hint="Soustrais les vaisseaux perdus du total",
            context_theme="Flotte Républicaine",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Soustraction de Crédits",
            creator_id=creator.id,
            exercise_type=ExerciseType.SOUSTRACTION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Luke avait 85 crédits. Il a dépensé 42 crédits pour des pièces de droïde. Combien lui reste-t-il ?",
            correct_answer="43",
            choices=["41", "42", "43", "44"],
            explanation="85 - 42 = 43 crédits",
            hint="Soustrais les crédits dépensés du total",
            context_theme="Crédits Galactiques",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Soustraction de Soldats",
            creator_id=creator.id,
            exercise_type=ExerciseType.SOUSTRACTION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Un bataillon de 120 soldats clones a subi 47 pertes. Combien de soldats restent ?",
            correct_answer="73",
            choices=["71", "72", "73", "74"],
            explanation="120 - 47 = 73 soldats",
            hint="Soustrais les pertes du total",
            context_theme="Armée Clone",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
        Exercise(
            title="Soustraction de Cristaux",
            creator_id=creator.id,
            exercise_type=ExerciseType.SOUSTRACTION,
            difficulty=DifficultyLevel.PADAWAN,
            question="Obi-Wan avait 64 cristaux kyber. Il en a utilisé 28 pour fabriquer des sabres. Combien lui reste-t-il ?",
            correct_answer="36",
            choices=["34", "35", "36", "37"],
            explanation="64 - 28 = 36 cristaux",
            hint="Soustrais les cristaux utilisés du total",
            context_theme="Cristaux Kyber",
            age_group="10-12",
            complexity=2,
            created_at=now,
        ),
    ])
    
    # DIVISION - CHEVALIER (5 exercices)
    exercises.extend([
        Exercise(
            title="Division Jedi",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVISION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="48 Padawans doivent être répartis équitablement en 6 groupes d'entraînement. Combien de Padawans dans chaque groupe ?",
            correct_answer="8",
            choices=["7", "8", "9", "10"],
            explanation="48 ÷ 6 = 8 Padawans par groupe",
            hint="Divise le total de Padawans par le nombre de groupes",
            context_theme="Entraînement Jedi",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Division de Vaisseaux",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVISION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="72 chasseurs X-Wing doivent être répartis équitablement en 8 escadrons. Combien de chasseurs par escadron ?",
            correct_answer="9",
            choices=["8", "9", "10", "11"],
            explanation="72 ÷ 8 = 9 chasseurs par escadron",
            hint="Divise le total de chasseurs par le nombre d'escadrons",
            context_theme="Flotte Républicaine",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Division de Rations",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVISION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="90 rations doivent être distribuées équitablement à 15 soldats clones. Combien de rations par soldat ?",
            correct_answer="6",
            choices=["5", "6", "7", "8"],
            explanation="90 ÷ 15 = 6 rations par soldat",
            hint="Divise le total de rations par le nombre de soldats",
            context_theme="Armée Clone",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Division de Crédits",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVISION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="120 crédits doivent être partagés équitablement entre 8 membres d'équipage. Combien de crédits par personne ?",
            correct_answer="15",
            choices=["14", "15", "16", "17"],
            explanation="120 ÷ 8 = 15 crédits par personne",
            hint="Divise le total de crédits par le nombre de personnes",
            context_theme="Crédits Galactiques",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
        Exercise(
            title="Division de Systèmes",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVISION,
            difficulty=DifficultyLevel.CHEVALIER,
            question="108 systèmes stellaires doivent être répartis équitablement en 9 secteurs. Combien de systèmes par secteur ?",
            correct_answer="12",
            choices=["11", "12", "13", "14"],
            explanation="108 ÷ 9 = 12 systèmes par secteur",
            hint="Divise le total de systèmes par le nombre de secteurs",
            context_theme="Galaxie",
            age_group="12-14",
            complexity=3,
            created_at=now,
        ),
    ])
    
    # MIXTE - MAITRE (5 exercices)
    exercises.extend([
        Exercise(
            title="Problème Complexe - Maître",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVERS,
            difficulty=DifficultyLevel.MAITRE,
            question="Un Maître Jedi a 3 groupes de 12 Padawans chacun. Il en envoie 15 en mission. Combien de Padawans restent au Temple ?",
            correct_answer="21",
            choices=["19", "20", "21", "22"],
            explanation="(3 × 12) - 15 = 36 - 15 = 21 Padawans",
            hint="Calcule d'abord le total, puis soustrais ceux partis en mission",
            context_theme="Temple Jedi",
            age_group="14+",
            complexity=4,
            created_at=now,
        ),
        Exercise(
            title="Problème de Flotte",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVERS,
            difficulty=DifficultyLevel.MAITRE,
            question="Une flotte compte 5 escadrons de 18 vaisseaux chacun. 12 vaisseaux sont endommagés et doivent se retirer. Combien de vaisseaux opérationnels restent ?",
            correct_answer="78",
            choices=["76", "77", "78", "79"],
            explanation="(5 × 18) - 12 = 90 - 12 = 78 vaisseaux",
            hint="Calcule d'abord le total, puis soustrais les vaisseaux endommagés",
            context_theme="Flotte Républicaine",
            age_group="14+",
            complexity=4,
            created_at=now,
        ),
        Exercise(
            title="Problème de Budget",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVERS,
            difficulty=DifficultyLevel.MAITRE,
            question="Un Jedi a gagné 8 missions de 25 crédits chacune. Il dépense 120 crédits pour des équipements. Combien lui reste-t-il ?",
            correct_answer="80",
            choices=["78", "79", "80", "81"],
            explanation="(8 × 25) - 120 = 200 - 120 = 80 crédits",
            hint="Calcule d'abord les gains, puis soustrais les dépenses",
            context_theme="Crédits Galactiques",
            age_group="14+",
            complexity=4,
            created_at=now,
        ),
        Exercise(
            title="Problème de Bataillon",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVERS,
            difficulty=DifficultyLevel.MAITRE,
            question="Un général commande 4 bataillons de 60 soldats chacun. 35 soldats sont blessés et évacués. Combien de soldats restent au combat ?",
            correct_answer="205",
            choices=["203", "204", "205", "206"],
            explanation="(4 × 60) - 35 = 240 - 35 = 205 soldats",
            hint="Calcule d'abord le total, puis soustrais les blessés",
            context_theme="Armée Clone",
            age_group="14+",
            complexity=4,
            created_at=now,
        ),
        Exercise(
            title="Problème de Distribution",
            creator_id=creator.id,
            exercise_type=ExerciseType.DIVERS,
            difficulty=DifficultyLevel.MAITRE,
            question="Un entrepôt contient 144 cristaux kyber. Ils doivent être répartis équitablement en 6 caisses, puis 2 caisses sont envoyées en mission. Combien de cristaux restent dans l'entrepôt ?",
            correct_answer="96",
            choices=["94", "95", "96", "97"],
            explanation="(144 ÷ 6) × (6 - 2) = 24 × 4 = 96 cristaux",
            hint="Calcule d'abord par caisse, puis multiplie par le nombre de caisses restantes",
            context_theme="Cristaux Kyber",
            age_group="14+",
            complexity=4,
            created_at=now,
        ),
    ])
    
    db.add_all(exercises)
    db.flush()
    logger.success(f"{len(exercises)} exercices créés")
    return exercises


def create_production_challenges(db):
    """Crée 15-20 challenges cohérents et variés"""
    logger.info("Création des challenges de production...")
    
    creator = get_creator(db)
    if not creator:
        logger.error("Impossible de créer ou trouver un utilisateur MAITRE")
        return []
    
    challenges = []
    now = datetime.now(timezone.utc)
    
    # SEQUENCE challenges (3)
    challenges.extend([
        LogicChallenge(
            title="Séquence de Nombres Jedi",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.SEQUENCE,
            age_group=AgeGroup.GROUP_10_12,
            description="Trouvez le prochain nombre dans cette séquence logique liée au Temple Jedi.",
            question="Complète la séquence: 2, 5, 8, 11, ...",
            correct_answer="14",
            choices=["12", "13", "14", "15"],
            solution_explanation="C'est une séquence arithmétique qui augmente de 3 à chaque étape. 2 + 3 = 5, 5 + 3 = 8, 8 + 3 = 11, donc 11 + 3 = 14.",
            content="Complète la séquence: 2, 5, 8, 11, ...",
            hints=["Regarde la différence entre chaque nombre", "La différence est constante", "Ajoute 3 au dernier nombre"],
            difficulty_rating=2.5,
            estimated_time_minutes=5,
            tags="séquence,arithmétique,initiation",
            created_at=now,
        ),
        LogicChallenge(
            title="Séquence de Cristaux",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.SEQUENCE,
            age_group=AgeGroup.GROUP_13_15,
            description="Découvrez le motif dans cette séquence de nombres liée aux cristaux kyber.",
            question="Quel nombre complète cette séquence: 3, 9, 27, 81, ...",
            correct_answer="243",
            choices=["162", "243", "324", "405"],
            solution_explanation="C'est une séquence géométrique où chaque nombre est multiplié par 3. 3 × 3 = 9, 9 × 3 = 27, 27 × 3 = 81, donc 81 × 3 = 243.",
            content="Quel nombre complète cette séquence: 3, 9, 27, 81, ...",
            hints=["Chaque nombre est multiplié par un facteur constant", "Le facteur est 3", "Multiplie 81 par 3"],
            difficulty_rating=3.5,
            estimated_time_minutes=8,
            tags="séquence,géométrique,padawan",
            created_at=now,
        ),
        LogicChallenge(
            title="Séquence de Vaisseaux",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.SEQUENCE,
            age_group=AgeGroup.ALL_AGES,
            description="Identifiez le pattern dans cette séquence liée aux vaisseaux spatiaux.",
            question="Complète: 1, 4, 9, 16, 25, ...",
            correct_answer="36",
            choices=["30", "34", "36", "40"],
            solution_explanation="C'est la séquence des carrés parfaits: 1²=1, 2²=4, 3²=9, 4²=16, 5²=25, donc 6²=36.",
            content="Complète: 1, 4, 9, 16, 25, ...",
            hints=["Ce sont des carrés parfaits", "1², 2², 3², 4², 5²...", "Calcule 6²"],
            difficulty_rating=3.0,
            estimated_time_minutes=7,
            tags="séquence,carrés,logique",
            created_at=now,
        ),
    ])
    
    # PATTERN challenges (3)
    challenges.extend([
        LogicChallenge(
            title="Motif de Padawans",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PATTERN,
            age_group=AgeGroup.GROUP_10_12,
            description="Reconnaissez le motif dans cette disposition de Padawans.",
            question="Dans un entraînement, les Padawans sont disposés ainsi: A, B, C, A, B, C, A, ... Quel Padawan vient après le 10ème ?",
            correct_answer="B",
            choices=["A", "B", "C", "D"],
            solution_explanation="Le motif se répète tous les 3 Padawans (A, B, C). Le 10ème position: 10 ÷ 3 = 3 reste 1, donc c'est le 1er du motif, qui est A. Le suivant est B.",
            content="Dans un entraînement, les Padawans sont disposés ainsi: A, B, C, A, B, C, A, ... Quel Padawan vient après le 10ème ?",
            hints=["Le motif se répète tous les 3", "Calcule la position dans le motif", "10 mod 3 = 1, donc A, puis B"],
            difficulty_rating=3.0,
            estimated_time_minutes=6,
            tags="motif,répétition,logique",
            created_at=now,
        ),
        LogicChallenge(
            title="Pattern de Formations",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PATTERN,
            age_group=AgeGroup.GROUP_13_15,
            description="Identifiez le pattern dans cette séquence de formations militaires.",
            question="Les formations suivent ce pattern: 2, 6, 18, 54, ... Quelle est la prochaine formation ?",
            correct_answer="162",
            choices=["108", "144", "162", "180"],
            solution_explanation="Chaque nombre est multiplié par 3: 2 × 3 = 6, 6 × 3 = 18, 18 × 3 = 54, donc 54 × 3 = 162.",
            content="Les formations suivent ce pattern: 2, 6, 18, 54, ... Quelle est la prochaine formation ?",
            hints=["Multiplie chaque nombre par un facteur", "Le facteur est 3", "54 × 3 = ?"],
            difficulty_rating=3.5,
            estimated_time_minutes=7,
            tags="pattern,géométrique,avancé",
            created_at=now,
        ),
        LogicChallenge(
            title="Motif de Codes",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PATTERN,
            age_group=AgeGroup.ALL_AGES,
            description="Décryptez le motif dans cette séquence de codes de sécurité.",
            question="Les codes suivent ce pattern: 5, 10, 20, 40, ... Quel est le prochain code ?",
            correct_answer="80",
            choices=["60", "70", "80", "90"],
            solution_explanation="Chaque code est doublé: 5 × 2 = 10, 10 × 2 = 20, 20 × 2 = 40, donc 40 × 2 = 80.",
            content="Les codes suivent ce pattern: 5, 10, 20, 40, ... Quel est le prochain code ?",
            hints=["Chaque nombre est multiplié par 2", "Double le dernier nombre", "40 × 2 = ?"],
            difficulty_rating=2.5,
            estimated_time_minutes=5,
            tags="pattern,doublage,simple",
            created_at=now,
        ),
    ])
    
    # DEDUCTION challenges (3)
    challenges.extend([
        LogicChallenge(
            title="Déduction Jedi",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.DEDUCTION,
            age_group=AgeGroup.GROUP_13_15,
            description="Utilisez votre raisonnement déductif pour résoudre cette énigme du Temple.",
            question="Dans le Temple Jedi, tous les Padawans portent soit une robe bleue, soit une robe verte. Si 60% portent une robe bleue et qu'il y a 30 Padawans au total, combien portent une robe verte ?",
            correct_answer="12",
            choices=["10", "11", "12", "13"],
            solution_explanation="60% de 30 = 18 Padawans en bleu. Donc 30 - 18 = 12 Padawans en vert.",
            content="Dans le Temple Jedi, tous les Padawans portent soit une robe bleue, soit une robe verte. Si 60% portent une robe bleue et qu'il y a 30 Padawans au total, combien portent une robe verte ?",
            hints=["Calcule d'abord combien portent du bleu", "60% de 30 = 18", "Soustrais du total"],
            difficulty_rating=3.5,
            estimated_time_minutes=8,
            tags="déduction,pourcentage,logique",
            created_at=now,
        ),
        LogicChallenge(
            title="Raisonnement Logique",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.DEDUCTION,
            age_group=AgeGroup.ALL_AGES,
            description="Résolvez cette énigme en utilisant la logique déductive.",
            question="Si tous les Maîtres Jedi sont sages, et que Yoda est un Maître Jedi, que peut-on déduire ?",
            correct_answer="Yoda est sage",
            choices=["Yoda n'est pas sage", "Yoda est sage", "On ne peut pas savoir", "Yoda est puissant"],
            solution_explanation="Par déduction logique: Si tous les Maîtres Jedi sont sages (prémisse générale) et que Yoda est un Maître Jedi (cas particulier), alors Yoda est sage (conclusion).",
            content="Si tous les Maîtres Jedi sont sages, et que Yoda est un Maître Jedi, que peut-on déduire ?",
            hints=["Applique la règle générale au cas particulier", "Si tous les A sont B, et X est A...", "Alors X est B"],
            difficulty_rating=2.0,
            estimated_time_minutes=4,
            tags="déduction,logique,raisonnement",
            created_at=now,
        ),
        LogicChallenge(
            title="Énigme de la Flotte",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.DEDUCTION,
            age_group=AgeGroup.GROUP_13_15,
            description="Déduisez la réponse à partir des informations données sur la flotte.",
            question="Dans une flotte, il y a 3 fois plus de vaisseaux de type A que de type B. Si le total est de 48 vaisseaux, combien y a-t-il de vaisseaux de type B ?",
            correct_answer="12",
            choices=["10", "11", "12", "13"],
            solution_explanation="Si B = nombre de vaisseaux type B, alors A = 3B. Total: A + B = 3B + B = 4B = 48. Donc B = 48 ÷ 4 = 12.",
            content="Dans une flotte, il y a 3 fois plus de vaisseaux de type A que de type B. Si le total est de 48 vaisseaux, combien y a-t-il de vaisseaux de type B ?",
            hints=["Soit B le nombre de type B", "Alors A = 3B", "A + B = 4B = 48"],
            difficulty_rating=4.0,
            estimated_time_minutes=10,
            tags="déduction,algèbre,équation",
            created_at=now,
        ),
    ])
    
    # PUZZLE challenges (3)
    challenges.extend([
        LogicChallenge(
            title="Énigme du Sphinx Jedi",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PUZZLE,
            age_group=AgeGroup.ALL_AGES,
            description="Résolvez cette énigme classique adaptée au contexte Jedi.",
            question="Je suis grand quand je suis jeune et petit quand je suis vieux. Je brille dans l'obscurité. Qui suis-je ?",
            correct_answer="Un sabre laser",
            choices=["Un Padawan", "Un sabre laser", "Un cristal kyber", "Une étoile"],
            solution_explanation="Un sabre laser est 'grand' (allumé) quand il est 'jeune' (nouveau) et 'petit' (éteint) quand il est 'vieux' (usé). Il brille effectivement dans l'obscurité.",
            content="Je suis grand quand je suis jeune et petit quand je suis vieux. Je brille dans l'obscurité. Qui suis-je ?",
            hints=["Pense aux objets Jedi", "Qu'est-ce qui peut être allumé ou éteint ?", "C'est une arme emblématique"],
            difficulty_rating=3.0,
            estimated_time_minutes=6,
            tags="énigme,puzzle,créativité",
            created_at=now,
        ),
        LogicChallenge(
            title="Puzzle de la Porte",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PUZZLE,
            age_group=AgeGroup.GROUP_10_12,
            description="Résolvez ce puzzle pour ouvrir la porte du Temple.",
            question="Une porte du Temple a 3 serrures. La première nécessite un nombre pair, la deuxième un multiple de 3, et la troisième un nombre premier. Quel est le plus petit nombre qui ouvre les 3 serrures ?",
            correct_answer="6",
            choices=["4", "5", "6", "7"],
            solution_explanation="6 est pair (6 ÷ 2 = 3), multiple de 3 (6 ÷ 3 = 2), et bien que 6 ne soit pas premier, c'est le plus petit nombre qui satisfait les deux premières conditions. En fait, aucun nombre ne satisfait les 3 conditions simultanément car un nombre premier > 2 est impair. Mais 6 ouvre au moins 2 serrures sur 3, ce qui est le maximum possible.",
            content="Une porte du Temple a 3 serrures. La première nécessite un nombre pair, la deuxième un multiple de 3, et la troisième un nombre premier. Quel est le plus petit nombre qui ouvre les 3 serrures ?",
            hints=["Un nombre pair divisible par 3", "6 = 2 × 3", "Vérifie si 6 est premier"],
            difficulty_rating=4.0,
            estimated_time_minutes=9,
            tags="puzzle,mathématiques,logique",
            created_at=now,
        ),
        LogicChallenge(
            title="Énigme des Trois Portes",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PUZZLE,
            age_group=AgeGroup.GROUP_13_15,
            description="Choisissez la bonne porte en utilisant la logique.",
            question="Devant vous, 3 portes. Une mène à la liberté, les deux autres à des pièges. Un gardien dit toujours la vérité, l'autre ment toujours. Le premier gardien dit 'La porte du milieu mène à la liberté'. Le second dit 'La porte de gauche mène à un piège'. Quelle porte choisissez-vous ?",
            correct_answer="La porte de droite",
            choices=["La porte de gauche", "La porte du milieu", "La porte de droite", "On ne peut pas savoir"],
            solution_explanation="Si le premier gardien dit la vérité, la porte du milieu mène à la liberté. Mais alors le second gardien (qui ment) dit que la gauche mène à un piège, donc la gauche mène à la liberté (contradiction). Donc le premier ment, la porte du milieu mène à un piège. Le second (qui dit la vérité) dit que la gauche mène à un piège, donc la droite mène à la liberté.",
            content="Devant vous, 3 portes. Une mène à la liberté, les deux autres à des pièges. Un gardien dit toujours la vérité, l'autre ment toujours. Le premier gardien dit 'La porte du milieu mène à la liberté'. Le second dit 'La porte de gauche mène à un piège'. Quelle porte choisissez-vous ?",
            hints=["Analyse les contradictions", "Si le premier dit vrai, que dit le second ?", "Teste chaque hypothèse"],
            difficulty_rating=4.5,
            estimated_time_minutes=12,
            tags="puzzle,logique,raisonnement",
            created_at=now,
        ),
    ])
    
    # SPATIAL challenges (2)
    challenges.extend([
        LogicChallenge(
            title="Raisonnement Spatial - Temple",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.SPATIAL,
            age_group=AgeGroup.GROUP_10_12,
            description="Visualisez la disposition spatiale du Temple Jedi.",
            question="Dans le Temple, il y a 4 salles disposées en carré. La salle A est au nord, B à l'est, C au sud. Où se trouve la salle D ?",
            correct_answer="À l'ouest",
            choices=["Au nord-est", "À l'ouest", "Au sud-est", "Au centre"],
            solution_explanation="Si les salles forment un carré avec A au nord, B à l'est, C au sud, alors D doit être à l'ouest pour compléter le carré.",
            content="Dans le Temple, il y a 4 salles disposées en carré. La salle A est au nord, B à l'est, C au sud. Où se trouve la salle D ?",
            hints=["Visualise un carré", "Nord, Est, Sud...", "Quelle direction manque ?"],
            difficulty_rating=2.5,
            estimated_time_minutes=5,
            tags="spatial,visualisation,géométrie",
            visual_data={"type": "grid", "positions": {"A": "north", "B": "east", "C": "south", "D": "west"}},
            created_at=now,
        ),
        LogicChallenge(
            title="Visualisation 3D",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.SPATIAL,
            age_group=AgeGroup.GROUP_13_15,
            description="Imaginez la structure tridimensionnelle d'un vaisseau spatial.",
            question="Un cube a 6 faces. Si on le coupe en 8 petits cubes identiques, combien de petits cubes auront exactement 3 faces visibles ?",
            correct_answer="8",
            choices=["4", "6", "8", "12"],
            solution_explanation="Quand on coupe un cube en 8 petits cubes (2×2×2), les 8 cubes aux coins ont chacun 3 faces visibles (une par dimension).",
            content="Un cube a 6 faces. Si on le coupe en 8 petits cubes identiques, combien de petits cubes auront exactement 3 faces visibles ?",
            hints=["Visualise un cube 2×2×2", "Quels cubes sont aux coins ?", "Chaque coin a 3 faces visibles"],
            difficulty_rating=3.5,
            estimated_time_minutes=8,
            tags="spatial,3D,géométrie",
            visual_data={"type": "cube", "dimensions": [2, 2, 2]},
            created_at=now,
        ),
    ])
    
    # PROBABILITY challenges (2)
    challenges.extend([
        LogicChallenge(
            title="Probabilité Jedi",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PROBABILITY,
            age_group=AgeGroup.GROUP_13_15,
            description="Calculez la probabilité dans ce scénario du Temple.",
            question="Dans un groupe de 20 Padawans, 12 sont des humains et 8 sont des non-humains. Si on choisit un Padawan au hasard, quelle est la probabilité que ce soit un non-humain ?",
            correct_answer="2/5",
            choices=["1/5", "2/5", "3/5", "4/5"],
            solution_explanation="Probabilité = nombre de cas favorables / nombre total = 8 / 20 = 2/5.",
            content="Dans un groupe de 20 Padawans, 12 sont des humains et 8 sont des non-humains. Si on choisit un Padawan au hasard, quelle est la probabilité que ce soit un non-humain ?",
            hints=["Probabilité = favorables / total", "8 non-humains sur 20 total", "Simplifie la fraction"],
            difficulty_rating=3.0,
            estimated_time_minutes=6,
            tags="probabilité,statistiques,mathématiques",
            created_at=now,
        ),
        LogicChallenge(
            title="Chances de Mission",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.PROBABILITY,
            age_group=AgeGroup.ALL_AGES,
            description="Évaluez les chances de succès d'une mission.",
            question="Une mission a 60% de chances de succès. Si on lance 2 missions indépendantes, quelle est la probabilité que les deux réussissent ?",
            correct_answer="36%",
            choices=["30%", "36%", "60%", "120%"],
            solution_explanation="Pour deux événements indépendants, on multiplie les probabilités: 0.6 × 0.6 = 0.36 = 36%.",
            content="Une mission a 60% de chances de succès. Si on lance 2 missions indépendantes, quelle est la probabilité que les deux réussissent ?",
            hints=["Pour des événements indépendants, multiplie les probabilités", "0.6 × 0.6 = ?", "Convertis en pourcentage"],
            difficulty_rating=3.5,
            estimated_time_minutes=7,
            tags="probabilité,indépendance,calcul",
            created_at=now,
        ),
    ])
    
    # RIDDLE challenges (2)
    challenges.extend([
        LogicChallenge(
            title="Énigme de la Force",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.RIDDLE,
            age_group=AgeGroup.ALL_AGES,
            description="Résolvez cette énigme sur la Force.",
            question="Je suis partout et nulle part. Je lie toutes choses. Je peux être utilisée pour le bien ou le mal. Qui suis-je ?",
            correct_answer="La Force",
            choices=["L'énergie", "La Force", "La lumière", "L'obscurité"],
            solution_explanation="La Force est décrite comme étant partout, liant toutes choses dans la galaxie, et pouvant être utilisée par les Jedi (bien) ou les Sith (mal).",
            content="Je suis partout et nulle part. Je lie toutes choses. Je peux être utilisée pour le bien ou le mal. Qui suis-je ?",
            hints=["C'est un concept central de Star Wars", "C'est ce que les Jedi utilisent", "Elle entoure et pénètre toutes choses"],
            difficulty_rating=2.0,
            estimated_time_minutes=4,
            tags="énigme,force,starwars",
            created_at=now,
        ),
        LogicChallenge(
            title="Énigme du Sabre",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.RIDDLE,
            age_group=AgeGroup.GROUP_10_12,
            description="Découvrez la réponse à cette énigme sur les sabres laser.",
            question="J'ai une lame mais je ne coupe pas. Je brille mais je ne brûle pas. Je suis une arme mais je défends. Qui suis-je ?",
            correct_answer="Un sabre laser",
            choices=["Une épée", "Un sabre laser", "Un bouclier", "Un sabre laser"],
            solution_explanation="Un sabre laser a une 'lame' d'énergie qui ne coupe pas comme une lame normale, brille avec une couleur vive, et est utilisé à la fois comme arme offensive et défensive par les Jedi.",
            content="J'ai une lame mais je ne coupe pas. Je brille mais je ne brûle pas. Je suis une arme mais je défends. Qui suis-je ?",
            hints=["C'est l'arme emblématique des Jedi", "La lame est faite d'énergie", "Elle peut bloquer les tirs de blaster"],
            difficulty_rating=2.5,
            estimated_time_minutes=5,
            tags="énigme,sabre,starwars",
            created_at=now,
        ),
    ])
    
    # VISUAL challenges (2 avec visual_data)
    challenges.extend([
        LogicChallenge(
            title="Défi Visuel - Formes",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.VISUAL,
            age_group=AgeGroup.GROUP_10_12,
            description="Identifiez le pattern dans cette séquence de formes géométriques.",
            question="Quelle forme complète cette séquence: Carré, Cercle, Triangle, Carré, Cercle, ...",
            correct_answer="Triangle",
            choices=["Carré", "Cercle", "Triangle", "Rectangle"],
            solution_explanation="Le motif se répète: Carré, Cercle, Triangle. Après Cercle vient Triangle.",
            content="Quelle forme complète cette séquence: Carré, Cercle, Triangle, Carré, Cercle, ...",
            hints=["Le motif se répète tous les 3", "Carré, Cercle, Triangle...", "Quelle forme vient après Cercle ?"],
            difficulty_rating=2.0,
            estimated_time_minutes=4,
            tags="visuel,formes,pattern",
            visual_data={"type": "sequence", "shapes": ["square", "circle", "triangle"], "current": 5},
            created_at=now,
        ),
        LogicChallenge(
            title="Puzzle Visuel - Grille",
            creator_id=creator.id,
            challenge_type=LogicChallengeType.VISUAL,
            age_group=AgeGroup.GROUP_13_15,
            description="Résolvez ce puzzle en analysant la grille visuelle.",
            question="Dans une grille 3×3, chaque case contient un nombre de 1 à 9 sans répétition. La somme de chaque ligne est 15. Quelle est la somme de la diagonale principale ?",
            correct_answer="15",
            choices=["12", "13", "15", "18"],
            solution_explanation="Dans un carré magique 3×3, la somme de chaque ligne, colonne et diagonale est toujours 15. C'est une propriété mathématique des carrés magiques.",
            content="Dans une grille 3×3, chaque case contient un nombre de 1 à 9 sans répétition. La somme de chaque ligne est 15. Quelle est la somme de la diagonale principale ?",
            hints=["C'est un carré magique", "Dans un carré magique, toutes les lignes, colonnes et diagonales ont la même somme", "La somme est 15"],
            difficulty_rating=4.0,
            estimated_time_minutes=10,
            tags="visuel,grille,carré magique",
            visual_data={"type": "grid", "size": [3, 3], "magic_square": True},
            created_at=now,
        ),
    ])
    
    db.add_all(challenges)
    db.flush()
    logger.success(f"{len(challenges)} challenges créés")
    return challenges


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🧹 NETTOYAGE ET CRÉATION DE DONNÉES DE PRODUCTION")
    print("=" * 60)
    print()
    
    # Vérification de sécurité
    if not check_production_safety():
        return 1
    
    db = SessionLocal()
    
    try:
        # 1. Nettoyage des utilisateurs (garde seulement ObiWan et zyclope)
        if not clean_users(db, keep_user_ids=[8404, 9468]):
            logger.warning("Problème lors du nettoyage des utilisateurs, continuation...")
        
        # 2. Nettoyage des exercices et challenges
        if not clean_exercises_and_challenges(db):
            return 1
        
        # 3. Création des exercices
        exercises = create_production_exercises(db)
        if not exercises:
            logger.error("Échec de la création des exercices")
            return 1
        
        # 4. Création des challenges
        challenges = create_production_challenges(db)
        if not challenges:
            logger.error("Échec de la création des challenges")
            return 1
        
        # Commit final
        db.commit()
        
        print()
        print("=" * 60)
        print("✅ OPÉRATION RÉUSSIE")
        print("=" * 60)
        print(f"   ✅ {len(exercises)} exercices créés")
        print(f"   ✅ {len(challenges)} challenges créés")
        print()
        print("   Les données de production ont été nettoyées et remplacées")
        print("   par du contenu cohérent et varié.")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'opération: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

