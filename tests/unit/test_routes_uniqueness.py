"""
Test d'unicité des routes API : détecte les collisions method+path.

Si deux routes partagent le même (method, path), Starlette peut router
vers la mauvaise handler. Ce test échoue en cas de collision.
"""
import pytest
from starlette.routing import Mount, Route

from server.routes import get_routes


def _collect_routes(routes, prefix: str = "") -> list[tuple[str, str]]:
    """Extrait tous les (method, path) depuis get_routes(), y compris sous-Mount."""
    result = []
    for r in routes:
        if isinstance(r, Route):
            path = prefix + r.path
            for method in r.methods:
                result.append((method, path))
        elif isinstance(r, Mount):
            mount_path = r.path.rstrip("/")
            for child in r.routes:
                if isinstance(child, Route):
                    child_path = f"{mount_path}{child.path}"
                    for method in child.methods:
                        result.append((method, child_path))
                # Mount imbriqué non utilisé dans notre code
    return result


@pytest.mark.unit
def test_no_route_collision_method_path():
    """Aucune route ne doit partager le même (method, path)."""
    routes = get_routes()
    pairs = _collect_routes(routes)

    seen: dict[tuple[str, str], int] = {}
    duplicates = []
    for i, (method, path) in enumerate(pairs):
        key = (method, path)
        if key in seen:
            duplicates.append((method, path, seen[key], i))
        else:
            seen[key] = i

    assert not duplicates, (
        f"Collisions method+path détectées: {duplicates}. "
        "Chaque (method, path) doit être unique."
    )
