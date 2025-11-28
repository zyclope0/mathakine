#!/usr/bin/env python3
"""
Module de nettoyage automatique des données de test
Approche académique pour garantir l'isolation des tests et la propreté de la base de données.

Ce module implémente les meilleures pratiques pour :
1. Identifier automatiquement les données de test
2. Nettoyer après chaque test de manière sécurisée
3. Préserver les données légitimes (utilisateurs permanents, exercices valides)
4. Fournir des mécanismes de rollback en cas d'erreur
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

from app.models.user import User
from app.models.exercise import Exercise
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.logic_challenge import LogicChallenge
from app.models.logic_challenge import LogicChallengeAttempt

logger = logging.getLogger(__name__)

# Cette classe n'est pas un test, c'est un utilitaire
# pytest: disable=collection
class TestDataManager:
    """
    Gestionnaire centralisé pour les données de test.
    Implémente une approche académique avec traçabilité complète.
    """
    
    # Patterns pour identifier les données de test
    TEST_PATTERNS = {
        'usernames': [
            'test_%', 'new_test_%', 'duplicate_%', '%_test_%',
            'user_stats_%', 'rec_cascade_%', 'attempt_error_%',
            'nonexistent_%', 'record_%', 'starlette_%',
            'cascade_%', 'creator_%', 'malformed_%', 'disable_%',
            'flow_%', 'invalid_%', 'jedi_%', 'dashboard_test_%',
            'login_test_%', 'cascade_test_%'
        ],
        'emails': [
            'test@%', '%test%@%', 'cascade_%@%', 'dashboard_%@%'
        ],
        'exercise_titles': [
            '%test%', '%Test%', '%TEST%', 'Cascade %', 'Dashboard %'
        ],
        'challenge_titles': [
            '%test%', '%Test%', '%TEST%', 'Défi Auto-%', 'Nouveau défi%'
        ]
    }
    
    # Utilisateurs permanents à préserver (ne jamais supprimer)
    PERMANENT_USERS = {
        'ObiWan',  # Nouvel utilisateur de test permanent
        'maitre_yoda',
        'padawan1', 
        'gardien1'
    }
    
    def __init__(self, db_session: Session):
        """
        Initialise le gestionnaire avec une session de base de données.
        
        Args:
            db_session: Session SQLAlchemy active
        """
        self.db = db_session
        self.cleanup_log = []
        self.preserved_items = []
        
    def identify_test_data(self) -> Dict[str, List[int]]:
        """
        Identifie toutes les données de test dans la base de données.
        
        Returns:
            Dict contenant les IDs des entités de test par type
        """
        logger.info("🔍 Identification des données de test...")
        
        test_data = {
            'users': [],
            'exercises': [],
            'challenges': [],
            'attempts': [],
            'progress': [],
            'recommendations': [],
            'challenge_attempts': []
        }
        
        # 1. Identifier les utilisateurs de test (sauf permanents)
        user_conditions = []
        for pattern in self.TEST_PATTERNS['usernames']:
            user_conditions.append(f"username LIKE '{pattern}'")
        for pattern in self.TEST_PATTERNS['emails']:
            user_conditions.append(f"email LIKE '{pattern}'")
        
        # Exclure les utilisateurs permanents
        permanent_exclusion = "', '".join(self.PERMANENT_USERS)
        user_query = f"""
            SELECT id FROM users 
            WHERE ({' OR '.join(user_conditions)})
            AND username NOT IN ('{permanent_exclusion}')
        """
        
        result = self.db.execute(text(user_query))
        test_data['users'] = [row[0] for row in result.fetchall()]
        
        # 2. Identifier les exercices de test
        exercise_conditions = []
        for pattern in self.TEST_PATTERNS['exercise_titles']:
            exercise_conditions.append(f"title LIKE '{pattern}'")
        
        if exercise_conditions:
            exercise_query = f"""
                SELECT id FROM exercises 
                WHERE {' OR '.join(exercise_conditions)}
            """
            result = self.db.execute(text(exercise_query))
            test_data['exercises'] = [row[0] for row in result.fetchall()]
        
        # 3. Identifier les défis logiques de test
        challenge_conditions = []
        for pattern in self.TEST_PATTERNS['challenge_titles']:
            challenge_conditions.append(f"title LIKE '{pattern}'")
        
        if challenge_conditions:
            challenge_query = f"""
                SELECT id FROM logic_challenges 
                WHERE {' OR '.join(challenge_conditions)}
            """
            result = self.db.execute(text(challenge_query))
            test_data['challenges'] = [row[0] for row in result.fetchall()]
        
        # 4. Identifier les données liées aux utilisateurs de test
        if test_data['users']:
            user_ids_str = ','.join(map(str, test_data['users']))
            
            # Tentatives
            result = self.db.execute(text(f"SELECT id FROM attempts WHERE user_id IN ({user_ids_str})"))
            test_data['attempts'] = [row[0] for row in result.fetchall()]
            
            # Progression
            result = self.db.execute(text(f"SELECT id FROM progress WHERE user_id IN ({user_ids_str})"))
            test_data['progress'] = [row[0] for row in result.fetchall()]
            
            # Recommandations
            result = self.db.execute(text(f"SELECT id FROM recommendations WHERE user_id IN ({user_ids_str})"))
            test_data['recommendations'] = [row[0] for row in result.fetchall()]
            
            # Tentatives de défis logiques
            result = self.db.execute(text(f"SELECT id FROM logic_challenge_attempts WHERE user_id IN ({user_ids_str})"))
            test_data['challenge_attempts'] = [row[0] for row in result.fetchall()]
        
        # 5. Identifier les données liées aux exercices de test
        if test_data['exercises']:
            exercise_ids_str = ','.join(map(str, test_data['exercises']))
            
            # Tentatives liées aux exercices de test
            result = self.db.execute(text(f"SELECT id FROM attempts WHERE exercise_id IN ({exercise_ids_str})"))
            additional_attempts = [row[0] for row in result.fetchall()]
            test_data['attempts'].extend(additional_attempts)
            test_data['attempts'] = list(set(test_data['attempts']))  # Dédoublonner
        
        # 6. Identifier les données liées aux défis de test
        if test_data['challenges']:
            challenge_ids_str = ','.join(map(str, test_data['challenges']))
            
            # Tentatives de défis liées aux défis de test
            result = self.db.execute(text(f"SELECT id FROM logic_challenge_attempts WHERE challenge_id IN ({challenge_ids_str})"))
            additional_challenge_attempts = [row[0] for row in result.fetchall()]
            test_data['challenge_attempts'].extend(additional_challenge_attempts)
            test_data['challenge_attempts'] = list(set(test_data['challenge_attempts']))  # Dédoublonner
        
        # Log du résumé
        total_items = sum(len(items) for items in test_data.values())
        logger.info(f"📊 Données de test identifiées : {total_items} éléments")
        for data_type, items in test_data.items():
            if items:
                logger.info(f"  - {data_type}: {len(items)} éléments")
        
        return test_data
    
    def cleanup_test_data(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Nettoie les données de test de manière sécurisée.
        
        Args:
            dry_run: Si True, simule seulement le nettoyage
            
        Returns:
            Dict avec le résumé des opérations effectuées
        """
        logger.info(f"🧹 Début du nettoyage (dry_run={dry_run})...")
        
        # Vérifier l'état de la session avant de commencer
        from sqlalchemy.exc import InvalidRequestError, StatementError
        
        try:
            # Tester si la session est utilisable
            self.db.execute(text("SELECT 1"))
        except (InvalidRequestError, StatementError, Exception) as session_error:
            # La session est en état d'erreur, on ne peut pas nettoyer
            logger.warning(f"⚠️ Session en état d'erreur, nettoyage ignoré : {session_error}")
            return {
                'dry_run': dry_run,
                'success': False,
                'error': f"Session en état d'erreur : {str(session_error)}",
                'total_deleted': 0
            }
        
        # Identifier les données à supprimer
        test_data = self.identify_test_data()
        
        if dry_run:
            logger.info("🔍 MODE DRY-RUN : Aucune suppression ne sera effectuée")
            return {
                'dry_run': True,
                'identified_data': test_data,
                'total_items': sum(len(items) for items in test_data.values())
            }
        
        # Effectuer le nettoyage dans l'ordre correct (contraintes FK)
        deleted_counts = {}
        
        try:
            # 1. Supprimer les tentatives de défis logiques
            if test_data['challenge_attempts']:
                ids_str = ','.join(map(str, test_data['challenge_attempts']))
                result = self.db.execute(text(f"DELETE FROM logic_challenge_attempts WHERE id IN ({ids_str})"))
                deleted_counts['challenge_attempts'] = result.rowcount
                logger.info(f"  ✅ Supprimé {result.rowcount} tentatives de défis logiques")
            
            # 2. Supprimer les tentatives d'exercices
            if test_data['attempts']:
                ids_str = ','.join(map(str, test_data['attempts']))
                result = self.db.execute(text(f"DELETE FROM attempts WHERE id IN ({ids_str})"))
                deleted_counts['attempts'] = result.rowcount
                logger.info(f"  ✅ Supprimé {result.rowcount} tentatives d'exercices")
            
            # 3. Supprimer les recommandations
            if test_data['recommendations']:
                ids_str = ','.join(map(str, test_data['recommendations']))
                result = self.db.execute(text(f"DELETE FROM recommendations WHERE id IN ({ids_str})"))
                deleted_counts['recommendations'] = result.rowcount
                logger.info(f"  ✅ Supprimé {result.rowcount} recommandations")
            
            # 4. Supprimer la progression
            if test_data['progress']:
                ids_str = ','.join(map(str, test_data['progress']))
                result = self.db.execute(text(f"DELETE FROM progress WHERE id IN ({ids_str})"))
                deleted_counts['progress'] = result.rowcount
                logger.info(f"  ✅ Supprimé {result.rowcount} entrées de progression")
            
            # 5. Supprimer les défis logiques de test
            if test_data['challenges']:
                ids_str = ','.join(map(str, test_data['challenges']))
                result = self.db.execute(text(f"DELETE FROM logic_challenges WHERE id IN ({ids_str})"))
                deleted_counts['challenges'] = result.rowcount
                logger.info(f"  ✅ Supprimé {result.rowcount} défis logiques")
            
            # 6. Supprimer les exercices de test
            if test_data['exercises']:
                ids_str = ','.join(map(str, test_data['exercises']))
                result = self.db.execute(text(f"DELETE FROM exercises WHERE id IN ({ids_str})"))
                deleted_counts['exercises'] = result.rowcount
                logger.info(f"  ✅ Supprimé {result.rowcount} exercices")
            
            # 7. Supprimer les utilisateurs de test (en dernier)
            if test_data['users']:
                ids_str = ','.join(map(str, test_data['users']))
                result = self.db.execute(text(f"DELETE FROM users WHERE id IN ({ids_str})"))
                deleted_counts['users'] = result.rowcount
                logger.info(f"  ✅ Supprimé {result.rowcount} utilisateurs")
            
            # Commit toutes les suppressions
            self.db.commit()
            
            total_deleted = sum(deleted_counts.values())
            logger.info(f"🎉 Nettoyage terminé : {total_deleted} éléments supprimés")
            
            return {
                'dry_run': False,
                'success': True,
                'deleted_counts': deleted_counts,
                'total_deleted': total_deleted,
                'preserved_users': list(self.PERMANENT_USERS)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage : {str(e)}")
            self.db.rollback()
            return {
                'dry_run': False,
                'success': False,
                'error': str(e),
                'deleted_counts': deleted_counts
            }
    
    @contextmanager
    def test_transaction(self):
        """
        Context manager pour les transactions de test avec rollback automatique.
        Garantit qu'aucune donnée de test ne persiste après le test.
        """
        savepoint = self.db.begin_nested()
        try:
            yield self.db
        except Exception:
            savepoint.rollback()
            raise
        finally:
            # Toujours faire un rollback pour les tests
            savepoint.rollback()
    
    def create_test_user(self, username_prefix: str = "test_user", **kwargs) -> User:
        """
        Crée un utilisateur de test avec un nom unique et traçable.
        
        Args:
            username_prefix: Préfixe pour le nom d'utilisateur
            **kwargs: Attributs supplémentaires pour l'utilisateur
            
        Returns:
            Instance User créée
        """
        unique_id = uuid.uuid4().hex[:8]
        timestamp = int(datetime.now(timezone.utc).timestamp())
        
        default_data = {
            'username': f"{username_prefix}_{unique_id}_{timestamp}",
            'email': f"{username_prefix}_{unique_id}@test.example.com",
            'hashed_password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
            'full_name': f"Test User {unique_id}",
            'created_at': datetime.now(timezone.utc)
        }
        
        # Fusionner avec les données fournies
        default_data.update(kwargs)
        
        user = User(**default_data)
        self.db.add(user)
        self.db.flush()  # Pour obtenir l'ID
        
        logger.info(f"👤 Utilisateur de test créé : {user.username} (ID: {user.id})")
        return user
    
    def verify_cleanup(self) -> Dict[str, int]:
        """
        Vérifie que le nettoyage a été effectué correctement.
        
        Returns:
            Dict avec le nombre d'éléments de test restants par type
        """
        logger.info("🔍 Vérification du nettoyage...")
        
        remaining = {}
        test_data = self.identify_test_data()
        
        for data_type, items in test_data.items():
            remaining[data_type] = len(items)
        
        total_remaining = sum(remaining.values())
        
        if total_remaining == 0:
            logger.info("✅ Nettoyage vérifié : Aucune donnée de test restante")
        else:
            logger.warning(f"⚠️ {total_remaining} éléments de test restants détectés")
            for data_type, count in remaining.items():
                if count > 0:
                    logger.warning(f"  - {data_type}: {count} éléments")
        
        return remaining


# Fonctions utilitaires pour l'intégration avec pytest

def pytest_cleanup_test_data(db_session: Session, dry_run: bool = False) -> Dict[str, Any]:
    """
    Fonction d'intégration pour pytest.
    À utiliser dans les fixtures de nettoyage automatique.
    """
    manager = TestDataManager(db_session)
    return manager.cleanup_test_data(dry_run=dry_run)

def pytest_create_test_user(db_session: Session, **kwargs) -> User:
    """
    Fonction d'intégration pour pytest.
    Crée un utilisateur de test avec nettoyage automatique.
    """
    manager = TestDataManager(db_session)
    return manager.create_test_user(**kwargs)

@contextmanager
def isolated_test_transaction(db_session: Session):
    """
    Context manager pour des tests complètement isolés.
    Garantit qu'aucune donnée ne persiste après le test.
    """
    manager = TestDataManager(db_session)
    with manager.test_transaction() as session:
        yield session 