"""
Service de gÃ©nÃ©ration d'exercices par IA en streaming.
Extrait la logique de generate_ai_exercise_stream depuis exercise_handlers.
"""

import json
import traceback
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.ai_config import AIConfig
from app.core.ai_generation_policy import (
    build_exercise_ai_stream_kwargs,
    resolve_exercise_ai_model,
)
from app.core.config import settings
from app.core.db_boundary import sync_db_session
from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.services.core.enhanced_server_adapter import EnhancedServerAdapter
from app.services.exercises.exercise_ai_validation import (
    format_validation_error_message,
    validate_exercise_ai_output,
)
from app.utils.error_handler import get_safe_error_message
from app.utils.generation_metrics import generation_metrics
from app.utils.json_utils import extract_json_from_text
from app.utils.latex_utils import sanitize_exercise_text_fields
from app.utils.token_tracker import token_tracker

logger = get_logger(__name__)

METRICS_EXERCISE_AI_PREFIX = "exercise_ai"
EXERCISE_AI_GENERIC_ERROR_MESSAGE = (
    "Erreur inattendue lors de la g\u00e9n\u00e9ration de l'exercice. R\u00e9essayez."
)
EXERCISE_AI_TRANSIENT_ERROR_MESSAGE = (
    "Erreur temporaire lors de la g\u00e9n\u00e9ration de l'exercice. R\u00e9essayez."
)
EXERCISE_AI_POLICY_ERROR_MESSAGE = (
    "Configuration du service d'exercices IA indisponible. R\u00e9essayez plus tard."
)
EXERCISE_AI_INVALID_JSON_MESSAGE = (
    "La r\u00e9ponse g\u00e9n\u00e9r\u00e9e est invalide. R\u00e9essayez."
)
EXERCISE_AI_PERSISTENCE_ERROR_MESSAGE = "Impossible d'enregistrer l'exercice g\u00e9n\u00e9r\u00e9. R\u00e9essayez plus tard."


def _exercise_ai_metrics_key(exercise_type: str) -> str:
    """Cle metriques / tokens : prefixe stable + type (pas de collision avec les defis)."""
    t = (exercise_type or "unknown").strip().lower()
    return f"{METRICS_EXERCISE_AI_PREFIX}:{t}"


DIFFICULTY_RANGES = {
    "INITIE": {
        "min": 1,
        "max": 20,
        "desc": "nombres simples de 1 Ã  20",
    },
    "PADAWAN": {"min": 1, "max": 100, "desc": "nombres jusqu'Ã  100"},
    "CHEVALIER": {
        "min": 10,
        "max": 500,
        "desc": "nombres jusqu'Ã  500, calculs intermÃ©diaires",
    },
    "MAITRE": {
        "min": 50,
        "max": 1000,
        "desc": "nombres jusqu'Ã  1000, problÃ¨mes complexes",
    },
    "GRAND_MAITRE": {
        "min": 100,
        "max": 10000,
        "desc": "grands nombres, problÃ¨mes avancÃ©s",
    },
}


def _persist_exercise_ai_sync(
    normalized_exercise: Dict[str, Any],
    locale: str = "fr",
) -> Optional[int]:
    """
    Persiste un exercice gÃ©nÃ©rÃ© en base via sync_db_session.
    Retourne l'id de l'exercice crÃ©Ã© ou None.
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
    """DÃ©tecte si le prompt demande un contexte thÃ©matique personnalisÃ©."""
    if not prompt or not prompt.strip():
        return False
    keywords = ["thÃ¨me", "theme", "contexte", "histoire", "univers", "monde"]
    return any(word in prompt.lower() for word in keywords)


def build_exercise_system_prompt(
    exercise_type: str,
    derived_difficulty: str,
    age_group: str,
    diff_info: Dict[str, Any],
    default_theme: str,
) -> str:
    """Construit le prompt systÃ¨me pour la gÃ©nÃ©ration d'exercices."""
    theme_line = f"- Contexte par dÃ©faut : {default_theme}" if default_theme else ""
    return f"""Tu es un crÃ©ateur d'exercices mathÃ©matiques pÃ©dagogiques.

## CONTRAINTES OBLIGATOIRES
- Type d'exercice : **{exercise_type}** (STRICTEMENT ce type, aucun autre)
- Niveau : {derived_difficulty} ({diff_info['desc']})
- Groupe d'Ã¢ge cible : {age_group}
{theme_line}

## GUIDE PAR TYPE
- addition/soustraction/multiplication/division : opÃ©ration unique du type demandÃ©
- fractions : opÃ©rations avec fractions (addition, simplification, comparaison)
- geometrie : pÃ©rimÃ¨tres, aires, volumes avec formules adaptÃ©es au niveau
- texte : problÃ¨me concret avec mise en situation, nÃ©cessitant raisonnement
- mixte : combiner 2-3 opÃ©rations diffÃ©rentes dans un mÃªme calcul
- divers : suites logiques, pourcentages, conversions, probabilitÃ©s simples

## RÃˆGLES QUALITÃ‰
1. La question doit Ãªtre claire et sans ambiguÃ¯tÃ©
2. Les 4 choix doivent inclure : la bonne rÃ©ponse + 3 erreurs plausibles (erreurs de calcul typiques)
3. L'explication doit dÃ©tailler le raisonnement Ã©tape par Ã©tape, avec des calculs COHÃ‰RENTS avec la rÃ©ponse
4. L'indice doit GUIDER sans donner la rÃ©ponse (ex: "Quelle opÃ©ration pour trouver le total ?")
5. CRITIQUE: VÃ©rifie que correct_answer correspond EXACTEMENT aux calculs dans l'explication. Pas de contradiction.
6. FRACTIONS (moitiÃ©/tiers/etc.) : formule A = totalÃ—frac1, B = totalÃ—frac2, puis (total - A - B). L'explication doit suivre EXACTEMENT ces calculs et conclure par correct_answer. INTERDIT : inventer une "erreur", une "correction" ou un recalcul contradictoire. Exemple : 120 cristaux, 1/2 rouges (60) + 1/3 bleus (40) = 100 â†’ ni rouges ni bleus = 20. Jamais 30.

## FORMATAGE MATHÃ‰MATIQUE (OBLIGATOIRE)
Toutes les expressions mathÃ©matiques DOIVENT Ãªtre Ã©crites en LaTeX dans les champs `question`, `explanation` et `hint`.
- Formule inline : $a + b = c$ (dÃ©limiteurs $ ... $)
- Formule bloc centrÃ©e : $$\\frac{{a}}{{b}} = c$$ (pour les Ã©tapes clÃ©s de l'explication)
- OpÃ©rateurs : $\\times$ (Ã—), $\\div$ (Ã·), $\\frac{{a}}{{b}}$ (fraction), $a^2$ (exposant), $\\sqrt{{x}}$ (racine)
- Exemples corrects :
  - "Calcule $3 \\times 4$" âœ… â€” "Calcule 3 Ã— 4" âŒ
  - "Explication : $\\frac{{1}}{{2}} + \\frac{{1}}{{3}} = \\frac{{5}}{{6}}$" âœ…
  - "L'aire est $\\pi \\times r^2$" âœ… â€” "L'aire est Ï€ Ã— rÂ²" âŒ
- CRITIQUE LaTeX : AprÃ¨s une fraction $\\frac{{a}}{{b}}$, TOUJOURS mettre un espace avant le mot ou nombre suivant.
  Ex: "$\\frac{{1}}{{8}}$ du total" âœ… â€” "$\\frac{{1}}{{8}}81$ du total" âŒ (le 81 collÃ© casse le rendu)
  Ex: "$\\frac{{2}}{{7}}$ de 72" âœ… â€” "$\\frac{{2}}{{7}}72$" âŒ
- Le texte narratif (contexte Star Wars, etc.) reste en prose normale, seules les maths sont en LaTeX.

## FORMAT JSON STRICT
{{
  "title": "Titre court et engageant",
  "question": "Ã‰noncÃ© complet du problÃ¨me",
  "correct_answer": "RÃ©ponse numÃ©rique uniquement",
  "choices": ["choix1", "choix2", "choix3", "choix4"],
  "explanation": "Explication pÃ©dagogique dÃ©taillÃ©e",
  "hint": "Piste sans rÃ©vÃ©ler la solution"
}}"""


def build_exercise_user_prompt(
    prompt: Optional[str],
    exercise_type: str,
    derived_difficulty: str,
) -> str:
    """Construit le prompt utilisateur."""
    if prompt and prompt.strip():
        return f"""INSTRUCTIONS PERSONNALISÃ‰ES DE L'UTILISATEUR (PRIORITAIRES) :
"{prompt.strip()}"

CrÃ©e un exercice de type {exercise_type} (niveau {derived_difficulty}) en respectant ces instructions personnalisÃ©es."""
    return f"CrÃ©e un exercice de type {exercise_type} pour le niveau {derived_difficulty} avec un contexte spatial engageant."


async def generate_exercise_stream(
    exercise_type: str,
    age_group: str,
    derived_difficulty: str,
    prompt: str,
    locale: str = "fr",
    user_id: Optional[int] = None,
) -> AsyncGenerator[str, None]:
    """
    GÃ©nÃ©rateur async qui produit des Ã©vÃ©nements SSE (f"data: {json.dumps(...)}\n\n").
    """
    start_time = datetime.now()
    metrics_key = _exercise_ai_metrics_key(exercise_type)
    resolved_model: str = "unknown"

    def _duration_s() -> float:
        return (datetime.now() - start_time).total_seconds()

    try:
        try:
            from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError
        except ImportError:
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type="openai_import_error",
            )
            yield f"data: {json.dumps({'type': 'error', 'message': 'BibliothÃ¨que OpenAI non installÃ©e'})}\n\n"
            return

        if not settings.OPENAI_API_KEY:
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type="openai_api_key_missing",
            )
            yield f"data: {json.dumps({'type': 'error', 'message': 'OpenAI API key non configurÃ©e'})}\n\n"
            return

        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=AIConfig.DEFAULT_TIMEOUT,
        )
        diff_info = DIFFICULTY_RANGES.get(
            derived_difficulty, DIFFICULTY_RANGES["PADAWAN"]
        )
        default_theme = (
            "spatial/galactique (vaisseaux, planÃ¨tes, Ã©toiles - sans rÃ©fÃ©rences Star Wars)"
            if not _has_custom_theme(prompt)
            else ""
        )

        system_prompt = build_exercise_system_prompt(
            exercise_type, derived_difficulty, age_group, diff_info, default_theme
        )
        user_prompt = build_exercise_user_prompt(
            prompt, exercise_type, derived_difficulty
        )

        try:
            model = resolve_exercise_ai_model()
            resolved_model = model
            system_prompt += "\n\nCRITIQUE : Retourne UNIQUEMENT un objet JSON valide, sans texte ou markdown avant/aprÃ¨s."
            api_kwargs = build_exercise_ai_stream_kwargs(
                model=model,
                exercise_type=exercise_type,
                system_content=system_prompt,
                user_content=user_prompt,
            )
        except ValueError as policy_error:
            logger.error(f"Configuration IA exercices invalide: {policy_error}")
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type="exercise_ai_policy_error",
            )
            safe_message = get_safe_error_message(
                policy_error,
                default=EXERCISE_AI_POLICY_ERROR_MESSAGE,
            )
            yield f"data: {json.dumps({'type': 'error', 'message': safe_message})}\n\n"
            return

        yield f"data: {json.dumps({'type': 'status', 'message': 'GÃ©nÃ©ration en cours...'})}\n\n"

        @retry(
            stop=stop_after_attempt(AIConfig.MAX_RETRIES),
            wait=wait_exponential(
                multiplier=AIConfig.RETRY_BACKOFF_MULTIPLIER,
                min=AIConfig.RETRY_MIN_WAIT,
                max=AIConfig.RETRY_MAX_WAIT,
            ),
            retry=retry_if_exception_type((RateLimitError, APIError, APITimeoutError)),
            reraise=True,
        )
        async def create_stream_with_retry():
            return await client.chat.completions.create(**api_kwargs)

        try:
            stream = await create_stream_with_retry()
        except (RateLimitError, APIError, APITimeoutError) as api_error:
            logger.error(
                f"Erreur OpenAI exercices apr\u00e8s {AIConfig.MAX_RETRIES} tentatives: {api_error}"
            )
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type=type(api_error).__name__,
            )
            safe_message = get_safe_error_message(
                api_error,
                default=EXERCISE_AI_TRANSIENT_ERROR_MESSAGE,
            )
            yield f"data: {json.dumps({'type': 'error', 'message': safe_message})}\n\n"
            return
        except Exception as stream_error:
            logger.error(
                f"Erreur inattendue lors de l'initialisation du stream exercices IA: {stream_error}"
            )
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type=type(stream_error).__name__,
            )
            safe_message = get_safe_error_message(
                stream_error,
                default=EXERCISE_AI_GENERIC_ERROR_MESSAGE,
            )
            yield f"data: {json.dumps({'type': 'error', 'message': safe_message})}\n\n"
            return

        full_response = ""
        prompt_tokens_estimate = (len(system_prompt) + len(user_prompt)) // 4
        completion_tokens_estimate = 0

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                completion_tokens_estimate = len(full_response) // 4
            usage = getattr(chunk, "usage", None)
            if usage is not None:
                if getattr(usage, "prompt_tokens", None) is not None:
                    prompt_tokens_estimate = int(usage.prompt_tokens)
                if getattr(usage, "completion_tokens", None) is not None:
                    completion_tokens_estimate = int(usage.completion_tokens)

        def _track_openai_cost() -> None:
            token_tracker.track_usage(
                challenge_type=metrics_key,
                prompt_tokens=max(0, prompt_tokens_estimate),
                completion_tokens=max(0, completion_tokens_estimate),
                model=resolved_model,
            )

        try:
            exercise_data = extract_json_from_text(full_response)
        except json.JSONDecodeError as json_error:
            logger.error(f"Exercice IA JSON invalide: {json_error}")
            logger.debug(f"Extrait reponse: {full_response[:800]!r}")
            _track_openai_cost()
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type="json_decode_error",
            )
            yield f"data: {json.dumps({'type': 'error', 'message': EXERCISE_AI_INVALID_JSON_MESSAGE})}\n\n"
            return

        q, expl, h = sanitize_exercise_text_fields(
            exercise_data.get("question", ""),
            exercise_data.get("explanation", ""),
            exercise_data.get("hint", ""),
        )
        title_raw = exercise_data.get("title", f"Exercice {exercise_type} {age_group}")
        ca_raw = str(exercise_data.get("correct_answer", ""))
        choices_raw = exercise_data.get("choices", [])

        valid, reasons = validate_exercise_ai_output(
            exercise_type=exercise_type,
            title=str(title_raw),
            question=q,
            correct_answer=ca_raw,
            choices=choices_raw,
            explanation=expl,
            hint=h,
        )
        if not valid:
            logger.warning(
                f"Validation metier exercice IA refusee (non persistee): {reasons}"
            )
            _track_openai_cost()
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                auto_corrected=False,
                duration_seconds=_duration_s(),
                error_type="exercise_ai_validation_failed",
            )
            msg = format_validation_error_message(reasons)
            yield f"data: {json.dumps({'type': 'error', 'message': msg})}\n\n"
            return

        choices_clean = [str(c).strip() for c in choices_raw]
        title_clean = (
            str(title_raw).strip()
            if title_raw is not None
            else f"Exercice {exercise_type} {age_group}"
        )
        normalized_exercise = {
            "exercise_type": exercise_type,
            "age_group": age_group,
            "difficulty": derived_difficulty,
            "title": title_clean,
            "question": q,
            "correct_answer": str(exercise_data.get("correct_answer", "")).strip(),
            "choices": choices_clean,
            "explanation": expl,
            "hint": h,
            "ai_generated": True,
            "tags": "ai,generated",
        }

        persist_error: Optional[str] = None
        try:
            exercise_id = await run_db_bound(
                _persist_exercise_ai_sync,
                normalized_exercise,
                locale,
            )
            if exercise_id:
                normalized_exercise["id"] = exercise_id
            else:
                persist_error = "sauvegarde_sans_identifiant"
        except Exception as save_error:
            persist_error = str(save_error)
            logger.warning(f"Erreur lors de la sauvegarde exercice IA: {save_error}")

        _track_openai_cost()

        if persist_error is not None:
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=True,
                auto_corrected=False,
                duration_seconds=_duration_s(),
                error_type="persistence_error",
            )
            yield f"data: {json.dumps({'type': 'error', 'message': EXERCISE_AI_PERSISTENCE_ERROR_MESSAGE})}\n\n"
            return

        generation_metrics.record_generation(
            challenge_type=metrics_key,
            success=True,
            validation_passed=True,
            auto_corrected=False,
            duration_seconds=_duration_s(),
        )

        yield f"data: {json.dumps({'type': 'exercise', 'exercise': normalized_exercise})}\n\n"

    except Exception as gen_error:
        logger.error(f"Erreur lors de la gÃ©nÃ©ration IA: {gen_error}")
        logger.debug(traceback.format_exc())
        generation_metrics.record_generation(
            challenge_type=metrics_key,
            success=False,
            validation_passed=False,
            duration_seconds=_duration_s(),
            error_type=type(gen_error).__name__,
        )
        safe_message = get_safe_error_message(
            gen_error,
            default=EXERCISE_AI_GENERIC_ERROR_MESSAGE,
        )
        yield f"data: {json.dumps({'type': 'error', 'message': safe_message})}\n\n"
