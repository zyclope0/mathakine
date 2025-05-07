from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict, Generic, TypeVar, Union
from enum import Enum

# Type générique pour les réponses
T = TypeVar('T')

class StatusCode(str, Enum):
    """Codes d'état standardisés pour l'API (Codes de Transmission)"""
    SUCCESS = "success"  # Succès
    ERROR = "error"      # Erreur
    WARNING = "warning"  # Avertissement
    INFO = "info"        # Information

class ErrorCode(str, Enum):
    """Codes d'erreur standardisés (Codes de Défaillance)"""
    NOT_FOUND = "not_found"                 # Ressource non trouvée
    ALREADY_EXISTS = "already_exists"       # Conflit, ressource déjà existante
    VALIDATION_ERROR = "validation_error"   # Erreur de validation des données
    AUTHENTICATION_ERROR = "auth_error"     # Erreur d'authentification
    PERMISSION_ERROR = "permission_error"   # Erreur de permission
    SERVER_ERROR = "server_error"           # Erreur serveur interne
    DATABASE_ERROR = "database_error"       # Erreur de base de données
    EXTERNAL_API_ERROR = "external_error"   # Erreur d'API externe
    RATE_LIMIT_ERROR = "rate_limit"         # Limite de taux dépassée
    INVALID_OPERATION = "invalid_operation" # Opération invalide

class PageInfo(BaseModel):
    """Information de pagination (Coordonnées de Navigation)"""
    page: int = Field(..., ge=1, description="Page actuelle")
    page_size: int = Field(..., ge=1, description="Nombre d'éléments par page")
    total_pages: int = Field(..., ge=0, description="Nombre total de pages")
    total_items: int = Field(..., ge=0, description="Nombre total d'éléments")
    has_next: bool = Field(..., description="S'il existe une page suivante")
    has_prev: bool = Field(..., description="S'il existe une page précédente")

class ResponseMeta(BaseModel):
    """Métadonnées de réponse (Données de Transmission)"""
    code: StatusCode
    message: str = Field(..., description="Message décrivant le résultat de l'opération")
    error_code: Optional[ErrorCode] = Field(None, description="Code d'erreur si applicable")
    pagination: Optional[PageInfo] = Field(None, description="Information de pagination si applicable")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Informations de débogage (en mode debug uniquement)")

class Response(BaseModel, Generic[T]):
    """Réponse API standard (Transmission Galactique)"""
    meta: ResponseMeta
    data: Optional[T] = Field(None, description="Données de la réponse")

class ListResponse(Response[List[T]], Generic[T]):
    """Réponse API pour listes paginées (Liste de Transmission)"""
    data: List[T] = Field(..., description="Liste des éléments")

class ValidationError(BaseModel):
    """Détails d'une erreur de validation (Rapport d'Anomalie)"""
    field: str = Field(..., description="Champ concerné par l'erreur")
    message: str = Field(..., description="Message d'erreur")
    code: Optional[str] = Field(None, description="Code d'erreur spécifique")

class ErrorResponse(BaseModel):
    """Réponse d'erreur détaillée (Rapport de Défaillance)"""
    meta: ResponseMeta
    errors: Optional[List[ValidationError]] = Field(None, description="Liste détaillée des erreurs de validation")

class HealthCheck(BaseModel):
    """État de santé de l'API (État des Systèmes)"""
    status: str = Field(..., description="État général du service")
    version: str = Field(..., description="Version de l'API")
    uptime: float = Field(..., description="Temps de fonctionnement en secondes")
    database_status: str = Field(..., description="État de la base de données")
    environment: str = Field(..., description="Environnement d'exécution")
    dependencies: Dict[str, str] = Field(..., description="État des dépendances externes") 