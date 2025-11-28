"""
Utilitaires pour le parsing JSON.
"""
import json
from typing import Any, List, Optional, Union


def make_json_serializable(obj: Any) -> Any:
    """
    Convertit un objet en une structure sérialisable en JSON.
    Gère les MagicMock, les objets avec attributs, les datetime, etc.
    
    Args:
        obj: Objet à convertir
    
    Returns:
        Objet sérialisable (dict, list, str, int, float, bool, None)
    """
    # Détecter MagicMock et autres objets mock
    if hasattr(obj, '__class__') and 'Mock' in obj.__class__.__name__:
        # Si c'est un MagicMock, essayer de le convertir en dict
        try:
            # Si l'objet a un dict, l'utiliser
            if hasattr(obj, '__dict__'):
                return {k: make_json_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
            # Sinon, retourner une représentation string
            return str(obj)
        except Exception:
            return str(obj)
    
    # Gérer les dictionnaires
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    
    # Gérer les listes
    if isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    
    # Gérer les types de base sérialisables
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    
    # Gérer les datetime
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    
    # Gérer les objets avec attributs (modèles SQLAlchemy, Pydantic, etc.)
    if hasattr(obj, '__dict__'):
        try:
            return {k: make_json_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        except Exception:
            return str(obj)
    
    # Fallback: convertir en string
    try:
        return str(obj)
    except Exception:
        return None


def parse_choices_json(choices_value: Optional[Union[str, dict, list]]) -> Optional[List[str]]:
    """
    Parse les choix d'exercice depuis différents formats JSON.
    
    Args:
        choices_value: Valeur des choix (string JSON, dict, list, ou None)
    
    Returns:
        Liste de strings ou None
    """
    if not choices_value:
        return None
    
    if isinstance(choices_value, list):
        # Déjà une liste
        return choices_value
    
    if isinstance(choices_value, str):
        # String JSON à parser
        try:
            parsed = json.loads(choices_value)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                # Dict JSONB : extraire les valeurs
                return list(parsed.values()) if parsed else None
            return None
        except (json.JSONDecodeError, TypeError):
            return None
    
    if isinstance(choices_value, dict):
        # Dict JSONB : extraire les valeurs
        return list(choices_value.values()) if choices_value else None
    
    return None

