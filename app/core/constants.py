"""
Constants centralisées pour l'application Mathakine
Ce fichier contient toutes les constantes utilisées dans l'application.
"""
from app.core.logging_config import get_logger
from app.models.exercise import DifficultyLevel, ExerciseType

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
    GRAND_MAITRE = DifficultyLevel.GRAND_MAITRE.value
    
    ALL_LEVELS = [INITIE, PADAWAN, CHEVALIER, MAITRE, GRAND_MAITRE]
    
    # Mapping pour la normalisation des niveaux
    LEVEL_ALIASES = {
        INITIE: [INITIE, "initié", "initie", "easy", "facile", "debutant", "débutant"],
        PADAWAN: [PADAWAN, "padawan", "medium", "moyen", "intermediaire", "intermédiaire"],
        CHEVALIER: [CHEVALIER, "chevalier", "hard", "difficile", "avance", "avancé"],
        MAITRE: [MAITRE, "maitre", "maître", "expert", "très difficile", "tres difficile"],
        GRAND_MAITRE: [GRAND_MAITRE, "grand maitre", "grand maître", "grandmaitre", "master", "adulte"]
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
    # Inclut tous les formats possibles du frontend et de l'API
    AGE_ALIASES = {
        GROUP_6_8: ["6-8", "6-8 ans", "6 to 8 ans", "6_8", "group_6_8", "6-8ans"],
        GROUP_9_11: ["9-11", "9-11 ans", "9 to 11 ans", "9_11", "group_9_11", "9-11ans", "10-12"],
        GROUP_12_14: ["12-14", "12-14 ans", "12 to 14 ans", "12_14", "group_12_14", "12-14ans", "13-15"],
        GROUP_15_17: ["15-17", "15-17 ans", "15 to 17 ans", "15_17", "group_15_17", "15-17ans"],
        ADULT: ["adulte", "adultes", "adult", "adults", "18+", "majeur"],
        ALL_AGES: ["tous-ages", "tous ages", "all ages", "all", "tous", "all_ages", "tousages"],
    }

def normalize_age_group(age_group):
    """
    Normalise le groupe d'âge vers le format standard (6-8, 9-11, etc.)
    
    Args:
        age_group: Le groupe d'âge en entrée (peut être dans différents formats)
        
    Returns:
        Le groupe d'âge normalisé (ex: "6-8", "9-11", etc.)
    """
    if not age_group:
        return AgeGroups.GROUP_9_11  # Défaut : 9-11 ans (milieu de gamme)

    age_group_str = str(age_group).lower().strip()
    
    # Nettoyer les espaces et caractères spéciaux
    age_group_clean = age_group_str.replace(' ', '').replace('_', '-')

    # Parcourir tous les groupes d'âge et leurs alias
    for group_key, aliases in AgeGroups.AGE_ALIASES.items():
        # Vérifier correspondance exacte ou nettoyée
        for alias in aliases:
            alias_clean = alias.lower().replace(' ', '').replace('_', '-')
            if age_group_clean == alias_clean or age_group_str == alias.lower():
                return group_key
    
    # Tentative de correspondance partielle (ex: "9" → "9-11")
    for group_key in AgeGroups.ALL_GROUPS:
        if group_key.startswith(age_group_clean.split('-')[0] + '-'):
            return group_key
    
    # Si aucune correspondance trouvée, retourner le groupe par défaut
    logger.warning(f"Groupe d'âge non reconnu: '{age_group}', utilisation de {AgeGroups.GROUP_9_11} par défaut")
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
        logger.info(f"⚠️ Groupe d'âge non reconnu: {age_group}, utilisation de {DifficultyLevels.PADAWAN} par défaut")
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
    DifficultyLevels.MAITRE: "Maître",
    DifficultyLevels.GRAND_MAITRE: "Grand Maître"
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
    },
    DifficultyLevels.GRAND_MAITRE: {
        ExerciseTypes.ADDITION: {"min": 1000, "max": 10000},
        ExerciseTypes.SUBTRACTION: {"min1": 1000, "max1": 10000, "min2": 500, "max2": 5000},
        ExerciseTypes.MULTIPLICATION: {"min": 50, "max": 200},
        ExerciseTypes.DIVISION: {"min_divisor": 20, "max_divisor": 100, "min_result": 50, "max_result": 200},
        ExerciseTypes.MIXTE: {"min": 100, "max": 1000, "operations": 5},
        "default": {"min": 1000, "max": 10000}
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
    'SEQUENCE', 'PATTERN', 'VISUAL', 'PUZZLE', 'GRAPH', 
    'RIDDLE', 'DEDUCTION', 'CHESS', 'CODING', 'PROBABILITY'
]

CHALLENGE_TYPES_API = [
    'sequence', 'pattern', 'visual', 'puzzle', 'graph',
    'riddle', 'deduction', 'chess', 'coding', 'probability'
]

# Mapping pour la normalisation des types de challenge
CHALLENGE_TYPE_ALIASES = {
    'SEQUENCE': ['sequence', 'seq', 'suite', 'séquence'],
    'PATTERN': ['pattern', 'motif', 'grille'],
    'VISUAL': ['visual', 'visuel', 'spatial', 'forme', 'formes'],
    'PUZZLE': ['puzzle', 'casse-tete', 'casse-tête'],
    'GRAPH': ['graph', 'graphe', 'reseau', 'réseau', 'chemin'],
    'RIDDLE': ['riddle', 'enigme', 'énigme'],
    'DEDUCTION': ['deduction', 'déduction', 'logique', 'logic'],
    'CHESS': ['chess', 'echecs', 'échecs', 'echiquier', 'échiquier'],
    'CODING': ['coding', 'codage', 'crypto', 'cryptographie', 'labyrinthe', 'maze'],
    'PROBABILITY': ['probability', 'probabilite', 'probabilité', 'proba', 'chance'],
}


def normalize_challenge_type(challenge_type):
    """
    Normalise le type de challenge vers le format DB (MAJUSCULE).
    
    Args:
        challenge_type: Le type de challenge en entrée (peut être dans différents formats)
        
    Returns:
        Le type de challenge normalisé en majuscule (ex: "SEQUENCE", "PATTERN", etc.)
        ou None si le type n'est pas reconnu
    """
    if not challenge_type:
        return None

    challenge_type_str = str(challenge_type).lower().strip()
    
    # Vérifier correspondance directe avec les types API
    if challenge_type_str in CHALLENGE_TYPES_API:
        return challenge_type_str.upper()
    
    # Vérifier correspondance directe avec les types DB
    if challenge_type_str.upper() in CHALLENGE_TYPES_DB:
        return challenge_type_str.upper()
    
    # Parcourir tous les alias
    for type_key, aliases in CHALLENGE_TYPE_ALIASES.items():
        for alias in aliases:
            if challenge_type_str == alias.lower():
                return type_key
    
    # Type non reconnu
    logger.warning(f"Type de challenge non reconnu: '{challenge_type}'")
    return None

# Groupes d'âge challenges (These are effectively replicated now in AgeGroups class above)
# AGE_GROUPS_DB = ['GROUP_6_8', 'GROUP_9_11', 'GROUP_9_12', 'GROUP_10_12', 'GROUP_13_15', 'GROUP_16_18', 'ALL_AGES']

# AGE_GROUP_MAPPING (These are effectively replicated now in AgeGroups.AGE_ALIASES)
# AGE_GROUP_MAPPING = {
#     'age_6_8': 'GROUP_6_8', 'age_9_11': 'GROUP_9_11', 'age_9_12': 'GROUP_9_12', 'age_10_12': 'GROUP_10_12',
#     'age_12_15': 'GROUP_13_15', 'age_13_15': 'GROUP_13_15', 'age_16_18': 'GROUP_16_18', 'all_ages': 'ALL_AGES',
#     '6-8': 'GROUP_6_8', '9-11': 'GROUP_9_11', '9-12': 'GROUP_9_12', '10-12': 'GROUP_10_12',
#     '12-15': 'GROUP_13_15', '13-15': 'GROUP_13_15', '16-18': 'GROUP_16_18',
#     'GROUP_6_8': 'GROUP_6_8', 'GROUP_9_11': 'GROUP_9_11', 'GROUP_9_12': 'GROUP_9_12',
#     'GROUP_10_12': 'GROUP_10_12', 'GROUP_13_15': 'GROUP_13_15', 'GROUP_16_18': 'GROUP_16_18', 'ALL_AGES': 'ALL_AGES',
# }

# Difficultés par âge (challenges) - This can be renamed to AGE_GROUP_DIFFICULTY_MAPPING_FOR_CHALLENGES if needed
# For now, it's distinct from AGE_GROUP_LIMITS
# DIFFICULTY_BY_AGE_GROUP is still used in generate_ai_challenge_stream in challenge_handlers.py
# So I should keep it as is, or clarify its role.

# Les fonctions normalize_challenge_type et normalize_age_group sont définies ci-dessus et utilisées pour les challenges

# Remove the import of DifficultyLevel, as it's no longer used here.