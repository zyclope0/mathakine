from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models.exercise import Exercise
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    responses={404: {"description": "Non trouvé"}},
)

@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(5, ge=1, le=20, description="Nombre maximum de recommandations à retourner")
):
    """Récupère les recommandations personnalisées pour l'utilisateur connecté"""
    
    # Récupérer les recommandations existantes ou en générer de nouvelles
    recommendations = RecommendationService.get_user_recommendations(db, current_user.id, limit)
    
    # Si aucune recommandation n'existe, générer de nouvelles recommandations
    if not recommendations:
        RecommendationService.generate_recommendations(db, current_user.id)
        recommendations = RecommendationService.get_user_recommendations(db, current_user.id, limit)
    
    # Préparer la réponse avec les informations des exercices
    response = []
    for rec in recommendations:
        # Marquer comme affichée
        RecommendationService.mark_recommendation_as_shown(db, rec.id)
        
        # Créer l'objet de réponse
        rec_response = RecommendationResponse(
            id=rec.id,
            exercise_type=rec.exercise_type,
            difficulty=rec.difficulty,
            priority=rec.priority,
            reason=rec.reason,
            exercise_id=rec.exercise_id
        )
        
        # Ajouter les informations de l'exercice si présent
        if rec.exercise_id:
            exercise = db.query(Exercise).filter(Exercise.id == rec.exercise_id).first()
            if exercise:
                rec_response.exercise_title = exercise.title
                rec_response.exercise_question = exercise.question
        
        response.append(rec_response)
    
    return response

@router.post("/{recommendation_id}/clicked", status_code=status.HTTP_200_OK)
def mark_recommendation_clicked(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marque une recommandation comme ayant été cliquée"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommandation non trouvée"
        )
    
    RecommendationService.mark_recommendation_as_clicked(db, recommendation_id)
    return {"status": "success"}

@router.post("/{recommendation_id}/completed", status_code=status.HTTP_200_OK)
def mark_recommendation_completed(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marque une recommandation comme complétée"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommandation non trouvée"
        )
    
    RecommendationService.mark_recommendation_as_completed(db, recommendation_id)
    return {"status": "success"}

@router.post("/generate", status_code=status.HTTP_200_OK, response_model=List[RecommendationResponse])
def generate_new_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(5, ge=1, le=20, description="Nombre maximum de recommandations à retourner")
):
    """Génère de nouvelles recommandations pour l'utilisateur connecté"""
    # Supprimer les anciennes recommandations et en générer de nouvelles
    RecommendationService.generate_recommendations(db, current_user.id)
    
    # Récupérer les nouvelles recommandations
    recommendations = RecommendationService.get_user_recommendations(db, current_user.id, limit)
    
    # Préparer la réponse
    response = []
    for rec in recommendations:
        # Marquer comme affichée
        RecommendationService.mark_recommendation_as_shown(db, rec.id)
        
        # Créer l'objet de réponse
        rec_response = RecommendationResponse(
            id=rec.id,
            exercise_type=rec.exercise_type,
            difficulty=rec.difficulty,
            priority=rec.priority,
            reason=rec.reason,
            exercise_id=rec.exercise_id
        )
        
        # Ajouter les informations de l'exercice si présent
        if rec.exercise_id:
            exercise = db.query(Exercise).filter(Exercise.id == rec.exercise_id).first()
            if exercise:
                rec_response.exercise_title = exercise.title
                rec_response.exercise_question = exercise.question
        
        response.append(rec_response)
    
    return response 