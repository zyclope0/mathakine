"""
Schémas Pydantic pour les sessions utilisateur
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class UserSessionBase(BaseModel):
    """Schéma de base pour une session utilisateur"""

    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location_data: Optional[Dict[str, Any]] = None


class UserSessionInDB(UserSessionBase):
    """Schéma pour une session en base de données (avec tous les champs)"""

    id: int
    user_id: int
    session_token: str
    is_active: bool
    last_activity: datetime
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSession(BaseModel):
    """Schéma pour une session utilisateur (réponse API)"""

    id: int
    device_info: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location_data: Optional[Dict[str, Any]] = None
    is_active: bool
    last_activity: datetime
    created_at: datetime
    expires_at: datetime
    is_current: bool = False  # Pour indiquer si c'est la session actuelle

    model_config = ConfigDict(from_attributes=True)


class UserSessionRevoke(BaseModel):
    """Schéma pour la révocation d'une session"""

    success: bool
    message: str
