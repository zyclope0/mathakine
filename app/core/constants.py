"""
Constants centralisées pour l'application Mathakine
Ce fichier contient toutes les constantes utilisées dans l'application.
"""
from app.models.exercise import ExerciseType, DifficultyLevel

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
    
    ALL_TYPES = [ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, FRACTIONS, GEOMETRIE, TEXTE, MIXTE, DIVERS]
    
    # Mapping pour la normalisation des types
    TYPE_ALIASES = {
        ADDITION: [ADDITION, "addition", "add", "+", "plus"],
        SUBTRACTION: [SUBTRACTION, "soustraction", "subtract", "sub", "-", "minus"],
        MULTIPLICATION: [MULTIPLICATION, "multiplication", "multiply", "mult", "times", "*", "×"],
        DIVISION: [DIVISION, "division", "divide", "div", "/", "÷"],
        FRACTIONS: [FRACTIONS, "fractions", "fraction", "frac"],
        GEOMETRIE: [GEOMETRIE, "geometrie", "geometry", "geo"],
        TEXTE: [TEXTE, "texte", "text", "question"],
        MIXTE: [MIXTE, "mixte", "mixed", "combiné", "combine"],
        DIVERS: [DIVERS, "divers", "misc", "other"]
    }

# Niveaux de difficulté - compatible avec l'enum DifficultyLevel
class DifficultyLevels:
    INITIE = DifficultyLevel.INITIE.value
    PADAWAN = DifficultyLevel.PADAWAN.value
    CHEVALIER = DifficultyLevel.CHEVALIER.value
    MAITRE = DifficultyLevel.MAITRE.value
    
    ALL_LEVELS = [INITIE, PADAWAN, CHEVALIER, MAITRE]
    
    # Mapping pour la normalisation des niveaux
    LEVEL_ALIASES = {
        INITIE: [INITIE, "initié", "initie", "easy", "facile", "debutant", "débutant"],
        PADAWAN: [PADAWAN, "padawan", "medium", "moyen", "intermediaire", "intermédiaire"],
        CHEVALIER: [CHEVALIER, "chevalier", "hard", "difficile", "avance", "avancé"],
        MAITRE: [MAITRE, "maitre", "maître", "expert", "très difficile", "tres difficile"]
    }

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
        GARDIEN: ["view_own", "view_all", "create_exercises", "modify_own", "modify_all"],
        ARCHIVISTE: ["view_own", "view_all", "create_exercises", "modify_own", "modify_all", "delete", "admin"]
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
    DifficultyLevels.MAITRE: "Maître"
}

# Limites numériques par difficulté et type d'exercice
DIFFICULTY_LIMITS = {
    DifficultyLevels.INITIE: {
        ExerciseTypes.ADDITION: {"min": 1, "max": 10},
        ExerciseTypes.SUBTRACTION: {"min1": 5, "max1": 20, "min2": 1, "max2": 5},
        ExerciseTypes.MULTIPLICATION: {"min": 1, "max": 5},
        ExerciseTypes.DIVISION: {"min_divisor": 2, "max_divisor": 5, "min_result": 1, "max_result": 5},
        ExerciseTypes.MIXTE: {"min": 1, "max": 10, "operations": 2},
        "default": {"min": 1, "max": 10}
    },
    DifficultyLevels.PADAWAN: {
        ExerciseTypes.ADDITION: {"min": 10, "max": 50},
        ExerciseTypes.SUBTRACTION: {"min1": 20, "max1": 70, "min2": 10, "max2": 20},
        ExerciseTypes.MULTIPLICATION: {"min": 5, "max": 10},
        ExerciseTypes.DIVISION: {"min_divisor": 2, "max_divisor": 10, "min_result": 5, "max_result": 10},
        ExerciseTypes.MIXTE: {"min": 5, "max": 20, "operations": 2},
        "default": {"min": 10, "max": 50}
    },
    DifficultyLevels.CHEVALIER: {
        ExerciseTypes.ADDITION: {"min": 50, "max": 200},
        ExerciseTypes.SUBTRACTION: {"min1": 100, "max1": 250, "min2": 50, "max2": 100},
        ExerciseTypes.MULTIPLICATION: {"min": 10, "max": 20},
        ExerciseTypes.DIVISION: {"min_divisor": 5, "max_divisor": 15, "min_result": 8, "max_result": 20},
        ExerciseTypes.MIXTE: {"min": 10, "max": 50, "operations": 3},
        "default": {"min": 50, "max": 200}
    },
    DifficultyLevels.MAITRE: {
        ExerciseTypes.ADDITION: {"min": 200, "max": 1000},
        ExerciseTypes.SUBTRACTION: {"min1": 250, "max1": 1000, "min2": 100, "max2": 500},
        ExerciseTypes.MULTIPLICATION: {"min": 20, "max": 50},
        ExerciseTypes.DIVISION: {"min_divisor": 10, "max_divisor": 30, "min_result": 10, "max_result": 50},
        ExerciseTypes.MIXTE: {"min": 20, "max": 100, "operations": 4},
        "default": {"min": 200, "max": 1000}
    }
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

# Paramètres de pagination
class PaginationConfig:
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 50
    DEFAULT_PAGE = 1

# Paramètres de journalisation
class LoggingLevels:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Configuration de sécurité
class SecurityConfig:
    TOKEN_EXPIRY_MINUTES = 60 * 24 * 7  # 7 jours (pour compatibilité)
    ALGORITHM = "HS256"
    # Utiliser la valeur de settings.ACCESS_TOKEN_EXPIRE_MINUTES (7 jours) pour cohérence
    # Cette constante est dépréciée, utiliser app.core.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours (aligné avec config.py)
    
# Statut des exercices
class ExerciseStatus:
    ACTIVE = True
    INACTIVE = False
    ARCHIVED = True
    NOT_ARCHIVED = False


# ============================================================================
# CHALLENGES - Constantes centralisées (Phase 3, Nov 2025)
# ============================================================================

# Types de challenges (PostgreSQL ENUM)
CHALLENGE_TYPES_DB = [
    'SEQUENCE', 'PATTERN', 'VISUAL', 'SPATIAL', 'PUZZLE', 'GRAPH', 
    'RIDDLE', 'DEDUCTION', 'CHESS', 'CODING', 'PROBABILITY', 'CUSTOM'
]

CHALLENGE_TYPES_API = [
    'sequence', 'pattern', 'visual', 'spatial', 'puzzle', 'graph',
    'riddle', 'deduction', 'chess', 'coding', 'probability', 'custom'
]

# Groupes d'âge challenges
AGE_GROUPS_DB = ['GROUP_6_8', 'GROUP_9_11', 'GROUP_9_12', 'GROUP_10_12', 'GROUP_13_15', 'GROUP_16_18', 'ALL_AGES']

AGE_GROUP_MAPPING = {
    'age_6_8': 'GROUP_6_8', 'age_9_11': 'GROUP_9_11', 'age_9_12': 'GROUP_9_12', 'age_10_12': 'GROUP_10_12',
    'age_12_15': 'GROUP_13_15', 'age_13_15': 'GROUP_13_15', 'age_16_18': 'GROUP_16_18', 'all_ages': 'ALL_AGES',
    '6-8': 'GROUP_6_8', '9-11': 'GROUP_9_11', '9-12': 'GROUP_9_12', '10-12': 'GROUP_10_12',
    '12-15': 'GROUP_13_15', '13-15': 'GROUP_13_15', '16-18': 'GROUP_16_18',
    'GROUP_6_8': 'GROUP_6_8', 'GROUP_9_11': 'GROUP_9_11', 'GROUP_9_12': 'GROUP_9_12',
    'GROUP_10_12': 'GROUP_10_12', 'GROUP_13_15': 'GROUP_13_15', 'GROUP_16_18': 'GROUP_16_18', 'ALL_AGES': 'ALL_AGES',
}

# Difficultés par âge
DIFFICULTY_BY_AGE_GROUP = {
    'GROUP_6_8': 1.5, 'GROUP_9_11': 2.5, 'GROUP_9_12': 2.0, 'GROUP_10_12': 2.0,
    'GROUP_13_15': 3.5, 'GROUP_16_18': 4.0, 'ALL_AGES': 3.0,
}


def normalize_challenge_type(challenge_type_raw: str):
    """Normalise un type de challenge vers PostgreSQL."""
    if not challenge_type_raw:
        return None
    normalized = challenge_type_raw.upper().strip()
    return normalized if normalized in CHALLENGE_TYPES_DB else None


def normalize_age_group(age_group_raw: str):
    """Normalise un groupe d'âge vers PostgreSQL."""
    if not age_group_raw:
        return None
    normalized_input = age_group_raw.strip()
    # Essayer d'abord avec la valeur telle quelle (pour les valeurs déjà normalisées)
    result = AGE_GROUP_MAPPING.get(normalized_input)
    if result:
        return result
    # Essayer en minuscules
    result = AGE_GROUP_MAPPING.get(normalized_input.lower())
    if result:
        return result
    # Essayer en majuscules
    result = AGE_GROUP_MAPPING.get(normalized_input.upper())
    if result:
        return result
    # Si la valeur est déjà dans AGE_GROUPS_DB, la retourner telle quelle
    if normalized_input.upper() in AGE_GROUPS_DB:
        return normalized_input.upper()
    return None


def calculate_difficulty_for_age_group(age_group: str) -> float:
    """Calcule difficulté recommandée selon âge."""
    return DIFFICULTY_BY_AGE_GROUP.get(age_group, 2.5)