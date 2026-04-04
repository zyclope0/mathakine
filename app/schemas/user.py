import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.core.user_roles import CanonicalUserRole, normalize_user_role
from app.core.user_age_group import USER_AGE_GROUP_VALUES

# Schémas pour la manipulation des utilisateurs


class UserBase(BaseModel):
    """Schéma de base pour les champs profil utilisateur exposés à l'API."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nom d'utilisateur unique (3-50 caractères)",
    )
    email: EmailStr = Field(..., description="Adresse email valide")
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Nom complet de l'utilisateur"
    )
    role: Optional[CanonicalUserRole] = Field(
        default=CanonicalUserRole.APPRENANT,
        description=(
            "Rôle canonique du compte. "
            "Valeurs API : apprenant, enseignant, moderateur, admin. "
            "Les alias legacy restent acceptés temporairement en entrée."
        ),
    )
    grade_level: Optional[int] = Field(
        None, ge=1, le=12, description="Niveau scolaire (1-12)"
    )
    learning_style: Optional[str] = Field(
        None, description="Style d'apprentissage préféré"
    )
    preferred_difficulty: Optional[str] = Field(None, description="Difficulté préférée")
    preferred_theme: Optional[str] = Field(
        "spatial",
        description="Thème préféré: spatial, minimalist, ocean, dune, forest, peach",
    )
    accessibility_settings: Optional[Dict[str, Any]] = Field(
        None, description="Paramètres d'accessibilité personnalisés"
    )

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores"
            )
        return v

    @field_validator("preferred_theme")
    @classmethod
    def theme_valid(cls, v):
        # Accepter les thèmes UI (light/dark) et les thèmes visuels (spatial, minimalist, ocean, dune, forest, peach, dino; neutral pour rétrocompat)
        valid_themes = [
            "light",
            "dark",
            "spatial",
            "minimalist",
            "ocean",
            "dune",
            "forest",
            "peach",
            "dino",
            "neutral",
        ]
        if v is not None and v not in valid_themes:
            raise ValueError(
                f"Le thème doit être l'un des suivants: {', '.join(valid_themes)}"
            )
        return v

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if v is None:
            return v
        return normalize_user_role(v).value


class UserCreate(UserBase):
    """Schéma pour l'inscription (création de compte)."""

    password: str = Field(
        ..., min_length=8, description="Mot de passe (8 caractères minimum)"
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """Vérifie que le mot de passe est suffisamment fort"""
        from app.core.security import validate_password_strength

        err = validate_password_strength(v)
        if err:
            raise ValueError(err)
        return v


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    grade_level: Optional[int] = None
    grade_system: Optional[str] = Field(
        None, max_length=20, description="Système scolaire: suisse (Harmos) ou unifie"
    )
    age_group: Optional[str] = Field(
        None,
        max_length=10,
        description="Tranche d'âge pédagogique (6-8, 9-11, 12-14, 15+) ; inapplicable si Harmos",
    )
    learning_style: Optional[str] = None
    preferred_difficulty: Optional[str] = None
    learning_goal: Optional[str] = Field(
        None,
        max_length=100,
        description="Objectif pédagogique (réviser, préparer_exam, progresser, etc.)",
    )
    practice_rhythm: Optional[str] = Field(
        None,
        max_length=50,
        description="Rythme souhaité (10min/jour, 30min/semaine, etc.)",
    )
    preferred_theme: Optional[str] = Field(
        None,
        description="Thème préféré (spatial, minimalist, ocean, dune, forest, peach, dino)",
    )
    accessibility_settings: Optional[Dict[str, bool]] = Field(
        None, description="Paramètres d'accessibilité"
    )
    # Paramètres Settings
    notification_preferences: Optional[Dict[str, bool]] = Field(
        None,
        description="Préférences de notifications (achievements, progress, recommendations, news)",
    )
    language_preference: Optional[str] = Field(
        None, description="Langue préférée (fr, en)"
    )
    timezone: Optional[str] = Field(None, description="Fuseau horaire")
    is_public_profile: Optional[bool] = Field(None, description="Profil public")
    allow_friend_requests: Optional[bool] = Field(
        None, description="Autoriser les demandes d'amis"
    )
    show_in_leaderboards: Optional[bool] = Field(
        None, description="Afficher dans les classements"
    )
    data_retention_consent: Optional[bool] = Field(
        None, description="Consentement conservation données"
    )
    marketing_consent: Optional[bool] = Field(
        None, description="Consentement marketing"
    )

    @field_validator("age_group")
    @classmethod
    def validate_age_group(cls, v):
        if v is not None and v not in USER_AGE_GROUP_VALUES:
            raise ValueError(
                "Tranche d'âge invalide. Valeurs : "
                + ", ".join(sorted(USER_AGE_GROUP_VALUES))
            )
        return v

    @field_validator("preferred_theme")
    @classmethod
    def validate_theme(cls, v):
        # Accepter les thèmes UI (light/dark) et les thèmes visuels (spatial, minimalist, ocean, dune, forest, peach, dino; neutral pour rétrocompat)
        valid_themes = [
            "light",
            "dark",
            "spatial",
            "minimalist",
            "ocean",
            "dune",
            "forest",
            "peach",
            "dino",
            "neutral",
        ]
        if v is not None and v not in valid_themes:
            raise ValueError(
                f"Le thème doit être l'un des suivants: {', '.join(valid_themes)}"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "nouveau.utilisateur@exemple.com",
                "full_name": "Alex Martin",
                "password": "NewPassword123!",
                "is_active": True,
                "grade_level": 5,
                "learning_style": "visuel",
                "preferred_difficulty": "chevalier",
                "preferred_theme": "spatial",
                "accessibility_settings": {"high_contrast": True, "large_text": False},
            }
        },
        "json_encoders": {dict: lambda v: json.dumps(v)},
    }


class User(UserBase):
    """Schéma de réponse utilisateur (lecture)."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    """Schéma aligné sur le modèle ORM utilisateur (usage interne / persistance)."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schéma pour l'authentification (Vérification d'identité)"""

    username: str
    password: str


class SchemaUserRole(str, Enum):
    """Contrat public canonique des rôles utilisateur."""

    APPRENANT = CanonicalUserRole.APPRENANT.value
    ENSEIGNANT = CanonicalUserRole.ENSEIGNANT.value
    MODERATEUR = CanonicalUserRole.MODERATEUR.value
    ADMIN = CanonicalUserRole.ADMIN.value


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: Optional[int] = None


class RefreshTokenResponse(BaseModel):
    """Schéma pour la réponse de rafraîchissement de token"""

    access_token: str
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


class RefreshTokenRequest(BaseModel):
    """Schéma pour la requête de rafraîchissement de token"""

    refresh_token: str = Field(..., description="Token de rafraîchissement à utiliser")


class ValidateTokenRequest(BaseModel):
    """Schéma pour la validation d'un token d'accès (sync-cookie frontend)."""

    token: str = Field(..., description="Token JWT à valider")


class UserPasswordUpdate(BaseModel):
    """Schéma pour la mise à jour du mot de passe d'un utilisateur"""

    current_password: str = Field(..., description="Mot de passe actuel")
    new_password: str = Field(
        ..., min_length=8, description="Nouveau mot de passe (8 caractères minimum)"
    )

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        """Vérifie que le mot de passe est suffisamment fort"""
        from app.core.security import validate_password_strength

        err = validate_password_strength(v)
        if err:
            raise ValueError(err)
        return v

    @model_validator(mode="after")
    def passwords_different(self):
        """Le nouveau mot de passe doit être différent de l'actuel."""
        if self.current_password == self.new_password:
            raise ValueError("Le nouveau mot de passe doit être différent de l'ancien.")
        return self


class ForgotPasswordRequest(BaseModel):
    """Schéma pour la demande de réinitialisation de mot de passe"""

    email: EmailStr = Field(..., description="Adresse email associée au compte")


class ResendVerificationRequest(BaseModel):
    """Schéma pour le renvoi d'email de vérification."""

    email: EmailStr = Field(..., description="Adresse email du compte")


class ResetPasswordRequest(BaseModel):
    """Schéma pour la réinitialisation de mot de passe avec token."""

    token: str = Field(..., description="Token de réinitialisation")
    password: str = Field(..., min_length=8, description="Nouveau mot de passe")
    password_confirm: str = Field(..., description="Confirmation du mot de passe")

    @field_validator("token")
    @classmethod
    def token_not_empty(cls, v):
        if not v or not str(v).strip():
            raise ValueError("Token de réinitialisation manquant")
        return str(v).strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        """Vérifie que le mot de passe est suffisamment fort."""
        from app.core.security import validate_password_strength

        err = validate_password_strength(v)
        if err:
            raise ValueError(err)
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        """Vérifie que le mot de passe et la confirmation correspondent."""
        if self.password != self.password_confirm:
            raise ValueError("Les mots de passe ne correspondent pas")
        return self


class ForgotPasswordResponse(BaseModel):
    """Schéma pour la réponse de demande de réinitialisation"""

    message: str = Field(..., description="Message de confirmation")
    success: bool = Field(..., description="Statut de la demande")
