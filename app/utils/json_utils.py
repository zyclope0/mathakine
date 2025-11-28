"""
Utilitaires pour le parsing JSON.
"""
import json
from typing import Any, List, Optional, Union


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

