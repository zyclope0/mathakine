"""
Politique locale du générateur d'exercices simples (non-LLM).

Centralise formulations et règles de présentation testables :
- titres : banques finies, rotation déterministe (pas d'aléatoire décoratif)
- référence documentaire vers les plages numériques : DIFFICULTY_LIMITS dans app.core.constants

La vérité mathématique reste construite dans exercise_generator.py / helpers ;
ce module ne fait que l'habillage et le choix d'index stable.
"""

from __future__ import annotations

from typing import Final, Sequence


def pick_title_variant(variants: Sequence[str], *, salt: int) -> str:
    """
    Choisit une variante de façon déterministe.

    salt : typiquement une combinaison d'entiers du problème (ex. num1 + num2 + result)
    pour corréler légèrement titre et énoncé sans dépendre de random().
    """
    if not variants:
        return ""
    idx = abs(int(salt)) % len(variants)
    return variants[idx]


# --- Titres sobres par type (générateur simple) --------------------------------

SIMPLE_TITLE_ADDITION: Final[tuple[str, ...]] = (
    "Addition : trouver la somme",
    "Somme de deux nombres",
    "Calcul mental — addition",
    "Addition de deux termes",
)

SIMPLE_TITLE_SUBTRACTION: Final[tuple[str, ...]] = (
    "Soustraction : ce qui reste",
    "Différence entre deux nombres",
    "Calcul mental — soustraction",
    "Retrancher pour trouver le reste",
)

SIMPLE_TITLE_MULTIPLICATION: Final[tuple[str, ...]] = (
    "Multiplication : le produit",
    "Produit de deux facteurs",
    "Calcul mental — multiplication",
    "Multiplier deux nombres",
)

SIMPLE_TITLE_DIVISION: Final[tuple[str, ...]] = (
    "Division : le quotient",
    "Partage équitable (quotient)",
    "Calcul mental — division",
    "Diviser en parts égales",
)

SIMPLE_TITLE_FRACTIONS: Final[tuple[str, ...]] = (
    "Fractions : partie d'un tout",
    "Lire une fraction",
    "Numérateur et dénominateur",
    "Représenter une part",
)

SIMPLE_TITLE_GEOMETRIE: Final[tuple[str, ...]] = (
    "Géométrie : mesure",
    "Périmètre ou aire",
    "Figure et grandeur",
    "Calcul sur une figure",
)

SIMPLE_TITLE_MIXTE: Final[tuple[str, ...]] = (
    "Calcul en chaîne",
    "Plusieurs opérations",
    "Ordre des opérations",
    "Expression à calculer",
)

SIMPLE_TITLE_DIVERS: Final[tuple[str, ...]] = (
    "Problème varié",
    "Logique et nombres",
    "Suite ou conversion",
    "Question ouverte",
)

SIMPLE_TITLE_TEXTE: Final[tuple[str, ...]] = (
    "Problème à étapes",
    "Situation et calcul",
    "Lecture et raisonnement",
    "Problème concret",
)
