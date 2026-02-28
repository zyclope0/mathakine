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

import app.core.constants as constants
from app.core.config import settings

# Importer les constantes et fonctions centralisées
from app.core.constants import (
    CHALLENGE_TYPES_API,
    CHALLENGE_TYPES_DB,
    calculate_difficulty_for_age_group,
    normalize_age_group,
)
from app.core.messages import SystemMessages
from app.exceptions import ChallengeNotFoundError

# NOTE: challenge_service_translations_adapter archivé - utiliser fonctions de challenge_service.py
from app.services import challenge_service
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from app.services.logic_challenge_service import LogicChallengeService
from app.utils.db_utils import db_session
from app.utils.error_handler import (
    ErrorHandler,
    api_error_response,
    get_safe_error_message,
)
from app.utils.request_utils import parse_json_body_any
from app.utils.translation import parse_accept_language
from server.auth import (
    optional_auth,
    require_auth,
    require_auth_sse,
    require_full_access,
)


@require_auth
@require_full_access
async def get_challenges_list(request: Request):
    """
    Liste des défis logiques avec filtres optionnels.
    Route: GET /api/challenges
    """
    from app.schemas.logic_challenge import ChallengeListItem, ChallengeListResponse
    from server.handlers.challenge_list_params import parse_challenge_list_params

    try:
        current_user = request.state.user
        p = parse_challenge_list_params(request)

        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language)
        logger.debug(
            f"API - Paramètres: limit={p.limit}, skip={p.skip}, order={p.order}, "
            f"hide_completed={p.hide_completed}"
        )

        user_id = current_user.get("id")
        exclude_ids: list[int] = []

        async with db_session() as db:
            if p.hide_completed and user_id:
                exclude_ids = challenge_service.get_user_completed_challenges(
                    db, user_id
                )
            challenges = challenge_service.list_challenges(
                db=db,
                challenge_type=p.challenge_type,
                age_group=p.age_group_db,
                tags=p.search,
                limit=p.limit,
                offset=p.skip,
                order=p.order,
                exclude_ids=exclude_ids if exclude_ids else None,
            )
            challenges_list = [
                ChallengeListItem.model_validate(
                    challenge_service.challenge_to_api_dict(c)
                )
                for c in challenges
            ]
            total = challenge_service.count_challenges(
                db=db,
                challenge_type=p.challenge_type,
                age_group=p.age_group_db,
                exclude_ids=exclude_ids if exclude_ids else None,
            )

        if p.active_only:
            challenges_list = [c for c in challenges_list if not c.is_archived]

        page = (p.skip // p.limit) + 1 if p.limit > 0 else 1
        has_more = (p.skip + len(challenges_list)) < total
        response_data = ChallengeListResponse(
            items=challenges_list,
            total=total,
            page=page,
            limit=p.limit,
            hasMore=has_more,
        )
        logger.info(
            f"Récupération réussie de {len(challenges_list)} défis sur {total} total (locale: {locale})"
        )
        return JSONResponse(response_data.model_dump())
    except ValueError as filter_validation_error:
        logger.error(f"Erreur de validation des paramètres: {filter_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=[str(filter_validation_error)],
            user_message="Les paramètres de filtrage sont invalides.",
        )
    except Exception as challenges_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération des défis: {challenges_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenges_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération des défis.",
        )


@require_auth
@require_full_access
async def get_challenge(request: Request):
    """
    Récupère un défi logique par son ID.
    Route: GET /api/challenges/{challenge_id}
    """
    try:
        current_user = request.state.user

        challenge_id = int(request.path_params.get("challenge_id"))

        # Récupérer la locale depuis le header Accept-Language
        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language)

        async with db_session() as db:
            from app.services.challenge_service import get_challenge_for_api

            challenge_dict = get_challenge_for_api(db, challenge_id)

        logger.info(
            f"Récupération réussie du défi logique {challenge_id} (locale: {locale})"
        )
        return JSONResponse(challenge_dict)
    except ChallengeNotFoundError:
        return api_error_response(404, "Défi logique non trouvé")
    except ValueError as id_validation_error:
        logger.error(f"Erreur de validation: {id_validation_error}")
        return ErrorHandler.create_validation_error(
            errors=["ID de défi invalide"],
            user_message="L'identifiant du défi est invalide.",
        )
    except Exception as challenge_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération du défi: {challenge_retrieval_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=challenge_retrieval_error,
            status_code=500,
            user_message="Erreur lors de la récupération du défi.",
        )


@require_auth
@require_full_access
async def submit_challenge_answer(request: Request):
    """
    Soumet une réponse à un défi logique.
    Route: POST /api/challenges/{challenge_id}/attempt
    """
    try:
        current_user = request.state.user

        user_id = current_user.get("id")
        if not user_id:
            return api_error_response(401, "Utilisateur invalide")

        challenge_id = int(request.path_params.get("challenge_id"))
        data_or_err = await parse_json_body_any(request)
        if isinstance(data_or_err, JSONResponse):
            return data_or_err
        data = data_or_err

        user_solution = data.get("user_solution") or data.get("answer")
        time_spent = data.get("time_spent")
        hints_used_raw = data.get("hints_used", [])

        # Convertir hints_used de liste à entier (nombre d'indices utilisés)
        # Le modèle attend un Integer, pas une liste
        if isinstance(hints_used_raw, list):
            hints_used_count = len(hints_used_raw)
        elif isinstance(hints_used_raw, int):
            hints_used_count = hints_used_raw
        else:
            hints_used_count = 0

        if not user_solution:
            return api_error_response(400, "Réponse requise")

        async with db_session() as db:
            challenge = LogicChallengeService.get_challenge_or_raise(db, challenge_id)

            # Vérifier la réponse
            def _normalize_accents(text: str) -> str:
                """Retire les accents pour tolérance (carré→carre, élève→eleve)."""
                import unicodedata

                return (
                    "".join(
                        c
                        for c in unicodedata.normalize("NFD", text)
                        if unicodedata.category(c) != "Mn"
                    )
                    if text
                    else ""
                )

            def _normalize_shape_answer(text: str) -> str:
                """Normalise pour VISUAL : synonymes, accents, ordre forme+couleur."""
                if not text:
                    return ""
                t = text.lower().strip()
                for old, new in [
                    ("rectangle", "carre"),
                    ("square", "carre"),
                    ("circle", "cercle"),
                    ("carré", "carre"),
                    ("étoile", "etoile"),
                    ("losange", "losange"),
                ]:
                    if old in t:
                        t = t.replace(old, new)
                t = _normalize_accents(t)
                # Accepter "bleu carre" ou "carre bleu" -> normaliser en "carre bleu"
                mots = t.split()
                formes = {
                    "carre",
                    "cercle",
                    "triangle",
                    "rectangle",
                    "losange",
                    "etoile",
                    "hexagone",
                    "pentagone",
                }
                couleurs = {
                    "rouge",
                    "bleu",
                    "vert",
                    "jaune",
                    "orange",
                    "violet",
                    "rose",
                    "gris",
                    "noir",
                    "blanc",
                    "red",
                    "blue",
                    "green",
                    "yellow",
                }
                f, c = None, None
                for m in mots:
                    if m in formes:
                        f = m
                    elif m in couleurs:
                        c = m
                if f and c:
                    t = f"{f} {c}"
                return t

            def _parse_multi_visual_answer(text: str) -> list:
                """Parse multi-cellules VISUAL. Formats acceptés :
                - 'Position 6: carré bleu, Position 9: triangle vert'
                - '6:cercle rouge,9:étoile jaune' (format IA)
                """
                if not text or not text.strip():
                    return []
                parts = []
                for segment in text.replace(",", " , ").split(","):
                    segment = segment.strip()
                    if not segment:
                        continue
                    # Format "Position 6: xxx" ou "6: xxx"
                    if ":" in segment:
                        pos_part, ans_part = segment.split(":", 1)
                        ans_part = ans_part.strip()
                        pos_digits = "".join(c for c in pos_part if c.isdigit())
                        if pos_digits and ans_part and not ans_part.isdigit():
                            # Segment ressemble à "6:cercle rouge" ou "Position 6: cercle rouge"
                            parts.append(
                                (int(pos_digits), _normalize_shape_answer(ans_part))
                            )
                            continue
                    parts.append((0, _normalize_shape_answer(segment)))
                if parts:
                    return parts
                return [(0, _normalize_shape_answer(text))] if text.strip() else []

            # Fonction helper pour parser une réponse (gère format liste Python et CSV)
            def parse_answer_to_list(answer: str) -> list:
                """Parse une réponse en liste, gérant plusieurs formats."""
                answer = str(answer).strip()

                # Format liste Python : "['Rouge', 'Vert', 'Jaune', 'Bleu']"
                if answer.startswith("[") and answer.endswith("]"):
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
                    for item in inner.split(","):
                        item = item.strip().strip("'").strip('"').strip().lower()
                        if item:
                            items.append(item)
                    return items

                # Format CSV simple : "Rouge,Vert,Jaune,Bleu" ou "O, O, X, O"
                if "," in answer:
                    return [
                        item.strip().lower()
                        for item in answer.split(",")
                        if item.strip()
                    ]

                # Séparateur espaces : "O O X O" (sans virgules)
                parts = [p.strip().lower() for p in answer.split() if p.strip()]
                if len(parts) > 1:
                    return parts

                # Valeur simple
                return [answer.lower()] if answer else []

            def compare_deduction_answers(
                user_answer: str, correct_answer: str
            ) -> bool:
                """
                Compare les réponses pour les défis de déduction.
                Format attendu: "Emma:Chimie:700,Lucas:Info:600,..." ou format dict-like
                L'ordre des associations n'a pas d'importance, seul le contenu compte.
                Normalise les ordinaux français (1er, 2ème, 3ème...) en chiffres (1, 2, 3...).
                """
                # Mapping ordinaux français → chiffre (frontend affiche "1er", "2ème" etc.)
                _ORDINAL_NORM = {
                    "1er": "1",
                    "1ère": "1",
                    "1e": "1",
                    "1ere": "1",
                    "2ème": "2",
                    "2eme": "2",
                    "2e": "2",
                    "3ème": "3",
                    "3eme": "3",
                    "3e": "3",
                    "4ème": "4",
                    "4eme": "4",
                    "4e": "4",
                    "5ème": "5",
                    "5eme": "5",
                    "5e": "5",
                    "6ème": "6",
                    "6eme": "6",
                    "6e": "6",
                    "7ème": "7",
                    "7eme": "7",
                    "7e": "7",
                    "8ème": "8",
                    "8eme": "8",
                    "8e": "8",
                    "9ème": "9",
                    "9eme": "9",
                    "9e": "9",
                    "10ème": "10",
                    "10eme": "10",
                    "10e": "10",
                }

                def _norm_ordinal(s: str) -> str:
                    """Normalise un ordinal français en chiffre."""
                    t = s.strip().lower()
                    return _ORDINAL_NORM.get(t, t)

                def parse_associations(answer: str) -> set:
                    """Parse les associations en set de tuples normalisés."""
                    answer = str(answer).strip().lower()
                    associations = set()

                    # Format "entité:val1:val2,..."
                    if ":" in answer:
                        for part in answer.split(","):
                            part = part.strip()
                            if part:
                                # Normaliser ordinaux + tri pour ignorer l'ordre
                                raw = [e.strip() for e in part.split(":") if e.strip()]
                                elements = tuple(
                                    sorted([_norm_ordinal(e) for e in raw])
                                )
                                if elements:
                                    associations.add(elements)
                    # Format dict-like ou JSON
                    elif "{" in answer:
                        try:
                            import json

                            data = json.loads(answer.replace("'", '"'))
                            if isinstance(data, dict):
                                for key, values in data.items():
                                    if isinstance(values, dict):
                                        elements = tuple(
                                            sorted(
                                                [str(key).lower()]
                                                + [
                                                    str(v).lower()
                                                    for v in values.values()
                                                ]
                                            )
                                        )
                                    else:
                                        elements = tuple(
                                            sorted(
                                                [str(key).lower(), str(values).lower()]
                                            )
                                        )
                                    associations.add(elements)
                        except (
                            json.JSONDecodeError,
                            ValueError,
                            TypeError,
                            AttributeError,
                        ):
                            pass

                    return associations

                user_assoc = parse_associations(user_answer)
                correct_assoc = parse_associations(correct_answer)

                logger.debug(
                    f"Deduction comparison - User: {user_assoc}, Correct: {correct_assoc}"
                )

                # Comparer les sets
                return user_assoc == correct_assoc

            # Déterminer le type de challenge pour choisir la méthode de comparaison
            challenge_type = (
                str(challenge.challenge_type).lower()
                if challenge.challenge_type
                else ""
            )

            # Comparaison spéciale pour les défis de déduction
            if "deduction" in challenge_type and ":" in user_solution:
                is_correct = compare_deduction_answers(
                    user_solution, challenge.correct_answer
                )
                logger.debug(
                    f"Comparaison déduction - User: {user_solution[:100]}, Correct: {challenge.correct_answer[:100] if challenge.correct_answer else 'None'}, Result: {is_correct}"
                )
            elif "probability" in challenge_type:

                def _parse_probability_value(text: str) -> float | None:
                    """Parse 6/10, 3/5, 0.6, 60% → valeur décimale."""
                    if not text or not isinstance(text, str):
                        return None
                    t = text.strip()
                    if "/" in t:
                        try:
                            a, b = t.split("/", 1)
                            num, den = float(a.strip()), float(b.strip())
                            return num / den if den else None
                        except (ValueError, ZeroDivisionError):
                            return None
                    if "%" in t:
                        try:
                            return float(t.replace("%", "").strip()) / 100
                        except ValueError:
                            return None
                    try:
                        return float(t.replace(",", "."))
                    except ValueError:
                        return None

                u_val = _parse_probability_value(user_solution)
                c_val = _parse_probability_value(challenge.correct_answer or "")
                is_correct = (
                    u_val is not None
                    and c_val is not None
                    and abs(u_val - c_val) < 0.001
                )
                if (
                    not is_correct
                    and user_solution.strip()
                    == (challenge.correct_answer or "").strip()
                ):
                    is_correct = True
                logger.debug(
                    f"Comparaison PROBABILITY - User: {user_solution}, Correct: {challenge.correct_answer}, Parsed: {u_val}/{c_val}, Result: {is_correct}"
                )
            elif "chess" in challenge_type:

                def _normalize_chess_answer(text: str) -> str:
                    """Normalise une réponse échecs pour comparaison tolérante."""
                    if not text or not isinstance(text, str):
                        return ""
                    import re

                    t = text.strip()
                    # Retirer numéros de coups (1. 2. 3. 1) 2) etc.)
                    t = re.sub(r"\d+[.)]\s*", "", t)
                    # Collapser espaces multiples et normaliser
                    t = re.sub(r"\s+", " ", t).strip()
                    # Notation anglaise → française (Q->D, R->T, B->F, N->C, K->R)
                    _en_to_fr = {
                        "Q": "D",
                        "R": "T",
                        "B": "F",
                        "N": "C",
                        "K": "R",
                        "P": "P",
                    }
                    parts = t.split()
                    out = []
                    for p in parts:
                        if len(p) >= 1 and p[0].upper() in _en_to_fr:
                            out.append(_en_to_fr[p[0].upper()] + p[1:])
                        else:
                            out.append(p)
                    t = " ".join(out).upper()
                    # Comparaison sans espaces (tolérance "Dg8+ Txg8 Cf7#" = "Dg8+Txg8Cf7#")
                    return t.replace(" ", "")

                u_norm = _normalize_chess_answer(user_solution)
                correct_raw = challenge.correct_answer or ""
                # Accepter plusieurs solutions (duals) séparées par " | "
                correct_variants = [
                    s.strip() for s in correct_raw.split("|") if s.strip()
                ]
                correct_norms = [_normalize_chess_answer(v) for v in correct_variants]
                is_correct = (
                    u_norm in correct_norms
                    if correct_norms
                    else u_norm == _normalize_chess_answer(correct_raw)
                )
                logger.debug(
                    f"Comparaison CHESS - User norm: {u_norm}, Correct: {correct_norms}, Result: {is_correct}"
                )
            elif "graph" in challenge_type:
                # Liste de nœuds : accepter tout ordre (comparaison par ensemble)
                user_list = parse_answer_to_list(user_solution)
                correct_list = parse_answer_to_list(challenge.correct_answer or "")
                user_set = {u.strip().upper() for u in user_list if u.strip()}
                correct_set = {c.strip().upper() for c in correct_list if c.strip()}
                # Liste de nœuds (set) vs chemin (ordre) : si aucun élément ne contient "-", c'est un set
                is_node_list = len(correct_set) > 1 and not any(
                    "-" in str(c) for c in correct_list
                )
                if is_node_list:
                    is_correct = user_set == correct_set
                else:
                    # Chemin ou valeur unique : comparaison ordonnée
                    is_correct = user_list == correct_list
                logger.debug(
                    f"Comparaison GRAPH - User: {user_set if is_node_list else user_list}, Correct: {correct_set if is_node_list else correct_list}, Result: {is_correct}"
                )
            elif "visual" in challenge_type or "pattern" in challenge_type:
                # PATTERN avec grille : source de vérité = analyse du pattern, pas correct_answer en base
                computed_pattern_answer = None
                if "pattern" in challenge_type:
                    vd = challenge.visual_data
                    if isinstance(vd, dict) and vd.get("grid"):
                        from app.services.challenge_validator import (
                            analyze_pattern,
                            compute_pattern_answers_multi,
                        )

                        grid = vd["grid"]
                        # Plusieurs "?" → format "O, O, X, O" (ordre ligne par ligne)
                        computed_multi = compute_pattern_answers_multi(grid)
                        if computed_multi:
                            computed_pattern_answer = computed_multi
                        else:
                            for i, row in enumerate(grid):
                                if not isinstance(row, (list, tuple)):
                                    continue
                                for j, cell in enumerate(row):
                                    if cell == "?" or (
                                        isinstance(cell, str) and "?" in str(cell)
                                    ):
                                        computed_pattern_answer = analyze_pattern(
                                            grid, i, j
                                        )
                                        break
                                if computed_pattern_answer is not None:
                                    break
                effective_correct = (
                    computed_pattern_answer or challenge.correct_answer or ""
                ).strip()
                if computed_pattern_answer:
                    logger.debug(
                        f"PATTERN: réponse calculée depuis la grille = '{computed_pattern_answer}'"
                    )
                # PATTERN multi-cellules : format "O, O, X, O" (liste de symboles, ordre des "?")
                is_pattern_multi_csv = (
                    "pattern" in challenge_type
                    and effective_correct
                    and "," in effective_correct
                    and "position" not in effective_correct.lower()
                )
                if is_pattern_multi_csv:
                    user_list = parse_answer_to_list(user_solution)
                    correct_list = parse_answer_to_list(effective_correct)
                    user_norm = [_normalize_shape_answer(u) for u in user_list]
                    correct_norm = [_normalize_shape_answer(c) for c in correct_list]
                    is_correct = len(user_norm) == len(correct_norm) and all(
                        u == c for u, c in zip(user_norm, correct_norm)
                    )
                else:
                    # VISUAL/PATTERN : tolérance synonymes, format "Position 6: x, Position 9: y"
                    user_parts = _parse_multi_visual_answer(user_solution)
                    correct_parts = _parse_multi_visual_answer(effective_correct or "")
                    is_multi_position = (
                        len(correct_parts) > 1 and any(p[0] > 0 for p in correct_parts)
                    ) or (len(user_parts) > 1 and any(p[0] > 0 for p in user_parts))
                    if is_multi_position:
                        if len(correct_parts) == 1 and len(user_parts) == 1:
                            is_correct = user_parts[0][1] == correct_parts[0][1]
                        elif len(user_parts) == len(correct_parts):
                            correct_sorted = sorted(correct_parts, key=lambda x: x[0])
                            user_sorted = sorted(user_parts, key=lambda x: x[0])
                            by_position = all(
                                u[1] == c[1]
                                for u, c in zip(user_sorted, correct_sorted)
                            )
                            if not by_position and all(u[0] == 0 for u in user_parts):
                                user_answers = {p[1] for p in user_parts if p[1]}
                                correct_answers = {p[1] for p in correct_parts if p[1]}
                                is_correct = user_answers == correct_answers
                            else:
                                is_correct = by_position
                        else:
                            user_answers = {p[1] for p in user_parts if p[1]}
                            correct_answers = {p[1] for p in correct_parts if p[1]}
                            is_correct = user_answers == correct_answers and len(
                                user_answers
                            ) == len(correct_answers)
                    else:
                        user_list = parse_answer_to_list(user_solution)
                        correct_list = parse_answer_to_list(effective_correct)
                        u = user_list[0] if user_list else ""
                        c = correct_list[0] if correct_list else ""
                        is_correct = _normalize_shape_answer(
                            u
                        ) == _normalize_shape_answer(c)
                logger.debug(f"Comparaison VISUAL/PATTERN - Result: {is_correct}")
            else:
                user_list = parse_answer_to_list(user_solution)
                correct_list = parse_answer_to_list(challenge.correct_answer)
                logger.debug(
                    f"Comparaison réponse - User: {user_list}, Correct: {correct_list}"
                )
                if len(user_list) > 1 or len(correct_list) > 1:
                    is_correct = user_list == correct_list
                else:
                    u = user_list[0] if user_list else ""
                    c = correct_list[0] if correct_list else ""
                    is_correct = u == c

            attempt_data = {
                "user_id": user_id,
                "challenge_id": challenge_id,
                "user_solution": user_solution,
                "is_correct": is_correct,
                "time_spent": time_spent,
                "hints_used": hints_used_count,
            }
            logger.debug(
                f"Tentative d'enregistrement de challenge avec attempt_data: {attempt_data}"
            )
            attempt = LogicChallengeService.record_attempt(db, attempt_data)
            if not attempt:
                return api_error_response(500, "Impossible d'enregistrer la tentative.")
            logger.debug(f"Tentative challenge créée: {attempt.id}")

            # Lot C / B5 : vérifier les badges (défis logiques, mixte) après une tentative correcte
            new_badges = []
            if is_correct:
                try:
                    from app.services.badge_service import BadgeService

                    badge_service = BadgeService(db)
                    new_badges = badge_service.check_and_award_badges(user_id)
                except Exception as badge_err:
                    logger.warning(f"Badge check après défi: {badge_err}")

            # Mettre à jour la série d'entraînement (streak) — toute tentative compte
            try:
                from app.services.streak_service import update_user_streak

                update_user_streak(db, user_id)
            except Exception:
                pass

            # Notification « Tu approches » si pas de nouveau badge mais un proche
            progress_notif = None
            if not new_badges:
                try:
                    from app.services.badge_service import BadgeService

                    svc = BadgeService(db)
                    progress_notif = svc.get_closest_progress_notification(user_id)
                except Exception:
                    pass

            response_data = {
                "is_correct": is_correct,
                "explanation": challenge.solution_explanation if is_correct else None,
                "new_badges": new_badges,
            }
            if progress_notif:
                response_data["progress_notification"] = progress_notif

            if not is_correct:
                # Ne pas révéler la bonne réponse immédiatement, mais la donner dans l'explication après plusieurs tentatives
                hints_list = (
                    challenge.hints if isinstance(challenge.hints, list) else []
                )
                response_data["hints_remaining"] = len(hints_list) - hints_used_count

            return JSONResponse(response_data)
    except ChallengeNotFoundError:
        return api_error_response(404, "Défi logique non trouvé")
    except ValueError:
        return api_error_response(400, "ID de défi invalide")
    except Exception as submission_error:
        logger.error(f"Erreur lors de la soumission de la réponse: {submission_error}")
        import traceback

        logger.debug(traceback.format_exc())
        return api_error_response(500, get_safe_error_message(submission_error))


async def get_challenge_hint(request: Request):
    """
    Récupère un indice pour un défi logique.
    Route: GET /api/challenges/{challenge_id}/hint
    """
    try:
        challenge_id = int(request.path_params.get("challenge_id"))
        level = int(request.query_params.get("level", 1))

        async with db_session() as db:
            challenge = LogicChallengeService.get_challenge_or_raise(db, challenge_id)

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
                return api_error_response(
                    400, f"Indice de niveau {level} non disponible"
                )

            # Retourner l'indice spécifique au niveau demandé (index 0-based)
            hint_text = hints[level - 1] if level <= len(hints) else None
            return JSONResponse(
                {"hint": hint_text}
            )  # Retourner l'indice spécifique au niveau
    except ChallengeNotFoundError:
        return api_error_response(404, "Défi logique non trouvé")
    except ValueError:
        return api_error_response(400, "ID de défi ou niveau invalide")
    except Exception as hint_retrieval_error:
        logger.error(
            f"Erreur lors de la récupération de l'indice: {hint_retrieval_error}"
        )
        traceback.print_exc()
        return api_error_response(500, get_safe_error_message(hint_retrieval_error))


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

        async with db_session() as db:
            completed_ids = challenge_service.get_user_completed_challenges(db, user_id)

        logger.debug(
            f"Récupération de {len(completed_ids)} challenges complétés pour l'utilisateur {user_id}"
        )
        return JSONResponse({"completed_ids": completed_ids})

    except Exception as completed_challenges_error:
        logger.error(
            f"Erreur lors de la récupération des challenges complétés: {completed_challenges_error}"
        )
        logger.debug(traceback.format_exc())
        return ErrorHandler.create_error_response(
            error=completed_challenges_error,
            status_code=500,
            user_message="Erreur lors de la récupération des challenges complétés.",
        )


@require_auth_sse
@require_full_access
async def generate_ai_challenge_stream(request: Request):
    """
    Génère un challenge avec OpenAI en streaming SSE.
    Délègue la logique au service challenge_ai_service.
    """
    try:
        current_user = request.state.user
        challenge_type_raw = request.query_params.get("challenge_type", "sequence")
        age_group_raw = request.query_params.get("age_group", "10-12")
        prompt_raw = request.query_params.get("prompt", "")

        from app.services.challenge_ai_service import (
            generate_challenge_stream as svc_generate_stream,
        )
        from app.utils.prompt_sanitizer import (
            sanitize_user_prompt,
            validate_prompt_safety,
        )
        from app.utils.sse_utils import SSE_HEADERS, sse_error_response

        is_safe, safety_reason = validate_prompt_safety(prompt_raw)
        if not is_safe:
            logger.warning(f"Prompt utilisateur rejeté pour sécurité: {safety_reason}")
            return sse_error_response(f"Prompt invalide: {safety_reason}")

        prompt = sanitize_user_prompt(prompt_raw)

        challenge_type = challenge_type_raw.lower()
        valid_types = [
            "sequence",
            "pattern",
            "visual",
            "puzzle",
            "graph",
            "riddle",
            "deduction",
            "chess",
            "coding",
            "probability",
        ]
        if challenge_type not in valid_types:
            logger.warning(
                f"Type de challenge invalide: {challenge_type_raw}, utilisation de 'sequence' par défaut"
            )
            challenge_type = "sequence"

        normalized_age_group = normalize_age_group(age_group_raw)
        age_group = (
            normalized_age_group
            if normalized_age_group
            else constants.AgeGroups.GROUP_6_8
        )

        user_id = current_user.get("id")
        if user_id:
            from app.utils.rate_limiter import rate_limiter

            allowed, rate_limit_reason = rate_limiter.check_rate_limit(
                user_id=user_id, max_per_hour=10, max_per_day=50
            )
            if not allowed:
                logger.warning(
                    f"Rate limit atteint pour utilisateur {user_id}: {rate_limit_reason}"
                )
                return sse_error_response(
                    f"Limite de génération atteinte: {rate_limit_reason}"
                )

        if not settings.OPENAI_API_KEY:
            return sse_error_response("OpenAI API key non configurée")

        accept_language = request.headers.get("Accept-Language", "fr")
        locale = parse_accept_language(accept_language) or "fr"

        async def generate():
            async for event in svc_generate_stream(
                challenge_type=challenge_type,
                age_group=age_group,
                prompt=prompt,
                user_id=user_id,
                locale=locale,
            ):
                yield event

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers=dict(SSE_HEADERS),
        )

    except Exception as ai_stream_error:
        logger.error(f"Erreur dans generate_ai_challenge_stream: {ai_stream_error}")
        traceback.print_exc()
        return sse_error_response("Erreur lors de la génération")
