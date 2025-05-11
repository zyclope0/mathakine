from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from app.models.logic_challenge import LogicChallengeType, AgeGroup

# Schémas pour la manipulation des défis logiques



class LogicChallengeBase(BaseModel):
    """Schéma de base pour les défis de logique (Épreuves du Conseil Jedi)"""
    title: str = Field(..., min_length=3, max_length=100,
                    description="Titre du défi (3-100 caractères)")
    challenge_type: LogicChallengeType = Field(...,
                                           description="Type de défi logique")
    age_group: AgeGroup = Field(...,
                             description="Groupe d'âge cible")
    description: str = Field(..., min_length=10,
                         description="Énoncé du problème (min 10 caractères)")
    correct_answer: str = Field(...,
                             description="Réponse correcte au défi")
    solution_explanation: str = Field(..., min_length=10,
                                  description="Explication détaillée de la solution")

    # Champs optionnels
    hint_level1: Optional[str] = Field(None,
                                    description="Premier indice (aide basique)")
    hint_level2: Optional[str] = Field(None,
                                    description="Deuxième indice (aide intermédiaire)")
    hint_level3: Optional[str] = Field(None,
                                    description="Troisième indice (aide avancée)")
    difficulty_rating: float = Field(3.0, ge=1.0, le=5.0,
                                 description="Niveau de difficulté (1-5)")
    estimated_time_minutes: int = Field(15, ge=1, le=120,
                                     description="Temps estimé pour résoudre (en minutes)")
    tags: Optional[str] = Field(None,
                             description="Tags séparés par des virgules")

    @field_validator('correct_answer')
    @classmethod


    def answer_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("La réponse correcte ne peut pas être vide")
        return v

    @field_validator('description')
    @classmethod


    def description_not_too_short(cls, v):
        if len(v) < 10:
            raise ValueError("La description doit contenir au moins 10 caractères")
        return v

    @field_validator('solution_explanation')
    @classmethod


    def explanation_not_too_short(cls, v):
        if len(v) < 10:
            raise ValueError("L'explication de la solution doit contenir au moins 10 caractères")
        return v



class LogicChallengeCreate(LogicChallengeBase):
    """Schéma pour la création d'un défi logique"""
    visual_data: Optional[Dict[str, Any]] = Field(None,
                                             description="Données pour visualisation (graphes
                                                 , formes, etc.)")
    image_url: Optional[str] = Field(None,
                                 description="URL de l'image associée")
    source_reference: Optional[str] = Field(None,
                                        description="Source (concours, livre, etc.)")
    is_template: bool = Field(False,
                           description="S'il s'agit d'un template pour génération")
    generation_parameters: Optional[Dict[str, Any]] = Field(None,
                                                       description="Paramètres pour la génération")



class LogicChallengeUpdate(BaseModel):
    """Schéma pour la mise à jour d'un défi logique"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    challenge_type: Optional[LogicChallengeType] = None
    age_group: Optional[AgeGroup] = None
    description: Optional[str] = Field(None, min_length=10)
    correct_answer: Optional[str] = None
    solution_explanation: Optional[str] = Field(None, min_length=10)
    visual_data: Optional[Dict[str, Any]] = None
    hint_level1: Optional[str] = None
    hint_level2: Optional[str] = None
    hint_level3: Optional[str] = None
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    estimated_time_minutes: Optional[int] = Field(None, ge=1, le=120)
    image_url: Optional[str] = None
    source_reference: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_template: Optional[bool] = None
    generation_parameters: Optional[Dict[str, Any]] = None

    @field_validator('description')
    @classmethod


    def description_not_too_short(cls, v):
        if v is not None and len(v) < 10:
            raise ValueError("La description doit contenir au moins 10 caractères")
        return v

    @field_validator('solution_explanation')
    @classmethod


    def explanation_not_too_short(cls, v):
        if v is not None and len(v) < 10:
            raise ValueError("L'explication de la solution doit contenir au moins 10 caractères")
        return v



class LogicChallengeInDB(LogicChallengeBase):
    """Schéma pour un défi logique en base de données"""
    id: int
    creator_id: Optional[int] = None
    visual_data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    source_reference: Optional[str] = None
    is_template: bool
    generation_parameters: Optional[Dict[str, Any]] = None
    success_rate: float
    is_active: bool
    is_archived: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class LogicChallenge(LogicChallengeInDB):
    """Schéma pour un défi logique complet"""
    model_config = ConfigDict(from_attributes=True)

# Schémas pour les tentatives de résolution



class LogicChallengeAttemptBase(BaseModel):
    """Schéma de base pour les tentatives de résolution de défis logiques"""
    challenge_id: int = Field(..., description="ID du défi logique")
    user_answer: str = Field(..., description="Réponse fournie par l'utilisateur")
    time_spent: Optional[float] = Field(None, ge=0.0,
                                     description="Temps passé en secondes")
    hint_level1_used: bool = Field(False, description="Premier indice utilisé")
    hint_level2_used: bool = Field(False, description="Deuxième indice utilisé")
    hint_level3_used: bool = Field(False, description="Troisième indice utilisé")
    notes: Optional[str] = Field(None, description="Notes personnelles de l'utilisateur")

    @field_validator('user_answer')
    @classmethod


    def answer_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("La réponse ne peut pas être vide")
        return v



class LogicChallengeAttemptCreate(LogicChallengeAttemptBase):
    """Schéma pour la création d'une tentative de résolution de défi logique"""
    pass



class LogicChallengeAttemptUpdate(BaseModel):
    """Schéma pour la mise à jour d'une tentative de résolution"""
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    time_spent: Optional[float] = Field(None, ge=0.0)
    hint_level1_used: Optional[bool] = None
    hint_level2_used: Optional[bool] = None
    hint_level3_used: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator('user_answer')
    @classmethod


    def answer_not_empty(cls, v):
        if v is not None and (not v or v.isspace()):
            raise ValueError("La réponse ne peut pas être vide")
        return v



class LogicChallengeAttemptInDB(LogicChallengeAttemptBase):
    """Schéma pour une tentative de résolution en base de données"""
    id: int
    user_id: int
    is_correct: bool
    attempt_number: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class LogicChallengeAttempt(LogicChallengeAttemptInDB):
    """Schéma pour une tentative de résolution complète"""
    challenge_title: Optional[str] = None
    challenge_type: Optional[LogicChallengeType] = None
    age_group: Optional[AgeGroup] = None

    model_config = ConfigDict(from_attributes=True)



class LogicChallengeStats(BaseModel):
    """Statistiques sur un défi logique"""
    challenge_id: int
    view_count: int
    attempt_count: int
    success_rate: float
    average_time: Optional[float] = None
    hint_usage_rate: Optional[Dict[str, float]] = None  # Taux d'utilisation de chaque niveau d'indice

    model_config = ConfigDict(from_attributes=True)



class LogicChallengeAttemptResult(BaseModel):
    """Résultat d'une tentative de résolution d'un défi logique"""
    is_correct: bool = Field(..., description="Si la réponse est correcte")
    feedback: str = Field(..., description="Retour sur la tentative")
    explanation: Optional[str] = Field(None, description="Explication de la solution (si correct)")
    hints: Optional[List[str]] = Field(None, description="Indices pour aider (si incorrect)")

    model_config = ConfigDict(from_attributes=True)
