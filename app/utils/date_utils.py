"""
Utilitaires pour le formatage des dates.
"""
from typing import Optional, Any
from datetime import datetime


def format_date_for_json(date_value: Optional[Any]) -> Optional[str]:
    """
    Formate une date pour la sérialisation JSON.
    
    Args:
        date_value: Valeur de date (datetime, str, ou None)
    
    Returns:
        String ISO format ou None
    """
    if not date_value:
        return None
    
    if hasattr(date_value, 'isoformat'):
        # Objet datetime
        return date_value.isoformat()
    elif isinstance(date_value, str):
        # Déjà formaté en string
        return date_value
    
    return None


def format_dates_for_json(data: dict, date_fields: list[str] = None) -> dict:
    """
    Formate plusieurs champs de date dans un dictionnaire.
    
    Args:
        data: Dictionnaire contenant les données
        date_fields: Liste des champs à formater (par défaut: ['created_at', 'updated_at'])
    
    Returns:
        Dictionnaire avec les dates formatées
    """
    if date_fields is None:
        date_fields = ['created_at', 'updated_at']
    
    result = data.copy()
    for field in date_fields:
        if field in result:
            result[field] = format_date_for_json(result[field])
    
    return result

