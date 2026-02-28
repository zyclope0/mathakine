"""
Parsing des paramètres pour les listes admin (users, exercises, challenges).
"""

from dataclasses import dataclass
from typing import Optional

from starlette.requests import Request

from app.utils.pagination import parse_pagination_params


@dataclass
class AdminUsersParams:
    search: str
    role: str
    is_active: Optional[bool]
    skip: int
    limit: int


def parse_admin_users_params(request: Request) -> AdminUsersParams:
    """Parse GET /api/admin/users."""
    q = dict(request.query_params)
    search = (q.get("search") or "").strip()
    role = (q.get("role") or "").strip().lower()
    is_active_param = q.get("is_active")
    is_active = (
        str(is_active_param).lower() in ("true", "1", "yes")
        if is_active_param is not None
        else None
    )
    skip, limit = parse_pagination_params(q, default_limit=20, max_limit=100)
    return AdminUsersParams(
        search=search, role=role, is_active=is_active, skip=skip, limit=limit
    )


@dataclass
class AdminListParams:
    """Params communs : search, sort, order, skip, limit, archived."""

    search: str
    sort: str
    order: str
    skip: int
    limit: int
    archived: Optional[bool]


def _parse_archived(query_params: dict) -> Optional[bool]:
    p = query_params.get("archived")
    if p is None:
        return None
    return str(p).lower() in ("true", "1", "yes")


def parse_admin_exercises_params(
    request: Request,
) -> tuple[AdminListParams, Optional[str]]:
    """Parse GET /api/admin/exercises. Returns (base_params, exercise_type)."""
    q = dict(request.query_params)
    search = (q.get("search") or "").strip()
    sort = (q.get("sort") or "created_at").strip().lower()
    order = (q.get("order") or "desc").strip().lower()
    skip, limit = parse_pagination_params(q, default_limit=20, max_limit=100)
    archived = _parse_archived(q)
    exercise_type = (q.get("type") or "").strip().upper() or None
    base = AdminListParams(
        search=search, sort=sort, order=order, skip=skip, limit=limit, archived=archived
    )
    return base, exercise_type


def parse_admin_challenges_params(
    request: Request,
) -> tuple[AdminListParams, Optional[str]]:
    """Parse GET /api/admin/challenges. Returns (base_params, challenge_type)."""
    q = dict(request.query_params)
    search = (q.get("search") or "").strip()
    sort = (q.get("sort") or "created_at").strip().lower()
    order = (q.get("order") or "desc").strip().lower()
    skip, limit = parse_pagination_params(q, default_limit=20, max_limit=100)
    archived = _parse_archived(q)
    challenge_type = (q.get("type") or "").strip().lower() or None
    base = AdminListParams(
        search=search, sort=sort, order=order, skip=skip, limit=limit, archived=archived
    )
    return base, challenge_type
