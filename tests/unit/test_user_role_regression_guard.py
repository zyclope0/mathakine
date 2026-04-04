from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

FILES_THAT_MUST_USE_CANONICAL_USER_ROLES = [
    REPO_ROOT / "app" / "schemas" / "user.py",
    REPO_ROOT / "app" / "schemas" / "admin.py",
    REPO_ROOT / "app" / "services" / "auth" / "auth_service.py",
    REPO_ROOT / "app" / "services" / "auth" / "auth_session_service.py",
    REPO_ROOT / "app" / "services" / "users" / "user_service.py",
    REPO_ROOT / "app" / "services" / "admin" / "admin_content_service.py",
    REPO_ROOT / "server" / "auth.py",
    REPO_ROOT / "server" / "handlers" / "admin_handlers.py",
    REPO_ROOT / "server" / "routes" / "admin.py",
    REPO_ROOT / "frontend" / "types" / "api.ts",
    REPO_ROOT / "frontend" / "hooks" / "useAuth.ts",
    REPO_ROOT / "frontend" / "hooks" / "useAdminUsers.ts",
    REPO_ROOT / "frontend" / "components" / "auth" / "ProtectedRoute.tsx",
    REPO_ROOT / "frontend" / "components" / "layout" / "Header.tsx",
    REPO_ROOT / "frontend" / "components" / "layout" / "MaintenanceOverlay.tsx",
    REPO_ROOT / "frontend" / "app" / "dashboard" / "page.tsx",
    REPO_ROOT / "frontend" / "app" / "home-learner" / "page.tsx",
    REPO_ROOT / "frontend" / "app" / "admin" / "layout.tsx",
    REPO_ROOT / "frontend" / "app" / "admin" / "page.tsx",
    REPO_ROOT / "frontend" / "app" / "admin" / "users" / "page.tsx",
]

LEGACY_USER_ROLE_NAMES = ("padawan", "maitre", "gardien", "archiviste")


def test_active_user_role_boundaries_do_not_reference_legacy_names_outside_compat_layers():
    offenders: list[str] = []

    for path in FILES_THAT_MUST_USE_CANONICAL_USER_ROLES:
        content = path.read_text(encoding="utf-8")
        lower_content = content.lower()
        matches = [legacy_name for legacy_name in LEGACY_USER_ROLE_NAMES if legacy_name in lower_content]
        if matches:
            offenders.append(f"{path.relative_to(REPO_ROOT)} -> {', '.join(matches)}")

    assert offenders == [], (
        "Des noms legacy de rôles utilisateur subsistent dans le code actif hors couches de compatibilité :\n"
        + "\n".join(offenders)
    )
