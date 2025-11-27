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

            # Récupérer les stats récentes (30 derniers jours) pour mieux cibler
            from app.services.user_service import UserService
            recent_stats = UserService.get_user_stats(db, user_id, time_range="30")
            performance_by_type = recent_stats.get("by_exercise_type", {})
            
            # Analyser les performances récentes
            progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
            recent_attempts = db.query(Attempt).filter(
                Attempt.user_id == user_id,
                Attempt.created_at > datetime.now(timezone.utc) - timedelta(days=30)
            ).order_by(Attempt.created_at.desc()).limit(50).all()
            
            # Récupérer les exercices complétés dans les 7 derniers jours pour éviter les doublons
            recently_completed_exercise_ids = set()
            recent_completed_attempts = db.query(Attempt).filter(
                Attempt.user_id == user_id,
                Attempt.is_correct == True,
                Attempt.created_at > datetime.now(timezone.utc) - timedelta(days=7)
            ).all()
            for attempt in recent_completed_attempts:
                if attempt.exercise_id:
                    recently_completed_exercise_ids.add(attempt.exercise_id)
            
            # Supprimer les anciennes recommandations non complétées
            db.query(Recommendation).filter(
                Recommendation.user_id == user_id,
                Recommendation.is_completed == False
            ).delete()
            
            # Générer de nouvelles recommandations
            recommendations = []
            
            # 1. Recommandations basées sur les domaines à améliorer (utilisant les stats récentes)
            # Prioriser les types avec faible taux de réussite récent
            for ex_type_key, type_stats in performance_by_type.items():
                # Normaliser le type d'exercice (peut être en minuscules depuis SQL)
                ex_type = str(ex_type_key).lower()
                success_rate = type_stats.get("success_rate", 0)
                total = type_stats.get("total", 0)
                
                # Seulement recommander si au moins 3 tentatives récentes pour avoir des données fiables
                if total >= 3 and success_rate < 70:
                    # Déterminer la priorité selon le taux de réussite
                    if success_rate < 50:
                        priority = 9  # Urgent
                        reason = f"Votre taux de réussite en {ex_type} est de {success_rate}%. Continuons à progresser !"
                    else:
                        priority = 8  # Important
                        reason = f"Pour améliorer votre taux de réussite en {ex_type} ({success_rate}%)"
                    
                    # Trouver le niveau de difficulté le plus approprié
                    # Utiliser le niveau le plus pratiqué récemment ou le niveau actuel du Progress
                    target_difficulty = None
                    for progress in progress_records:
                        if str(progress.exercise_type).lower() == ex_type:
                            target_difficulty = progress.difficulty
                            break
                    
                    if not target_difficulty:
                        target_difficulty = "INITIE"  # Par défaut
                    
                    # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                    valid_types = [t.value for t in ExerciseType]
                    valid_difficulties = [d.value for d in DifficultyLevel]
                    
                    # Trouver des exercices appropriés pour améliorer cette compétence
                    # Utiliser func.lower pour comparer sans tenir compte de la casse
                    exercise_query = db.query(Exercise).filter(
                        func.lower(Exercise.exercise_type) == ex_type,
                        Exercise.difficulty == target_difficulty,
                        Exercise.exercise_type.in_(valid_types),
                        Exercise.difficulty.in_(valid_difficulties),
                        Exercise.is_archived == False,
                        Exercise.is_active == True
                    )
                    
                    # Exclure les exercices récemment complétés
                    if recently_completed_exercise_ids:
                        exercise_query = exercise_query.filter(~Exercise.id.in_(list(recently_completed_exercise_ids)))
                    
                    exercises = exercise_query.order_by(func.random()).limit(2).all()
                    
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
                                priority=priority,
                                reason=reason
                            ))
            
            # 2. Recommandations pour monter en niveau (progression) - basé sur stats récentes
            for ex_type_key, type_stats in performance_by_type.items():
                # Normaliser le type d'exercice
                ex_type = str(ex_type_key).lower()
                success_rate = type_stats.get("success_rate", 0)
                total = type_stats.get("total", 0)
                
                # Si taux de réussite > 85% avec au moins 5 tentatives récentes, proposer niveau supérieur
                if total >= 5 and success_rate > 85:
                    # Trouver le niveau actuel depuis Progress
                    current_difficulty = None
                    for progress in progress_records:
                        if str(progress.exercise_type).lower() == ex_type:
                            current_difficulty = progress.difficulty
                            break
                    
                    if not current_difficulty:
                        continue  # Pas de niveau trouvé, passer au suivant
                    
                    # Proposer des exercices du niveau supérieur
                    next_difficulty = RecommendationService._get_next_difficulty(current_difficulty)
                    if next_difficulty:
                        # FILTRE CRITIQUE : Exclure les exercices avec des types/difficultés invalides
                        valid_types = [t.value for t in ExerciseType]
                        valid_difficulties = [d.value for d in DifficultyLevel]
                        
                        # Normaliser ex_type pour la comparaison
                        exercise_type_filter = ex_type
                        for enum_type in ExerciseType:
                            if enum_type.value.lower() == ex_type:
                                exercise_type_filter = enum_type.value
                                break
                        
                        exercise_query = db.query(Exercise).filter(
                            func.lower(Exercise.exercise_type) == ex_type,
                            Exercise.difficulty == next_difficulty,
                            Exercise.exercise_type.in_(valid_types),
                            Exercise.difficulty.in_(valid_difficulties),
                            Exercise.is_archived == False,
                            Exercise.is_active == True
                        )
                        
                        # Exclure les exercices récemment complétés
                        if recently_completed_exercise_ids:
                            exercise_query = exercise_query.filter(~Exercise.id.in_(list(recently_completed_exercise_ids)))
                        
                        exercises = exercise_query.order_by(func.random()).limit(1).all()
                        
                        for ex in exercises:
                            recommendations.append(Recommendation(
                                user_id=user_id,
                                exercise_type=ex.exercise_type,
                                difficulty=ex.difficulty,
                                exercise_id=ex.id,
                                priority=7,
                                reason=f"Excellent ! Vous avez {success_rate}% de réussite en {ex.exercise_type}. Essayons le niveau {next_difficulty} !"
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
                        user_level = "INITIE"
                    
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
                        # Vérifier que l'exercice n'a pas été complété récemment
                        if ex.id not in recently_completed_exercise_ids:
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
                    Exercise.difficulty == "INITIE",  # Commencer par le niveau le plus simple
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                    Exercise.is_archived == False,
                    Exercise.is_active == True
                ).order_by(func.random()).limit(1).all()
                
                for ex in exercises:
                    # Vérifier que l'exercice n'a pas été complété récemment
                    if ex.id not in recently_completed_exercise_ids:
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
                
                exercise_query = db.query(Exercise).filter(
                    Exercise.exercise_type.in_(valid_types),
                    Exercise.difficulty.in_(valid_difficulties),
                    Exercise.is_archived == False,
                    Exercise.is_active == True
                )
                
                # Exclure les exercices récemment complétés
                if recently_completed_exercise_ids:
                    exercise_query = exercise_query.filter(~Exercise.id.in_(list(recently_completed_exercise_ids)))
                
                random_exercises = exercise_query.order_by(func.random()).limit(3).all()
                
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
            
        except Exception as recommendations_generation_error:
            logger.error(f"Erreur dans la génération des recommandations: {str(recommendations_generation_error)}")
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
        except Exception as mark_shown_error:
            logger.error(f"Erreur lors du marquage de la recommandation comme montrée: {str(mark_shown_error)}")
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
        except Exception as mark_clicked_error:
            logger.error(f"Erreur lors du marquage de la recommandation comme cliquée: {str(mark_clicked_error)}")
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
        except Exception as mark_completed_error:
            logger.error(f"Erreur lors du marquage de la recommandation comme complétée: {str(mark_completed_error)}")
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
        # Utiliser les mêmes valeurs que les énumérations DifficultyLevel (en majuscules)
        difficulty_levels = ["INITIE", "PADAWAN", "CHEVALIER", "MAITRE"]
        try:
            current_index = difficulty_levels.index(current_difficulty.upper())
            if current_index < len(difficulty_levels) - 1:
                return difficulty_levels[current_index + 1]
        except ValueError:
            pass
        return None 