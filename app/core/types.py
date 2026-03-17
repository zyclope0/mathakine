"""
TypedDict centralisés pour les retours de services.

Remplace les Dict[str, Any] génériques par des types vérifiables statiquement.
Phase 2, item 2.9 — audit architecture 03/2026.
Phase 4, item 4.1 — complétion TypedDict services (03/2026).
"""

from typing import Any, Dict, List, Optional, Tuple, TypedDict

# ── Admin badge create flow (F3, F4) ─────────────────────────────────────────


class BadgeCreatePrepared(TypedDict):
    """Données normalisées pour création badge admin (flux F3)."""

    code: str
    name: str
    description: Optional[str]
    icon_url: Optional[str]
    category: Optional[str]
    difficulty: str
    points_reward: int
    is_secret: bool
    requirements: Optional[Dict[str, Any]]
    star_wars_title: Optional[str]


ValidationResult = Tuple[Optional[str], int]
"""Résultat validation : (error_message, status_code) ou (None, 0) si valide."""


# ── Auth / tokens ────────────────────────────────────────────────────────────


class TokenResponse(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: Optional[int]


class TokenRefreshResponse(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str


class PaginatedResponse(TypedDict):
    items: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int


class DashboardStats(TypedDict):
    total_exercises: int
    total_challenges: int
    correct_answers: int
    success_rate: float
    experience_points: int
    performance_by_type: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    level: Dict[str, Any]
    progress_over_time: "ChartData"
    exercises_by_day: "ChartData"
    lastUpdated: str


class PerformanceByType(TypedDict):
    completed: int
    correct: int
    success_rate: float


class ChartDataset(TypedDict, total=False):
    label: str
    data: List[Any]
    borderColor: str
    backgroundColor: str


class ChartData(TypedDict):
    labels: List[str]
    datasets: List[ChartDataset]


# ── Progression utilisateur ──────────────────────────────────────────────────


class UserProgressDict(TypedDict):
    total_attempts: int
    correct_attempts: int
    accuracy: float
    average_time: float
    exercises_completed: int
    highest_streak: int
    current_streak: int
    by_category: Dict[str, Any]


class ChallengesProgressDict(TypedDict):
    completed_challenges: int
    total_challenges: int
    success_rate: float
    average_time: float
    challenges: List[Dict[str, Any]]


# ── Statistiques challenges ──────────────────────────────────────────────────


class ChallengeStatsDict(TypedDict, total=False):
    challenge_id: int
    title: str
    total_attempts: int
    correct_attempts: int
    success_rate: float
    unique_users: int
    difficulty_rating: Optional[float]


# ── Administration — stats / logs / modération ───────────────────────────────


class AuditLogItemDict(TypedDict):
    id: int
    admin_user_id: Optional[int]
    admin_username: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[Dict[str, Any]]
    created_at: Optional[str]


class AuditLogPageDict(TypedDict):
    items: List[AuditLogItemDict]
    total: int


class ModerationDict(TypedDict):
    exercises: List[Dict[str, Any]]
    challenges: List[Dict[str, Any]]
    total_exercises: int
    total_challenges: int


class AdminReportDict(TypedDict):
    period: str
    days: int
    new_users: int
    attempts_exercises: int
    attempts_challenges: int
    total_attempts: int
    success_rate: float
    active_users: int


# ── Administration — listes utilisateurs ─────────────────────────────────────


class AdminUserItemDict(TypedDict):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: Optional[str]


class AdminUserListDict(TypedDict):
    items: List[AdminUserItemDict]
    total: int
