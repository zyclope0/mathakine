from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.user import UserRole
from enum import Enum

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
    """Schéma pour la création d'un utilisateur (Recrutement d'un Padawan)"""
    password: str = Field(..., min_length=8, 
                        description="Mot de passe (8 caractères minimum)")
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        """Vérifie que le mot de passe est suffisamment fort"""
        if len(v) < 8:
            raise ValueError("Le mot de passe doit faire au moins 8 caractères")
        if not any(char.isdigit() for char in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        if not any(char.isupper() for char in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        return v



class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur (Évolution d'un Jedi)"""
    username: Optional[str] = Field(None, min_length=3, max_length=50,
                                description="Nom d'utilisateur unique (3-50 caractères)")
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8,
                                description="Nouveau mot de passe (8 caractères minimum)")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    learning_style: Optional[str] = None
    preferred_difficulty: Optional[str] = None
    preferred_theme: Optional[str] = None
    accessibility_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(extra="forbid", validate_default=True)



class User(UserBase):
    """Schéma pour un utilisateur (Membre de l'Ordre Jedi)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class UserInDB(UserBase):
    """Schéma pour un utilisateur en base de données (Archives Jedi)"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



class UserLogin(BaseModel):
    """Schéma pour l'authentification (Vérification d'identité)"""
    username: str
    password: str



class UserRole(str, Enum):
    PADAWAN = "padawan"
    CHEVALIER = "chevalier"
    MAITRE = "maitre"
    ADMIN = "admin"

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str
    role: Optional[str] = None
    exp: Optional[int] = None

class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str  # "access" ou "refresh"
    role: Optional[str] = None
