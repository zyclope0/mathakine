"""
Constants centralisées pour l'application Mathakine
Ce fichier contient toutes les constantes utilisées dans l'application.
"""
from app.models.exercise import ExerciseType, DifficultyLevel

# Types d'exercices - compatible avec l'enum ExerciseType
class ExerciseTypes:
    ADDITION = ExerciseType.ADDITION.value
    SUBTRACTION = ExerciseType.SOUSTRACTION.value
    MULTIPLICATION = ExerciseType.MULTIPLICATION.value
    DIVISION = ExerciseType.DIVISION.value
    FRACTIONS = ExerciseType.FRACTIONS.value
    GEOMETRIE = ExerciseType.GEOMETRIE.value
    DIVERS = ExerciseType.DIVERS.value
    
    ALL_TYPES = [ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, FRACTIONS, GEOMETRIE, DIVERS]
    
    # Mapping pour la normalisation des types
    TYPE_ALIASES = {
        ADDITION: [ADDITION, "add", "+", "plus"],
        SUBTRACTION: [SUBTRACTION, "subtract", "sub", "soustraction", "-", "minus"],
        MULTIPLICATION: [MULTIPLICATION, "multiply", "mult", "times", "*", "×"],
        DIVISION: [DIVISION, "divide", "div", "/", "÷"],
        FRACTIONS: [FRACTIONS, "fraction", "frac"],
        GEOMETRIE: [GEOMETRIE, "geometry", "geo"],
        DIVERS: [DIVERS, "misc", "divers", "other"]
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
        INITIE: [INITIE, "initié", "easy", "facile", "debutant", "débutant"],
        PADAWAN: [PADAWAN, "medium", "moyen", "intermediaire", "intermédiaire"],
        CHEVALIER: [CHEVALIER, "hard", "difficile", "avance", "avancé"],
        MAITRE: [MAITRE, "maître", "expert", "très difficile", "tres difficile"]
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
        "default": {"min": 1, "max": 10}
    },
    DifficultyLevels.PADAWAN: {
        ExerciseTypes.ADDITION: {"min": 10, "max": 50},
        ExerciseTypes.SUBTRACTION: {"min1": 20, "max1": 70, "min2": 10, "max2": 20},
        ExerciseTypes.MULTIPLICATION: {"min": 5, "max": 10},
        ExerciseTypes.DIVISION: {"min_divisor": 2, "max_divisor": 10, "min_result": 5, "max_result": 10},
        "default": {"min": 10, "max": 50}
    },
    DifficultyLevels.CHEVALIER: {
        ExerciseTypes.ADDITION: {"min": 50, "max": 100},
        ExerciseTypes.SUBTRACTION: {"min1": 70, "max1": 120, "min2": 20, "max2": 70},
        ExerciseTypes.MULTIPLICATION: {"min": 10, "max": 15},
        ExerciseTypes.DIVISION: {"min_divisor": 5, "max_divisor": 12, "min_result": 10, "max_result": 15},
        "default": {"min": 50, "max": 100}
    },
    DifficultyLevels.MAITRE: {
        ExerciseTypes.ADDITION: {"min": 100, "max": 500},
        ExerciseTypes.SUBTRACTION: {"min1": 120, "max1": 500, "min2": 70, "max2": 120},
        ExerciseTypes.MULTIPLICATION: {"min": 15, "max": 30},
        ExerciseTypes.DIVISION: {"min_divisor": 10, "max_divisor": 20, "min_result": 15, "max_result": 25},
        "default": {"min": 100, "max": 500}
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
    TOKEN_EXPIRY_MINUTES = 60 * 24 * 7  # 7 jours
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
# Statut des exercices
class ExerciseStatus:
    ACTIVE = True
    INACTIVE = False
    ARCHIVED = True
    NOT_ARCHIVED = False 