from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.logic_challenge import AgeGroup, LogicChallengeType

# Schémas pour la manipulation des défis logiques

# Lot IA9 — modalité UI exposée sur GET /api/challenges/{id} (voir challenge_api_mapper).
ChallengeResponseModeLiteral = Literal[
    "open_text",
    "single_choice",
    "interactive_visual",
    "interactive_order",
    "interactive_grid",
]


class LogicChallengeBase(BaseModel):
    """Schéma de base pour les défis de logique mathématique."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titre du défi (3-100 caractères)",
    )
    challenge_type: LogicChallengeType = Field(..., description="Type de défi logique")
    age_group: AgeGroup = Field(..., description="Groupe d'âge cible")
    description: str = Field(
        ..., min_length=10, description="Énoncé du problème (min 10 caractères)"
    )
    correct_answer: str = Field(..., description="Réponse correcte au défi")
    solution_explanation: str = Field(
        ..., min_length=10, description="Explication détaillée de la solution"
    )

    # Champs optionnels
    hints: Optional[List[str]] = Field(
        None, description="Liste des indices (aide progressive)"
    )
    difficulty_rating: float = Field(
        3.0, ge=1.0, le=5.0, description="Niveau de difficulté (1-5)"
    )
    estimated_time_minutes: int = Field(
        15, ge=1, le=120, description="Temps estimé pour résoudre (en minutes)"
    )
    tags: Optional[str] = Field(None, description="Tags séparés par des virgules")

    @field_validator("correct_answer")
    @classmethod
    def answer_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("La réponse correcte ne peut pas être vide")
        return v

    @field_validator("description")
    @classmethod
    def description_not_too_short(cls, v):
        if len(v) < 10:
            raise ValueError("La description doit contenir au moins 10 caractères")
        return v

    @field_validator("solution_explanation")
    @classmethod
    def explanation_not_too_short(cls, v):
        if len(v) < 10:
            raise ValueError(
                "L'explication de la solution doit contenir au moins 10 caractères"
            )
        return v


class LogicChallengeCreate(LogicChallengeBase):
    """Schéma pour la création d'un défi logique"""

    visual_data: Optional[Dict[str, Any]] = Field(
        None, description="Données pour visualisation (graphes, formes, etc.)"
    )
    image_url: Optional[str] = Field(None, description="URL de l'image associée")
    source_reference: Optional[str] = Field(
        None, description="Source (concours, livre, etc.)"
    )
    is_template: bool = Field(
        False, description="S'il s'agit d'un template pour génération"
    )
    generation_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Paramètres pour la génération"
    )


class LogicChallengeUpdate(BaseModel):
    """Schéma pour la mise à jour d'un défi logique"""

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    challenge_type: Optional[LogicChallengeType] = None
    age_group: Optional[AgeGroup] = None
    description: Optional[str] = Field(None, min_length=10)
    correct_answer: Optional[str] = None
    solution_explanation: Optional[str] = Field(None, min_length=10)
    visual_data: Optional[Dict[str, Any]] = None
    hints: Optional[List[str]] = None
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    estimated_time_minutes: Optional[int] = Field(None, ge=1, le=120)
    image_url: Optional[str] = None
    source_reference: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_template: Optional[bool] = None
    generation_parameters: Optional[Dict[str, Any]] = None

    @field_validator("description")
    @classmethod
    def description_not_too_short(cls, v):
        if v is not None and len(v) < 10:
            raise ValueError("La description doit contenir au moins 10 caractères")
        return v

    @field_validator("solution_explanation")
    @classmethod
    def explanation_not_too_short(cls, v):
        if v is not None and len(v) < 10:
            raise ValueError(
                "L'explication de la solution doit contenir au moins 10 caractères"
            )
        return v


class LogicChallengeInDB(LogicChallengeBase):
    """Schéma pour un défi logique en base de données"""

    id: int
    difficulty_tier: Optional[int] = Field(
        None, ge=1, le=12, description="F42 — matrice âge × difficulté (1–12)"
    )
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
    user_solution: str = Field(..., description="Réponse fournie par l'utilisateur")
    time_spent: Optional[float] = Field(
        None, ge=0.0, description="Temps passé en secondes"
    )
    hints_used: Optional[List[int]] = Field(
        None, description="Liste des indices utilisés (ex: [1, 2])"
    )
    notes: Optional[str] = Field(
        None, description="Notes personnelles de l'utilisateur"
    )

    @field_validator("user_solution")
    @classmethod
    def answer_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError("La réponse ne peut pas être vide")
        return v


class LogicChallengeAttemptCreate(LogicChallengeAttemptBase):
    """Schéma pour la création d'une tentative de résolution de défi logique"""

    pass


class ChallengeAttemptRequest(BaseModel):
    """
    Payload pour POST /api/challenges/{id}/attempt.
    Accepte 'answer' ou 'user_solution'. hints_used: liste ou entier (→ count).
    """

    user_solution: str = Field(..., description="Réponse fournie (alias: answer)")
    time_spent: Optional[float] = Field(
        None, ge=0.0, description="Temps passé en secondes"
    )
    hints_used: Optional[Union[List[Any], int]] = Field(
        None, description="Indices utilisés: liste ou entier"
    )

    @model_validator(mode="before")
    @classmethod
    def accept_answer_alias(cls, data: Any) -> Any:
        """Accepte 'answer' comme alias de 'user_solution' (compat frontend)."""
        if isinstance(data, dict):
            sol = data.get("user_solution") or data.get("answer")
            if sol is not None:
                data = {**data, "user_solution": str(sol).strip() if sol else ""}
        return data

    @field_validator("user_solution")
    @classmethod
    def answer_not_empty(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("Réponse requise")
        return v

    @property
    def hints_used_count(self) -> int:
        """Nombre d'indices utilisés (liste→len, int→valeur, sinon 0)."""
        if self.hints_used is None:
            return 0
        if isinstance(self.hints_used, list):
            return len(self.hints_used)
        if isinstance(self.hints_used, int):
            return self.hints_used
        return 0


class LogicChallengeAttemptUpdate(BaseModel):
    """Schéma pour la mise à jour d'une tentative de résolution"""

    user_solution: Optional[str] = None
    is_correct: Optional[bool] = None
    time_spent: Optional[float] = Field(None, ge=0.0)
    hints_used: Optional[List[int]] = None
    notes: Optional[str] = None

    @field_validator("user_solution")
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


class ChallengeListItem(BaseModel):
    """Un challenge dans la liste GET /api/challenges."""

    id: int
    title: str
    description: str
    challenge_type: str
    age_group: str
    difficulty_tier: Optional[int] = None
    difficulty: Optional[str] = None
    tags: Optional[str] = None
    difficulty_rating: Optional[float] = None
    estimated_time_minutes: Optional[int] = None
    success_rate: Optional[float] = None
    view_count: int = 0
    is_archived: bool = False


class ChallengeListResponse(BaseModel):
    """Réponse paginée GET /api/challenges."""

    items: List[ChallengeListItem]
    total: int
    page: int
    limit: int
    hasMore: bool


class ChallengeHintResponse(BaseModel):
    """Réponse GET /api/challenges/{id}/hint."""

    hint: str = Field(..., description="Indice demandé")


ChallengeAgeGroupSourceLiteral = Literal["explicit", "profile", "fallback"]


class ChallengeStreamPersonalizationMeta(BaseModel):
    """Métadonnées F42 pour prompts, calibration et audit ``generation_parameters``."""

    explicit_age_group: Optional[str] = Field(None, max_length=64)
    user_context_age_group: str = Field(
        default="tous-ages",
        max_length=64,
        description="Tranche d'âge issue du contexte reco profil (peut être tous-ages).",
    )
    age_group_source: ChallengeAgeGroupSourceLiteral = Field(
        default="fallback",
        description="explicit = âge choisi dans l'UI ; profile = profil F42 ; fallback = enveloppe par défaut.",
    )
    target_pedagogical_band: str = Field(
        default="learning",
        max_length=32,
        description="Bande pédagogique (discovery / learning / consolidation).",
    )
    user_target_difficulty_tier: Optional[int] = Field(
        None, ge=1, le=12, description="Tier profil avant recalcul éventuel."
    )
    resolved_target_tier: Optional[int] = Field(
        None,
        ge=1,
        le=12,
        description="Tier effectif pour la génération (âge résolu × bande).",
    )
    target_difficulty_rating_hint: Optional[float] = Field(
        None, ge=1.0, le=5.0, description="Hint 1–5 pour la policy de difficulté."
    )
    calibration_text: str = Field(
        default="",
        max_length=2000,
        description="Texte de calibrage F42 injecté dans le prompt système.",
    )

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class GenerateChallengeStreamPostBody(BaseModel):
    """Corps JSON POST /api/challenges/generate-ai-stream (contrat symétrique aux exercices)."""

    challenge_type: str = Field(default="sequence", max_length=64)
    age_group: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Omis ou null : résolution via le profil utilisateur authentifié (F42).",
    )
    prompt: str = Field(default="", max_length=8000)

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class GenerateChallengeStreamQuery(BaseModel):
    """Paramètres préparés pour la génération IA streaming (LOT 3 boundary)."""

    challenge_type: str = Field(
        ..., description="Type normalisé (sequence, pattern, etc.)"
    )
    age_group: str = Field(
        ..., description="Groupe d'âge format service (6-8, 9-11, etc.)"
    )
    prompt: str = Field(default="", description="Prompt utilisateur sanitized")
    user_id: Optional[int] = Field(None, description="ID utilisateur authentifié")
    locale: str = Field(default="fr", description="Locale (Accept-Language résolu)")
    personalization: Optional[ChallengeStreamPersonalizationMeta] = Field(
        None,
        description="Contexte F42 (audit + calibration) — champs additifs, non requis par les clients.",
    )


class LogicChallengeStats(BaseModel):
    """Statistiques sur un défi logique"""

    challenge_id: int
    view_count: int
    attempt_count: int
    success_rate: float
    average_time: Optional[float] = None
    hint_usage_rate: Optional[Dict[str, float]] = (
        None  # Taux d'utilisation de chaque niveau d'indice
    )

    model_config = ConfigDict(from_attributes=True)


class LogicChallengeAttemptResult(BaseModel):
    """Résultat d'une tentative de résolution d'un défi logique"""

    is_correct: bool = Field(..., description="Si la réponse est correcte")
    feedback: str = Field(..., description="Retour sur la tentative")
    explanation: Optional[str] = Field(
        None, description="Explication de la solution (si correct)"
    )
    hints: Optional[List[str]] = Field(
        None, description="Indices pour aider (si incorrect)"
    )

    model_config = ConfigDict(from_attributes=True)


# --- DTOs use case Attempt (LOT B1) ---


class SubmitChallengeAttemptCommand(BaseModel):
    """Commande pour soumettre une tentative de défi logique."""

    challenge_id: int = Field(..., description="ID du défi")
    user_id: int = Field(..., description="ID de l'utilisateur")
    user_solution: str = Field(..., description="Réponse fournie")
    time_spent: Optional[float] = Field(
        None, ge=0.0, description="Temps passé en secondes"
    )
    hints_used_count: int = Field(0, ge=0, description="Nombre d'indices utilisés")


class ChallengeBadgeEarned(BaseModel):
    """Badge débloqué lors d'une tentative (contrat API préservé)."""

    badge_id: Optional[int] = Field(None, serialization_alias="id")
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    thematic_title: Optional[str] = Field(
        None,
        description=(
            "Libellé narratif optionnel du badge (clé publique préférée, F43-A4). "
            "Même valeur que la colonne persistée `achievements.star_wars_title`."
        ),
    )
    star_wars_title: Optional[str] = Field(
        None,
        description=(
            "Alias legacy (F43-A4) — même valeur que `thematic_title` ; conservé pour "
            "compatibilité clients ; ne pas privilégier pour les nouveaux intégrateurs."
        ),
    )
    difficulty: Optional[str] = None
    points_reward: Optional[int] = None
    earned_at: Optional[str] = None


class ChallengeProgressNotification(BaseModel):
    """Notification de progression vers un badge (contrat historique: name, remaining)."""

    name: Optional[str] = None
    remaining: Optional[int] = None


class SubmitChallengeAttemptResult(BaseModel):
    """Résultat de la soumission d'une tentative (POST /api/challenges/{id}/attempt)."""

    is_correct: bool = Field(..., description="Si la réponse est correcte")
    explanation: Optional[str] = Field(None, description="Explication (si correct)")
    new_badges: List[ChallengeBadgeEarned] = Field(
        default_factory=list, description="Nouveaux badges débloqués"
    )
    progress_notification: Optional[ChallengeProgressNotification] = Field(
        None, description="Progression vers le prochain badge"
    )
    hints_remaining: Optional[int] = Field(
        None, description="Indices restants (si incorrect)"
    )
    points_earned: Optional[int] = Field(
        None,
        description="Points crédités sur cette tentative (défi correct, attribution réussie)",
    )


# --- DTO use case Stream (LOT B1) ---


class PrepareStreamContextResult(BaseModel):
    """Résultat de la préparation du contexte SSE génération IA."""

    query: Optional[GenerateChallengeStreamQuery] = None
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error_message is None
