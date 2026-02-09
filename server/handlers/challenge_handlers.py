"""
Handlers pour les défis logiques (API Starlette)
"""
import json
import traceback
from datetime import datetime

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from server.auth import require_auth, optional_auth, require_auth_sse
from app.core.config import settings
# Importer les constantes et fonctions centralisées
from app.core.constants import (CHALLENGE_TYPES_API, CHALLENGE_TYPES_DB, normalize_age_group, calculate_difficulty_for_age_group)
import app.core.constants as constants
from app.core.messages import SystemMessages
# NOTE: challenge_service_translations_adapter archivé - utiliser fonctions de challenge_service.py
from app.services import challenge_service
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.logic_challenge_service import LogicChallengeService
from app.utils.error_handler import ErrorHandler
from app.utils.translation import parse_accept_language


@require_auth
async def get_challenges_list(request: Request):
    """
    Liste des défis logiques avec filtres optionnels.
    Route: GET /api/challenges
    """
    try:
        current_user = request.state.user
        
        # Récupérer les paramètres de requête
        challenge_type_raw = request.query_params.get('challenge_type')
        age_group_raw = request.query_params.get('age_group')
        search = request.query_params.get('search') or request.query_params.get('q')  # Support 'search' et 'q'
        skip = int(request.query_params.get('skip', 0))
        limit_param = request.query_params.get('limit')
        limit = int(limit_param) if limit_param else 20
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        
        # Normaliser les filtres pour correspondre aux valeurs PostgreSQL
        challenge_type = constants.normalize_challenge_type(challenge_type_raw) if challenge_type_raw else None
        # Utiliser normalize_age_group_for_db pour obtenir la valeur ENUM PostgreSQL
        from app.services.challenge_service import normalize_age_group_for_db
        age_group_db = normalize_age_group_for_db(age_group_raw) if age_group_raw else None
        age_group = normalize_age_group(age_group_raw) if age_group_raw else None  # Format string pour logs
        
        # Calculer la page à partir de skip et limit
        page = (skip // limit) + 1 if limit > 0 else 1
        
        # Récupérer la locale depuis le header Accept-Language
        accept_language = request.headers.get('Accept-Language', 'fr')
        locale = parse_accept_language(accept_language)

        logger.debug(f"API - Paramètres reçus: limit={limit}, skip={skip}, page={page}, challenge_type_raw={challenge_type_raw}, challenge_type_normalized={challenge_type}, age_group_raw={age_group_raw}, age_group_db={age_group_db}, search={search}, locale={locale}")

        # Utiliser le service ORM challenge_service
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Récupérer les challenges via la fonction list_challenges
            challenges = challenge_service.list_challenges(
                db=db,
                challenge_type=challenge_type,
                age_group=age_group_db,  # Utiliser la valeur ENUM DB
                tags=search,  # Utiliser search comme filtre tags
                limit=limit,
                offset=skip
            )
            # Convertir les objets en dicts avec normalisation age_group pour frontend
            from app.services.challenge_service import normalize_age_group_for_frontend
            challenges_list = [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "challenge_type": c.challenge_type,
                    "age_group": normalize_age_group_for_frontend(c.age_group),
                    "difficulty": c.difficulty,
                    "tags": c.tags,
                    "difficulty_rating": c.difficulty_rating,
                    "estimated_time_minutes": c.estimated_time_minutes,
                    "success_rate": c.success_rate,
                    "view_count": c.view_count,
                    "is_archived": c.is_archived
                } for c in challenges
            ]
            
            # Compter le total pour la pagination (même session)
            total = challenge_service.count_challenges(
                db=db,
                challenge_type=challenge_type,
                age_group=age_group_db  # Utiliser la valeur ENUM DB
            )
        finally:
            EnhancedServerAdapter.close_db_session(db)
        
        # Filtrer les défis archivés si nécessaire (déjà fait dans la query, mais double vérification)
        if active_only:
            challenges_list = [c for c in challenges_list if not c.get('is_archived', False)]

        # Log pour déboguer
        logger.debug(f"API - Retour de {len(challenges_list)} défis sur {total} total (limit demandé: {limit}, page: {page})")
        if len(challenges_list) > 0:
            logger.debug(f"API - Premier défi: id={challenges_list[0].get('id')}, title={challenges_list[0].get('title')}")
        
        # Retourner le format paginé standardisé
        has_more = (skip + len(challenges_list)) < total
        
        response_data = {
            "items": challenges_list,
            "total": total,
            "page": page,
            "limit": limit,
            "hasMore": has_more
        }

        logger.info(f"Récupération réussie de {len(challenges_list)} défis logiques sur {total} total (locale: {locale})")
        return JSONResponse(response_data)
    except ValueError as filter_validation_error:
        logger.error(f"Erreur de validation des paramètres: {filter_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=[str(filter_validation_error)],
            user_message="Les paramètres de filtrage sont invalides."
        )
    except Exception as challenges_retrieval_error:
        logger.error(f"Erreur lors de la récupération des défis: {challenges_retrieval_error}")
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenges_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération des défis."
        )


@require_auth
async def get_challenge(request: Request):
    """
    Récupère un défi logique par son ID.
    Route: GET /api/challenges/{challenge_id}
    """
    try:
        current_user = request.state.user
        
        challenge_id = int(request.path_params.get('challenge_id'))
        
        # Récupérer la locale depuis le header Accept-Language
        accept_language = request.headers.get('Accept-Language', 'fr')
        locale = parse_accept_language(accept_language)
        
        # Utiliser le service ORM challenge_service
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Récupérer le challenge via get_challenge_by_id
            from app.models.logic_challenge import LogicChallenge
            challenge = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
            if challenge:
                # Parser les champs JSON si nécessaire
                import json as json_module
                
                def safe_parse_json(value, default=None):
                    """Parse JSON en gérant les cas None, string vide, ou JSON invalide"""
                    if not value:
                        return default if default is not None else []
                    if isinstance(value, str):
                        try:
                            return json_module.loads(value)
                        except (json_module.JSONDecodeError, ValueError):
                            return default if default is not None else []
                    return value
                
                # Normaliser age_group pour le frontend
                from app.services.challenge_service import normalize_age_group_for_frontend
                
                challenge_dict = {
                    "id": challenge.id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "challenge_type": challenge.challenge_type,
                    "age_group": normalize_age_group_for_frontend(challenge.age_group),
                    "difficulty": challenge.difficulty,
                    "question": challenge.question,
                    "correct_answer": challenge.correct_answer,
                    "choices": safe_parse_json(challenge.choices, []),
                    "solution_explanation": challenge.solution_explanation,
                    "visual_data": safe_parse_json(challenge.visual_data, {}),
                    "hints": safe_parse_json(challenge.hints, []),
                    "tags": challenge.tags,
                    "difficulty_rating": challenge.difficulty_rating,
                    "estimated_time_minutes": challenge.estimated_time_minutes,
                    "success_rate": challenge.success_rate,
                    "view_count": challenge.view_count,
                    "is_active": challenge.is_active,
                    "is_archived": challenge.is_archived
                }
            else:
                challenge_dict = None
        finally:
            EnhancedServerAdapter.close_db_session(db)
        
        if not challenge_dict:
            return ErrorHandler.create_not_found_error(
                resource_name="Défi logique",
                user_message="Ce défi logique n'existe pas ou a été supprimé."
            )
        
        logger.info(f"Récupération réussie du défi logique {challenge_id} (locale: {locale})")
        return JSONResponse(challenge_dict)
    except ValueError as id_validation_error:
        logger.error(f"Erreur de validation: {id_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=["ID de défi invalide"],
            user_message="L'identifiant du défi est invalide."
        )
    except Exception as challenge_retrieval_error:
        logger.error(f"Erreur lors de la récupération du défi: {challenge_retrieval_error}")
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenge_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération du défi."
        )


@require_auth
async def submit_challenge_answer(request: Request):
    """
    Soumet une réponse à un défi logique.
    Route: POST /api/challenges/{challenge_id}/attempt
    """
    try:
        current_user = request.state.user
        
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"error": "Utilisateur invalide"}, status_code=401)
        
        challenge_id = int(request.path_params.get('challenge_id'))
        data = await request.json()
        
        user_solution = data.get('user_solution') or data.get('answer')
        time_spent = data.get('time_spent')
        hints_used_raw = data.get('hints_used', [])
        
        # Convertir hints_used de liste à entier (nombre d'indices utilisés)
        # Le modèle attend un Integer, pas une liste
        if isinstance(hints_used_raw, list):
            hints_used_count = len(hints_used_raw)
        elif isinstance(hints_used_raw, int):
            hints_used_count = hints_used_raw
        else:
            hints_used_count = 0
        
        if not user_solution:
            return JSONResponse({"error": "Réponse requise"}, status_code=400)
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Récupérer le défi
            challenge = LogicChallengeService.get_challenge(db, challenge_id)
            if not challenge:
                return JSONResponse({"error": "Défi logique non trouvé"}, status_code=404)
            
            # Vérifier la réponse
            # Fonction helper pour parser une réponse (gère format liste Python et CSV)
            def parse_answer_to_list(answer: str) -> list:
                """Parse une réponse en liste, gérant plusieurs formats."""
                answer = str(answer).strip()
                
                # Format liste Python : "['Rouge', 'Vert', 'Jaune', 'Bleu']"
                if answer.startswith('[') and answer.endswith(']'):
                    try:
                        import ast
                        parsed = ast.literal_eval(answer)
                        if isinstance(parsed, list):
                            return [str(item).strip().lower() for item in parsed]
                    except (ValueError, SyntaxError):
                        pass
                    # Fallback: retirer les crochets et parser manuellement
                    inner = answer[1:-1]
                    # Retirer les quotes autour de chaque élément
                    items = []
                    for item in inner.split(','):
                        item = item.strip().strip("'").strip('"').strip().lower()
                        if item:
                            items.append(item)
                    return items
                
                # Format CSV simple : "Rouge,Vert,Jaune,Bleu"
                if ',' in answer:
                    return [item.strip().lower() for item in answer.split(',') if item.strip()]
                
                # Valeur simple
                return [answer.lower()] if answer else []
            
            def compare_deduction_answers(user_answer: str, correct_answer: str) -> bool:
                """
                Compare les réponses pour les défis de déduction.
                Format attendu: "Emma:Chimie:700,Lucas:Info:600,..." ou format dict-like
                L'ordre des associations n'a pas d'importance, seul le contenu compte.
                """
                def parse_associations(answer: str) -> set:
                    """Parse les associations en set de tuples normalisés."""
                    answer = str(answer).strip().lower()
                    associations = set()
                    
                    # Format "entité:val1:val2,..."
                    if ':' in answer:
                        for part in answer.split(','):
                            part = part.strip()
                            if part:
                                # Normaliser : trier les éléments pour ignorer l'ordre interne
                                elements = tuple(sorted([e.strip() for e in part.split(':') if e.strip()]))
                                if elements:
                                    associations.add(elements)
                    # Format dict-like ou JSON
                    elif '{' in answer:
                        try:
                            import json
                            data = json.loads(answer.replace("'", '"'))
                            if isinstance(data, dict):
                                for key, values in data.items():
                                    if isinstance(values, dict):
                                        elements = tuple(sorted([str(key).lower()] + [str(v).lower() for v in values.values()]))
                                    else:
                                        elements = tuple(sorted([str(key).lower(), str(values).lower()]))
                                    associations.add(elements)
                        except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
                            pass
                    
                    return associations
                
                user_assoc = parse_associations(user_answer)
                correct_assoc = parse_associations(correct_answer)
                
                logger.debug(f"Deduction comparison - User: {user_assoc}, Correct: {correct_assoc}")
                
                # Comparer les sets
                return user_assoc == correct_assoc
            
            # Déterminer le type de challenge pour choisir la méthode de comparaison
            challenge_type = str(challenge.challenge_type).lower() if challenge.challenge_type else ''
            
            # Comparaison spéciale pour les défis de déduction
            if 'deduction' in challenge_type and ':' in user_solution:
                is_correct = compare_deduction_answers(user_solution, challenge.correct_answer)
                logger.debug(f"Comparaison déduction - User: {user_solution[:100]}, Correct: {challenge.correct_answer[:100] if challenge.correct_answer else 'None'}, Result: {is_correct}")
            else:
                # Parser les deux réponses pour autres types
                user_list = parse_answer_to_list(user_solution)
                correct_list = parse_answer_to_list(challenge.correct_answer)
                
                logger.debug(f"Comparaison réponse - User: {user_list}, Correct: {correct_list}")
                
                # Comparer les listes (ordre important pour les puzzles)
                if len(user_list) > 1 or len(correct_list) > 1:
                    is_correct = user_list == correct_list
                else:
                    # Comparaison simple pour les réponses à un seul élément
                    user_normalized = user_list[0] if user_list else ''
                    correct_normalized = correct_list[0] if correct_list else ''
                    is_correct = user_normalized == correct_normalized
            
            # NOTE: attempt_service_translations archivé - utiliser LogicChallengeAttempt ORM
            from app.models.logic_challenge import LogicChallengeAttempt
            
            attempt_data = {
                "user_id": user_id,
                "challenge_id": challenge_id,
                "user_solution": user_solution,
                "is_correct": is_correct,
                "time_spent": time_spent,
                "hints_used": hints_used_count  # Utiliser le nombre d'indices, pas la liste
            }
            
            logger.debug(f"Tentative d'enregistrement de challenge avec attempt_data: {attempt_data}")
            attempt = LogicChallengeAttempt(**attempt_data)
            db.add(attempt)
            db.commit()
            db.refresh(attempt)
            logger.debug(f"Tentative challenge créée: {attempt.id}")
            
            response_data = {
                'is_correct': is_correct,
                'explanation': challenge.solution_explanation if is_correct else None,
            }
            
            if not is_correct:
                # Ne pas révéler la bonne réponse immédiatement, mais la donner dans l'explication après plusieurs tentatives
                hints_list = challenge.hints if isinstance(challenge.hints, list) else []
                response_data['hints_remaining'] = len(hints_list) - hints_used_count
            
            return JSONResponse(response_data)
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except ValueError:
        return JSONResponse({"error": "ID de défi invalide"}, status_code=400)
    except Exception as submission_error:
        logger.error(f"Erreur lors de la soumission de la réponse: {submission_error}")
        import traceback
        logger.debug(traceback.format_exc())
        return JSONResponse({"error": f"Erreur: {str(submission_error)}"}, status_code=500)


async def get_challenge_hint(request: Request):
    """
    Récupère un indice pour un défi logique.
    Route: GET /api/challenges/{challenge_id}/hint
    """
    try:
        challenge_id = int(request.path_params.get('challenge_id'))
        level = int(request.query_params.get('level', 1))
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            challenge = LogicChallengeService.get_challenge(db, challenge_id)
            if not challenge:
                return JSONResponse({"error": "Défi logique non trouvé"}, status_code=404)
            
            # Récupérer les indices
            hints = challenge.hints
            if isinstance(hints, str):
                try:
                    hints = json.loads(hints)
                except (json.JSONDecodeError, ValueError):
                    # Si le parsing échoue, traiter comme une liste vide
                    hints = []
            elif hints is None:
                hints = []
            
            # S'assurer que hints est une liste
            if not isinstance(hints, list):
                hints = []
            
            if level < 1 or level > len(hints):
                return JSONResponse({"error": f"Indice de niveau {level} non disponible"}, status_code=400)
            
            # Retourner l'indice spécifique au niveau demandé (index 0-based)
            hint_text = hints[level - 1] if level <= len(hints) else None
            return JSONResponse({"hint": hint_text})  # Retourner l'indice spécifique au niveau
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except ValueError:
        return JSONResponse({"error": "ID de défi ou niveau invalide"}, status_code=400)
    except Exception as hint_retrieval_error:
        logger.error(f"Erreur lors de la récupération de l'indice: {hint_retrieval_error}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(hint_retrieval_error)}"}, status_code=500)


@optional_auth
async def get_completed_challenges_ids(request: Request):
    """
    Récupère la liste des IDs de challenges complétés par l'utilisateur actuel.
    Route: GET /api/challenges/completed-ids
    """
    try:
        current_user = request.state.user
        if not current_user:
            return JSONResponse({"completed_ids": []}, status_code=200)
        
        user_id = current_user.get("id")
        if not user_id:
            return JSONResponse({"completed_ids": []}, status_code=200)
        
        # Récupérer les IDs de challenges avec au moins une tentative correcte
        from server.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # D'abord, vérifier combien de tentatives existent pour cet utilisateur
            check_query = """
                SELECT COUNT(*) as total_attempts,
                       COUNT(CASE WHEN is_correct = true THEN 1 END) as correct_attempts
                FROM logic_challenge_attempts 
                WHERE user_id = %s
            """
            cursor.execute(check_query, (user_id,))
            stats = cursor.fetchone()
            logger.debug(f"Statistiques pour user_id {user_id}: total={stats[0]}, correctes={stats[1]}")
            
            # Ensuite, récupérer les IDs de challenges complétés
            query = """
                SELECT DISTINCT challenge_id 
                FROM logic_challenge_attempts 
                WHERE user_id = %s AND is_correct = true
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            completed_ids = [row[0] for row in rows] if rows else []
            
            logger.debug(f"Récupération de {len(completed_ids)} challenges complétés pour l'utilisateur {user_id}")
            logger.debug(f"IDs complétés: {completed_ids}")
            return JSONResponse({"completed_ids": completed_ids})
        finally:
            cursor.close()
            conn.close()
            
    except Exception as completed_challenges_error:
        logger.error(f"Erreur lors de la récupération des challenges complétés: {completed_challenges_error}")
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_challenges_error,
            status_code=500,
            user_message="Erreur lors de la récupération des challenges complétés."
        )


@require_auth
async def start_challenge(request: Request):
    """
    Handler pour démarrer un défi (placeholder).
    Route: POST /api/challenges/start/{challenge_id}
    """
    try:
        current_user = request.state.user
        
        challenge_id = int(request.path_params.get('challenge_id'))
        user_id = current_user.get('id')
        logger.info(f"Défi {challenge_id} démarré par l'utilisateur {user_id}. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": f"Le défi {challenge_id} a été enregistré comme démarré pour l'utilisateur {user_id}. La fonctionnalité est en cours de développement."},
            status_code=200
        )
    except ValueError:
        return JSONResponse({"error": "ID de défi invalide"}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du défi: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@require_auth
async def get_challenge_progress(request: Request):
    """
    Handler pour récupérer la progression d'un défi pour l'utilisateur actuel (placeholder).
    Route: GET /api/challenges/progress/{challenge_id}
    """
    try:
        current_user = request.state.user
        
        challenge_id = int(request.path_params.get('challenge_id'))
        user_id = current_user.get('id')
        logger.info(f"Accès à la progression du défi {challenge_id} pour l'utilisateur {user_id}. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": f"La fonctionnalité de progression pour le défi {challenge_id} pour l'utilisateur {user_id} est en cours de développement."},
            status_code=200
        )
    except ValueError:
        return JSONResponse({"error": "ID de défi invalide"}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la progression du défi: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@require_auth
async def get_challenge_rewards(request: Request):
    """
    Handler pour récupérer les récompenses d'un défi (placeholder).
    Route: GET /api/challenges/rewards/{challenge_id}
    """
    try:
        current_user = request.state.user
        
        challenge_id = int(request.path_params.get('challenge_id'))
        logger.info(f"Accès aux récompenses du défi {challenge_id} par l'utilisateur {current_user.get('id')}. Fonctionnalité en développement.")

        return JSONResponse(
            {"message": f"La fonctionnalité de récompenses pour le défi {challenge_id} est en cours de développement."},
            status_code=200
        )
    except ValueError:
        return JSONResponse({"error": "ID de défi invalide"}, status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des récompenses du défi: {e}")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@require_auth_sse
async def generate_ai_challenge_stream(request: Request):
    """
    Génère un challenge avec OpenAI en streaming SSE.
    Permet un affichage progressif de la génération pour une meilleure UX.
    Crée des challenges de type mathélogique avec visual_data selon le type.
    """
    try:
        current_user = request.state.user
        
        # Récupérer les paramètres de la requête
        challenge_type_raw = request.query_params.get('challenge_type', 'sequence')
        age_group_raw = request.query_params.get('age_group', '10-12')
        prompt_raw = request.query_params.get('prompt', '')
        
        # Sanitizer le prompt utilisateur pour éviter l'injection
        from app.utils.prompt_sanitizer import (sanitize_user_prompt,
                                                validate_prompt_safety)
        is_safe, safety_reason = validate_prompt_safety(prompt_raw)
        if not is_safe:
            logger.warning(f"Prompt utilisateur rejeté pour sécurité: {safety_reason}")
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': f'Prompt invalide: {safety_reason}'})}\n\n"
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        prompt = sanitize_user_prompt(prompt_raw)
        
        # Normaliser le type de challenge
        challenge_type = challenge_type_raw.lower()
        valid_types = ['sequence', 'pattern', 'visual', 'puzzle', 'graph', 'riddle', 'deduction', 'chess', 'coding', 'probability']
        if challenge_type not in valid_types:
            logger.warning(f"Type de challenge invalide: {challenge_type_raw}, utilisation de 'sequence' par défaut")
            challenge_type = 'sequence'
        
        # Normaliser le groupe d'âge
        normalized_age_group = normalize_age_group(age_group_raw)
        age_group = normalized_age_group if normalized_age_group else constants.AgeGroups.GROUP_6_8  # Valeur par défaut
        
        # Rate limiting par utilisateur
        from app.utils.rate_limiter import rate_limiter
        user_id = current_user.get('id')
        if user_id:
            allowed, rate_limit_reason = rate_limiter.check_rate_limit(
                user_id=user_id,
                max_per_hour=10,  # 10 générations par heure
                max_per_day=50    # 50 générations par jour
            )
            if not allowed:
                logger.warning(f"Rate limit atteint pour utilisateur {user_id}: {rate_limit_reason}")
                async def error_generator():
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Limite de génération atteinte: {rate_limit_reason}'})}\n\n"
                return StreamingResponse(
                    error_generator(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                    }
                )
        
        # Vérifier que la clé OpenAI est configurée
        if not settings.OPENAI_API_KEY:
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'OpenAI API key non configurée'})}\n\n"
            
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        async def generate():
            start_time = datetime.now()
            generation_success = False
            validation_passed = True
            auto_corrected = False
            
            try:
                # Importer OpenAI de manière conditionnelle
                try:
                    from openai import AsyncOpenAI
                except ImportError:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Bibliothèque OpenAI non installée'})}\n\n"
                    return
                
                # Récupérer les paramètres OpenAI adaptatifs
                from app.core.ai_config import AIConfig
                ai_params = AIConfig.get_openai_params(challenge_type)
                
                # Créer le client OpenAI avec timeout
                client = AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    timeout=ai_params["timeout"]
                )
                
                # Construire le prompt système avec instructions pour les challenges mathélogiques
                # Définir les paramètres de difficulté selon le groupe d'âge
                age_group_params = {
                    "6-8": {"complexity": "très simple", "numbers_max": 20, "steps": "1-2", "vocabulary": "élémentaire, mots simples", "display": "6-8 ans"},
                    "9-11": {"complexity": "simple à moyen", "numbers_max": 100, "steps": "2-3", "vocabulary": "accessible aux enfants", "display": "9-11 ans"},
                    "12-14": {"complexity": "moyen", "numbers_max": 500, "steps": "3-4", "vocabulary": "langage courant", "display": "12-14 ans"},
                    "15-17": {"complexity": "moyen à complexe", "numbers_max": 1000, "steps": "4-5", "vocabulary": "langage précis", "display": "15-17 ans"},
                    "adulte": {"complexity": "complexe", "numbers_max": 10000, "steps": "5+", "vocabulary": "langage technique possible", "display": "adultes"},
                    "tous-ages": {"complexity": "simple à moyen", "numbers_max": 100, "steps": "2-3", "vocabulary": "accessible à tous", "display": "tous âges"},
                }
                
                # Log pour debug
                logger.info(f"Génération challenge: type={challenge_type}, age_group_raw={age_group_raw}, age_group_normalized={age_group}")
                
                # Obtenir les paramètres ou fallback
                if age_group not in age_group_params:
                    logger.warning(f"Groupe d'âge '{age_group}' non trouvé dans le mapping, utilisation de '9-11' par défaut")
                params = age_group_params.get(age_group, age_group_params["9-11"])
                
                system_prompt = f"""Tu es un assistant pédagogique spécialisé dans la création de défis mathélogiques (logique mathématique).

RÈGLE ABSOLUE : Tu DOIS créer un défi de type "{challenge_type}" uniquement. Ne crée JAMAIS un défi d'un autre type.

GROUPE D'ÂGE CIBLE : {age_group} ans
- Complexité : {params["complexity"]}
- Nombres : max {params["numbers_max"]}
- Étapes de raisonnement : {params["steps"]}
- Vocabulaire : {params["vocabulary"]}

Types de défis possibles :
- "sequence" : Défis de séquences logiques (nombres, formes, motifs qui se suivent)
- "pattern" : Défis de motifs à identifier dans une grille ou un arrangement
- "visual" : Défis visuels et spatiaux (formes, couleurs, rotation, symétrie, positionnement)
- "puzzle" : Défis de puzzle (réorganisation, ordre logique, étapes)
- "graph" : Défis avec graphes et relations (chemins, connexions, réseaux)
- "riddle" : Énigmes logiques avec raisonnement
- "deduction" : Défis de déduction logique (inférence, conclusion)
- "probability" : Défis de probabilités simples
- "coding" : Défis de CRYPTOGRAPHIE et DÉCODAGE (code César, substitution alphabétique, binaire, symboles secrets)
- "chess" : Défis d'échecs (mat en X coups, meilleur coup)

CONTEXTE MATHÉLOGIQUE :
Inspire-toi des exercices de mathélogique qui combinent :
- Raisonnement logique
- Éléments visuels (grilles, formes, couleurs)
- Patterns et séquences
- Déduction et inférence
- Problèmes résolubles avec une méthode claire

RÈGLE IMPORTANTE POUR LES INDICES :
Les indices (hints) doivent être des PISTES pédagogiques qui guident l'élève vers la solution, MAIS NE DOIVENT JAMAIS donner la réponse directement.
- ✅ BON : "Regarde la différence entre chaque élément"
- ✅ BON : "Quel pattern se répète ?"
- ✅ BON : "Pense à l'ordre logique des étapes"
- ❌ MAUVAIS : "La réponse est X"
- ❌ MAUVAIS : "Il faut faire Y puis Z"

Les indices doivent encourager la réflexion sans révéler la solution.

VISUAL_DATA OBLIGATOIRE :
Tu DOIS créer un objet visual_data adapté au type de défi :
- SEQUENCE : {{"sequence": [2, 4, 6, 8], "pattern": "n+2"}}
- PATTERN : {{"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]], "size": 3}}
- PUZZLE : {{"pieces": ["Rouge", "Bleu", "Vert", "Jaune"], "hints": ["L'indice 1 qui aide à trouver l'ordre", "L'indice 2 qui aide à trouver l'ordre", "L'indice 3 qui aide à trouver l'ordre"], "description": "Description du contexte du puzzle"}}
  IMPORTANT PUZZLE : Tu DOIS toujours fournir des indices (hints) suffisants pour que l'utilisateur puisse déduire l'ordre correct ! Sans indices, le puzzle est impossible à résoudre.
- GRAPH : {{"nodes": ["A", "B", "C", "D"], "edges": [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]]}} // IMPORTANT : Tous les noms de nœuds dans edges DOIVENT exister dans nodes
- DEDUCTION (grille logique) : {{"type": "logic_grid", "entities": {{"personnes": ["Alice", "Bob", "Charlie"], "metiers": ["Médecin", "Avocat", "Ingénieur"], "villes": ["Paris", "Lyon", "Marseille"]}}, "clues": ["Alice n'est pas médecin", "L'avocat vit à Lyon", "Charlie ne vit pas à Paris"], "description": "Grille de déduction logique à trois dimensions"}}
  IMPORTANT DEDUCTION : 
  - Le visual_data DOIT contenir "type": "logic_grid" et "entities" avec les catégories
  - La première catégorie dans "entities" est celle sur laquelle l'utilisateur fait ses associations (personnes, élèves, etc.)
  - correct_answer DOIT être au format : "Alice:Médecin:Paris,Bob:Avocat:Lyon,Charlie:Ingénieur:Marseille"
  - Les associations sont séparées par des virgules, les éléments de chaque association par des ":"
  - Les clues doivent permettre de déduire la solution unique
- VISUAL (inclut spatial) : 
  * Pour symétrie/rotation : {{"type": "symmetry", "symmetry_line": "vertical", "layout": [{{"position": 0, "shape": "triangle", "side": "left"}}, {{"position": 1, "shape": "rectangle", "side": "left"}}, {{"position": 2, "shape": "?", "side": "right", "question": true}}, {{"position": 3, "shape": "cercle", "side": "right"}}], "shapes": ["triangle", "rectangle", "?", "cercle"], "arrangement": "horizontal", "description": "Ligne de symétrie verticale au centre"}}
  * Pour formes colorées : {{"shapes": ["cercle rouge", "triangle vert", "carré bleu", "cercle rouge", "triangle vert", "carré ?"], "arrangement": "ligne"}}
  * Pour autres : {{"shapes": ["cercle", "carré", "triangle"], "arrangement": "ligne"}} ou {{"ascii": "ASCII art"}}
- CODING (cryptographie et décodage) :
  * Pour code César : {{"type": "caesar", "encoded_message": "KHOOR", "shift": 3, "alphabet": "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "hint": "Chaque lettre est décalée de 3 positions", "description": "Décode ce message secret en utilisant le code César"}}
  * Pour substitution : {{"type": "substitution", "encoded_message": "YFWJ", "key": {{"A": "Y", "B": "Z", "C": "A", "D": "B", "E": "C", "F": "D", "G": "E", "H": "F", "I": "G", "J": "H", "K": "I", "L": "J", "M": "K", "N": "L", "O": "M", "P": "N", "Q": "O", "R": "P", "S": "Q", "T": "R", "U": "S", "V": "T", "W": "U", "X": "V", "Y": "W", "Z": "X"}}, "partial_key": {{"Y": "A", "F": "H", "W": "E", "J": "L"}}, "description": "Utilise la table de correspondance partielle pour décoder le message"}}
  * Pour binaire : {{"type": "binary", "encoded_message": "01001000 01001001", "hint": "Chaque groupe de 8 bits représente une lettre ASCII", "description": "Convertis ce code binaire en lettres"}}
  * Pour symboles : {{"type": "symbols", "encoded_message": "★●★ ▲■", "key": {{"★": "A", "●": "B", "▲": "C", "■": "D"}}, "description": "Utilise la clé pour décoder les symboles"}}
  * Pour algorithme simple : {{"type": "algorithm", "steps": ["Prends le nombre de départ", "Multiplie par 2", "Ajoute 5", "Divise par le nombre de départ", "Résultat ?"], "input": 3, "description": "Suis les étapes avec le nombre donné"}}
  ⚠️⚠️⚠️ RÈGLES CRITIQUES POUR CODING - LIRE ATTENTIVEMENT ⚠️⚠️⚠️
  
  ❌ CE QUI EST STRICTEMENT INTERDIT POUR LE TYPE "coding" :
  - "sequence" avec des nombres (2, 4, 8, 16...) → C'est le type SEQUENCE, pas CODING !
  - "pattern" avec motifs → C'est le type PATTERN, pas CODING !
  - "shapes", "formes", "couleurs" → C'est le type VISUAL, pas CODING !
  - Multiplications simples (n*2, n+3) → C'est SEQUENCE ou PATTERN !
  - Tout défi qui n'implique pas de DÉCODER UN MESSAGE SECRET
  
  ✅ CE QU'EST VRAIMENT LE TYPE "coding" (CRYPTOGRAPHIE) :
  - DÉCODER un MESSAGE SECRET composé de LETTRES ou SYMBOLES
  - Le visual_data DOIT contenir "type" parmi : "caesar", "substitution", "binary", "symbols", "maze"
  - correct_answer = le MOT ou la PHRASE décodé(e) (ex: "CHAT", "BONJOUR", "OUI")
  
  ✅ EXEMPLES VALIDES DE DÉFIS "coding" :
  - Code César : "FKDW" avec décalage 3 → réponse "CHAT"
  - Substitution : "YFW" avec A→Y, H→F, E→W → réponse "AHE"
  - Binaire : "01000011 01000001 01010100" → réponse "CAT"
  - Symboles : "★●★" avec ★=O, ●=U, →=I → réponse "OUO"
  - Labyrinthe : grille avec robot à programmer → réponse "BAS, DROITE, DROITE"
  
  ❌ EXEMPLES INVALIDES (NE PAS FAIRE POUR "coding") :
  - Séquence 5, 10, 20, 40, ? → UTILISER LE TYPE "sequence" !
  - Grille avec formes et couleurs → UTILISER LE TYPE "visual" !
  - Pattern dans une grille → UTILISER LE TYPE "pattern" !
  - "Labyrinthe de nombres" avec numbers: [1,2,3,4,5...] et target: X → CE N'EST PAS DE LA CRYPTO !
  - Tout défi avec "numbers", "target", "movement_options" → INVALIDE !
  - Robot qui navigue dans une liste de NOMBRES → UTILISER SEQUENCE ou PUZZLE !
  
  ⛔⛔⛔ ERREURS FATALES À ÉVITER ABSOLUMENT ⛔⛔⛔
  SI TU GÉNÈRES UN DÉFI "coding" AVEC :
  - "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9] → ERREUR FATALE
  - "target": un_nombre → ERREUR FATALE  
  - "movement_options": [1, 2] → ERREUR FATALE
  - N'importe quelle liste de nombres sans MESSAGE À DÉCODER → ERREUR FATALE
  
  CODING = DÉCODER UN MESSAGE SECRET EN LETTRES/SYMBOLES, PAS naviguer dans des nombres !

- CHESS (échecs) :
  * Pour mat en X coups : {{"board": [["r", "n", "b", "q", "k", "b", "n", "r"], ["p", "p", "p", "p", "p", "p", "p", "p"], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["P", "P", "P", "P", "P", "P", "P", "P"], ["R", "N", "B", "Q", "K", "B", "N", "R"]], "turn": "white", "objective": "mat_en_3", "question": "Les blancs jouent et font mat en 3 coups"}}
  * Notation des pièces : K/k=Roi, Q/q=Dame, R/r=Tour, B/b=Fou, N/n=Cavalier, P/p=Pion
  * MAJUSCULE = pièce BLANCHE, minuscule = pièce noire
  * Cases vides = "" (chaîne vide)
  * board[0] = rangée 8 (haut), board[7] = rangée 1 (bas)
  * board[row][0] = colonne a, board[row][7] = colonne h
  * correct_answer = notation algébrique des coups : "Qh7+, Kf8, Qf7#" ou "Dd7+, Rf8, Df7#"
  * IMPORTANT : Le board doit représenter une position RÉALISTE avec une solution VÉRIFIABLE
  * Inclure "highlight_positions" pour montrer les pièces clés : [["row", "col"], ...]
  
IMPORTANT pour VISUAL :
- Si le défi utilise des associations forme-couleur, tu DOIS montrer AU MOINS UN EXEMPLE VISIBLE de chaque association AVANT la question.
  Exemple MAUVAIS : ["cercle rouge", "triangle vert", "carré ?"] → L'utilisateur ne sait pas quelle couleur va avec "carré"
  Exemple BON : ["cercle rouge", "carré bleu", "triangle vert", "cercle rouge", "carré ?"] → L'utilisateur voit que carré = bleu
- L'utilisateur doit pouvoir DÉDUIRE la réponse à partir des éléments visibles, pas deviner au hasard.
- Si le défi concerne la symétrie, tu DOIS utiliser la structure "symmetry" avec "layout" et "symmetry_line".
- Ne génère JAMAIS de JSON malformé avec des clés comme "arrangement": "[" ou des valeurs invalides.

VALIDATION LOGIQUE OBLIGATOIRE :
Avant de retourner le JSON, tu DOIS vérifier la cohérence logique :

1. Pour PATTERN avec grille :
   - Analyse le pattern dans la grille (lignes, colonnes, diagonales)
   - Détermine quelle réponse correspond au pattern observé
   - Assure-toi que correct_answer correspond EXACTEMENT à cette réponse
   - Exemple : Si grid = [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]]
     → Le pattern X-O-X suggère que ? = X
     → correct_answer DOIT être "X", pas "O"

2. Pour SEQUENCE :
   - Analyse la séquence pour déterminer le prochain élément
   - Vérifie que correct_answer correspond à cette analyse
   - Exemple : Si sequence = [2, 4, 6, 8]
     → Pattern : +2 à chaque étape
     → Prochain élément = 10
     → correct_answer DOIT être "10"

3. Pour PUZZLE :
   - Tu DOIS fournir des indices (hints) qui permettent de DÉDUIRE l'ordre
   - Chaque indice doit donner une information utile (ex: "Le rouge vient avant le bleu", "Le vert est en 3ème position")
   - Vérifie que correct_answer contient tous les éléments de pieces
   - Vérifie que l'ordre donné par correct_answer est DÉDUCTIBLE à partir des indices
   - L'explication doit montrer comment utiliser les indices pour trouver l'ordre

4. Pour VISUAL avec formes et couleurs :
   - Si la réponse est une couleur (ex: "bleu", "rouge"), tu DOIS montrer cette couleur AVEC une autre forme dans les éléments visibles
   - Exemple : Si correct_answer = "bleu" et c'est pour un carré manquant, il DOIT y avoir un autre "carré bleu" visible dans shapes
   - L'utilisateur ne peut PAS deviner une couleur qu'il n'a jamais vue associée à une forme
   - La description doit expliquer la règle à trouver (ex: "Chaque forme a sa propre couleur")

5. Pour DEDUCTION (grille logique) :
   - Tu DOIS fournir des clues (indices) qui permettent de déduire UNE SEULE solution
   - Chaque entité de la première catégorie doit être associée à exactement une valeur de chaque autre catégorie
   - correct_answer DOIT utiliser le format "Entité1:Val1:Val2,Entité2:Val1:Val2,..."
   - Exemple : Si entities = {{"eleves": ["Emma", "Lucas"], "matieres": ["Maths", "Français"], "scores": [80, 90]}}
     Et la solution est Emma→Maths→90, Lucas→Français→80
     → correct_answer = "Emma:Maths:90,Lucas:Français:80"
   - L'ordre des associations (Emma avant Lucas) n'a pas d'importance
   - Vérifie que les indices permettent de trouver cette solution unique

6. Pour CODING (cryptographie) - VALIDATION STRICTE :
   - Tu DOIS fournir un "type" parmi : "caesar", "substitution", "binary", "symbols", "algorithm", "maze"
   - ERREUR FATALE si visual_data contient : "shapes", "arrangement", "cercle", "carré", "triangle", "couleur"
   - ERREUR FATALE si visual_data contient : "numbers", "target", "movement_options" (ce n'est pas de la crypto !)
   - Ces éléments appartiennent au type "visual", "pattern" ou "sequence", PAS à "coding" !
   - Pour "caesar" : fournis "encoded_message" (lettres encodées), "shift" (1-25), correct_answer = mot décodé
     Exemple : encoded_message="FKDW", shift=3, correct_answer="CHAT"
   - Pour "substitution" : fournis "encoded_message", "key" ou "partial_key" (table lettre→lettre)
   - Pour "binary" : fournis "encoded_message" (groupes de 8 bits : "01001111 01010101 01001001"), correct_answer = "OUI"
   - Pour "symbols" : fournis "encoded_message" avec symboles (★●▲), "key" (table symbole→lettre)
   - Pour "algorithm" : fournis "steps" (instructions), "input" (nombre), correct_answer = résultat
   - Pour "maze" : fournis "maze" (grille de murs #), "start", "end", correct_answer = directions (BAS, DROITE...)
   - correct_answer est TOUJOURS du texte en clair (lettres/mots décodés, directions, ou un nombre pour algorithm)

7. Pour CHESS (échecs) :
   - Tu DOIS fournir "board" : tableau 2D de 8x8 représentant l'échiquier
   - Notation : K=Roi blanc, k=roi noir, Q/q=Dame, R/r=Tour, B/b=Fou, N/n=Cavalier, P/p=Pion
   - MAJUSCULE = BLANC, minuscule = noir, "" = case vide
   - board[0] = rangée 8 (côté noir), board[7] = rangée 1 (côté blanc)
   - "turn" : "white" ou "black" pour indiquer qui joue
   - "objective" : "mat_en_1", "mat_en_2", "mat_en_3", "meilleur_coup", etc.
   - correct_answer : notation algébrique française (Dd4+, Txe5, Cf3, O-O, e4, etc.) ou standard (Qd4+, Rxe5, Nf3, O-O, e4)
   - Pour mat en X coups : donner la séquence complète séparée par virgules
   - Exemple : correct_answer = "Dd7+, Rf8, Df7#" (Dame d7 échec, Roi f8, Dame f7 mat)
   - IMPORTANT : La position doit être LÉGALE et la solution VÉRIFIABLE
   - Éviter les positions impossibles (ex: 10 fous, roi en échec au mauvais tour)

8. Vérification finale :
   - La solution_explanation DOIT expliquer pourquoi correct_answer est correct
   - L'explication DOIT être cohérente avec le visual_data
   - L'explication NE DOIT PAS être contradictoire avec correct_answer

EXEMPLES VALIDES DE PATTERNS :

Exemple 1 - Pattern correct :
visual_data: {{"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "?", "X"]]}}
correct_answer: "O" ✅
solution_explanation: "En observant la colonne du milieu, on voit X-O-X. Le pattern se répète, donc ? = O."

Exemple 2 - Pattern correct :
visual_data: {{"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]]}}
correct_answer: "X" ✅
solution_explanation: "En observant la colonne de droite et la ligne du bas, le pattern X-O-X se répète. Donc ? = X."

Retourne uniquement le défi au format JSON valide avec ces champs:
{{
  "title": "Titre du défi mathélogique (accrocheur, adapté à {age_group} ans)",
  "description": "Description claire du problème avec contexte engageant",
  "question": "Question spécifique et précise à résoudre",
  "correct_answer": "Réponse correcte (VALIDÉE pour correspondre au pattern)",
  "solution_explanation": "Explication détaillée adaptée à {age_group} ans (COHÉRENTE avec correct_answer)",
  "hints": ["Indice 1 (piste pédagogique)", "Indice 2 (piste)", "Indice 3 (piste)"],
  "visual_data": {{...}},
  "difficulty_rating": X.X // Note de 1.0 à 5.0 adaptée au groupe d'âge
}}

RÈGLES DE DIFFICULTÉ (difficulty_rating) :
- 6-8 ans : 1.0 à 2.0 (très facile)
- 9-11 ans : 2.0 à 3.0 (facile à moyen)
- 12-14 ans : 3.0 à 4.0 (moyen)
- 15-17 ans : 3.5 à 4.5 (moyen-difficile)
- adulte : 4.0 à 5.0 (difficile)

Assure-toi que le visual_data est complet et permet une visualisation interactive.
IMPORTANT : Vérifie TOUJOURS la cohérence logique avant de retourner le JSON."""
                
                # Construire le prompt utilisateur avec le groupe d'âge normalisé
                user_prompt = f"""Crée un défi mathélogique de type "{challenge_type}" pour des enfants/élèves de {age_group} ans.

CONTRAINTES OBLIGATOIRES :
- Type de défi : {challenge_type} (pas un autre type !)
- Groupe d'âge : {age_group} ans (adapter la complexité et le vocabulaire)
- Le visual_data DOIT correspondre au type {challenge_type}
- La difficulté doit être adaptée à {age_group} ans"""
                
                # Si l'utilisateur a fourni un prompt personnalisé, l'intégrer en priorité
                if prompt:
                    user_prompt += f"""

DEMANDE PERSONNALISÉE DE L'UTILISATEUR (à respecter en priorité) :
{prompt}

Note : Respecte la demande ci-dessus tout en gardant le type "{challenge_type}" et le groupe d'âge {age_group}."""
                
                # Envoyer un message de démarrage
                yield f"data: {json.dumps({'type': 'status', 'message': 'Génération en cours...'})}\n\n"
                
                # Créer le stream OpenAI avec paramètres adaptatifs et retry logic
                from openai import APIError, APITimeoutError, RateLimitError
                from tenacity import (retry, retry_if_exception_type,
                                      stop_after_attempt, wait_exponential)
                
                @retry(
                    stop=stop_after_attempt(AIConfig.MAX_RETRIES),
                    wait=wait_exponential(
                        multiplier=AIConfig.RETRY_BACKOFF_MULTIPLIER,
                        min=AIConfig.RETRY_MIN_WAIT,
                        max=AIConfig.RETRY_MAX_WAIT
                    ),
                    retry=retry_if_exception_type((RateLimitError, APIError, APITimeoutError)),
                    reraise=True
                )
                async def create_stream_with_retry():
                    # Construire les paramètres selon le modèle
                    api_kwargs = {
                        "model": ai_params["model"],
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "stream": True,
                        "response_format": {"type": "json_object"}
                    }
                    
                    # GPT-5.x utilise max_completion_tokens, reasoning_effort et verbosity
                    if AIConfig.is_gpt5_model(ai_params["model"]):
                        api_kwargs["max_completion_tokens"] = ai_params["max_tokens"]
                        api_kwargs["reasoning_effort"] = ai_params.get("reasoning_effort", "medium")
                        api_kwargs["verbosity"] = ai_params.get("verbosity", "low")
                        # Temperature seulement si reasoning = none
                        if ai_params.get("reasoning_effort") == "none" and "temperature" in ai_params:
                            api_kwargs["temperature"] = ai_params["temperature"]
                    else:
                        # Modèles legacy (GPT-4.x) utilisent max_tokens et temperature
                        api_kwargs["max_tokens"] = ai_params["max_tokens"]
                        api_kwargs["temperature"] = ai_params.get("temperature", 0.5)
                    
                    logger.info(f"Appel API avec params: model={ai_params['model']}, reasoning={ai_params.get('reasoning_effort', 'N/A')}")
                    return await client.chat.completions.create(**api_kwargs)
                
                try:
                    stream = await create_stream_with_retry()
                except (RateLimitError, APIError, APITimeoutError) as api_error:
                    logger.error(f"Erreur API OpenAI après {AIConfig.MAX_RETRIES} tentatives: {api_error}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Erreur lors de la génération après plusieurs tentatives: {str(api_error)}'})}\n\n"
                    return
                except Exception as unexpected_error:
                    logger.error(f"Erreur inattendue lors de la génération: {unexpected_error}")
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Erreur inattendue lors de la génération'})}\n\n"
                    return
                
                full_response = ""
                prompt_tokens_estimate = 0
                completion_tokens_estimate = 0
                
                # Estimer les tokens du prompt (approximation: ~4 caractères par token)
                prompt_length = len(system_prompt) + len(user_prompt)
                prompt_tokens_estimate = prompt_length // 4
                
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        # Estimer les tokens de completion (approximation)
                        completion_tokens_estimate = len(full_response) // 4
                    
                    # Récupérer les métriques d'usage si disponibles dans le chunk
                    if hasattr(chunk, 'usage') and chunk.usage:
                        prompt_tokens_estimate = chunk.usage.prompt_tokens or prompt_tokens_estimate
                        completion_tokens_estimate = chunk.usage.completion_tokens or completion_tokens_estimate
                
                # Parser la réponse JSON complète
                # GPT-5.1 avec reasoning peut inclure du texte avant/après le JSON
                logger.info(f"Réponse reçue: {len(full_response)} caractères, ~{len(full_response)//4} tokens estimés")
                
                try:
                    # Essayer d'abord le parsing direct
                    try:
                        challenge_data = json.loads(full_response)
                    except json.JSONDecodeError:
                        # Chercher le JSON dans la réponse (entre { et })
                        logger.warning("Parsing JSON direct échoué, tentative d'extraction...")
                        json_match = None
                        
                        # Trouver le premier { et le dernier }
                        start_idx = full_response.find('{')
                        end_idx = full_response.rfind('}')
                        
                        if start_idx != -1:
                            # JSON commence par {, extraire jusqu'au dernier }
                            if end_idx != -1 and end_idx > start_idx:
                                json_str = full_response[start_idx:end_idx + 1]
                            else:
                                # JSON tronqué - pas de } trouvé, prendre tout depuis {
                                json_str = full_response[start_idx:]
                                logger.warning(f"JSON tronqué détecté (pas de '}}' final), longueur: {len(json_str)}")
                            
                            try:
                                challenge_data = json.loads(json_str)
                                logger.info("JSON extrait avec succès après nettoyage")
                            except json.JSONDecodeError as inner_error:
                                # Essayer de nettoyer les commentaires // ou /* */
                                import re
                                json_cleaned = re.sub(r'//.*?\n', '\n', json_str)  # Supprimer // comments
                                json_cleaned = re.sub(r'/\*.*?\*/', '', json_cleaned, flags=re.DOTALL)  # Supprimer /* */ comments
                                
                                try:
                                    challenge_data = json.loads(json_cleaned)
                                    logger.info("JSON extrait après suppression des commentaires")
                                except json.JSONDecodeError as clean_error:
                                    # JSON tronqué - essayer de le compléter automatiquement
                                    logger.warning(f"JSON invalide, tentative de complétion automatique... Erreur: {clean_error}")
                                    
                                    # Compter les accolades et crochets non fermés
                                    open_braces = json_cleaned.count('{') - json_cleaned.count('}')
                                    open_brackets = json_cleaned.count('[') - json_cleaned.count(']')
                                    
                                    logger.info(f"Accolades non fermées: {open_braces}, Crochets non fermés: {open_brackets}")
                                    
                                    # Fermer les strings ouvertes (chercher le dernier " non échappé)
                                    if json_cleaned.count('"') % 2 == 1:
                                        # Terminer la string en cours avec une valeur vide
                                        json_cleaned += '..."'
                                        logger.info("String non terminée fermée")
                                    
                                    # Si on est au milieu d'une valeur (après un :), ajouter une valeur par défaut
                                    last_colon = json_cleaned.rfind(':')
                                    last_close = max(json_cleaned.rfind('}'), json_cleaned.rfind(']'), json_cleaned.rfind('"'))
                                    if last_colon > last_close:
                                        # On est après un : sans valeur
                                        json_cleaned += '""'
                                        logger.info("Valeur manquante ajoutée")
                                    
                                    # Fermer les structures ouvertes
                                    json_cleaned += ']' * open_brackets
                                    json_cleaned += '}' * open_braces
                                    
                                    try:
                                        challenge_data = json.loads(json_cleaned)
                                        logger.info("JSON récupéré après complétion automatique")
                                    except json.JSONDecodeError as final_error:
                                        logger.error(f"Impossible de parser le JSON même après complétion: {final_error}")
                                        logger.info(f"Réponse brute (1500 chars): {full_response[:1500]}")
                                        logger.info(f"JSON après complétion (500 chars fin): ...{json_cleaned[-500:]}")
                                        raise
                        else:
                            logger.error(f"Pas de JSON trouvé dans la réponse (pas de '{{' trouvé)")
                            logger.info(f"Réponse brute (1500 chars): {full_response[:1500]}")
                            raise json.JSONDecodeError("Pas de JSON trouvé", full_response, 0)
                    
                    # Vérifier que les données essentielles sont présentes
                    if not challenge_data.get("title") or not challenge_data.get("description"):
                        logger.error(f"Données de challenge incomplètes: {challenge_data}")
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Les données générées sont incomplètes (titre ou description manquant)'})}\n\n"
                        return
                    
                    # VALIDATION LOGIQUE POST-GÉNÉRATION
                    from app.services.challenge_validator import (
                        auto_correct_challenge, validate_challenge_logic)
                    
                    challenge_data['challenge_type'] = challenge_type
                    is_valid, validation_errors = validate_challenge_logic(challenge_data)
                    
                    if not is_valid:
                        logger.warning(f"Challenge généré avec erreurs de validation: {validation_errors}")
                        logger.info("Tentative de correction automatique...")
                        
                        # Tenter une correction automatique
                        corrected_challenge = auto_correct_challenge(challenge_data)
                        
                        # Re-vérifier après correction
                        is_valid_after_correction, remaining_errors = validate_challenge_logic(corrected_challenge)
                        
                        if is_valid_after_correction:
                            logger.info("Correction automatique réussie")
                            challenge_data = corrected_challenge
                            auto_corrected = True
                            validation_passed = True
                        else:
                            logger.error(f"Correction automatique impossible. Erreurs restantes: {remaining_errors}")
                            validation_passed = False
                            # Envoyer un avertissement mais continuer quand même
                            errors_str = ", ".join(remaining_errors[:2])
                            yield f"data: {json.dumps({'type': 'warning', 'message': f'Avertissement: {errors_str}'})}\n\n"
                    else:
                        logger.debug("Challenge validé avec succès")
                        validation_passed = True
                    
                    # Normaliser les données pour correspondre au format attendu
                    # Le groupe d'âge est déjà normalisé depuis le frontend, mais vérifier si l'IA a changé quelque chose
                    ai_age_group = challenge_data.get("age_group")
                    if ai_age_group and ai_age_group != age_group:
                        # L'IA a peut-être changé le groupe d'âge, le re-normaliser mais préférer celui du frontend
                        logger.warning(f"IA a changé le groupe d'âge de {age_group} à {ai_age_group}, conservation de {age_group}")
                    # Toujours utiliser le groupe d'âge normalisé depuis le frontend
                    final_age_group = age_group
                    
                    # Utiliser la difficulté de l'IA si fournie et valide, sinon calculer selon l'âge
                    ai_difficulty = challenge_data.get("difficulty_rating")
                    expected_difficulty = calculate_difficulty_for_age_group(final_age_group)
                    if ai_difficulty and isinstance(ai_difficulty, (int, float)) and 1.0 <= ai_difficulty <= 5.0:
                        # Vérifier que la difficulté est adaptée au groupe d'âge
                        # Si la difficulté de l'IA est trop éloignée, utiliser celle calculée
                        if abs(ai_difficulty - expected_difficulty) > 1.5:
                            logger.info(f"Difficulté IA ({ai_difficulty}) ajustée pour groupe d'âge {final_age_group} -> {expected_difficulty}")
                            final_difficulty = expected_difficulty
                        else:
                            final_difficulty = float(ai_difficulty)
                    else:
                        final_difficulty = expected_difficulty
                    
                    normalized_challenge = {
                        "challenge_type": challenge_type.upper(),
                        "age_group": final_age_group,  # Utiliser la valeur normalisée depuis le frontend (préservée)
                        "title": challenge_data.get("title", f"Défi {challenge_type}"),
                        "description": challenge_data.get("description", ""),
                        "question": challenge_data.get("question", ""),
                        "correct_answer": str(challenge_data.get("correct_answer", "")),
                        "solution_explanation": challenge_data.get("solution_explanation", ""),
                        "hints": challenge_data.get("hints", []),
                        "visual_data": challenge_data.get("visual_data", {}),
                        "difficulty_rating": final_difficulty,  # Difficulté adaptée au groupe d'âge
                        "estimated_time_minutes": 10,
                        "tags": "ai,generated,mathélogique"
                    }
                    
                    # Vérification finale que le challenge normalisé est valide
                    if not normalized_challenge.get("title") or not normalized_challenge.get("description"):
                        logger.error(f"Challenge normalisé invalide: {normalized_challenge}")
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Erreur lors de la normalisation des données'})}\n\n"
                        return
                    
                    # Optionnellement sauvegarder en base de données
                    try:
                        accept_language = request.headers.get("Accept-Language")
                        locale = parse_accept_language(accept_language) or "fr"
                        
                        db = EnhancedServerAdapter.get_db_session()
                        try:
                            # NOTE: challenge_service_translations archivé - utiliser challenge_service.create_challenge
                            # La fonction create_challenge() n'accepte pas le paramètre locale
                            created_challenge = challenge_service.create_challenge(
                                db=db,
                                title=normalized_challenge['title'],
                                description=normalized_challenge['description'],
                                challenge_type=normalized_challenge['challenge_type'],
                                age_group=normalized_challenge['age_group'],
                                question=normalized_challenge.get('question'),
                                correct_answer=normalized_challenge['correct_answer'],
                                solution_explanation=normalized_challenge['solution_explanation'],
                                hints=normalized_challenge.get('hints', []),
                                visual_data=normalized_challenge.get('visual_data', {}),
                                difficulty_rating=normalized_challenge.get('difficulty_rating', 3.0),
                                estimated_time_minutes=normalized_challenge.get('estimated_time_minutes', 10),
                                tags=normalized_challenge.get('tags', 'ai,generated'),
                                creator_id=current_user.get('id')
                            )
                            
                            # Vérifier que le challenge a été créé avec succès
                            # created_challenge est un objet LogicChallenge, pas un dictionnaire
                            if created_challenge and hasattr(created_challenge, 'title') and created_challenge.title:
                                # Track token usage
                                from app.utils.token_tracker import \
                                    token_tracker
                                usage_stats = token_tracker.track_usage(
                                    challenge_type=challenge_type,
                                    prompt_tokens=prompt_tokens_estimate,
                                    completion_tokens=completion_tokens_estimate,
                                    model=ai_params["model"]
                                )
                                logger.debug(f"Token usage tracked: {usage_stats}")
                                
                                # Enregistrer les métriques de génération réussie
                                generation_success = True
                                duration = (datetime.now() - start_time).total_seconds()
                                from app.utils.generation_metrics import \
                                    generation_metrics
                                generation_metrics.record_generation(
                                    challenge_type=challenge_type,
                                    success=True,
                                    validation_passed=validation_passed,
                                    auto_corrected=auto_corrected,
                                    duration_seconds=duration
                                )
                                
                                # Convertir l'objet LogicChallenge en dictionnaire pour la réponse JSON
                                from app.services.challenge_service import normalize_age_group_for_frontend
                                challenge_dict = {
                                    'id': created_challenge.id,
                                    'title': created_challenge.title,
                                    'description': created_challenge.description,
                                    'challenge_type': str(created_challenge.challenge_type) if hasattr(created_challenge.challenge_type, 'value') else created_challenge.challenge_type,
                                    'age_group': normalize_age_group_for_frontend(created_challenge.age_group),
                                    'question': created_challenge.question,
                                    'correct_answer': created_challenge.correct_answer,
                                    'solution_explanation': created_challenge.solution_explanation,
                                    'hints': created_challenge.hints or [],
                                    'visual_data': created_challenge.visual_data or {},
                                    'difficulty_rating': created_challenge.difficulty_rating,
                                    'estimated_time_minutes': created_challenge.estimated_time_minutes,
                                    'tags': created_challenge.tags,
                                    'is_active': created_challenge.is_active,
                                    'created_at': created_challenge.created_at.isoformat() if created_challenge.created_at else None
                                }
                                # Envoyer le challenge complet au client
                                yield f"data: {json.dumps({'type': 'challenge', 'challenge': challenge_dict})}\n\n"
                            else:
                                logger.error(f"Challenge créé mais invalide: {created_challenge}")
                                # Envoyer quand même le challenge normalisé (sans sauvegarde)
                                yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
                            
                        except Exception as db_error:
                            logger.error(f"Erreur lors de la sauvegarde du challenge: {db_error}")
                            logger.debug(traceback.format_exc())
                            # Vérifier que normalized_challenge a un title avant d'envoyer
                            if normalized_challenge.get('title'):
                                # Envoyer quand même le challenge généré (sans sauvegarde)
                                yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
                            else:
                                yield f"data: {json.dumps({'type': 'error', 'message': 'Erreur lors de la sauvegarde et challenge invalide'})}\n\n"
                        finally:
                            db.close()
                            
                    except Exception as save_error:
                        logger.error(f"Erreur lors de la sauvegarde: {save_error}")
                        logger.debug(traceback.format_exc())
                        # Vérifier que normalized_challenge a un title avant d'envoyer
                        if normalized_challenge.get('title'):
                            # Envoyer quand même le challenge généré
                            yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'error', 'message': 'Erreur lors de la sauvegarde et challenge invalide'})}\n\n"
                    
                    # Message de fin
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
                except json.JSONDecodeError as json_error:
                    logger.error(f"Erreur de parsing JSON: {json_error}")
                    logger.debug(f"Réponse reçue: {full_response[:500]}")
                    duration = (datetime.now() - start_time).total_seconds()
                    from app.utils.generation_metrics import generation_metrics
                    generation_metrics.record_generation(
                        challenge_type=challenge_type,
                        success=False,
                        validation_passed=False,
                        duration_seconds=duration,
                        error_type="json_decode_error"
                    )
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Erreur lors du parsing de la réponse JSON'})}\n\n"
                    
            except Exception as gen_error:
                logger.error(f"Erreur lors de la génération: {gen_error}")
                logger.debug(traceback.format_exc())
                duration = (datetime.now() - start_time).total_seconds()
                from app.utils.generation_metrics import generation_metrics
                generation_metrics.record_generation(
                    challenge_type=challenge_type,
                    success=False,
                    validation_passed=False,
                    duration_seconds=duration,
                    error_type=type(gen_error).__name__
                )
                yield f"data: {json.dumps({'type': 'error', 'message': str(gen_error)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as ai_stream_error:
        logger.error(f"Erreur dans generate_ai_challenge_stream: {ai_stream_error}")
        logger.debug(traceback.format_exc())
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'message': 'Erreur lors de la génération'})}\n\n"
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

