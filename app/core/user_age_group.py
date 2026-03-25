"""
Tranches d'âge pédagogiques persistées sur le profil utilisateur (F42 phase 1).

Valeurs stables pour API / DB (alignées contenu exercices / défis).
"""

from typing import FrozenSet

# Libellés UX « espace » réservés au dashboard parent (ROADMAP) — pas utilisés ici.
USER_AGE_GROUP_VALUES: FrozenSet[str] = frozenset({"6-8", "9-11", "12-14", "15+"})
