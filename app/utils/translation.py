"""
Utilitaires pour gérer les traductions des données dans la base de données.

Les traductions sont stockées en JSONB avec la structure :
{
  "fr": "Texte en français",
  "en": "Text in English"
}

Pour les arrays :
{
  "fr": ["Choix 1", "Choix 2"],
  "en": ["Choice 1", "Choice 2"]
}
"""

from typing import Any, Dict, List, Optional

from app.core.config import settings


def get_translated_text(
    translations: Optional[Dict[str, Any]],
    locale: str = "fr",
    fallback_locale: str = "fr",
) -> Optional[str]:
    """
    Récupère le texte traduit depuis un objet JSONB de traductions.

    Args:
        translations: Dictionnaire JSONB des traductions {locale: text}
        locale: Locale demandée (fr, en, etc.)
        fallback_locale: Locale de repli si la traduction n'existe pas

    Returns:
        Texte traduit ou None
    """
    if not translations:
        return None

    # Essayer la locale demandée
    if locale in translations and translations[locale]:
        return translations[locale]

    # Fallback vers la locale par défaut
    if fallback_locale in translations and translations[fallback_locale]:
        return translations[fallback_locale]

    # Fallback vers la première locale disponible
    if translations:
        first_locale = next(iter(translations))
        return translations[first_locale]

    return None


def get_translated_array(
    translations: Optional[Dict[str, List[str]]],
    locale: str = "fr",
    fallback_locale: str = "fr",
) -> Optional[List[str]]:
    """
    Récupère un array traduit depuis un objet JSONB de traductions.

    Args:
        translations: Dictionnaire JSONB des traductions {locale: [items]}
        locale: Locale demandée
        fallback_locale: Locale de repli

    Returns:
        Liste traduite ou None
    """
    if not translations:
        return None

    if locale in translations and translations[locale]:
        return translations[locale]

    if fallback_locale in translations and translations[fallback_locale]:
        return translations[fallback_locale]

    if translations:
        first_locale = next(iter(translations))
        return translations[first_locale]

    return None



def parse_accept_language(accept_language: Optional[str]) -> str:
    """
    Parse le header Accept-Language et retourne la locale préférée.

    Args:
        accept_language: Header Accept-Language (ex: "en-US,en;q=0.9,fr;q=0.8")

    Returns:
        Locale préférée (fr, en, etc.) ou "fr" par défaut
    """
    if not accept_language:
        return "fr"

    # Extraire la première locale (la plus préférée)
    first_locale = accept_language.split(",")[0].split(";")[0].strip()

    # Extraire le code langue (ex: "en-US" -> "en")
    lang_code = first_locale.split("-")[0].lower()

    # Valider que c'est une locale supportée
    supported_locales = ["fr", "en"]

    if lang_code in supported_locales:
        return lang_code

    return "fr"
