"""
Routes API pour Mathakine (backend Starlette).

Agrège les routes par domaine pour la maintenabilité.
Chaque module routes/* expose get_xxx_routes().
"""

from typing import List

from starlette.routing import Mount, Route

from server.routes.admin import get_admin_routes
from server.routes.auth import get_auth_routes
from server.routes.badges import get_badges_routes
from server.routes.challenges import get_challenges_routes
from server.routes.core import get_core_routes
from server.routes.exercises import get_exercises_routes
from server.routes.misc import get_misc_routes
from server.routes.users import get_users_routes


def get_routes() -> List:
    """
    Retourne la liste complète des routes API.
    """
    routes: List = []
    routes.extend(get_core_routes())
    routes.extend(get_auth_routes())
    routes.extend(get_users_routes())
    routes.extend(get_exercises_routes())
    routes.extend(get_badges_routes())
    routes.extend(get_admin_routes())
    routes.extend(get_misc_routes())
    routes.extend(get_challenges_routes())
    return routes
