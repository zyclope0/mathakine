"""
Constantes spécifiques aux défis logiques (LogicChallenge).

Extrait de constants.py — Phase 4, item 4.2 — audit architecture 03/2026.
Ce module peut être importé directement :
    from app.core.constants_challenge import CHALLENGE_TYPES_DB, normalize_challenge_type
"""

from app.core.logging_config import get_logger
from app.models.logic_challenge import AgeGroup

logger = get_logger(__name__)

# Types de challenges (valeurs PostgreSQL ENUM)
CHALLENGE_TYPES_DB = [
    "SEQUENCE",
    "PATTERN",
    "VISUAL",
    "PUZZLE",
    "GRAPH",
    "RIDDLE",
    "DEDUCTION",
    "CHESS",
    "CODING",
    "PROBABILITY",
]

CHALLENGE_TYPES_API = [
    "sequence",
    "pattern",
    "visual",
    "puzzle",
    "graph",
    "riddle",
    "deduction",
    "chess",
    "coding",
    "probability",
]

# Mapping pour la normalisation des types de challenge
CHALLENGE_TYPE_ALIASES = {
    "SEQUENCE": ["sequence", "seq", "suite", "séquence"],
    "PATTERN": ["pattern", "motif", "grille"],
    "VISUAL": ["visual", "visuel", "spatial", "forme", "formes"],
    "PUZZLE": ["puzzle", "casse-tete", "casse-tête"],
    "GRAPH": ["graph", "graphe", "reseau", "réseau", "chemin"],
    "RIDDLE": ["riddle", "enigme", "énigme"],
    "DEDUCTION": ["deduction", "déduction", "logique", "logic"],
    "CHESS": ["chess", "echecs", "échecs", "echiquier", "échiquier"],
    "CODING": ["coding", "codage", "crypto", "cryptographie", "labyrinthe", "maze"],
    "PROBABILITY": ["probability", "probabilite", "probabilité", "proba", "chance"],
}


def normalize_challenge_type(challenge_type):
    """
    Normalise le type de challenge vers le format DB (MAJUSCULE).

    Returns:
        Le type normalisé en majuscule (ex: "SEQUENCE") ou None si non reconnu.
    """
    if not challenge_type:
        return None

    challenge_type_str = str(challenge_type).lower().strip()

    if challenge_type_str in CHALLENGE_TYPES_API:
        return challenge_type_str.upper()

    if challenge_type_str.upper() in CHALLENGE_TYPES_DB:
        return challenge_type_str.upper()

    for type_key, aliases in CHALLENGE_TYPE_ALIASES.items():
        for alias in aliases:
            if challenge_type_str == alias.lower():
                return type_key

    logger.warning(f"Type de challenge non reconnu: '{challenge_type}'")
    return None


# Groupes d'âge pour les challenges (valeurs ENUM PostgreSQL)
AGE_GROUPS_DB = [e.value for e in AgeGroup]
