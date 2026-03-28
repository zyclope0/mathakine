"""
Service de génération d'exercices par IA en streaming.
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
from app.core.difficulty_tier import build_exercise_generation_profile
from app.core.logging_config import get_logger
from app.core.runtime import run_db_bound
from app.services.core.enhanced_server_adapter import EnhancedServerAdapter
from app.services.exercises.exercise_ai_validation import (
    format_validation_error_message,
    validate_exercise_ai_output,
)
from app.utils.circuit_breaker import (
    OPENAI_CIRCUIT_OPEN_USER_MESSAGE,
    is_countable_openai_failure,
    openai_workload_circuit_breaker,
)
from app.utils.error_handler import get_safe_error_message
from app.utils.generation_metrics import generation_metrics
from app.utils.json_utils import extract_json_from_text
from app.utils.latex_utils import sanitize_exercise_text_fields
from app.utils.token_tracker import token_tracker

logger = get_logger(__name__)

METRICS_EXERCISE_AI_PREFIX = "exercise_ai"
EXERCISE_AI_GENERIC_ERROR_MESSAGE = (
    "Erreur inattendue lors de la génération de l'exercice. Réessayez."
)
EXERCISE_AI_TRANSIENT_ERROR_MESSAGE = (
    "Erreur temporaire lors de la génération de l'exercice. Réessayez."
)
EXERCISE_AI_POLICY_ERROR_MESSAGE = (
    "Configuration du service d'exercices IA indisponible. Réessayez plus tard."
)
EXERCISE_AI_INVALID_JSON_MESSAGE = "La réponse générée est invalide. Réessayez."
EXERCISE_AI_PERSISTENCE_ERROR_MESSAGE = (
    "Impossible d'enregistrer l'exercice généré. Réessayez plus tard."
)

# Événement terminal SSE (aligné sur le flux défis : fin de flux contrôlée après succès ou erreurs métier/validation/persistance).
_SSE_DONE = f"data: {json.dumps({'type': 'done'})}\n\n"


def _exercise_ai_metrics_key(exercise_type: str) -> str:
    """Clé métriques / tokens : préfixe stable + type (pas de collision avec les défis)."""
    t = (exercise_type or "unknown").strip().lower()
    return f"{METRICS_EXERCISE_AI_PREFIX}:{t}"


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
    calibration_desc: str = "",
) -> str:
    """Construit le prompt système pour la génération d'exercices."""
    theme_line = f"- Contexte par défaut : {default_theme}" if default_theme else ""
    cal_line = (
        f"- Calibrage pédagogique : {calibration_desc}" if calibration_desc else ""
    )
    return f"""Tu es un créateur d'exercices mathématiques pédagogiques.

## CONTRAINTES OBLIGATOIRES
- Type d'exercice : **{exercise_type}** (STRICTEMENT ce type, aucun autre)
- Niveau : {derived_difficulty} ({diff_info['desc']})
- Groupe d'âge cible : {age_group}
{cal_line}
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
  - "Calcule $3 \\times 4$" (correct) vs "Calcule 3 x 4" (incorrect)
  - "Explication : $\\frac{{1}}{{2}} + \\frac{{1}}{{3}} = \\frac{{5}}{{6}}$" (correct)
  - "L'aire est $\\pi \\times r^2$" (correct) vs "L'aire est pi x r^2" (incorrect)
- CRITIQUE LaTeX : Après une fraction $\\frac{{a}}{{b}}$, TOUJOURS mettre un espace avant le mot ou nombre suivant.
  Ex: "$\\frac{{1}}{{8}}$ du total" (correct) vs "$\\frac{{1}}{{8}}81$ du total" (incorrect) (le 81 colle casse le rendu)
  Ex: "$\\frac{{2}}{{7}}$ de 72" (correct) vs "$\\frac{{2}}{{7}}72$" (incorrect)
- Le texte narratif (contexte spatial, etc.) reste en prose normale, seules les maths sont en LaTeX.

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
            yield f"data: {json.dumps({'type': 'error', 'message': 'Bibliothèque OpenAI non installée'})}\n\n"
            return

        if not settings.OPENAI_API_KEY:
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type="openai_api_key_missing",
            )
            yield f"data: {json.dumps({'type': 'error', 'message': 'OpenAI API key non configurée'})}\n\n"
            return

        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=AIConfig.DEFAULT_TIMEOUT,
        )
        diff_info = DIFFICULTY_RANGES.get(
            derived_difficulty, DIFFICULTY_RANGES["PADAWAN"]
        )
        default_theme = (
            "spatial/galactique (vaisseaux, planètes, étoiles)"
            if not _has_custom_theme(prompt)
            else ""
        )

        gen_profile = build_exercise_generation_profile(
            exercise_type, age_group, derived_difficulty
        )

        system_prompt = build_exercise_system_prompt(
            exercise_type,
            derived_difficulty,
            age_group,
            diff_info,
            default_theme,
            calibration_desc=gen_profile["calibration_desc"],
        )
        user_prompt = build_exercise_user_prompt(
            prompt, exercise_type, derived_difficulty
        )

        try:
            model = resolve_exercise_ai_model()
            resolved_model = model
            system_prompt += "\n\nCRITIQUE : Retourne UNIQUEMENT un objet JSON valide, sans texte ou markdown avant/après."
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

        if not openai_workload_circuit_breaker.check_allow():
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type="openai_circuit_open",
            )
            yield f"data: {json.dumps({'type': 'error', 'message': OPENAI_CIRCUIT_OPEN_USER_MESSAGE})}\n\n"
            return

        yield f"data: {json.dumps({'type': 'status', 'message': 'Génération en cours...'})}\n\n"

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
            if is_countable_openai_failure(api_error):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error(
                f"Erreur OpenAI exercices après {AIConfig.MAX_RETRIES} tentatives: {api_error}"
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
            if is_countable_openai_failure(stream_error):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
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

        try:
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
        except (RateLimitError, APIError, APITimeoutError) as stream_api_error:
            if is_countable_openai_failure(stream_api_error):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error(
                f"Erreur OpenAI exercices pendant le stream: {stream_api_error}"
            )
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type=type(stream_api_error).__name__,
            )
            safe_message = get_safe_error_message(
                stream_api_error,
                default=EXERCISE_AI_TRANSIENT_ERROR_MESSAGE,
            )
            yield f"data: {json.dumps({'type': 'error', 'message': safe_message})}\n\n"
            return
        except Exception as stream_other:
            if is_countable_openai_failure(stream_other):
                openai_workload_circuit_breaker.record_countable_failure()
            else:
                openai_workload_circuit_breaker.probe_finished_without_countable_outcome()
            logger.error(
                f"Erreur inattendue pendant le stream exercices IA: {stream_other}"
            )
            generation_metrics.record_generation(
                challenge_type=metrics_key,
                success=False,
                validation_passed=False,
                duration_seconds=_duration_s(),
                error_type=type(stream_other).__name__,
            )
            safe_message = get_safe_error_message(
                stream_other,
                default=EXERCISE_AI_GENERIC_ERROR_MESSAGE,
            )
            yield f"data: {json.dumps({'type': 'error', 'message': safe_message})}\n\n"
            return

        openai_workload_circuit_breaker.record_success()

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
            logger.debug(f"Extrait réponse: {full_response[:800]!r}")
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
                f"Validation métier exercice IA refusée (non persistée): {reasons}"
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
            yield _SSE_DONE
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
            yield _SSE_DONE
            return

        generation_metrics.record_generation(
            challenge_type=metrics_key,
            success=True,
            validation_passed=True,
            auto_corrected=False,
            duration_seconds=_duration_s(),
        )

        yield f"data: {json.dumps({'type': 'exercise', 'exercise': normalized_exercise})}\n\n"
        yield _SSE_DONE

    except Exception as gen_error:
        logger.error(f"Erreur lors de la génération IA: {gen_error}")
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
