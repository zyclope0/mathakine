"""
Constants centralisées pour l'application Mathakine.

Architecture (Phase 4, item 4.2) :
- constants_challenge.py : constantes domaine LogicChallenge (types, aliases, normalize)
- constants.py          : hub re-exportant tout + domaines exercise/age/user/config
"""

# Re-export du domaine challenge depuis son module dédié
from app.core.constants_challenge import (  # noqa: F401
    AGE_GROUPS_DB,
    CHALLENGE_TYPE_ALIASES,
    CHALLENGE_TYPES_API,
    CHALLENGE_TYPES_DB,
    normalize_challenge_type,
)
from app.core.logging_config import get_logger
from app.models.exercise import DifficultyLevel, ExerciseType
from app.models.logic_challenge import AgeGroup

logger = get_logger(__name__)


# Types d'exercices - compatible avec l'enum ExerciseType
class ExerciseTypes:
    ADDITION = ExerciseType.ADDITION.value
    SUBTRACTION = ExerciseType.SOUSTRACTION.value
    SOUSTRACTION = ExerciseType.SOUSTRACTION.value  # Alias pour compatibilité
    MULTIPLICATION = ExerciseType.MULTIPLICATION.value
    DIVISION = ExerciseType.DIVISION.value
    FRACTIONS = ExerciseType.FRACTIONS.value
    GEOMETRIE = ExerciseType.GEOMETRIE.value
    TEXTE = ExerciseType.TEXTE.value
    MIXTE = ExerciseType.MIXTE.value
    MIXED = ExerciseType.MIXTE.value  # Alias pour compatibilité
    DIVERS = ExerciseType.DIVERS.value

    ALL_TYPES = [
        ADDITION,
        SUBTRACTION,
        MULTIPLICATION,
        DIVISION,
        FRACTIONS,
        GEOMETRIE,
        TEXTE,
        MIXTE,
        DIVERS,
    ]

    # Mapping pour la normalisation des types
    TYPE_ALIASES = {
        ADDITION: [ADDITION, "addition", "add", "+", "plus"],
        SUBTRACTION: [SUBTRACTION, "soustraction", "subtract", "sub", "-", "minus"],
        MULTIPLICATION: [
            MULTIPLICATION,
            "multiplication",
            "multiply",
            "mult",
            "times",
            "*",
            "×",
        ],
        DIVISION: [DIVISION, "division", "divide", "div", "/", "÷"],
        FRACTIONS: [FRACTIONS, "fractions", "fraction", "frac"],
        GEOMETRIE: [GEOMETRIE, "geometrie", "geometry", "geo"],
        TEXTE: [TEXTE, "texte", "text", "question"],
        MIXTE: [MIXTE, "mixte", "mixed", "combiné", "combine"],
        DIVERS: [DIVERS, "divers", "misc", "other"],
    }


# Niveaux de difficulté - compatible avec l'enum DifficultyLevel
class DifficultyLevels:
    INITIE = DifficultyLevel.INITIE.value
    PADAWAN = DifficultyLevel.PADAWAN.value
    CHEVALIER = DifficultyLevel.CHEVALIER.value
    MAITRE = DifficultyLevel.MAITRE.value
    GRAND_MAITRE = DifficultyLevel.GRAND_MAITRE.value

    ALL_LEVELS = [INITIE, PADAWAN, CHEVALIER, MAITRE, GRAND_MAITRE]

    # Mapping pour la normalisation des niveaux
    LEVEL_ALIASES = {
        INITIE: [INITIE, "initié", "initie", "easy", "facile", "debutant", "débutant"],
        PADAWAN: [
            PADAWAN,
            "padawan",
            "medium",
            "moyen",
            "intermediaire",
            "intermédiaire",
        ],
        CHEVALIER: [CHEVALIER, "chevalier", "hard", "difficile", "avance", "avancé"],
        MAITRE: [
            MAITRE,
            "maitre",
            "maître",
            "expert",
            "très difficile",
            "tres difficile",
        ],
        GRAND_MAITRE: [
            GRAND_MAITRE,
            "grand maitre",
            "grand maître",
            "grandmaitre",
            "master",
            "adulte",
        ],
    }


# Groupes d'âge pour les exercices
# NOMENCLATURE OFFICIELLE : alignée avec le système scolaire français et le frontend
# - 6-8 ans : CP-CE2 (cycle 2)
# - 9-11 ans : CM1-CM2-6e (fin cycle 2, début cycle 3)
# - 12-14 ans : 5e-4e-3e (cycle 4, collège)
# - 15-17 ans : Lycée
class AgeGroups:
    GROUP_6_8 = "6-8"
    GROUP_9_11 = "9-11"
    GROUP_12_14 = "12-14"
    GROUP_15_17 = "15-17"
    ADULT = "adulte"
    ALL_AGES = "tous-ages"

    ALL_GROUPS = [GROUP_6_8, GROUP_9_11, GROUP_12_14, GROUP_15_17, ADULT, ALL_AGES]

    # Mapping pour la normalisation des groupes d'âge
    # Inclut tous les formats possibles du frontend et de l'API (age_*, GROUP_* pour challenges)
    AGE_ALIASES = {
        GROUP_6_8: [
            "6-8",
            "6-8 ans",
            "6 to 8 ans",
            "6_8",
            "group_6_8",
            "GROUP_6_8",
            "age_6_8",
            "6-8ans",
        ],
        GROUP_9_11: [
            "9-11",
            "9-11 ans",
            "9 to 11 ans",
            "9_11",
            "group_9_11",
            "GROUP_9_12",
            "GROUP_10_12",
            "age_9_12",
            "age_10_12",
            "9-11ans",
            "10-12",
        ],
        GROUP_12_14: [
            "12-14",
            "12-14 ans",
            "12 to 14 ans",
            "12_14",
            "group_12_14",
            "GROUP_13_15",
            "age_13_15",
            "12-14ans",
            "13-15",
        ],
        GROUP_15_17: [
            "15-17",
            "15-17 ans",
            "15 to 17 ans",
            "15_17",
            "group_15_17",
            "GROUP_16_18",
            "GROUP_15_17",
            "age_16_18",
            "15-17ans",
        ],
        ADULT: ["adulte", "adultes", "adult", "adults", "18+", "majeur"],
        ALL_AGES: [
            "tous-ages",
            "tous ages",
            "all ages",
            "all",
            "tous",
            "all_ages",
            "tousages",
        ],
    }


# P2 — pré-calcul : dict plat {alias_normalisé: groupe} pour lookup O(1)
_AGE_GROUP_LOOKUP: dict = {}
for _group_key, _aliases in AgeGroups.AGE_ALIASES.items():
    for _alias in _aliases:
        _AGE_GROUP_LOOKUP[_alias.lower().replace(" ", "").replace("_", "-")] = (
            _group_key
        )
        _AGE_GROUP_LOOKUP[_alias.lower()] = _group_key

# Pré-calcul correspondance partielle (premier chiffre → groupe)
_AGE_GROUP_PREFIX: dict = {}
for _group_key in AgeGroups.ALL_GROUPS:
    _prefix = _group_key.split("-")[0]
    _AGE_GROUP_PREFIX[_prefix] = _group_key


def normalize_age_group(age_group):
    """
    Normalise le groupe d'âge vers le format standard (6-8, 9-11, etc.)
    Utilise un dict pré-calculé pour un lookup O(1) au lieu de O(n*m).
    """
    if not age_group:
        return AgeGroups.GROUP_9_11

    age_group_str = str(age_group).lower().strip()
    age_group_clean = age_group_str.replace(" ", "").replace("_", "-")

    result = _AGE_GROUP_LOOKUP.get(age_group_clean) or _AGE_GROUP_LOOKUP.get(
        age_group_str
    )
    if result:
        return result

    # Correspondance partielle (ex: "9" → "9-11")
    prefix = age_group_clean.split("-")[0]
    result = _AGE_GROUP_PREFIX.get(prefix)
    if result:
        return result

    logger.warning(
        f"Groupe d'âge non reconnu: '{age_group}', utilisation de {AgeGroups.GROUP_9_11} par défaut"
    )
    return AgeGroups.GROUP_9_11


def get_difficulty_from_age_group(age_group: str) -> str:
    """
    Détermine le niveau de difficulté (INITIE, PADAWAN, ...) à partir du groupe d'âge.

    Mapping :
    - 6-8 ans → INITIE (débutant)
    - 9-11 ans → PADAWAN (intermédiaire)
    - 12-14 ans → CHEVALIER (avancé)
    - 15-17 ans → MAITRE (expert)
    - adulte → GRAND_MAITRE (expert+)
    - tous-ages → PADAWAN (accessible à tous)
    """
    if age_group == AgeGroups.GROUP_6_8:
        return DifficultyLevels.INITIE
    elif age_group in [AgeGroups.GROUP_9_11, AgeGroups.ALL_AGES]:
        return DifficultyLevels.PADAWAN
    elif age_group == AgeGroups.GROUP_12_14:
        return DifficultyLevels.CHEVALIER
    elif age_group == AgeGroups.GROUP_15_17:
        return DifficultyLevels.MAITRE
    elif age_group == AgeGroups.ADULT:
        return DifficultyLevels.GRAND_MAITRE
    else:
        # Valeur par défaut si le groupe d'âge n'est pas reconnu
        logger.info(
            f"⚠️ Groupe d'âge non reconnu: {age_group}, utilisation de {DifficultyLevels.PADAWAN} par défaut"
        )
        return DifficultyLevels.PADAWAN


def calculate_difficulty_for_age_group(age_group: str) -> float:
    """
    Calcule une note de difficulté numérique (1.0 à 5.0) à partir du groupe d'âge.
    Utilisée pour les challenges qui ont un rating de difficulté numérique.

    Mapping :
    - 6-8 ans → 1.5 (facile)
    - 9-11 ans → 2.5 (moyen)
    - 12-14 ans → 3.5 (difficile)
    - 15-17 ans → 4.0 (expert)
    - adulte → 4.5 (très expert)
    - tous-ages → 2.5 (accessible à tous)
    """
    difficulty_mapping = {
        AgeGroups.GROUP_6_8: 1.5,
        AgeGroups.GROUP_9_11: 2.5,
        AgeGroups.GROUP_12_14: 3.5,
        AgeGroups.GROUP_15_17: 4.0,
        AgeGroups.ADULT: 4.5,
        AgeGroups.ALL_AGES: 2.5,
    }
    return difficulty_mapping.get(age_group, 2.5)


# Rôles d'utilisateurs
class UserRoles:
    INITIE = "initie"  # Alias pour compatibilité (niveau utilisateur, pas rôle)
    PADAWAN = "padawan"
    CHEVALIER = "chevalier"
    MAITRE = "maitre"
    GARDIEN = "gardien"
    ARCHIVISTE = "archiviste"

    ALL_ROLES = [PADAWAN, CHEVALIER, MAITRE, GARDIEN, ARCHIVISTE]

    # Mapping des permissions par rôle (hiérarchique)
    ROLE_PERMISSIONS = {
        PADAWAN: ["view_own"],
        CHEVALIER: ["view_own", "create_exercises"],
        MAITRE: ["view_own", "create_exercises", "modify_own"],
        GARDIEN: [
            "view_own",
            "view_all",
            "create_exercises",
            "modify_own",
            "modify_all",
        ],
        ARCHIVISTE: [
            "view_own",
            "view_all",
            "create_exercises",
            "modify_own",
            "modify_all",
            "delete",
            "admin",
        ],
    }


# Noms d'affichage pour les types et niveaux
DISPLAY_NAMES = {
    # Types d'exercices
    ExerciseTypes.ADDITION: "Addition",
    ExerciseTypes.SUBTRACTION: "Soustraction",
    ExerciseTypes.MULTIPLICATION: "Multiplication",
    ExerciseTypes.DIVISION: "Division",
    ExerciseTypes.FRACTIONS: "Fractions",
    ExerciseTypes.GEOMETRIE: "Géométrie",
    ExerciseTypes.TEXTE: "Question textuelle",
    ExerciseTypes.MIXTE: "Exercice mixte",
    ExerciseTypes.DIVERS: "Divers",
    # Niveaux de difficulté
    DifficultyLevels.INITIE: "Initié",
    DifficultyLevels.PADAWAN: "Padawan",
    DifficultyLevels.CHEVALIER: "Chevalier",
    DifficultyLevels.MAITRE: "Maître",
    DifficultyLevels.GRAND_MAITRE: "Grand Maître",
}

# Limites numériques par difficulté et type d'exercice
DIFFICULTY_LIMITS = {
    DifficultyLevels.INITIE: {
        ExerciseTypes.ADDITION: {"min": 1, "max": 10},
        ExerciseTypes.SUBTRACTION: {"min1": 5, "max1": 20, "min2": 1, "max2": 5},
        ExerciseTypes.MULTIPLICATION: {"min": 1, "max": 5},
        ExerciseTypes.DIVISION: {
            "min_divisor": 2,
            "max_divisor": 5,
            "min_result": 1,
            "max_result": 5,
        },
        ExerciseTypes.MIXTE: {"min": 1, "max": 10, "operations": 2},
        "default": {"min": 1, "max": 10},
    },
    DifficultyLevels.PADAWAN: {
        ExerciseTypes.ADDITION: {"min": 10, "max": 50},
        ExerciseTypes.SUBTRACTION: {"min1": 20, "max1": 70, "min2": 10, "max2": 20},
        ExerciseTypes.MULTIPLICATION: {"min": 5, "max": 10},
        ExerciseTypes.DIVISION: {
            "min_divisor": 2,
            "max_divisor": 10,
            "min_result": 5,
            "max_result": 10,
        },
        ExerciseTypes.MIXTE: {"min": 5, "max": 20, "operations": 2},
        "default": {"min": 10, "max": 50},
    },
    DifficultyLevels.CHEVALIER: {
        ExerciseTypes.ADDITION: {"min": 50, "max": 200},
        ExerciseTypes.SUBTRACTION: {"min1": 100, "max1": 250, "min2": 50, "max2": 100},
        ExerciseTypes.MULTIPLICATION: {"min": 10, "max": 20},
        ExerciseTypes.DIVISION: {
            "min_divisor": 5,
            "max_divisor": 15,
            "min_result": 8,
            "max_result": 20,
        },
        ExerciseTypes.MIXTE: {"min": 10, "max": 50, "operations": 3},
        "default": {"min": 50, "max": 200},
    },
    DifficultyLevels.MAITRE: {
        ExerciseTypes.ADDITION: {"min": 200, "max": 1000},
        ExerciseTypes.SUBTRACTION: {
            "min1": 250,
            "max1": 1000,
            "min2": 100,
            "max2": 500,
        },
        ExerciseTypes.MULTIPLICATION: {"min": 20, "max": 50},
        ExerciseTypes.DIVISION: {
            "min_divisor": 10,
            "max_divisor": 30,
            "min_result": 10,
            "max_result": 50,
        },
        ExerciseTypes.MIXTE: {"min": 20, "max": 100, "operations": 4},
        "default": {"min": 200, "max": 1000},
    },
    DifficultyLevels.GRAND_MAITRE: {
        ExerciseTypes.ADDITION: {"min": 1000, "max": 10000},
        ExerciseTypes.SUBTRACTION: {
            "min1": 1000,
            "max1": 10000,
            "min2": 500,
            "max2": 5000,
        },
        ExerciseTypes.MULTIPLICATION: {"min": 50, "max": 200},
        ExerciseTypes.DIVISION: {
            "min_divisor": 20,
            "max_divisor": 100,
            "min_result": 50,
            "max_result": 200,
        },
        ExerciseTypes.MIXTE: {"min": 100, "max": 1000, "operations": 5},
        "default": {"min": 1000, "max": 10000},
    },
}


# Tags pour les exercices
class Tags:
    ALGORITHMIC = "algorithmique"
    AI = "ia"
    GENERATIVE = "generatif"
    STARWARS = "starwars"
    SIMPLE = "simple"
    ADVANCED = "avance"
    CHALLENGE = "defi"
    FRACTIONS = "fractions"
    GEOMETRY = "geometrie"
    LOGIC = "logique"
    PROBLEM_SOLVING = "resolution-probleme"


# Messages et préfixes spécifiques
class Messages:
    AI_EXERCISE_PREFIX = "TEST-ZAXXON"
    DEFAULT_ERROR = "Une erreur est survenue."
    DEFAULT_SUCCESS = "Opération réussie."

    # Messages d'erreur API (réponses JSON standardisées)
    JSON_BODY_INVALID = "Corps de requête JSON invalide ou manquant"
    JSON_BODY_NOT_OBJECT = "Le corps doit être un objet JSON"


# Paramètres de pagination
class PaginationConfig:
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 50
    DEFAULT_PAGE = 1


# Préférences utilisateur — valeurs acceptées
VALID_THEMES: frozenset = frozenset(
    {"spatial", "minimalist", "ocean", "dune", "forest", "peach", "dino", "neutral"}
)
VALID_LEARNING_STYLES: frozenset = frozenset(
    {"visuel", "auditif", "kinesthésique", "lecture"}
)


# Configuration de sécurité
class SecurityConfig:
    TOKEN_EXPIRY_MINUTES = 60 * 24 * 7  # 7 jours (pour compatibilité)
    ALGORITHM = "HS256"


# ── Domaine challenges — voir app/core/constants_challenge.py ────────────────
# Les imports en tête du fichier re-exportent : CHALLENGE_TYPES_DB, CHALLENGE_TYPES_API,
# CHALLENGE_TYPE_ALIASES, normalize_challenge_type, AGE_GROUPS_DB.

# Remove the import of DifficultyLevel, as it's no longer used here.
