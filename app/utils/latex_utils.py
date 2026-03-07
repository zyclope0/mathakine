"""
Utilitaires pour le formatage LaTeX (exercices, défis).

Corrige les bugs classiques de génération IA :
- \\frac{1}{8}81 → \\frac{1}{8} 81 (espace après fraction quand chiffres collés)
"""

import re


def sanitize_latex_fractions(text: str) -> str:
    """
    Corrige le bug : fraction LaTeX immédiatement suivie de chiffres sans espace.

    Ex: "on a prélevé $\\frac{1}{8}81$ du total" → "on a prélevé $\\frac{1}{8} 81$ du total"
    Sans cet espace, le parseur KaTeX fusionne et casse le rendu.
    """
    if not text or not isinstance(text, str):
        return text
    return re.sub(r"(\\frac\{\d+\}\{\d+\})(\d+)", r"\1 \2", text)


def sanitize_exercise_text_fields(
    question: str, explanation: str = "", hint: str = ""
) -> tuple[str, str, str]:
    """
    Applique la sanitization LaTeX aux champs texte d'un exercice.
    Retourne (question, explanation, hint) sanitizés.
    """
    return (
        sanitize_latex_fractions(question or ""),
        sanitize_latex_fractions(explanation or ""),
        sanitize_latex_fractions(hint or ""),
    )
