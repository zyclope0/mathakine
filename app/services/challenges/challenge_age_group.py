"""
Mapping des groupes d'âge challenge (frontend ↔ DB).

Extrait de challenge_service (I4) pour éviter la densité et permettre
une réutilisation par challenge_api_mapper sans dépendance circulaire.
"""

from app.core.logging_config import get_logger
from app.models.logic_challenge import AgeGroup

logger = get_logger(__name__)

# Mapping des groupes d'âge frontend vers les valeurs ENUM PostgreSQL
FRONTEND_TO_DB_AGE_GROUP = {
    "6-8": AgeGroup.GROUP_6_8,
    "9-11": AgeGroup.GROUP_10_12,
    "12-14": AgeGroup.GROUP_13_15,
    "15-17": AgeGroup.GROUP_15_17,
    "adulte": AgeGroup.ADULT,
    "tous-ages": AgeGroup.ALL_AGES,
    "10-12": AgeGroup.GROUP_10_12,
    "13-15": AgeGroup.GROUP_13_15,
    "all": AgeGroup.ALL_AGES,
    "enfant": AgeGroup.GROUP_6_8,
    "adolescent": AgeGroup.GROUP_13_15,
    "9-12": AgeGroup.GROUP_10_12,
    "12-13": AgeGroup.GROUP_13_15,
    "13+": AgeGroup.GROUP_15_17,
    "group_6_8": AgeGroup.GROUP_6_8,
    "group_10_12": AgeGroup.GROUP_10_12,
    "group_13_15": AgeGroup.GROUP_13_15,
    "group_15_17": AgeGroup.GROUP_15_17,
    "adult": AgeGroup.ADULT,
    "all_ages": AgeGroup.ALL_AGES,
}

# Mapping inverse : ENUM PostgreSQL vers format frontend
DB_TO_FRONTEND_AGE_GROUP = {
    AgeGroup.GROUP_6_8: "6-8",
    AgeGroup.GROUP_10_12: "9-11",
    AgeGroup.GROUP_13_15: "12-14",
    AgeGroup.GROUP_15_17: "15-17",
    AgeGroup.ADULT: "adulte",
    AgeGroup.ALL_AGES: "tous-ages",
}


def normalize_age_group_for_db(age_group: str) -> AgeGroup:
    """
    Convertit un groupe d'âge frontend vers une valeur ENUM PostgreSQL.
    """
    if not age_group:
        return AgeGroup.ALL_AGES
    age_group_lower = age_group.lower().strip()
    if age_group_lower in FRONTEND_TO_DB_AGE_GROUP:
        return FRONTEND_TO_DB_AGE_GROUP[age_group_lower]
    try:
        return AgeGroup(age_group_lower)
    except ValueError:
        pass
    logger.warning("Groupe d'âge non reconnu: {}, utilisation de ALL_AGES", age_group)
    return AgeGroup.ALL_AGES


def normalize_age_group_for_frontend(age_group) -> str:
    """
    Convertit une valeur ENUM PostgreSQL vers le format frontend.
    """
    if not age_group:
        return "tous-ages"
    if isinstance(age_group, str):
        age_group_lower = age_group.lower()
        for ag_enum, frontend_val in DB_TO_FRONTEND_AGE_GROUP.items():
            if ag_enum.value == age_group_lower or ag_enum.name == age_group.upper():
                return frontend_val
        return "tous-ages"
    return DB_TO_FRONTEND_AGE_GROUP.get(age_group, "tous-ages")
