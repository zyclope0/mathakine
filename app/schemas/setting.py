from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Union
from datetime import datetime

# Schémas pour la manipulation des paramètres de l'application

class SettingBase(BaseModel):
    """Schéma de base pour les paramètres (Configuration du Temple)"""
    key: str = Field(..., min_length=1, max_length=100, 
                  description="Clé du paramètre, unique et lisible")
    value: Optional[str] = Field(None, description="Valeur du paramètre (format texte)")
    value_json: Optional[Dict[str, Any]] = Field(None, 
                                            description="Valeur du paramètre (format JSON)")
    description: Optional[str] = Field(None, 
                                   description="Description de ce que fait le paramètre")
    category: Optional[str] = Field(None, 
                                description="Catégorie du paramètre (système, interface, etc.)")
    
    @validator('key')
    def key_valid(cls, v):
        if not v or v.isspace():
            raise ValueError("La clé ne peut pas être vide")
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError("La clé ne peut contenir que des lettres, chiffres, tirets, underscores et points")
        return v
    
    @validator('value', 'value_json')
    def value_not_both_none(cls, v, values, **kwargs):
        field = kwargs.get('field')
        if field.name == 'value_json' and v is None and values.get('value') is None:
            raise ValueError("Au moins une des valeurs 'value' ou 'value_json' doit être présente")
        return v

class SettingCreate(SettingBase):
    """Schéma pour la création d'un paramètre"""
    is_system: bool = Field(False, description="Si c'est un paramètre système (non modifiable par l'utilisateur)")
    is_public: bool = Field(True, description="Si visible dans l'interface")

class SettingUpdate(BaseModel):
    """Schéma pour la mise à jour d'un paramètre"""
    value: Optional[str] = None
    value_json: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_system: Optional[bool] = None
    is_public: Optional[bool] = None

class SettingInDB(SettingBase):
    """Schéma pour un paramètre en base de données"""
    id: int
    is_system: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class Setting(SettingInDB):
    """Schéma pour un paramètre complet"""
    class Config:
        orm_mode = True

class SettingValueResponse(BaseModel):
    """Réponse simple pour une valeur de paramètre"""
    key: str
    value: Union[str, Dict[str, Any], None]
    
    class Config:
        orm_mode = True

class SettingBatch(BaseModel):
    """Schéma pour l'envoi de plusieurs paramètres à la fois"""
    settings: Dict[str, Union[str, Dict[str, Any]]] = Field(..., 
                                                       description="Dictionnaire des paramètres à modifier")
    
    @validator('settings')
    def validate_batch(cls, v):
        if not v:
            raise ValueError("Le lot de paramètres ne peut pas être vide")
        if len(v) > 50:
            raise ValueError("Maximum 50 paramètres par lot")
        return v 