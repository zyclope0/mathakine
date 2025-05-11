from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.user import UserRole

# Schémas pour la manipulation des utilisateurs



class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs (Les bases d'un Padawan)"""
    username: str = Field(..., min_length=3, max_length=50,
                        description="Nom d'utilisateur unique (3-50 caractères)")
    email: EmailStr = Field(..., description="Adresse email valide")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100,
                                  description="Nom complet de l'utilisateur")
    role: Optional[UserRole] = Field(default=UserRole.PADAWAN,
                                  description="Rôle dans l'Ordre Jedi des Mathématiques")
    grade_level: Optional[int] = Field(None, ge=1, le=12,
                                    description="Niveau scolaire (1-12)")
    learning_style: Optional[str] = Field(None,
                                      description="Style d'apprentissage préféré")
    preferred_difficulty: Optional[str] = Field(None,
                                           description="Difficulté préférée")
    preferred_theme: Optional[str] = Field("light",
                                      description="Thème préféré: 'light' (Côté Lumineux) ou 'dark' (Côté Obscur)")
    accessibility_settings: Optional[Dict[str, Any]] = Field(None,
                                                        description="Paramètres d'accessibilité personnalisés")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores")
        return v

    @field_validator('preferred_theme')
    @classmethod


    def theme_valid(cls, v):
        if v not in ['light', 'dark']:
            raise ValueError("Le thème doit être 'light' (Côté Lumineux) ou 'dark' (Côté Obscur)")
        return v



class UserCreate(UserBase):
    """Schéma pour la création d'un nouvel utilisateur (Initiation d'un Padawan)"""
    password: str = Field(..., min_length=8,
                        description="Mot de passe (8 caractères minimum)")

    @field_validator('password')
    @classmethod


    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        if not any(char.isdigit() for char in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        if not any(char.isupper() for char in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        return v



class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur (Évolution d'un Padawan)"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    learning_style: Optional[str] = None
    preferred_difficulty: Optional[str] = None
    preferred_theme: Optional[str] = None
    accessibility_settings: Optional[Dict[str, Any]] = None

    @field_validator('preferred_theme')
    @classmethod


    def theme_valid(cls, v):
        if v is not None and v not in ['light', 'dark']:
            raise ValueError("Le thème doit être 'light' (Côté Lumineux) ou 'dark' (Côté Obscur)")
        return v



class UserInDB(UserBase):
    """Schéma pour un utilisateur en base de données (Archives Jedi)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class User(UserInDB):
    """Schéma d'un utilisateur (Carte d'identité Jedi)"""
    model_config = ConfigDict(from_attributes=True)



class UserLogin(BaseModel):
    """Schéma pour l'authentification (Vérification d'identité)"""
    username: str
    password: str



class Token(BaseModel):
    """Schéma pour un token d'authentification (Cristal d'Identité)"""
    access_token: str
    token_type: str



class TokenData(BaseModel):
    """Données contenues dans un token (Données du Cristal)"""
    username: Optional[str] = None
    role: Optional[UserRole] = None
