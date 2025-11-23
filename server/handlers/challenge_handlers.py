"""
Handlers pour les défis logiques (API Starlette)
"""
import traceback
import json
from datetime import datetime
from starlette.responses import JSONResponse, StreamingResponse
from starlette.requests import Request
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.logic_challenge_service import LogicChallengeService
# NOTE: challenge_service_translations_adapter archivé - utiliser fonctions de challenge_service.py
from app.services import challenge_service
from app.utils.translation import parse_accept_language
from app.core.messages import SystemMessages
from app.utils.error_handler import ErrorHandler
from app.core.config import settings
from loguru import logger

# Importer les constantes et fonctions centralisées
from app.core.constants import (
    normalize_challenge_type as normalize_challenge_type_for_db,
    CHALLENGE_TYPES_API,
    CHALLENGE_TYPES_DB,
    calculate_difficulty_for_age_group,
)


def normalize_age_group_for_db(age_group_raw: str) -> str:
    """
    Normalise un groupe d'âge vers les valeurs PostgreSQL valides.
    
    Valeurs PostgreSQL acceptées : GROUP_10_12, GROUP_13_15, ALL_AGES
    
    Args:
        age_group_raw: Valeur brute du groupe d'âge (peut être "adolescent", "10-12", "GROUP_10_12", etc.)
    
    Returns:
        Valeur normalisée pour PostgreSQL (GROUP_10_12, GROUP_13_15, ou ALL_AGES)
    """
    if not age_group_raw:
        return None  # Pas de filtre
    
    age_group_lower = age_group_raw.lower().strip()
    
    # Mapping des valeurs vers les valeurs PostgreSQL valides
    age_group_mapping = {
        # Valeurs textuelles
        'enfant': 'GROUP_10_12',
        'adolescent': 'GROUP_13_15',
        'adulte': 'ALL_AGES',
        # Valeurs avec tirets
        '9-12': 'GROUP_10_12',
        '10-12': 'GROUP_10_12',
        '12-13': 'GROUP_13_15',
        '13-15': 'GROUP_13_15',
        '13+': 'GROUP_13_15',
        # Valeurs avec underscores (déjà normalisées)
        'group_10_12': 'GROUP_10_12',
        'group_13_15': 'GROUP_13_15',
        'all_ages': 'ALL_AGES',
        'all': 'ALL_AGES',
        # Valeurs en majuscules (déjà normalisées)
        'GROUP_10_12': 'GROUP_10_12',
        'GROUP_13_15': 'GROUP_13_15',
        'ALL_AGES': 'ALL_AGES',
        # Valeurs avec préfixe AGE_
        'age_9_12': 'GROUP_10_12',
        'age_12_13': 'GROUP_13_15',
        'age_13_plus': 'GROUP_13_15',
    }
    
    # Chercher dans le mapping
    normalized = age_group_mapping.get(age_group_lower)
    if normalized:
        return normalized
    
    # Si la valeur commence par GROUP_, la mettre en majuscules
    if age_group_raw.upper().startswith('GROUP_'):
        return age_group_raw.upper()
    
    # Valeur invalide, ne pas filtrer
    logger.warning(f"Groupe d'âge non reconnu '{age_group_raw}', filtre ignoré")
    return None


async def get_challenges_list(request: Request):
    """
    Liste des défis logiques avec filtres optionnels.
    Route: GET /api/challenges
    """
    try:
        # Vérifier l'authentification
        from server.auth import get_current_user
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"detail": "Non authentifié"}, status_code=401)
        
        # Récupérer les paramètres de requête
        challenge_type_raw = request.query_params.get('challenge_type')
        age_group_raw = request.query_params.get('age_group')
        search = request.query_params.get('search') or request.query_params.get('q')  # Support 'search' et 'q'
        skip = int(request.query_params.get('skip', 0))
        limit_param = request.query_params.get('limit')
        limit = int(limit_param) if limit_param else 20
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        
        # Normaliser les filtres pour correspondre aux valeurs PostgreSQL
        challenge_type = normalize_challenge_type_for_db(challenge_type_raw) if challenge_type_raw else None
        age_group = normalize_age_group_for_db(age_group_raw) if age_group_raw else None
        
        # Calculer la page à partir de skip et limit
        page = (skip // limit) + 1 if limit > 0 else 1
        
        # Récupérer la locale depuis le header Accept-Language
        accept_language = request.headers.get('Accept-Language', 'fr')
        locale = parse_accept_language(accept_language)

        logger.debug(f"API - Paramètres reçus: limit={limit}, skip={skip}, page={page}, challenge_type_raw={challenge_type_raw}, challenge_type_normalized={challenge_type}, age_group_raw={age_group_raw}, age_group_normalized={age_group}, search={search}, locale={locale}")

        # Utiliser le service ORM challenge_service
        db = EnhancedServerAdapter.get_db_session()
        try:
            # Récupérer les challenges via la fonction list_challenges
            challenges = challenge_service.list_challenges(
                db=db,
                challenge_type=challenge_type,
                age_group=age_group,
                tags=search,  # Utiliser search comme filtre tags
                limit=limit,
                offset=skip
            )
            # Convertir les objets en dicts
            challenges_list = [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "challenge_type": c.challenge_type,
                    "age_group": c.age_group,
                    "difficulty": c.difficulty,
                    "tags": c.tags,
                    "difficulty_rating": c.difficulty_rating,
                    "estimated_time_minutes": c.estimated_time_minutes,
                    "success_rate": c.success_rate,
                    "view_count": c.view_count,
                    "is_archived": c.is_archived
                } for c in challenges
            ]
        finally:
            EnhancedServerAdapter.close_db_session(db)
        
        # Filtrer les défis archivés si nécessaire (déjà fait dans la query, mais double vérification)
        if active_only:
            challenges_list = [c for c in challenges_list if not c.get('is_archived', False)]
        
        # Compter le total pour la pagination (réutiliser la même session)
        db2 = EnhancedServerAdapter.get_db_session()
        try:
            total = challenge_service.count_challenges(
                db=db2,
                challenge_type=challenge_type,
                age_group=age_group
            )
        finally:
            EnhancedServerAdapter.close_db_session(db2)

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


async def get_challenge(request: Request):
    """
    Récupère un défi logique par son ID.
    Route: GET /api/challenges/{challenge_id}
    """
    try:
        # Vérifier l'authentification
        from server.auth import get_current_user
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"detail": "Non authentifié"}, status_code=401)
        
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
                
                challenge_dict = {
                    "id": challenge.id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "challenge_type": challenge.challenge_type,
                    "age_group": challenge.age_group,
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


async def submit_challenge_answer(request: Request):
    """
    Soumet une réponse à un défi logique.
    Route: POST /api/challenges/{challenge_id}/attempt
    """
    try:
        # Récupérer l'utilisateur actuel
        from server.auth import get_current_user
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse({"error": "Non authentifié"}, status_code=401)
        
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
                # Pour les puzzles, normaliser les réponses (insensible à la casse, espaces)
                user_answer_normalized = str(user_solution).strip().lower().replace(' ', '')
                correct_answer_normalized = str(challenge.correct_answer).strip().lower().replace(' ', '')
                
                # Pour les réponses de type liste (séparées par virgules), comparer les listes
                if ',' in user_answer_normalized or ',' in correct_answer_normalized:
                    # Normaliser les listes : trier et comparer
                    user_list = [item.strip() for item in user_answer_normalized.split(',') if item.strip()]
                    correct_list = [item.strip() for item in correct_answer_normalized.split(',') if item.strip()]
                    is_correct = user_list == correct_list
                else:
                    # Comparaison simple pour les autres types
                    is_correct = user_answer_normalized == correct_answer_normalized
                
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
            
            if not attempt:
                logger.error("ERREUR: La tentative de challenge n'a pas été enregistrée correctement")
                # On continue quand même pour retourner le résultat à l'utilisateur
            
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
                hints = json.loads(hints)
            elif hints is None:
                hints = []
            
            if level < 1 or level > len(hints):
                return JSONResponse({"error": f"Indice de niveau {level} non disponible"}, status_code=400)
            
            return JSONResponse({"hints": hints[:level]})  # Retourner tous les indices jusqu'au niveau demandé
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except ValueError:
        return JSONResponse({"error": "ID de défi ou niveau invalide"}, status_code=400)
    except Exception as hint_retrieval_error:
        logger.error(f"Erreur lors de la récupération de l'indice: {hint_retrieval_error}")
        traceback.print_exc()
        return JSONResponse({"error": f"Erreur: {str(e)}"}, status_code=500)


async def get_completed_challenges_ids(request: Request):
    """
    Récupère la liste des IDs de challenges complétés par l'utilisateur actuel.
    Route: GET /api/challenges/completed-ids
    """
    try:
        # Vérifier l'authentification
        from server.auth import get_current_user
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
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


async def generate_ai_challenge_stream(request: Request):
    """
    Génère un challenge avec OpenAI en streaming SSE.
    Permet un affichage progressif de la génération pour une meilleure UX.
    Crée des challenges de type mathélogique avec visual_data selon le type.
    """
    try:
        # Vérifier l'authentification
        from server.auth import get_current_user
        current_user = await get_current_user(request)
        if not current_user or not current_user.get("is_authenticated"):
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Non authentifié'})}\n\n"
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        # Récupérer les paramètres de la requête
        challenge_type_raw = request.query_params.get('challenge_type', 'sequence')
        age_group_raw = request.query_params.get('age_group', '10-12')
        prompt_raw = request.query_params.get('prompt', '')
        
        # Sanitizer le prompt utilisateur pour éviter l'injection
        from app.utils.prompt_sanitizer import sanitize_user_prompt, validate_prompt_safety
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
        valid_types = ['sequence', 'pattern', 'visual', 'spatial', 'puzzle', 'graph', 'riddle', 'deduction', 'chess', 'coding', 'probability', 'custom']
        if challenge_type not in valid_types:
            logger.warning(f"Type de challenge invalide: {challenge_type_raw}, utilisation de 'sequence' par défaut")
            challenge_type = 'sequence'
        
        # Normaliser le groupe d'âge vers les valeurs PostgreSQL valides AVANT génération IA
        normalized_age_group = normalize_age_group_for_db(age_group_raw)
        age_group = normalized_age_group if normalized_age_group else 'GROUP_10_12'  # Valeur par défaut si None
        
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
                system_prompt = f"""Tu es un assistant pédagogique spécialisé dans la création de défis mathélogiques (logique mathématique) pour enfants de 5 à 15 ans.

RÈGLE ABSOLUE : Tu DOIS créer un défi de type "{challenge_type}" uniquement. Ne crée JAMAIS un défi d'un autre type.

Types de défis possibles :
- "sequence" : Défis de séquences logiques (nombres, formes, motifs qui se suivent)
- "pattern" : Défis de motifs à identifier dans une grille ou un arrangement
- "visual" : Défis visuels avec formes, couleurs, arrangements spatiaux
- "spatial" : Défis de raisonnement spatial (rotation, symétrie, positionnement)
- "puzzle" : Défis de puzzle (réorganisation, ordre logique, étapes)
- "graph" : Défis avec graphes et relations (chemins, connexions, réseaux)
- "riddle" : Énigmes logiques avec raisonnement
- "deduction" : Défis de déduction logique (inférence, conclusion)

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
- PUZZLE : {{"pieces": ["Étape1", "Étape2", "Étape3", "Étape4"]}}
- GRAPH : {{"nodes": ["A", "B", "C", "D"], "edges": [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]]}} // IMPORTANT : Tous les noms de nœuds dans edges DOIVENT exister dans nodes
- VISUAL/SPATIAL : 
  * Pour symétrie : {{"type": "symmetry", "symmetry_line": "vertical", "layout": [{{"position": 0, "shape": "triangle", "side": "left"}}, {{"position": 1, "shape": "rectangle", "side": "left"}}, {{"position": 2, "shape": "?", "side": "right", "question": true}}, {{"position": 3, "shape": "cercle", "side": "right"}}], "shapes": ["triangle", "rectangle", "?", "cercle"], "arrangement": "horizontal", "description": "Ligne de symétrie verticale au centre"}}
  * Pour autres : {{"shapes": ["cercle", "carré", "triangle"], "arrangement": "ligne"}} ou {{"ascii": "ASCII art"}}
  
IMPORTANT pour SPATIAL : Si le défi concerne la symétrie, tu DOIS utiliser la structure "symmetry" avec "layout" et "symmetry_line". Ne génère JAMAIS de JSON malformé avec des clés comme "arrangement": "[" ou des valeurs invalides.

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
   - Vérifie que correct_answer contient tous les éléments de pieces
   - Vérifie que l'ordre est logique

4. Vérification finale :
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
  "title": "Titre du défi mathélogique",
  "description": "Description du problème avec contexte clair",
  "question": "Question spécifique à résoudre",
  "correct_answer": "Réponse correcte (VALIDÉE pour correspondre au pattern)",
  "solution_explanation": "Explication détaillée de la solution et de la méthode (COHÉRENTE avec correct_answer)",
  "hints": ["Indice 1 (piste pédagogique)", "Indice 2 (piste pédagogique)", "Indice 3 (piste pédagogique)"],
  "visual_data": {{...}} // Objet JSON adapté au type de défi
}}

Assure-toi que le visual_data est complet et permet une visualisation interactive.
IMPORTANT : Vérifie TOUJOURS la cohérence logique avant de retourner le JSON."""
                
                # Construire le prompt utilisateur avec le groupe d'âge normalisé
                user_prompt = f"Crée un défi mathélogique de type {challenge_type} pour le groupe d'âge {age_group}. IMPORTANT : Le défi DOIT être de type {challenge_type}, pas un autre type. Le visual_data DOIT être adapté à ce type. Le groupe d'âge du défi DOIT correspondre à {age_group}."
                if prompt:
                    user_prompt += f" {prompt}"
                
                # Envoyer un message de démarrage
                yield f"data: {json.dumps({'type': 'status', 'message': 'Génération en cours...'})}\n\n"
                
                # Créer le stream OpenAI avec paramètres adaptatifs et retry logic
                from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
                from openai import RateLimitError, APIError, APITimeoutError
                
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
                    return await client.chat.completions.create(
                        model=ai_params["model"],
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        stream=True,
                        temperature=ai_params["temperature"],
                        max_tokens=ai_params["max_tokens"],
                        response_format={"type": "json_object"}  # Forcer JSON
                    )
                
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
                try:
                    challenge_data = json.loads(full_response)
                    
                    # Vérifier que les données essentielles sont présentes
                    if not challenge_data.get("title") or not challenge_data.get("description"):
                        logger.error(f"Données de challenge incomplètes: {challenge_data}")
                        yield f"data: {json.dumps({'type': 'error', 'message': 'Les données générées sont incomplètes (titre ou description manquant)'})}\n\n"
                        return
                    
                    # VALIDATION LOGIQUE POST-GÉNÉRATION
                    from app.services.challenge_validator import validate_challenge_logic, auto_correct_challenge
                    
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
                    
                    # Calculer la difficulté adaptée au groupe d'âge
                    def calculate_difficulty_for_age_group(age_group: str) -> float:
                        """Calcule une difficulté appropriée selon le groupe d'âge."""
                        difficulty_map = {
                            'GROUP_10_12': 2.0,  # Facile pour 10-12 ans
                            'GROUP_13_15': 3.5,  # Moyen-difficile pour 13-15 ans
                            'ALL_AGES': 3.0,     # Moyen pour tous âges
                        }
                        return difficulty_map.get(age_group, 3.0)
                    
                    # Utiliser la difficulté de l'IA si fournie et valide, sinon calculer selon l'âge
                    ai_difficulty = challenge_data.get("difficulty_rating")
                    if ai_difficulty and isinstance(ai_difficulty, (int, float)) and 1.0 <= ai_difficulty <= 5.0:
                        # Vérifier que la difficulté est adaptée au groupe d'âge
                        expected_difficulty = calculate_difficulty_for_age_group(final_age_group)
                        # Si la difficulté de l'IA est trop éloignée, utiliser celle calculée
                        if abs(ai_difficulty - expected_difficulty) > 1.5:
                            logger.info(f"Difficulté IA ({ai_difficulty}) ajustée pour groupe d'âge {final_age_group} -> {expected_difficulty}")
                            final_difficulty = expected_difficulty
                        else:
                            final_difficulty = float(ai_difficulty)
                    else:
                        final_difficulty = calculate_difficulty_for_age_group(final_age_group)
                    
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
                                from app.utils.token_tracker import token_tracker
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
                                from app.utils.generation_metrics import generation_metrics
                                generation_metrics.record_generation(
                                    challenge_type=challenge_type,
                                    success=True,
                                    validation_passed=validation_passed,
                                    auto_corrected=auto_corrected,
                                    duration_seconds=duration
                                )
                                
                                # Convertir l'objet LogicChallenge en dictionnaire pour la réponse JSON
                                challenge_dict = {
                                    'id': created_challenge.id,
                                    'title': created_challenge.title,
                                    'description': created_challenge.description,
                                    'challenge_type': str(created_challenge.challenge_type) if hasattr(created_challenge.challenge_type, 'value') else created_challenge.challenge_type,
                                    'age_group': str(created_challenge.age_group) if hasattr(created_challenge.age_group, 'value') else created_challenge.age_group,
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

