"""
TypedDict centralisés pour les retours de services.

Remplace les Dict[str, Any] génériques par des types vérifiables statiquement.
Phase 2, item 2.9 — audit architecture 03/2026.
"""

from typing import Any, Dict, List, TypedDict


class TokenResponse(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: int


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
    progress_over_time: Dict[str, Any]
    exercises_by_day: Dict[str, Any]
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
