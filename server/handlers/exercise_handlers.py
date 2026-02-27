"""
Handlers pour la génération d'exercices (API)
"""

import json
import traceback

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, StreamingResponse

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.models.exercise import ExerciseType

# Import du service de badges
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.exercise_service import ExerciseService, ExerciseSubmitError
from app.utils.db_utils import db_session
from app.utils.error_handler import (
    ErrorHandler,
    api_error_response,
    get_safe_error_message,
)
from server.auth import optional_auth, require_auth, require_auth_sse
from server.exercise_generator import (
    ensure_explanation,
    generate_ai_exercise,
    generate_simple_exercise,
)


async def generate_exercise(request):
    """Génère un nouvel exercice en utilisant le groupe d'âge."""
    params = request.query_params
    exercise_type_raw = params.get("type") or params.get("exercise_type")
    age_group_raw = params.get("age_group")  # Changed from difficulty
    use_ai = params.get("ai", False)

    # Normaliser et valider les paramètres
    from server.exercise_generator import normalize_and_validate_exercise_params

    exercise_type, age_group, derived_difficulty = (
        normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
    )

    ai_generated = False
    if use_ai and str(use_ai).lower() in ["true", "1", "yes", "y"]:
        exercise_dict = generate_ai_exercise(exercise_type, age_group)
        ai_generated = True
    else:
        exercise_dict = generate_simple_exercise(exercise_type, age_group)

    exercise_dict = ensure_explanation(exercise_dict)
    logger.debug(f"Explication générée: {exercise_dict['explanation']}")
    try:
        # Extraire la locale
        from app.utils.translation import parse_accept_language

        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"

        async with db_session() as db:
            # Sauvegarder l'exercice avec age_group et la difficulté dérivée
            created_exercise = EnhancedServerAdapter.create_generated_exercise(
                db=db,
                exercise_type=exercise_dict["exercise_type"],
                age_group=exercise_dict["age_group"],  # Save age_group
                difficulty=exercise_dict["difficulty"],  # Save derived difficulty
                title=exercise_dict["title"],
                question=exercise_dict["question"],
                correct_answer=exercise_dict["correct_answer"],
                choices=exercise_dict["choices"],
                explanation=exercise_dict["explanation"],
                hint=exercise_dict.get("hint"),
                tags=exercise_dict.get("tags", "generated"),
                ai_generated=ai_generated,
                locale=locale,
            )
            if created_exercise:
                exercise_id = created_exercise["id"]
                logger.info(f"Nouvel exercice créé avec ID={exercise_id}")
                logger.debug(f"Explication: {exercise_dict['explanation']}")
            else:
                logger.error("Erreur: L'exercice n'a pas été créé")
                templates = request.app.state.templates
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "error": "Erreur de génération",
                        "message": "Impossible de créer l'exercice dans la base de données.",
                    },
                    status_code=500,
                )
        return RedirectResponse(url="/exercises?generated=true", status_code=303)
    except Exception as exercise_generation_error:
        logger.error(
            f"Erreur lors de la génération d'exercice: {exercise_generation_error}"
        )
        logger.debug(traceback.format_exc())
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": "Erreur de génération",
                "message": f"Impossible de générer l'exercice: {str(exercise_generation_error)}",
            },
            status_code=500,
        )


async def get_exercise(request):
    """Récupère un exercice par son ID (format API, sans correct_answer)."""
    exercise_id = request.path_params.get("exercise_id")
    try:
        async with db_session() as db:
            exercise = ExerciseService.get_exercise_for_api(db, int(exercise_id))
        if not exercise:
            return ErrorHandler.create_not_found_error(
                resource_type="Exercice", resource_id=exercise_id
            )
        return JSONResponse(exercise)
    except (ValueError, TypeError):
        return ErrorHandler.create_not_found_error(
            resource_type="Exercice", resource_id=exercise_id
        )
    except Exception as exercise_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération de l'exercice: {exercise_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            exercise_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération de l'exercice",
        )


@require_auth
async def submit_answer(request):
    """Orchestration HTTP : parse, valide, délègue à ExerciseService.submit_answer_result."""
    try:
        current_user = request.state.user
        data = await request.json()
        exercise_id = int(request.path_params.get("exercise_id"))
        selected_answer = data.get("answer") or data.get("selected_answer")
        time_spent = data.get("time_spent", 0)
        user_id = current_user.get("id", 1)

        if selected_answer is None:
            return api_error_response(400, "La réponse est requise.")

        logger.debug(
            f"Traitement de la réponse: exercise_id={exercise_id}, "
            f"selected_answer={selected_answer}"
        )

        async with db_session() as db:
            try:
                response_data = ExerciseService.submit_answer_result(
                    db, exercise_id, user_id, selected_answer, time_spent
                )
                return JSONResponse(response_data)
            except ExerciseSubmitError as e:
                return api_error_response(e.status_code, e.message)
            except Exception as db_error:
                error_msg = str(db_error)
                error_type = type(db_error).__name__
                logger.error(
                    f"❌ ERREUR DB lors de l'enregistrement: "
                    f"{error_type}: {error_msg}"
                )
                logger.debug(traceback.format_exc())
                return api_error_response(
                    500, "Erreur lors de l'enregistrement de la tentative"
                )

    except ExerciseSubmitError as e:
        return api_error_response(e.status_code, e.message)
    except Exception as response_processing_error:
        logger.error(
            f"❌ ERREUR lors du traitement de la réponse: "
            f"{type(response_processing_error).__name__}: "
            f"{response_processing_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            response_processing_error,
            status_code=500,
            user_message="Erreur lors du traitement de la réponse",
        )


@optional_auth
async def get_exercises_list(request):
    """Retourne la liste des exercices avec pagination. Ordre aléatoire par défaut pour varier l'entraînement."""
    try:
        logger.debug("[STEP 1] Début de get_exercises_list")
        current_user = getattr(request.state, "user", None)

        # Récupérer les paramètres de requête
        limit_param = request.query_params.get("limit")
        limit = int(limit_param) if limit_param else 20
        skip = int(request.query_params.get("skip", 0))
        exercise_type_raw = request.query_params.get("exercise_type", None)
        age_group_raw = request.query_params.get(
            "age_group", None
        )  # Changed from difficulty
        search = request.query_params.get("search") or request.query_params.get(
            "q"
        )  # Support 'search' et 'q'
        order = (request.query_params.get("order") or "random").lower()
        hide_completed = (
            request.query_params.get("hide_completed", "false").lower() == "true"
        )

        logger.debug(
            f"[STEP 2] Params: limit={limit}, skip={skip}, type={exercise_type_raw}, age_group={age_group_raw}"
        )

        # Normaliser les paramètres de filtrage
        from server.exercise_generator import normalize_and_validate_exercise_params

        exercise_type, age_group, _ = normalize_and_validate_exercise_params(
            exercise_type_raw, age_group_raw
        )

        logger.debug(
            f"[STEP 3] Après normalisation: type={exercise_type}, age_group={age_group}"
        )

        # Si aucun paramètre n'était fourni, remettre à None pour ne pas filtrer
        if not exercise_type_raw:
            exercise_type = None
        if not age_group_raw:
            age_group = None

        # Calculer la page à partir de skip et limit
        page = (skip // limit) + 1 if limit > 0 else 1

        # Extraire la locale depuis le header Accept-Language
        from app.utils.translation import parse_accept_language

        accept_language = request.headers.get("Accept-Language")
        locale = parse_accept_language(accept_language) or "fr"

        logger.debug(
            f"[STEP 4] API - Paramètres finaux: limit={limit}, skip={skip}, page={page}, exercise_type={exercise_type}, age_group={age_group}, search={search}, locale={locale}"
        )

        user_id = current_user.get("id") if current_user else None

        async with db_session() as db:
            response_data = ExerciseService.get_exercises_list_for_api(
                db,
                limit=limit,
                skip=skip,
                exercise_type=exercise_type,
                age_group=age_group,
                search=search,
                order=order,
                hide_completed=hide_completed,
                user_id=user_id,
            )
            logger.debug(
                f"[STEP 5] Liste d'exercices: {len(response_data['items'])} éléments"
            )
            return JSONResponse(response_data)

    except Exception as exercises_list_error:
        logger.error(
            f"Erreur lors de la récupération des exercices: {exercises_list_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            exercises_list_error,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices",
        )


async def generate_exercise_api(request):
    """Génère un nouvel exercice via API JSON (POST) en utilisant le groupe d'âge."""
    try:
        # Récupérer les données JSON de la requête
        data = await request.json()
        exercise_type_raw = data.get("exercise_type")
        age_group_raw = data.get("age_group")  # Changed from difficulty
        use_ai = data.get("ai", False)

        # Normaliser et valider les paramètres
        from server.exercise_generator import normalize_and_validate_exercise_params

        exercise_type, age_group, derived_difficulty = (
            normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
        )

        logger.debug(
            f"Génération API: type={exercise_type_raw}→{exercise_type}, groupe d'âge={age_group_raw}→{age_group}, IA={use_ai}"
        )

        # Valider les paramètres
        if not exercise_type_raw or not age_group_raw:
            return JSONResponse(
                {"error": "Les paramètres 'exercise_type' et 'age_group' sont requis"},
                status_code=400,
            )

        # Générer l'exercice
        ai_generated = False
        if use_ai and str(use_ai).lower() in ["true", "1", "yes", "y"]:
            exercise_dict = generate_ai_exercise(exercise_type, age_group)
            ai_generated = True
        else:
            exercise_dict = generate_simple_exercise(exercise_type, age_group)

        exercise_dict = ensure_explanation(exercise_dict)

        # Optionnellement sauvegarder en base de données
        save_to_db = data.get("save", True)
        if save_to_db:
            try:
                # Extraire la locale
                from app.utils.translation import parse_accept_language

                accept_language = request.headers.get("Accept-Language")
                locale = parse_accept_language(accept_language) or "fr"

                async with db_session() as db:
                    # Sauvegarder l'exercice avec age_group et la difficulté dérivée
                    created_exercise = EnhancedServerAdapter.create_generated_exercise(
                        db=db,
                        exercise_type=exercise_dict["exercise_type"],
                        age_group=exercise_dict["age_group"],  # Save age_group
                        difficulty=exercise_dict[
                            "difficulty"
                        ],  # Save derived difficulty
                        title=exercise_dict["title"],
                        question=exercise_dict["question"],
                        correct_answer=exercise_dict["correct_answer"],
                        choices=exercise_dict["choices"],
                        explanation=exercise_dict["explanation"],
                        hint=exercise_dict.get("hint"),
                        tags=exercise_dict.get("tags", "generated"),
                        ai_generated=ai_generated,
                        locale=locale,
                    )
                    if created_exercise:
                        exercise_dict["id"] = created_exercise["id"]
                        logger.info(
                            f"Exercice sauvegardé avec ID={created_exercise['id']}"
                        )
            except Exception as save_error:
                logger.warning(f"Erreur lors de la sauvegarde: {save_error}")
                # Continuer même si la sauvegarde échoue

        # Retourner l'exercice généré
        return JSONResponse(exercise_dict)

    except Exception as api_generation_error:
        logger.error(
            f"Erreur lors de la génération d'exercice API: {api_generation_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            api_generation_error,
            status_code=500,
            user_message="Erreur lors de la génération de l'exercice",
        )


@require_auth_sse
async def generate_ai_exercise_stream(request):
    """
    Génère un exercice avec OpenAI en streaming SSE.
    Permet un affichage progressif de la génération pour une meilleure UX.
    """
    try:
        # Utilisateur authentifié via le décorateur @require_auth_sse
        current_user = request.state.user

        # Récupérer les paramètres de la requête
        exercise_type_raw = request.query_params.get("exercise_type", "addition")
        # Support des deux paramètres : age_group (nouveau) et difficulty (legacy)
        age_group_raw = request.query_params.get(
            "age_group"
        ) or request.query_params.get("difficulty", "6-8")
        prompt_raw = request.query_params.get("prompt", "")

        # Sanitizer le prompt utilisateur pour éviter l'injection
        from app.utils.prompt_sanitizer import (
            sanitize_user_prompt,
            validate_prompt_safety,
        )

        is_safe, safety_reason = validate_prompt_safety(prompt_raw)
        if not is_safe:
            logger.warning(f"Prompt utilisateur rejeté pour sécurité: {safety_reason}")
            from app.utils.sse_utils import sse_error_response

            return sse_error_response(f"Prompt invalide: {safety_reason}")
        prompt = sanitize_user_prompt(prompt_raw)

        # Normaliser et valider les paramètres de manière centralisée
        from server.exercise_generator import normalize_and_validate_exercise_params

        exercise_type, age_group, derived_difficulty = (
            normalize_and_validate_exercise_params(exercise_type_raw, age_group_raw)
        )

        # Vérifier que la clé OpenAI est configurée
        if not settings.OPENAI_API_KEY:
            from app.utils.sse_utils import sse_error_response

            return sse_error_response("OpenAI API key non configurée")

        async def generate():
            try:
                # Importer OpenAI de manière conditionnelle
                try:
                    from openai import AsyncOpenAI
                except ImportError:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Bibliothèque OpenAI non installée'})}\n\n"
                    return

                client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

                # Définir les plages de nombres selon la difficulté
                difficulty_ranges = {
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
                diff_info = difficulty_ranges.get(
                    derived_difficulty, difficulty_ranges["PADAWAN"]
                )

                # Déterminer le contexte thématique
                has_custom_theme = prompt and any(
                    word in prompt.lower()
                    for word in [
                        "thème",
                        "theme",
                        "contexte",
                        "histoire",
                        "univers",
                        "monde",
                    ]
                )
                default_theme = (
                    "spatial/galactique (vaisseaux, planètes, étoiles - sans références Star Wars)"
                    if not has_custom_theme
                    else ""
                )

                # Construire le prompt système optimisé
                system_prompt = f"""Tu es un créateur d'exercices mathématiques pédagogiques.

## CONTRAINTES OBLIGATOIRES
- Type d'exercice : **{exercise_type}** (STRICTEMENT ce type, aucun autre)
- Niveau : {derived_difficulty} ({diff_info['desc']})
- Groupe d'âge cible : {age_group}
{f"- Contexte par défaut : {default_theme}" if default_theme else ""}

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

## FORMAT JSON STRICT
{{
  "title": "Titre court et engageant",
  "question": "Énoncé complet du problème",
  "correct_answer": "Réponse numérique uniquement",
  "choices": ["choix1", "choix2", "choix3", "choix4"],
  "explanation": "Explication pédagogique détaillée",
  "hint": "Piste sans révéler la solution"
}}"""

                # Modèle : o1/o3 pour fractions/texte/mixte/divers quand OPENAI_MODEL_REASONING est défini
                _reasoning_types = ("fractions", "texte", "mixte", "divers")
                model = (
                    settings.OPENAI_MODEL_REASONING
                    if settings.OPENAI_MODEL_REASONING
                    and exercise_type in _reasoning_types
                    else settings.OPENAI_MODEL
                )
                use_o1 = AIConfig.is_o1_model(model)
                use_o3 = AIConfig.is_o3_model(model)
                if use_o1:
                    system_prompt += "\n\nCRITIQUE : Retourne UNIQUEMENT un objet JSON valide, sans texte ou markdown avant/après."

                # Construire le prompt utilisateur - PRIORITÉ à la description personnalisée
                if prompt and prompt.strip():
                    # Si l'utilisateur a une description, elle est PRIORITAIRE
                    user_prompt = f"""INSTRUCTIONS PERSONNALISÉES DE L'UTILISATEUR (PRIORITAIRES) :
"{prompt.strip()}"

Crée un exercice de type {exercise_type} (niveau {derived_difficulty}) en respectant ces instructions personnalisées."""
                else:
                    # Pas de description personnalisée, utiliser le contexte par défaut
                    user_prompt = f"Crée un exercice de type {exercise_type} pour le niveau {derived_difficulty} avec un contexte spatial engageant."

                # Envoyer un message de démarrage (sans afficher le JSON brut)
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
                    api_kwargs["reasoning_effort"] = (
                        "low"  # Exercices plus simples que défis
                    )
                else:
                    api_kwargs["temperature"] = 0.7
                    api_kwargs["response_format"] = {"type": "json_object"}

                stream = await client.chat.completions.create(**api_kwargs)

                full_response = ""
                # Ne pas envoyer les chunks JSON au client (pas utile pour l'utilisateur)
                # On accumule juste la réponse complète en arrière-plan
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        # Ne plus envoyer les chunks JSON au client (masqué pour meilleure UX)

                # Parser la réponse JSON complète (o1 peut renvoyer du texte autour du JSON)
                from app.utils.json_utils import extract_json_from_text

                try:
                    exercise_data = extract_json_from_text(full_response)

                    # Normaliser les données pour correspondre au format attendu
                    # Utiliser les valeurs normalisées (déjà normalisées plus haut)
                    normalized_exercise = {
                        "exercise_type": exercise_type,  # Déjà normalisé
                        "age_group": age_group,  # Groupe d'âge normalisé
                        "difficulty": derived_difficulty,  # Difficulté dérivée du groupe d'âge
                        "title": exercise_data.get(
                            "title", f"Exercice {exercise_type} {age_group}"
                        ),
                        "question": exercise_data.get("question", ""),
                        "correct_answer": str(exercise_data.get("correct_answer", "")),
                        "choices": exercise_data.get("choices", []),
                        "explanation": exercise_data.get("explanation", ""),
                        "hint": exercise_data.get("hint", ""),
                        "ai_generated": True,
                        "tags": "ai,generated",
                    }

                    # Optionnellement sauvegarder en base de données
                    try:
                        # Extraire la locale depuis le header Accept-Language
                        from app.utils.translation import parse_accept_language

                        accept_language = request.headers.get("Accept-Language")
                        locale = parse_accept_language(accept_language) or "fr"

                        async with db_session() as db:
                            created_exercise = (
                                EnhancedServerAdapter.create_generated_exercise(
                                    db=db,
                                    exercise_type=normalized_exercise["exercise_type"],
                                    age_group=normalized_exercise["age_group"],
                                    difficulty=normalized_exercise["difficulty"],
                                    title=normalized_exercise["title"],
                                    question=normalized_exercise["question"],
                                    correct_answer=normalized_exercise[
                                        "correct_answer"
                                    ],
                                    choices=normalized_exercise["choices"],
                                    explanation=normalized_exercise["explanation"],
                                    hint=normalized_exercise.get("hint"),
                                    tags=normalized_exercise.get(
                                        "tags", "ai,generated"
                                    ),
                                    ai_generated=True,
                                    locale=locale,
                                )
                            )
                            if created_exercise:
                                normalized_exercise["id"] = created_exercise["id"]
                    except Exception as save_error:
                        logger.warning(f"Erreur lors de la sauvegarde: {save_error}")
                        # Continuer même si la sauvegarde échoue

                    # Envoyer l'exercice complet
                    yield f"data: {json.dumps({'type': 'exercise', 'exercise': normalized_exercise})}\n\n"

                except json.JSONDecodeError as json_error:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Erreur de parsing JSON: {str(json_error)}'})}\n\n"

            except Exception as ai_generation_error:
                logger.error(f"Erreur lors de la génération IA: {ai_generation_error}")
                logger.debug(traceback.format_exc())
                yield f"data: {json.dumps({'type': 'error', 'message': str(ai_generation_error)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Désactiver le buffering pour nginx
            },
        )

    except Exception as stream_error:
        logger.error(f"Erreur dans generate_ai_exercise_stream: {stream_error}")
        logger.debug(traceback.format_exc())
        from app.utils.sse_utils import sse_error_response

        return sse_error_response(str(stream_error))


@optional_auth
async def get_completed_exercises_ids(request: Request):
    """
    Récupère la liste des IDs d'exercices complétés par l'utilisateur actuel.
    Route: GET /api/exercises/completed-ids
    """
    try:
        # Utilisateur optionnellement authentifié via le décorateur @optional_auth
        current_user = request.state.user
        if not current_user:
            return JSONResponse({"completed_ids": []}, status_code=200)

        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"completed_ids": []}, status_code=200)

        # Récupérer les IDs d'exercices avec au moins une tentative correcte
        from server.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT DISTINCT exercise_id 
                FROM attempts 
                WHERE user_id = %s AND is_correct = true
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            completed_ids = [row[0] for row in rows] if rows else []

            logger.debug(
                f"Récupération de {len(completed_ids)} exercices complétés pour l'utilisateur {user_id}"
            )
            return JSONResponse({"completed_ids": completed_ids})
        finally:
            cursor.close()
            conn.close()

    except Exception as completed_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération des exercices complétés: {completed_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération des exercices complétés.",
        )


async def get_exercises_stats(request: Request):
    """
    Statistiques globales des Épreuves de l'Académie (exercices).

    Route: GET /api/exercises/stats

    Retourne les statistiques sur l'ensemble des exercices disponibles :
    - Nombre total d'épreuves dans l'Académie
    - Répartition par discipline (type d'exercice)
    - Répartition par rang (difficulté)
    - Répartition par groupe d'apprentis (groupe d'âge)
    - Statistiques de complétion globales

    Thème Académie des Sages :
    - Types → Disciplines mathématiques
    - Difficultés → Rangs de l'Académie (Initié → Grand Maître)
    - Groupes d'âge → Niveaux d'apprentissage
    """
    logger.info("=== DEBUT get_exercises_stats ===")
    try:
        async with db_session() as db:
            response_data = ExerciseService.get_exercises_stats_for_api(db)
            total_exercises = response_data["academy_statistics"]["total_exercises"]
            logger.info(
                f"Statistiques des épreuves récupérées: {total_exercises} épreuves actives"
            )
            return JSONResponse(response_data)

    except Exception as e:
        logger.error(
            f"Erreur lors de la récupération des statistiques d'exercices: {e}"
        )
        traceback.print_exc()
        return JSONResponse(
            {
                "archive_status": "Chroniques inaccessibles",
                "error": "Une perturbation empêche l'accès aux archives. Réessayez plus tard.",
                "details": str(e) if settings.LOG_LEVEL == "DEBUG" else None,
            },
            status_code=500,
        )
