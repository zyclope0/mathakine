"""
Utilitaires pour la gestion des valeurs d'énumération PostgreSQL.
"""
from typing import Any, Dict, Optional

from sqlalchemy import inspect
from sqlalchemy.orm import Session


def get_db_engine(db_session: Session) -> str:
    """
    Détecte le moteur de base de données utilisé (postgresql ou sqlite).
    
    Args:
        db_session: Session de base de données
        
    Returns:
        Nom du moteur de base de données ('postgresql' ou 'sqlite')
    """
    engine_name = db_session.bind.engine.name
    return engine_name

def is_postgresql(db_session: Session) -> bool:
    """
    Vérifie si le moteur de base de données est PostgreSQL.
    
    Args:
        db_session: Session de base de données
        
    Returns:
        True si le moteur est PostgreSQL, False sinon
    """
    engine_name = get_db_engine(db_session)
    return engine_name == 'postgresql'

# Mapping des valeurs d'énumération pour PostgreSQL
# Format: (nom_enum, valeur_python): valeur_postgresql
ENUM_MAPPING = {
    # UserRole - Valeurs PostgreSQL exactes
    ("UserRole", "padawan"): "PADAWAN",
    ("UserRole", "maitre"): "MAITRE",
    ("UserRole", "gardien"): "GARDIEN",
    ("UserRole", "archiviste"): "ARCHIVISTE",
    # Note: Le rôle ADMIN a été supprimé - ARCHIVISTE est maintenant le rôle admin suprême
    
    # ExerciseType - Valeurs PostgreSQL exactes  
    ("ExerciseType", "addition"): "ADDITION",
    ("ExerciseType", "soustraction"): "SOUSTRACTION",
    ("ExerciseType", "multiplication"): "MULTIPLICATION",
    ("ExerciseType", "division"): "DIVISION",
    ("ExerciseType", "mixed"): "MIXED",
    
    # DifficultyLevel - Valeurs PostgreSQL exactes
    ("DifficultyLevel", "initie"): "INITIE",
    ("DifficultyLevel", "padawan"): "PADAWAN", 
    ("DifficultyLevel", "chevalier"): "CHEVALIER",
    ("DifficultyLevel", "maitre"): "MAITRE",
    
    # LogicChallengeType - Valeurs PostgreSQL exactes
    ("LogicChallengeType", "sequence"): "SEQUENCE",
    ("LogicChallengeType", "pattern"): "PATTERN",
    ("LogicChallengeType", "visual"): "VISUAL",
    ("LogicChallengeType", "puzzle"): "PUZZLE",
    ("LogicChallengeType", "riddle"): "RIDDLE",
    ("LogicChallengeType", "deduction"): "DEDUCTION",
    ("LogicChallengeType", "spatial"): "VISUAL",  # SPATIAL fusionné dans VISUAL
    ("LogicChallengeType", "probability"): "PROBABILITY",
    ("LogicChallengeType", "graph"): "GRAPH",
    ("LogicChallengeType", "coding"): "CODING",
    ("LogicChallengeType", "chess"): "CHESS",
    ("LogicChallengeType", "custom"): "CUSTOM",
    
    # AgeGroup - Mapping complet Python vers PostgreSQL
    ("AgeGroup", "enfant"): "GROUP_10_12",       # enfant => 10-12
    ("AgeGroup", "adolescent"): "GROUP_13_15",   # adolescent => 13-15
    ("AgeGroup", "adulte"): "ALL_AGES",          # adulte => tous ages
    ("AgeGroup", "age_9_12"): "GROUP_10_12",     # 9-12 => 10-12
    ("AgeGroup", "age_12_13"): "GROUP_13_15",    # 12-13 => 13-15
    ("AgeGroup", "age_13_plus"): "GROUP_13_15",  # 13+ => 13-15
    ("AgeGroup", "9-12"): "GROUP_10_12",         # 9-12 => 10-12
    ("AgeGroup", "12-13"): "GROUP_13_15",        # 12-13 => 13-15
    ("AgeGroup", "13+"): "GROUP_13_15",          # 13+ => 13-15 (AJOUTÉ)
    ("AgeGroup", "group_10_12"): "GROUP_10_12",  # exact match
    ("AgeGroup", "group_13_15"): "GROUP_13_15",  # exact match
    ("AgeGroup", "all_ages"): "ALL_AGES",        # exact match
    # Anciennes valeurs pour compatibilité
    ("AgeGroup", "10-12"): "GROUP_10_12",
    ("AgeGroup", "13-15"): "GROUP_13_15",
    ("AgeGroup", "all"): "ALL_AGES",
}

def get_enum_value(enum_class, value, db: Optional[Session] = None) -> str:
    """
    Récupère la valeur PostgreSQL correspondant à une valeur d'énumération Python.
    
    Args:
        enum_class: Classe d'énumération (ex: UserRole, ExerciseType)
        value: Valeur de l'énumération (peut être une valeur de l'enum ou sa représentation string)
        db: Session de base de données (non utilisée, gardée pour compatibilité)
        
    Returns:
        Valeur adaptée pour PostgreSQL
    """
    # Si la valeur est None, retourner None
    if value is None:
        return None
    
    # Obtenir le nom de la classe d'énumération
    enum_name = enum_class.__name__
    
    # Si c'est un objet enum, obtenir sa valeur
    enum_value = value.value if hasattr(value, 'value') else value
    
    # Chercher dans le mapping
    mapping_key = (enum_name, enum_value)
    if mapping_key in ENUM_MAPPING:
        return ENUM_MAPPING[mapping_key]
    
    # Si pas trouvé, utiliser la valeur telle quelle mais en majuscules pour PostgreSQL
    return str(enum_value).upper()

def adapt_enum_for_db(enum_name: str, value: str, db: Optional[Session] = None) -> str:
    """
    Adapte une valeur d'énumération textuelle pour PostgreSQL.
    
    Args:
        enum_name: Nom de la classe d'énumération (ex: 'UserRole', 'ExerciseType')
        value: Valeur textuelle de l'énumération
        db: Session de base de données (non utilisée, gardée pour compatibilité)
        
    Returns:
        Valeur adaptée pour PostgreSQL
    """
    # Chercher dans le mapping
    mapping_key = (enum_name, value)
    if mapping_key in ENUM_MAPPING:
        return ENUM_MAPPING[mapping_key]
    
    # Si pas trouvé dans le mapping, utiliser la valeur en majuscules
    return value.upper()

def get_all_enum_values(db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Fournit toutes les valeurs d'énumération pour PostgreSQL.
    Utile pour les tests et fixtures.
    
    Args:
        db: Session de base de données (non utilisée, gardée pour compatibilité)
        
    Returns:
        Dictionnaire contenant toutes les valeurs d'énumération adaptées
    """
    from app.models.exercise import DifficultyLevel, ExerciseType
    from app.models.logic_challenge import AgeGroup, LogicChallengeType
    from app.models.user import UserRole
    
    return {
        "engine": "postgresql",
        "user_roles": {
            "padawan": get_enum_value(UserRole, UserRole.PADAWAN),
            "maitre": get_enum_value(UserRole, UserRole.MAITRE),
            "gardien": get_enum_value(UserRole, UserRole.GARDIEN),
            "archiviste": get_enum_value(UserRole, UserRole.ARCHIVISTE),
            # Note: ADMIN supprimé - ARCHIVISTE couvre maintenant tous les privilèges admin
        },
        "exercise_types": {
            "addition": get_enum_value(ExerciseType, ExerciseType.ADDITION),
            "soustraction": get_enum_value(ExerciseType, ExerciseType.SOUSTRACTION),
            "multiplication": get_enum_value(ExerciseType, ExerciseType.MULTIPLICATION),
            "division": get_enum_value(ExerciseType, ExerciseType.DIVISION),
            "fractions": get_enum_value(ExerciseType, ExerciseType.FRACTIONS),
            "geometrie": get_enum_value(ExerciseType, ExerciseType.GEOMETRIE),
            "texte": get_enum_value(ExerciseType, ExerciseType.TEXTE),
            "mixte": get_enum_value(ExerciseType, ExerciseType.MIXTE),
            "divers": get_enum_value(ExerciseType, ExerciseType.DIVERS)
        },
        "difficulty_levels": {
            "initie": get_enum_value(DifficultyLevel, DifficultyLevel.INITIE),
            "padawan": get_enum_value(DifficultyLevel, DifficultyLevel.PADAWAN),
            "chevalier": get_enum_value(DifficultyLevel, DifficultyLevel.CHEVALIER),
            "maitre": get_enum_value(DifficultyLevel, DifficultyLevel.MAITRE)
        },
        "challenge_types": {
            "sequence": get_enum_value(LogicChallengeType, LogicChallengeType.SEQUENCE),
            "puzzle": get_enum_value(LogicChallengeType, LogicChallengeType.PUZZLE),
            "pattern": get_enum_value(LogicChallengeType, LogicChallengeType.PATTERN),
            "visual": get_enum_value(LogicChallengeType, LogicChallengeType.VISUAL),
            "riddle": get_enum_value(LogicChallengeType, LogicChallengeType.PUZZLE),
            "deduction": get_enum_value(LogicChallengeType, LogicChallengeType.DEDUCTION),
            "spatial": get_enum_value(LogicChallengeType, LogicChallengeType.VISUAL),  # SPATIAL fusionné
            "probability": get_enum_value(LogicChallengeType, LogicChallengeType.PROBABILITY),
            "graph": get_enum_value(LogicChallengeType, LogicChallengeType.GRAPH),
            "coding": get_enum_value(LogicChallengeType, LogicChallengeType.CODING),
            "chess": get_enum_value(LogicChallengeType, LogicChallengeType.CHESS),
            "custom": get_enum_value(LogicChallengeType, LogicChallengeType.CUSTOM)
        },
        "age_groups": {
            # Seules les 3 valeurs existantes en PostgreSQL
            "group_10_12": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            "group_13_15": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
            "all_ages": get_enum_value(AgeGroup, AgeGroup.ALL_AGES),
            # Aliases pour rétrocompatibilité (mappent vers les valeurs existantes)
            "10-12": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            "13-15": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
            "all": get_enum_value(AgeGroup, AgeGroup.ALL_AGES),
            # Frontend values (mappent vers les valeurs existantes)
            "6-8": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            "9-11": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            "12-14": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
            "15-17": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
            "adulte": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
            "tous-ages": get_enum_value(AgeGroup, AgeGroup.ALL_AGES),
            # Legacy values (mappent vers les valeurs existantes)
            "enfant": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            "adolescent": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
            "9-12": get_enum_value(AgeGroup, AgeGroup.GROUP_10_12),
            "12-13": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15),
            "13+": get_enum_value(AgeGroup, AgeGroup.GROUP_13_15)
        }
    } 

def get_python_enum_value(enum_class, db_value: str) -> str:
    """
    Convertit une valeur PostgreSQL vers la valeur Python correspondante pour Pydantic.
    
    Args:
        enum_class: La classe d'énumération Python (ex: UserRole, AgeGroup)
        db_value: La valeur stockée dans PostgreSQL (ex: "PADAWAN", "GROUP_10_12")
    
    Returns:
        La valeur Python correspondante (ex: "padawan", "10-12")
    """
    enum_name = enum_class.__name__
    
    # Mapping inverse PostgreSQL -> Python
    reverse_mapping = {
        # UserRole
        ("UserRole", "PADAWAN"): "padawan",
        ("UserRole", "MAITRE"): "maitre", 
        ("UserRole", "GARDIEN"): "gardien",
        ("UserRole", "ARCHIVISTE"): "archiviste",
        
        # ExerciseType
        ("ExerciseType", "ADDITION"): "addition",
        ("ExerciseType", "SOUSTRACTION"): "soustraction",
        ("ExerciseType", "MULTIPLICATION"): "multiplication",
        ("ExerciseType", "DIVISION"): "division",
        ("ExerciseType", "MIXED"): "mixed",
        
        # DifficultyLevel
        ("DifficultyLevel", "INITIE"): "initie",
        ("DifficultyLevel", "PADAWAN"): "padawan",
        ("DifficultyLevel", "CHEVALIER"): "chevalier", 
        ("DifficultyLevel", "MAITRE"): "maitre",
        
        # LogicChallengeType
        ("LogicChallengeType", "SEQUENCE"): "sequence",
        ("LogicChallengeType", "PATTERN"): "pattern",
        ("LogicChallengeType", "VISUAL"): "visual",
        ("LogicChallengeType", "PUZZLE"): "puzzle",
        ("LogicChallengeType", "RIDDLE"): "riddle",
        ("LogicChallengeType", "DEDUCTION"): "deduction",
        ("LogicChallengeType", "SPATIAL"): "visual",  # SPATIAL affiché comme visual
        ("LogicChallengeType", "PROBABILITY"): "probability",
        ("LogicChallengeType", "GRAPH"): "graph",
        ("LogicChallengeType", "CODING"): "coding",
        ("LogicChallengeType", "CHESS"): "chess",
        ("LogicChallengeType", "CUSTOM"): "custom",
        
        # AgeGroup
        ("AgeGroup", "GROUP_10_12"): "10-12",
        ("AgeGroup", "GROUP_13_15"): "13-15",
        ("AgeGroup", "ALL_AGES"): "all",
    }
    
    # Chercher dans le mapping inverse
    key = (enum_name, db_value)
    if key in reverse_mapping:
        return reverse_mapping[key]
    
    # Si pas trouvé, essayer de deviner selon les patterns
    if db_value.startswith("GROUP_"):
        # GROUP_10_12 -> 10-12
        return db_value.replace("GROUP_", "").replace("_", "-")
    
    # Par défaut, retourner en minuscules
    return db_value.lower() 