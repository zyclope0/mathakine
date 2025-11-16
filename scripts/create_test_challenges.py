#!/usr/bin/env python3
"""
Script pour créer des défis logiques de test dans la base de données.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.models.user import User
from app.core.config import settings
from datetime import datetime, timezone
import json
from loguru import logger

def create_test_challenges():
    """Crée des défis logiques de test."""
    # Créer une session de base de données
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Vérifier combien de défis existent déjà
        existing_count = db.query(LogicChallenge).count()
        logger.info(f"Nombre de défis existants : {existing_count}")
        
        if existing_count > 0:
            logger.info("Des défis existent déjà. Voulez-vous quand même en ajouter ? (y/n)")
            response = input().strip().lower()
            if response != 'y':
                logger.info("Création annulée.")
                return
        
        # Récupérer un utilisateur existant ou créer un utilisateur de test
        user = db.query(User).first()
        if not user:
            logger.warning("Aucun utilisateur trouvé. Création d'un utilisateur de test...")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            user = User(
                username="test_creator",
                email="test@example.com",
                hashed_password=pwd_context.hash("test123"),
                role="padawan",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(user)
            db.flush()
            logger.info(f"Utilisateur de test créé : {user.username} (ID: {user.id})")
        
        # Créer des défis logiques variés
        # Note: Utiliser directement les objets enum comme dans db_init_service.py
        challenges = [
            LogicChallenge(
                title="Séquence de nombres pairs",
                creator_id=user.id,
                challenge_type=LogicChallengeType.SEQUENCE,
                age_group=AgeGroup.GROUP_10_12,
                description="Trouvez le prochain nombre dans la séquence",
                question="Complète la séquence: 2, 4, 6, 8, ...",
                correct_answer="10",
                choices=json.dumps(["9", "10", "12", "16"]),
                solution="C'est une séquence de nombres pairs, donc le prochain nombre est 10.",
                solution_explanation="C'est une séquence de nombres pairs. Chaque nombre est obtenu en ajoutant 2 au précédent. Donc 8 + 2 = 10.",
                content="Trouvez le prochain nombre dans la séquence: 2, 4, 6, 8, ...",
                hints=json.dumps([
                    "Regardez la différence entre chaque nombre.",
                    "La différence est constante entre chaque nombre.",
                    "C'est une séquence arithmétique avec une raison de 2."
                ]),
                difficulty_rating=2.0,
                estimated_time_minutes=5,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            LogicChallenge(
                title="Énigme de la bougie",
                creator_id=user.id,
                challenge_type=LogicChallengeType.RIDDLE,  # RIDDLE maintenant disponible dans PostgreSQL
                age_group=AgeGroup.ALL_AGES,
                description="Résoudre l'énigme classique",
                question="Je suis grand quand je suis jeune et petit quand je suis vieux. Qui suis-je?",
                correct_answer="Une bougie",
                choices=json.dumps(["Un arbre", "Une bougie", "Un homme", "Une montagne"]),
                solution="Une bougie est grande quand elle est neuve et se réduit à mesure qu'elle brûle.",
                solution_explanation="Une bougie est grande (haute) quand elle est neuve et se réduit (devient plus petite) à mesure qu'elle brûle et fond.",
                content="Je suis grand quand je suis jeune et petit quand je suis vieux. Qui suis-je?",
                hints=json.dumps([
                    "Pensez à quelque chose qui se consume.",
                    "C'est un objet qu'on utilise pour éclairer.",
                    "Il fond quand on l'utilise."
                ]),
                difficulty_rating=3.0,
                estimated_time_minutes=10,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            LogicChallenge(
                title="Pattern géométrique",
                creator_id=user.id,
                challenge_type=LogicChallengeType.PATTERN,
                age_group=AgeGroup.GROUP_13_15,
                description="Reconnaissez le motif dans cette séquence",
                question="Quel est le prochain nombre dans cette séquence : 1, 4, 9, 16, ... ?",
                correct_answer="25",
                choices=json.dumps(["20", "24", "25", "30"]),
                solution="Ce sont les carrés des nombres entiers : 1²=1, 2²=4, 3²=9, 4²=16, donc 5²=25.",
                solution_explanation="Cette séquence représente les carrés des nombres entiers : 1²=1, 2²=4, 3²=9, 4²=16. Le prochain nombre est donc 5²=25.",
                content="Quel est le prochain nombre dans cette séquence : 1, 4, 9, 16, ... ?",
                hints=json.dumps([
                    "Essayez de multiplier chaque nombre par lui-même.",
                    "Ce sont des carrés parfaits.",
                    "1=1², 4=2², 9=3², 16=4²..."
                ]),
                difficulty_rating=3.5,
                estimated_time_minutes=8,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            LogicChallenge(
                title="Déduction logique",
                creator_id=user.id,
                challenge_type=LogicChallengeType.DEDUCTION,
                age_group=AgeGroup.GROUP_13_15,  # Utiliser GROUP_13_15 au lieu de AGE_13_PLUS (non présent dans PostgreSQL)
                description="Utilisez votre logique pour résoudre ce problème",
                question="Si tous les A sont des B, et que certains B sont des C, peut-on dire que tous les A sont des C ?",
                correct_answer="Non",
                choices=json.dumps(["Oui", "Non", "Peut-être", "On ne peut pas savoir"]),
                solution="Non, on ne peut pas conclure que tous les A sont des C. Par exemple : tous les chats (A) sont des animaux (B), et certains animaux (B) sont des chiens (C), mais tous les chats ne sont pas des chiens.",
                solution_explanation="C'est un problème de logique syllogistique. Même si tous les A sont des B et que certains B sont des C, cela ne garantit pas que tous les A sont des C. Il faut un exemple concret pour comprendre.",
                content="Si tous les A sont des B, et que certains B sont des C, peut-on dire que tous les A sont des C ?",
                hints=json.dumps([
                    "Essayez avec des exemples concrets.",
                    "Pensez à des catégories d'objets.",
                    "Tous les chats sont des animaux, certains animaux sont des chiens..."
                ]),
                difficulty_rating=4.0,
                estimated_time_minutes=15,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            LogicChallenge(
                title="Puzzle de nombres",
                creator_id=user.id,
                challenge_type=LogicChallengeType.PUZZLE,
                age_group=AgeGroup.GROUP_10_12,
                description="Résolvez ce puzzle mathématique",
                question="Quel nombre multiplié par lui-même donne 64 ?",
                correct_answer="8",
                choices=json.dumps(["6", "7", "8", "9"]),
                solution="8 × 8 = 64",
                solution_explanation="Pour trouver ce nombre, on cherche la racine carrée de 64. 8 × 8 = 64, donc la réponse est 8.",
                content="Quel nombre multiplié par lui-même donne 64 ?",
                hints=json.dumps([
                    "Pensez à la table de multiplication.",
                    "Quel nombre fois lui-même donne 64 ?",
                    "C'est la racine carrée de 64."
                ]),
                difficulty_rating=2.5,
                estimated_time_minutes=5,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]
        
        db.add_all(challenges)
        db.commit()
        
        logger.success(f"✅ {len(challenges)} défis logiques créés avec succès !")
        logger.info(f"Créateur : {user.username} (ID: {user.id})")
        
        # Afficher les défis créés
        for challenge in challenges:
            logger.info(f"  - {challenge.title} (Type: {challenge.challenge_type.value}, Âge: {challenge.age_group.value})")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des défis : {e}")
        db.rollback()
        raise
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    logger.info("🚀 Création de défis logiques de test...")
    create_test_challenges()
    logger.info("✅ Terminé !")

