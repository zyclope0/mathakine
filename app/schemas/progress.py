from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Schémas pour la manipulation des progressions



class ProgressBase(BaseModel):
    """Schéma de base pour les progressions (Chemin vers la Maîtrise)"""
    exercise_type: str = Field(..., description="Type d'exercice (addition, soustraction, etc.)")
    difficulty: str = Field(..., description="Niveau de difficulté")
    total_attempts: int = Field(0, ge=0, description="Nombre total de tentatives")
    correct_attempts: int = Field(0, ge=0, description="Nombre de tentatives réussies")
    average_time: Optional[float] = Field(None, ge=0.0, description="Temps moyen pour résoudre (secondes)")
    completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0, description="Taux de complétion (%)")
    mastery_level: int = Field(1, description="Niveau de maîtrise (1-5)")

    @field_validator('correct_attempts')
    @classmethod


    def correct_not_greater_than_total(cls, v, info):
        values = info.data
        if 'total_attempts' in values and v > values['total_attempts']:
            raise ValueError("Le nombre de tentatives réussies ne peut pas dépasser le nombre total de tentatives")
        return v



class ProgressCreate(ProgressBase):
    """Schéma pour la création d'un enregistrement de progression"""
    user_id: int = Field(..., description="ID de l'utilisateur associé")



class ProgressUpdate(BaseModel):
    """Schéma pour la mise à jour d'un enregistrement de progression"""
    total_attempts: Optional[int] = Field(None, ge=0)
    correct_attempts: Optional[int] = Field(None, ge=0)
    average_time: Optional[float] = Field(None, ge=0.0)
    completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    streak: Optional[int] = Field(None, ge=0)
    highest_streak: Optional[int] = Field(None, ge=0)
    mastery_level: Optional[int] = Field(None, ge=1, le=5)
    awards: Optional[Dict[str, Any]] = None
    strengths: Optional[str] = None
    areas_to_improve: Optional[str] = None
    recommendations: Optional[str] = None

    @field_validator('correct_attempts')
    @classmethod


    def correct_not_greater_than_total(cls, v, info):
        values = info.data
        if v is not None and 'total_attempts' in values and values['total_attempts'] is not None\
            and v > values['total_attempts']:
            raise ValueError("Le nombre de tentatives réussies ne peut pas dépasser le nombre total de tentatives")
        return v

    @field_validator('highest_streak')
    @classmethod


    def highest_streak_not_less_than_streak(cls, v, info):
        values = info.data
        if v is not None and 'streak' in values and values['streak'] is not None\
            and v < values['streak']:
            raise ValueError("La meilleure série ne peut pas être inférieure à la série actuelle")
        return v



class ProgressInDB(ProgressBase):
    """Schéma pour un enregistrement de progression en base de données"""
    id: int
    user_id: int
    average_time: Optional[float] = None
    completion_rate: Optional[float] = None
    streak: int
    highest_streak: int
    mastery_level: int
    awards: Optional[Dict[str, Any]] = None
    strengths: Optional[str] = None
    areas_to_improve: Optional[str] = None
    recommendations: Optional[str] = None
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)



class Progress(ProgressInDB):
    """Schéma pour un enregistrement de progression complet (Carte de Progression)"""
    user_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class UserProgressSummary(BaseModel):
    """Résumé de la progression d'un utilisateur (Rapport du Conseil Jedi)"""
    user_id: int
    user_name: str
    overall_mastery: float = Field(..., ge=0.0, le=5.0, description="Niveau de maîtrise global (0-5)")
    total_exercises_completed: int
    strongest_area: Optional[str] = None
    weakest_area: Optional[str] = None
    recent_progress: Optional[List[Dict[str, Any]]] = None
    next_recommended_exercise_types: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class ProgressResponse(ProgressBase):
    """Schéma pour la réponse de progrès utilisateur"""
    last_updated: Optional[str] = Field(None, description="Date de dernière mise à jour")
    
    model_config = ConfigDict(from_attributes=True)


class RecentAttempt(BaseModel):
    """Schéma pour les tentatives récentes"""
    exercise_id: int = Field(..., description="ID de l'exercice")
    exercise_title: str = Field(..., description="Titre de l'exercice")
    is_correct: bool = Field(..., description="Si la tentative est correcte")
    time_spent: float = Field(..., description="Temps passé (secondes)")
    date: Optional[str] = Field(None, description="Date de la tentative")


class ProgressDetail(ProgressResponse):
    """Schéma détaillé pour les progrès utilisateur"""
    streak: int = Field(0, description="Série actuelle d'exercices réussis")
    highest_streak: int = Field(0, description="Meilleure série")
    strengths: Optional[str] = Field(None, description="Points forts identifiés")
    areas_to_improve: Optional[str] = Field(None, description="Domaines à améliorer")
    recent_attempts: List[RecentAttempt] = Field(default_factory=list, description="Tentatives récentes")
