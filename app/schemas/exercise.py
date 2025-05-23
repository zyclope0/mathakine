from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from app.models.exercise import ExerciseType, DifficultyLevel

# Schémas pour la manipulation des exercices

class ExerciseBase(BaseModel):
    """Schéma de base pour les exercices (Épreuves Jedi)"""
    title: str = Field(..., min_length=3, max_length=100,
                    description="Titre de l'exercice (3-100 caractères)")
    exercise_type: Union[str, ExerciseType] = Field(...,
                                     description="Type d'exercice mathématique")
    difficulty: Union[str, DifficultyLevel] = Field(...,
                                     description="Niveau de difficulté")
    question: str = Field(..., min_length=5,
                       description="Question de l'exercice (min 5 caractères)")
    correct_answer: str = Field(...,
                             description="Réponse correcte à la question")
    choices: Optional[List[str]] = Field(None,
                                     description="Options pour les questions à choix multiples")
    explanation: Optional[str] = Field(None,
                                    description="Explication de la solution")
    hint: Optional[str] = Field(None,
                             description="Indice pour aider l'élève")
    tags: Optional[str] = Field(None,
                             description="Tags séparés par des virgules")

    @field_validator('exercise_type')
    @classmethod
    def validate_exercise_type(cls, v):
        # Si c'est déjà un objet ExerciseType, retourner sa valeur
        if isinstance(v, ExerciseType):
            return v.value

        # Si c'est une chaîne, vérifier qu'elle correspond à une valeur valide
        if isinstance(v, str):
            # Convertir en minuscule pour comparaison
            v_lower = v.lower()
            valid_types = [t.value for t in ExerciseType]
            if v_lower in valid_types:
                return v_lower
            else:
                raise ValueError(f"Le type d'exercice '{v}' n'est pas valide. Valeurs possibles: {', '.join(valid_types)}")

        raise ValueError(f"Type non valide: {type(v)}")

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        # Si c'est déjà un objet DifficultyLevel, retourner sa valeur
        if isinstance(v, DifficultyLevel):
            return v.value

        # Si c'est une chaîne, vérifier qu'elle correspond à une valeur valide
        if isinstance(v, str):
            # Convertir en minuscule pour comparaison
            v_lower = v.lower()
            valid_difficulties = [d.value for d in DifficultyLevel]
            if v_lower in valid_difficulties:
                return v_lower
            else:
                raise ValueError(f"La difficulté '{v}' n'est pas valide. Valeurs possibles: {', '.join(valid_difficulties)}")

        raise ValueError(f"Type non valide: {type(v)}")

    @field_validator('correct_answer')
    @classmethod
    def answer_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("La réponse correcte ne peut pas être vide")
        return v

    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v, info):
        if v is not None:
            # Vérifier qu'il y a au moins 2 choix
            if len(v) < 2:
                raise ValueError("Il doit y avoir au moins 2 choix pour un QCM")

            # Vérifier que la réponse correcte est dans les choix
            values = info.data
            if 'correct_answer' in values and values['correct_answer'] not in v:
                raise ValueError("La réponse correcte doit être présente dans les choix")

            # Vérifier que les choix sont uniques
            if len(v) != len(set(v)):
                raise ValueError("Les choix doivent être uniques")

        return v

    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        # Vérifier que la question contient un point d'interrogation, deux points, point d'exclamation ou point final
        if not any(mark in v for mark in ['?', ':', '!', '.']):
            raise ValueError("La question doit contenir une ponctuation finale (?, :, !, .)")
        return v

class ExerciseCreate(ExerciseBase):
    """Schéma pour la création d'un exercice (Création d'une Épreuve)"""
    image_url: Optional[str] = Field(None,
                                  description="URL de l'image associée")
    audio_url: Optional[str] = Field(None,
                                  description="URL audio pour accessibilité")

class ExerciseUpdate(BaseModel):
    """Schéma pour la mise à jour d'un exercice (Modification d'une Épreuve)"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    exercise_type: Optional[Union[str, ExerciseType]] = None
    difficulty: Optional[Union[str, DifficultyLevel]] = None
    question: Optional[str] = Field(None, min_length=5)
    correct_answer: Optional[str] = None
    choices: Optional[List[str]] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None

    @field_validator('exercise_type')
    @classmethod
    def validate_exercise_type(cls, v):
        if v is None:
            return None

        # Si c'est déjà un objet ExerciseType, retourner sa valeur
        if isinstance(v, ExerciseType):
            return v.value

        # Si c'est une chaîne, vérifier qu'elle correspond à une valeur valide
        if isinstance(v, str):
            # Convertir en minuscule pour comparaison
            v_lower = v.lower()
            valid_types = [t.value for t in ExerciseType]
            if v_lower in valid_types:
                return v_lower
            else:
                raise ValueError(f"Le type d'exercice '{v}' n'est pas valide. Valeurs possibles: {', '.join(valid_types)}")

        raise ValueError(f"Type non valide: {type(v)}")

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        if v is None:
            return None

        # Si c'est déjà un objet DifficultyLevel, retourner sa valeur
        if isinstance(v, DifficultyLevel):
            return v.value

        # Si c'est une chaîne, vérifier qu'elle correspond à une valeur valide
        if isinstance(v, str):
            # Convertir en minuscule pour comparaison
            v_lower = v.lower()
            valid_difficulties = [d.value for d in DifficultyLevel]
            if v_lower in valid_difficulties:
                return v_lower
            else:
                raise ValueError(f"La difficulté '{v}' n'est pas valide. Valeurs possibles: {', '.join(valid_difficulties)}")

        raise ValueError(f"Type non valide: {type(v)}")

    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        if v is not None and not any(mark in v for mark in ['?', ':', '!', '.']):
            raise ValueError("La question doit contenir une ponctuation finale (?, :, !, .)")
        return v

    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v, info):
        if v is not None:
            # Vérifier qu'il y a au moins 2 choix
            if len(v) < 2:
                raise ValueError("Il doit y avoir au moins 2 choix pour un QCM")

            # Vérifier que les choix sont uniques
            if len(v) != len(set(v)):
                raise ValueError("Les choix doivent être uniques")

        return v

class ExerciseInDB(ExerciseBase):
    """Schéma pour un exercice en base de données (Archives des Épreuves)"""
    id: int
    creator_id: Optional[int] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    is_active: bool
    is_archived: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Exercise(ExerciseInDB):
    """Schéma pour un exercice complet (Holocron d'Épreuve)"""
    model_config = ConfigDict(from_attributes=True)

class ExerciseStats(BaseModel):
    """Statistiques sur un exercice (Données de l'Holocron)"""
    exercise_id: int
    view_count: int
    attempt_count: int
    success_rate: float
    average_time: Optional[float] = None

    model_config = ConfigDict(from_attributes=True) 