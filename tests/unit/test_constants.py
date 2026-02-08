"""
Tests constantes centralisées (Phase 3).
Teste app/core/constants.py créé dans la Phase 3.
"""
import pytest
from app.core.constants import (
    # Constantes challenges
    CHALLENGE_TYPES_DB,
    AGE_GROUPS_DB,
    AgeGroups,
    normalize_challenge_type,
    normalize_age_group,
    calculate_difficulty_for_age_group,
    # Constantes exercises
    ExerciseTypes,
    DifficultyLevels,
    DIFFICULTY_LIMITS,
    # Autres constantes
    UserRoles,
    Messages,
    DISPLAY_NAMES
)


# ==== Tests Challenge Types ====

def test_challenge_types_db_not_empty():
    """Vérifie que CHALLENGE_TYPES_DB contient des valeurs"""
    assert len(CHALLENGE_TYPES_DB) > 0, "CHALLENGE_TYPES_DB ne doit pas être vide"


def test_challenge_types_expected_values():
    """Vérifie que les types de challenges attendus existent (alignés avec CHALLENGE_TYPES_DB)"""
    expected_types = ["SEQUENCE", "PATTERN", "PUZZLE", "VISUAL", "DEDUCTION", "GRAPH", "RIDDLE", "CHESS", "CODING", "PROBABILITY"]
    
    for expected_type in expected_types:
        assert expected_type in CHALLENGE_TYPES_DB, f"{expected_type} manquant dans CHALLENGE_TYPES_DB"


def test_normalize_challenge_type_lowercase():
    """Test normalisation challenge_type minuscules (spatial → VISUAL via alias)"""
    assert normalize_challenge_type("sequence") == "SEQUENCE"
    assert normalize_challenge_type("pattern") == "PATTERN"
    assert normalize_challenge_type("puzzle") == "PUZZLE"
    assert normalize_challenge_type("visual") == "VISUAL"
    assert normalize_challenge_type("deduction") == "DEDUCTION"
    assert normalize_challenge_type("spatial") == "VISUAL"  # alias dans CHALLENGE_TYPE_ALIASES


def test_normalize_challenge_type_uppercase():
    """Test normalisation challenge_type majuscules (idempotent)"""
    assert normalize_challenge_type("SEQUENCE") == "SEQUENCE"
    assert normalize_challenge_type("PATTERN") == "PATTERN"
    assert normalize_challenge_type("PUZZLE") == "PUZZLE"


def test_normalize_challenge_type_mixedcase():
    """Test normalisation challenge_type mixte"""
    assert normalize_challenge_type("SeQuEnCe") == "SEQUENCE"
    assert normalize_challenge_type("PaTtErN") == "PATTERN"


def test_normalize_challenge_type_invalid():
    """Test normalisation challenge_type invalide"""
    assert normalize_challenge_type("invalid_type_xyz") is None
    assert normalize_challenge_type("") is None
    assert normalize_challenge_type("12345") is None


def test_normalize_challenge_type_none():
    """Test normalisation challenge_type None"""
    assert normalize_challenge_type(None) is None


# ==== Tests Age Groups ====

def test_age_groups_db_not_empty():
    """Vérifie que AGE_GROUPS_DB contient des valeurs"""
    assert len(AGE_GROUPS_DB) > 0, "AGE_GROUPS_DB ne doit pas être vide"


def test_age_groups_expected_values():
    """Vérifie que les groupes d'âge attendus existent (alignés avec AgeGroup enum)"""
    expected_groups = ["GROUP_6_8", "GROUP_10_12", "GROUP_13_15", "GROUP_15_17", "ADULT", "ALL_AGES"]
    
    for expected_group in expected_groups:
        assert expected_group in AGE_GROUPS_DB, f"{expected_group} manquant dans AGE_GROUPS_DB"


def test_normalize_age_group_with_age_prefix():
    """Test normalisation age_group avec préfixe 'age_' (retourne format canonique 6-8, 9-11, etc.)"""
    assert normalize_age_group("age_6_8") == "6-8"
    assert normalize_age_group("age_9_12") == "9-11"
    assert normalize_age_group("age_10_12") == "9-11"
    assert normalize_age_group("age_13_15") == "12-14"
    assert normalize_age_group("age_16_18") == "15-17"


def test_normalize_age_group_with_group_prefix():
    """Test normalisation age_group avec préfixe 'GROUP_' (retourne format canonique)"""
    assert normalize_age_group("GROUP_6_8") == "6-8"
    assert normalize_age_group("GROUP_10_12") == "9-11"
    assert normalize_age_group("GROUP_13_15") == "12-14"


def test_normalize_age_group_with_hyphen():
    """Test normalisation age_group avec tiret (ex: '10-12')"""
    assert normalize_age_group("6-8") == "6-8"
    assert normalize_age_group("10-12") == "9-11"
    assert normalize_age_group("13-15") == "12-14"


def test_normalize_age_group_invalid():
    """Test normalisation age_group invalide"""
    assert normalize_age_group("invalid_group") is None
    assert normalize_age_group("age_99_100") is None
    assert normalize_age_group("") is None


def test_normalize_age_group_none():
    """Test normalisation age_group None (retourne groupe par défaut)"""
    assert normalize_age_group(None) == AgeGroups.GROUP_9_11


# ==== Tests Calculate Difficulty ====

def test_calculate_difficulty_for_age_group_valid():
    """Test calcul difficulté pour groupes d'âge valides (format canonique 6-8, 9-11, etc.)"""
    # Jeunes enfants = plus facile
    assert calculate_difficulty_for_age_group("6-8") == 1.5
    
    # Enfants moyens
    assert calculate_difficulty_for_age_group("9-11") == 2.5
    
    # Adolescents = plus difficile
    assert calculate_difficulty_for_age_group("12-14") == 3.5
    assert calculate_difficulty_for_age_group("15-17") == 4.0


def test_calculate_difficulty_for_age_group_default():
    """Test calcul difficulté avec groupe invalide (retourne valeur par défaut)"""
    # Groupe invalide doit retourner difficulté par défaut (2.5)
    result = calculate_difficulty_for_age_group("INVALID_GROUP")
    assert result == 2.5, "Difficulté par défaut devrait être 2.5"


def test_calculate_difficulty_for_age_group_none():
    """Test calcul difficulté avec None"""
    result = calculate_difficulty_for_age_group(None)
    assert result == 2.5, "Difficulté par défaut devrait être 2.5"


# ==== Tests Exercise Types ====

def test_exercise_types_enum_exists():
    """Vérifie que ExerciseTypes existe"""
    assert ExerciseTypes is not None


def test_exercise_types_expected_values():
    """Vérifie que les types d'exercices attendus existent"""
    expected_types = ["ADDITION", "SOUSTRACTION", "MULTIPLICATION", "DIVISION", "MIXED"]
    
    for expected_type in expected_types:
        assert hasattr(ExerciseTypes, expected_type), f"{expected_type} manquant dans ExerciseTypes"


# ==== Tests Difficulty Levels ====

def test_difficulty_levels_enum_exists():
    """Vérifie que DifficultyLevels existe"""
    assert DifficultyLevels is not None


def test_difficulty_levels_expected_values():
    """Vérifie que les niveaux de difficulté attendus existent"""
    expected_levels = ["INITIE", "PADAWAN", "CHEVALIER", "MAITRE"]
    
    for expected_level in expected_levels:
        assert hasattr(DifficultyLevels, expected_level), f"{expected_level} manquant dans DifficultyLevels"


def test_difficulty_limits_exists():
    """Vérifie que DIFFICULTY_LIMITS existe"""
    assert DIFFICULTY_LIMITS is not None
    assert len(DIFFICULTY_LIMITS) > 0


# ==== Tests User Roles ====

def test_user_roles_enum_exists():
    """Vérifie que UserRoles existe"""
    assert UserRoles is not None


def test_user_roles_expected_values():
    """Vérifie que les rôles attendus existent"""
    expected_roles = ["INITIE", "PADAWAN", "CHEVALIER", "MAITRE", "GARDIEN"]
    
    for expected_role in expected_roles:
        assert hasattr(UserRoles, expected_role), f"{expected_role} manquant dans UserRoles"


# ==== Tests Display Names ====

def test_display_names_exists():
    """Vérifie que DISPLAY_NAMES existe"""
    assert DISPLAY_NAMES is not None
    assert len(DISPLAY_NAMES) > 0


def test_display_names_exercise_types():
    """Vérifie que DISPLAY_NAMES contient des noms pour les types d'exercices"""
    if "exercise_types" in DISPLAY_NAMES:
        exercise_types = DISPLAY_NAMES["exercise_types"]
        assert "ADDITION" in exercise_types
        assert "SOUSTRACTION" in exercise_types
        assert "MULTIPLICATION" in exercise_types


def test_display_names_difficulty_levels():
    """Vérifie que DISPLAY_NAMES contient des noms pour les niveaux"""
    if "difficulty_levels" in DISPLAY_NAMES:
        difficulty_levels = DISPLAY_NAMES["difficulty_levels"]
        assert "INITIE" in difficulty_levels
        assert "PADAWAN" in difficulty_levels
        assert "CHEVALIER" in difficulty_levels
        assert "MAITRE" in difficulty_levels


# ==== Tests Messages ====

def test_messages_exists():
    """Vérifie que Messages existe"""
    assert Messages is not None


# ==== Tests intégration ====

def test_constants_consistency():
    """Vérifie la cohérence entre les différentes constantes"""
    # Les valeurs normalisées doivent correspondre aux valeurs dans les listes
    normalized_sequence = normalize_challenge_type("sequence")
    assert normalized_sequence in CHALLENGE_TYPES_DB, "Incohérence SEQUENCE"
    
    # normalize_age_group retourne le format canonique (6-8, 9-11, etc.) qui est dans AgeGroups.ALL_GROUPS
    normalized_age = normalize_age_group("age_10_12")
    assert normalized_age in AgeGroups.ALL_GROUPS, "Incohérence age_10_12"


def test_all_constants_phase3_present():
    """Vérifie que toutes les constantes Phase 3 sont présentes"""
    # Liste des constantes qui doivent exister après Phase 3
    required_constants = [
        "CHALLENGE_TYPES_DB",
        "AGE_GROUPS_DB",
        "normalize_challenge_type",
        "normalize_age_group",
        "calculate_difficulty_for_age_group",
        "ExerciseTypes",
        "DifficultyLevels",
        "UserRoles"
    ]
    
    # Vérifier que toutes sont importables
    from app.core import constants
    for const_name in required_constants:
        assert hasattr(constants, const_name), f"Constante {const_name} manquante dans constants.py"

