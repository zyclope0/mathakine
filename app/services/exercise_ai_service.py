"""
Service de génération d'exercices par IA en streaming.
Extrait la logique de generate_ai_exercise_stream depuis exercise_handlers.
"""

import json
import traceback
from typing import Any, AsyncGenerator, Dict, Optional

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.utils.json_utils import extract_json_from_text
from app.utils.latex_utils import sanitize_exercise_text_fields

logger = get_logger(__name__)

DIFFICULTY_RANGES = {
    "INITIE": {
        "min": 1,
        "max": 20,
        "desc": "nombres simples de 1 à 20",
    },
    "PADAWAN": {"min": 1, "max": 100, "desc": "nombres jusqu'à 100"},
    "CHEVALIER": {
        "min": 10,
        "max": 500,
        "desc": "nombres jusqu'à 500, calculs intermédiaires",
    },
    "MAITRE": {
        "min": 50,
        "max": 1000,
        "desc": "nombres jusqu'à 1000, problèmes complexes",
    },
    "GRAND_MAITRE": {
        "min": 100,
        "max": 10000,
        "desc": "grands nombres, problèmes avancés",
    },
}

_REASONING_TYPES = ("fractions", "texte", "mixte", "divers")


def _get_model(exercise_type: str) -> str:
    """Retourne le modèle OpenAI adapté au type d'exercice."""
    return (
        settings.OPENAI_MODEL_REASONING
        if settings.OPENAI_MODEL_REASONING and exercise_type in _REASONING_TYPES
        else settings.OPENAI_MODEL
    )


def _persist_exercise_ai_sync(
    normalized_exercise: Dict[str, Any],
    locale: str = "fr",
) -> Optional[int]:
    """
    Persiste un exercice généré en base via sync_db_session.
    Retourne l'id de l'exercice créé ou None.
    """
    with sync_db_session() as db:
        created = EnhancedServerAdapter.create_generated_exercise(
            db=db,
            exercise_type=normalized_exercise["exercise_type"],
            age_group=normalized_exercise["age_group"],
            difficulty=normalized_exercise["difficulty"],
            title=normalized_exercise["title"],
            question=normalized_exercise["question"],
            correct_answer=normalized_exercise["correct_answer"],
            choices=normalized_exercise["choices"],
            explanation=normalized_exercise["explanation"],
            hint=normalized_exercise.get("hint"),
            tags=normalized_exercise.get("tags", "ai,generated"),
            ai_generated=True,
            locale=locale,
        )
        return created.get("id") if created else None


def _has_custom_theme(prompt: str) -> bool:
    """Détecte si le prompt demande un contexte thématique personnalisé."""
    if not prompt or not prompt.strip():
        return False
    keywords = ["thème", "theme", "contexte", "histoire", "univers", "monde"]
    return any(word in prompt.lower() for word in keywords)


def build_exercise_system_prompt(
    exercise_type: str,
    derived_difficulty: str,
    age_group: str,
    diff_info: Dict[str, Any],
    default_theme: str,
) -> str:
    """Construit le prompt système pour la génération d'exercices."""
    theme_line = f"- Contexte par défaut : {default_theme}" if default_theme else ""
    return f"""Tu es un créateur d'exercices mathématiques pédagogiques.

## CONTRAINTES OBLIGATOIRES
- Type d'exercice : **{exercise_type}** (STRICTEMENT ce type, aucun autre)
- Niveau : {derived_difficulty} ({diff_info['desc']})
- Groupe d'âge cible : {age_group}
{theme_line}

## GUIDE PAR TYPE
- addition/soustraction/multiplication/division : opération unique du type demandé
- fractions : opérations avec fractions (addition, simplification, comparaison)
- geometrie : périmètres, aires, volumes avec formules adaptées au niveau
- texte : problème concret avec mise en situation, nécessitant raisonnement
- mixte : combiner 2-3 opérations différentes dans un même calcul
- divers : suites logiques, pourcentages, conversions, probabilités simples

## RÈGLES QUALITÉ
1. La question doit être claire et sans ambiguïté
2. Les 4 choix doivent inclure : la bonne réponse + 3 erreurs plausibles (erreurs de calcul typiques)
3. L'explication doit détailler le raisonnement étape par étape, avec des calculs COHÉRENTS avec la réponse
4. L'indice doit GUIDER sans donner la réponse (ex: "Quelle opération pour trouver le total ?")
5. CRITIQUE: Vérifie que correct_answer correspond EXACTEMENT aux calculs dans l'explication. Pas de contradiction.
6. FRACTIONS (moitié/tiers/etc.) : formule A = total×frac1, B = total×frac2, puis (total - A - B). L'explication doit suivre EXACTEMENT ces calculs et conclure par correct_answer. INTERDIT : inventer une "erreur", une "correction" ou un recalcul contradictoire. Exemple : 120 cristaux, 1/2 rouges (60) + 1/3 bleus (40) = 100 → ni rouges ni bleus = 20. Jamais 30.

## FORMATAGE MATHÉMATIQUE (OBLIGATOIRE)
Toutes les expressions mathématiques DOIVENT être écrites en LaTeX dans les champs `question`, `explanation` et `hint`.
- Formule inline : $a + b = c$ (délimiteurs $ ... $)
- Formule bloc centrée : $$\\frac{{a}}{{b}} = c$$ (pour les étapes clés de l'explication)
- Opérateurs : $\\times$ (×), $\\div$ (÷), $\\frac{{a}}{{b}}$ (fraction), $a^2$ (exposant), $\\sqrt{{x}}$ (racine)
- Exemples corrects :
  - "Calcule $3 \\times 4$" ✅ — "Calcule 3 × 4" ❌
  - "Explication : $\\frac{{1}}{{2}} + \\frac{{1}}{{3}} = \\frac{{5}}{{6}}$" ✅
  - "L'aire est $\\pi \\times r^2$" ✅ — "L'aire est π × r²" ❌
- CRITIQUE LaTeX : Après une fraction $\\frac{{a}}{{b}}$, TOUJOURS mettre un espace avant le mot ou nombre suivant.
  Ex: "$\\frac{{1}}{{8}}$ du total" ✅ — "$\\frac{{1}}{{8}}81$ du total" ❌ (le 81 collé casse le rendu)
  Ex: "$\\frac{{2}}{{7}}$ de 72" ✅ — "$\\frac{{2}}{{7}}72$" ❌
- Le texte narratif (contexte Star Wars, etc.) reste en prose normale, seules les maths sont en LaTeX.

## FORMAT JSON STRICT
{{
  "title": "Titre court et engageant",
  "question": "Énoncé complet du problème",
  "correct_answer": "Réponse numérique uniquement",
  "choices": ["choix1", "choix2", "choix3", "choix4"],
  "explanation": "Explication pédagogique détaillée",
  "hint": "Piste sans révéler la solution"
}}"""


def build_exercise_user_prompt(
    prompt: Optional[str],
    exercise_type: str,
    derived_difficulty: str,
) -> str:
    """Construit le prompt utilisateur."""
    if prompt and prompt.strip():
        return f"""INSTRUCTIONS PERSONNALISÉES DE L'UTILISATEUR (PRIORITAIRES) :
"{prompt.strip()}"

Crée un exercice de type {exercise_type} (niveau {derived_difficulty}) en respectant ces instructions personnalisées."""
    return f"Crée un exercice de type {exercise_type} pour le niveau {derived_difficulty} avec un contexte spatial engageant."


async def generate_exercise_stream(
    exercise_type: str,
    age_group: str,
    derived_difficulty: str,
    prompt: str,
    locale: str = "fr",
    user_id: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """
    Générateur async qui produit des événements SSE (f"data: {json.dumps(...)}\n\n").
    """
    try:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Bibliothèque OpenAI non installée'})}\n\n"
            return

        if not settings.OPENAI_API_KEY:
            yield f"data: {json.dumps({'type': 'error', 'message': 'OpenAI API key non configurée'})}\n\n"
            return

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        diff_info = DIFFICULTY_RANGES.get(
            derived_difficulty, DIFFICULTY_RANGES["PADAWAN"]
        )
        default_theme = (
            "spatial/galactique (vaisseaux, planètes, étoiles - sans références Star Wars)"
            if not _has_custom_theme(prompt)
            else ""
        )

        system_prompt = build_exercise_system_prompt(
            exercise_type, derived_difficulty, age_group, diff_info, default_theme
        )
        user_prompt = build_exercise_user_prompt(
            prompt, exercise_type, derived_difficulty
        )

        model = _get_model(exercise_type)
        use_o1 = AIConfig.is_o1_model(model)
        use_o3 = AIConfig.is_o3_model(model)
        if use_o1:
            system_prompt += "\n\nCRITIQUE : Retourne UNIQUEMENT un objet JSON valide, sans texte ou markdown avant/après."

        yield f"data: {json.dumps({'type': 'status', 'message': 'Génération en cours...'})}\n\n"

        api_kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
        }
        if use_o1:
            api_kwargs["max_completion_tokens"] = 4000
        elif use_o3:
            api_kwargs["response_format"] = {"type": "json_object"}
            api_kwargs["max_completion_tokens"] = 4000
            api_kwargs["reasoning_effort"] = "low"
        else:
            api_kwargs["temperature"] = 0.7
            api_kwargs["response_format"] = {"type": "json_object"}

        stream = await client.chat.completions.create(**api_kwargs)

        full_response = ""
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content

        try:
            exercise_data = extract_json_from_text(full_response)
        except json.JSONDecodeError as json_error:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Erreur de parsing JSON: {str(json_error)}'})}\n\n"
            return

        q, expl, h = sanitize_exercise_text_fields(
            exercise_data.get("question", ""),
            exercise_data.get("explanation", ""),
            exercise_data.get("hint", ""),
        )
        normalized_exercise = {
            "exercise_type": exercise_type,
            "age_group": age_group,
            "difficulty": derived_difficulty,
            "title": exercise_data.get(
                "title", f"Exercice {exercise_type} {age_group}"
            ),
            "question": q,
            "correct_answer": str(exercise_data.get("correct_answer", "")),
            "choices": exercise_data.get("choices", []),
            "explanation": expl,
            "hint": h,
            "ai_generated": True,
            "tags": "ai,generated",
        }

        try:
            exercise_id = await run_db_bound(
                _persist_exercise_ai_sync,
                normalized_exercise,
                locale,
            )
            if exercise_id:
                normalized_exercise["id"] = exercise_id
        except Exception as save_error:
            logger.warning(f"Erreur lors de la sauvegarde: {save_error}")

        yield f"data: {json.dumps({'type': 'exercise', 'exercise': normalized_exercise})}\n\n"

    except Exception as gen_error:
        logger.error(f"Erreur lors de la génération IA: {gen_error}")
        logger.debug(traceback.format_exc())
        yield f"data: {json.dumps({'type': 'error', 'message': str(gen_error)})}\n\n"
