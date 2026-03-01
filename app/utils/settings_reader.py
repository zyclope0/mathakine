"""
Lecture des paramètres globaux (table settings).
Utilisé par middleware et handlers pour maintenance_mode, registration_enabled, etc.
"""

from app.models.setting import Setting
from app.utils.db_utils import db_session


async def get_setting_bool(key: str, default: bool = False) -> bool:
    """Lit une valeur booléenne depuis la table settings."""
    async with db_session() as db:
        row = db.query(Setting).filter(Setting.key == key).first()
        if not row or row.value is None:
            return default
        # Accès à row.value DANS le context manager (évite DetachedInstanceError)
        return str(row.value).lower() in ("true", "1", "yes", "on")
