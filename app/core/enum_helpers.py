"""
Module de fonctions utilitaires pour la manipulation sécurisée des énumérations.

Ce module centralise les opérations courantes sur les énumérations pour éviter
les problèmes de compatibilité entre SQLite et PostgreSQL.
"""
from enum import Enum
from typing import Type, TypeVar, Optional, Union, Any

# Type générique pour les énumérations
T = TypeVar('T', bound=Enum)


def get_enum_value(enum_item: Enum) -> str:
    """
    Récupère de manière sécurisée la valeur d'une énumération.
    
    Cette fonction évite les problèmes de chaînes de référence comme
    Enum.VALUE.value en s'assurant qu'on récupère uniquement la valeur simple.
    
    Args:
        enum_item: L'élément d'énumération dont on veut récupérer la valeur
        
    Returns:
        La valeur de l'énumération sous forme de chaîne
    """
    if not isinstance(enum_item, Enum):
        raise TypeError(f"L'objet {enum_item} n'est pas une énumération")
    
    # Récupérer directement la valeur de l'énumération de manière sécurisée
    return enum_item.value


def get_enum_name(enum_item: Enum) -> str:
    """
    Récupère de manière sécurisée le nom d'une énumération.
    
    Args:
        enum_item: L'élément d'énumération dont on veut récupérer le nom
        
    Returns:
        Le nom de l'énumération
    """
    if not isinstance(enum_item, Enum):
        raise TypeError(f"L'objet {enum_item} n'est pas une énumération")
    
    return enum_item.name


def validate_enum_value(enum_class: Type[T], value: str) -> T:
    """
    Valide qu'une valeur appartient à une classe d'énumération et renvoie l'élément correspondant.
    
    Args:
        enum_class: La classe d'énumération
        value: La valeur à valider
        
    Returns:
        L'élément d'énumération correspondant à la valeur
        
    Raises:
        ValueError: Si la valeur n'est pas valide pour cette énumération
    """
    try:
        return enum_class(value)
    except ValueError:
        # Construire un message d'erreur clair avec les valeurs autorisées
        valid_values = [e.value for e in enum_class]
        enum_name = enum_class.__name__
        raise ValueError(
            f"'{value}' n'est pas une valeur valide pour {enum_name}. "
            f"Valeurs autorisées: {', '.join(valid_values)}"
        )


def enum_to_dict(enum_class: Type[Enum]) -> dict:
    """
    Convertit une classe d'énumération en dictionnaire {name: value}.
    
    Utile pour les validations frontend ou pour les convertir en JSON.
    
    Args:
        enum_class: La classe d'énumération à convertir
        
    Returns:
        Un dictionnaire avec les noms et valeurs de l'énumération
    """
    return {item.name: item.value for item in enum_class}


def is_valid_enum_value(enum_class: Type[Enum], value: Any) -> bool:
    """
    Vérifie si une valeur est valide pour une classe d'énumération donnée.
    
    Args:
        enum_class: La classe d'énumération
        value: La valeur à vérifier
        
    Returns:
        True si la valeur est valide, False sinon
    """
    try:
        enum_class(value)
        return True
    except (ValueError, TypeError):
        return False


def get_enum_by_name(enum_class: Type[T], name: str) -> Optional[T]:
    """
    Récupère un élément d'énumération par son nom.
    
    Args:
        enum_class: La classe d'énumération
        name: Le nom de l'élément à récupérer
        
    Returns:
        L'élément d'énumération correspondant ou None si non trouvé
    """
    try:
        return enum_class[name]
    except KeyError:
        return None


def enum_values_list(enum_class: Type[Enum]) -> list:
    """
    Renvoie la liste des valeurs d'une énumération.
    
    Args:
        enum_class: La classe d'énumération
        
    Returns:
        Liste des valeurs de l'énumération
    """
    return [item.value for item in enum_class]


def enum_names_list(enum_class: Type[Enum]) -> list:
    """
    Renvoie la liste des noms d'une énumération.
    
    Args:
        enum_class: La classe d'énumération
        
    Returns:
        Liste des noms de l'énumération
    """
    return [item.name for item in enum_class] 