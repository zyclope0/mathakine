"""
Tranches d'âge pédagogiques persistées sur le profil utilisateur (F42 phase 1).

Valeurs stables pour API / DB (alignées contenu exercices / défis).
"""

from __future__ import annotations

from typing import FrozenSet, Optional

from app.core.constants import normalize_age_group

# Libellés UX « espace » réservés au dashboard parent (ROADMAP) — pas utilisés ici.
USER_AGE_GROUP_VALUES: FrozenSet[str] = frozenset({"6-8", "9-11", "12-14", "15+"})


def normalized_age_group_from_user_profile(user) -> Optional[str]:
    """
    F42 — Priorité du groupe d'âge persisté sur ``users.age_group``.

    Si la colonne est renseignée, renvoie la forme canonique (``normalize_age_group``).
    Sinon ``None`` : les appelants appliquent les fallbacks (grade, préférences, etc.).
    """
    raw = getattr(user, "age_group", None)
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    return normalize_age_group(s)
