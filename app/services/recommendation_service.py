from sqlalchemy.sql import func
from sqlalchemy import or_, and_, exists
from datetime import datetime, timedelta, timezone
from app.models.recommendation import Recommendation
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.progress import Progress
from app.models.user import User
import random
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    """Service analysant les performances et générant des recommandations personnalisées"""
    
    @staticmethod
    def generate_recommendations(db, user_id):
        """Génère des recommandations pour un utilisateur basé sur ses performances

        Args:
            db: Session SQLAlchemy
            user_id: ID de l'utilisateur

        Returns:
            list: Liste des recommandations générées
        """
        try:
            # Récupérer les données utilisateur
            user_exists = db.query(exists().where(User.id == user_id)).scalar()
            if not user_exists:
                logger.warning(f"Tentative de génération de recommandations pour un utilisateur inexistant: {user_id}")
                return []
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"Utilisateur {user_id} non trouvé")
                return []

            # Analyser les performances récentes
            progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
            recent_attempts = db.query(Attempt).filter(
                Attempt.user_id == user_id,
                Attempt.created_at > datetime.now() - timedelta(days=30)
            ).order_by(Attempt.created_at.desc()).limit(50).all()
            
            # Supprimer les anciennes recommandations non complétées
            db.query(Recommendation).filter(
                Recommendation.user_id == user_id,
                Recommendation.is_completed == False
            ).delete()
            
            # Générer de nouvelles recommandations
            recommendations = []
            
            # 1. Recommandations basées sur les domaines à améliorer
            for progress in progress_records:
                if progress.calculate_completion_rate() < 70:
                    # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                    valid_types = [t.value for t in ExerciseType]
                    valid_difficulties = [d.value for d in DifficultyLevel]
                    
                    # Trouver des exercices appropriés pour améliorer cette compétence
                    exercises = db.query(Exercise).filter(
                        Exercise.exercise_type == progress.exercise_type,
                        Exercise.difficulty == progress.difficulty,
                        Exercise.exercise_type.in_(valid_types),
                        Exercise.difficulty.in_(valid_difficulties),
                        Exercise.is_archived == False,
                        Exercise.is_active == True
                    ).order_by(func.random()).limit(2).all()
                    
                    for ex in exercises:
                        # Vérifier si l'utilisateur a déjà fait cet exercice
                        existing_attempt = db.query(Attempt).filter(
                            Attempt.user_id == user_id,
                            Attempt.exercise_id == ex.id
                        ).first()
                        
                        if not existing_attempt:
                            recommendations.append(Recommendation(
                                user_id=user_id,
                                exercise_type=ex.exercise_type,
                                difficulty=ex.difficulty,
                                exercise_id=ex.id,
                                priority=8,
                                reason=f"Pour renforcer vos compétences en {ex.exercise_type} niveau {ex.difficulty}"
                            ))
            
            # 2. Recommandations pour monter en niveau (progression)
            for progress in progress_records:
                if progress.calculate_completion_rate() > 85:
                    # Proposer des exercices du niveau supérieur
                    next_difficulty = RecommendationService._get_next_difficulty(progress.difficulty)
                    if next_difficulty:
                        # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                        valid_types = [t.value for t in ExerciseType]
                        valid_difficulties = [d.value for d in DifficultyLevel]
                        
                        exercises = db.query(Exercise).filter(
                            Exercise.exercise_type == progress.exercise_type,
                            Exercise.difficulty == next_difficulty,
                            Exercise.exercise_type.in_(valid_types),
                            Exercise.difficulty.in_(valid_difficulties),
                            Exercise.is_archived == False,
                            Exercise.is_active == True
                        ).order_by(func.random()).limit(1).all()
                        
                        for ex in exercises:
                            recommendations.append(Recommendation(
                                user_id=user_id,
                                exercise_type=ex.exercise_type,
                                difficulty=ex.difficulty,
                                exercise_id=ex.id,
                                priority=7,
                                reason=f"Vous êtes prêt à passer au niveau suivant en {ex.exercise_type}"
                            ))
            
            # 3. Recommandations pour maintenir les compétences (réactivation)
            # Trouver les compétences non pratiquées récemment
            # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides dès le départ
            valid_types = [t.value for t in ExerciseType]
            valid_difficulties = [d.value for d in DifficultyLevel]
            
            all_exercise_types = db.query(Exercise.exercise_type).filter(
                Exercise.exercise_type.in_(valid_types),
                Exercise.difficulty.in_(valid_difficulties)
            ).distinct().all()
            
            for ex_type in all_exercise_types:
                ex_type = ex_type[0]  # Extraction du tuple
                # Vérifier si ce type d'exercice a été pratiqué récemment
                # Utiliser une requête filtrée pour éviter les erreurs d'énumération
                recent_type_attempts = []
                for a in recent_attempts:
                    exercise = db.query(Exercise).filter(
                        Exercise.id == a.exercise_id,
                        Exercise.exercise_type.in_(valid_types),
                        Exercise.difficulty.in_(valid_difficulties)
                    ).first()
                    if exercise and exercise.exercise_type == ex_type:
                        recent_type_attempts.append(a)
                
                if not recent_type_attempts:
                    # Trouver le niveau le plus élevé maîtrisé par l'utilisateur pour ce type
                    user_level = None
                    for p in progress_records:
                        if p.exercise_type == ex_type and p.calculate_completion_rate() > 70:
                            user_level = p.difficulty
                    
                    # Si aucun niveau trouvé, proposer le niveau débutant
                    if not user_level:
                        user_level = "Initié"
                    
                    # Proposer un exercice pour maintenir cette compétence
                    exercises = db.query(Exercise).filter(
                        Exercise.exercise_type == ex_type,
                        Exercise.difficulty == user_level,
                        Exercise.exercise_type.in_(valid_types),
                        Exercise.difficulty.in_(valid_difficulties),
                        Exercise.is_archived == False,
                        Exercise.is_active == True
                    ).order_by(func.random()).limit(1).all()
                    
                    for ex in exercises:
                        recommendations.append(Recommendation(
                            user_id=user_id,
                            exercise_type=ex.exercise_type,
                            difficulty=ex.difficulty,
                            exercise_id=ex.id,
                            priority=5,
                            reason=f"Pour maintenir vos compétences en {ex.exercise_type}"
                        ))
            
            # 4. Recommandations de découverte (nouveaux types d'exercices)
            practised_types = set([p.exercise_type for p in progress_records])
            all_types = set([ex_type[0] for ex_type in all_exercise_types])
            new_types = all_types - practised_types
            
            for new_type in new_types:
                # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                valid_types = [t.value for t in ExerciseType]
                valid_difficulties = [d.value for d in DifficultyLevel]
                
                exercises = db.query(Exercise).filter(
                    Exercise.exercise_type == new_type,
                    Exercise.difficulty == "Initié",  # Commencer par le niveau le plus simple
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                    Exercise.is_archived == False,
                    Exercise.is_active == True
                ).order_by(func.random()).limit(1).all()
                
                for ex in exercises:
                    recommendations.append(Recommendation(
                        user_id=user_id,
                        exercise_type=ex.exercise_type,
                        difficulty=ex.difficulty,
                        exercise_id=ex.id,
                        priority=4,
                        reason=f"Découvrez un nouveau type d'exercice: {ex.exercise_type}"
                    ))
            
            # Si aucune recommandation n'a été générée, proposer quelques exercices aléatoires
            if not recommendations:
                # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                valid_types = [t.value for t in ExerciseType]
                valid_difficulties = [d.value for d in DifficultyLevel]
                
                logger.debug(f"Aucune recommandation générée, recherche d'exercices aléatoires...")
                logger.debug(f"Types valides: {valid_types}")
                logger.debug(f"Difficultés valides: {valid_difficulties}")
                
                random_exercises = db.query(Exercise).filter(
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                    Exercise.is_archived == False,
                    Exercise.is_active == True
                ).order_by(func.random()).limit(3).all()
                
                logger.debug(f"Exercices trouvés: {len(random_exercises)}")
                for ex in random_exercises:
                    logger.debug(f"  - {ex.title} ({ex.exercise_type}/{ex.difficulty})")
                
                for ex in random_exercises:
                    recommendations.append(Recommendation(
                        user_id=user_id,
                        exercise_type=ex.exercise_type,
                        difficulty=ex.difficulty,
                        exercise_id=ex.id,
                        priority=3,
                        reason="Pour continuer votre apprentissage"
                    ))
                
                logger.debug(f"Recommandations fallback créées: {len(recommendations)}")
            
            # Ajouter toutes les recommandations
            db.add_all(recommendations)
            db.commit()
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur dans la génération des recommandations: {str(e)}")
            db.rollback()
            return []
    
    @staticmethod
    def mark_recommendation_as_shown(db, recommendation_id):
        """Marque une recommandation comme ayant été montrée à l'utilisateur"""
        try:
            recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
            if recommendation:
                recommendation.shown_count += 1
                db.commit()
        except Exception as e:
            logger.error(f"Erreur lors du marquage de la recommandation comme montrée: {str(e)}")
            db.rollback()
    
    @staticmethod
    def mark_recommendation_as_clicked(db, recommendation_id):
        """Marque une recommandation comme ayant été cliquée par l'utilisateur"""
        try:
            recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
            if recommendation:
                recommendation.clicked_count += 1
                recommendation.last_clicked_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as e:
            logger.error(f"Erreur lors du marquage de la recommandation comme cliquée: {str(e)}")
            db.rollback()
    
    @staticmethod
    def mark_recommendation_as_completed(db, recommendation_id):
        """Marque une recommandation comme complétée"""
        try:
            recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
            if recommendation:
                recommendation.is_completed = True
                recommendation.completed_at = datetime.now(timezone.utc)
                db.commit()
        except Exception as e:
            logger.error(f"Erreur lors du marquage de la recommandation comme complétée: {str(e)}")
            db.rollback()
    
    @staticmethod
    def get_user_recommendations(db, user_id, limit=5):
        """Récupère les recommandations actives pour un utilisateur"""
        return db.query(Recommendation).filter(
            Recommendation.user_id == user_id,
            Recommendation.is_completed == False
        ).order_by(Recommendation.priority.desc()).limit(limit).all()
    
    @staticmethod
    def _get_next_difficulty(current_difficulty):
        """Retourne le niveau de difficulté suivant"""
        # Utiliser les mêmes valeurs que les énumérations DifficultyLevel
        difficulty_levels = ["initie", "padawan", "chevalier", "maitre"]
        try:
            current_index = difficulty_levels.index(current_difficulty.lower())
            if current_index < len(difficulty_levels) - 1:
                return difficulty_levels[current_index + 1]
        except ValueError:
            pass
        return None 