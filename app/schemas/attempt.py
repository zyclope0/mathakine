from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

# Schémas pour la manipulation des tentatives d'exercices



class AttemptBase(BaseModel):
    """Schéma de base pour les tentatives (Tentatives d'Accomplissement)"""
    exercise_id: int = Field(..., description="ID de l'exercice tenté")
    user_answer: str = Field(..., description="Réponse fournie par l'utilisateur")
    time_spent: Optional[float] = Field(None, ge=0.0,
                                     description="Temps passé en secondes")
    hints_used: Optional[int] = Field(0, ge=0,
                                   description="Nombre d'indices utilisés")
    device_info: Optional[str] = Field(None,
                                    description="Information sur l'appareil utilisé")

    @field_validator('user_answer')
    @classmethod


    def answer_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("La réponse ne peut pas être vide")
        return v



class AttemptCreate(AttemptBase):
    """Schéma pour la création d'une tentative (Enregistrement d'une Tentative)"""
    pass



class AttemptUpdate(BaseModel):
    """Schéma pour la mise à jour d'une tentative (rare)"""
    is_correct: Optional[bool] = None
    time_spent: Optional[float] = Field(None, ge=0.0)
    hints_used: Optional[int] = Field(None, ge=0)

    @field_validator('time_spent')
    @classmethod


    def time_spent_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Le temps passé ne peut pas être négatif")
        return v



class AttemptInDB(AttemptBase):
    """Schéma pour une tentative en base de données (Archives des Tentatives)"""
    id: int
    user_id: int
    is_correct: bool
    attempt_number: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class Attempt(AttemptInDB):
    """Schéma pour une tentative complète (Journal de Bord)"""
    exercise_title: Optional[str] = None
    exercise_type: Optional[str] = None
    exercise_difficulty: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class AttemptBatch(BaseModel):
    """Schéma pour l'envoi de plusieurs tentatives (Rapport de Mission)"""
    attempts: list[AttemptCreate] = Field(...,
                                       description="Liste des tentatives à enregistrer")

    @field_validator('attempts')
    @classmethod


    def validate_batch(cls, v):
        if not v:
            raise ValueError("Le lot de tentatives ne peut pas être vide")
        if len(v) > 50:
            raise ValueError("Maximum 50 tentatives par lot")
        return v



class AttemptStats(BaseModel):
    """Statistiques sur les tentatives d'un utilisateur (Analyse de Performance)"""
    total_attempts: int
    correct_attempts: int
    success_rate: float
    average_time: Optional[float] = None
    fastest_time: Optional[float] = None
    slowest_time: Optional[float] = None
    streak: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
