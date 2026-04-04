"""
Service admin pour la gestion du contenu (exercices, défis, badges, export CSV).

Extrait de AdminService.
Phase 3, item 3.3a — audit architecture 03/2026.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.user_roles import serialize_user_role
from app.models.achievement import Achievement, UserAchievement
from app.models.attempt import Attempt
from app.models.exercise import Exercise
from app.models.logic_challenge import (
    AgeGroup,
    LogicChallenge,
    LogicChallengeAttempt,
    LogicChallengeType,
)
from app.models.user import User
from app.schemas.admin import AdminContentMutationResult
from app.services.admin.admin_badge_create_flow import (
    persist_badge_create,
    prepare_badge_create_data,
    validate_badge_create_pre_persist,
)
from app.services.admin.admin_helpers import log_admin_action
from app.services.badges.badge_requirement_validation import validate_badge_requirements


class AdminContentService:
    """Opérations CRUD admin pour exercices, défis, badges et export."""

    @staticmethod
    def _coerce_challenge_difficulty_rating_value(raw: Any) -> float:
        """Normalise ``difficulty_rating`` admin (1.0–5.0) ; défaut 3.0 si absent/invalide."""
        if raw is None:
            return 3.0
        try:
            v = float(raw)
        except (TypeError, ValueError):
            return 3.0
        if v < 1.0 or v > 5.0:
            return 3.0
        return v

    # ── Badges ────────────────────────────────────────────────────────────

    @staticmethod
    def _achievement_to_detail(a: Achievement) -> Dict[str, Any]:
        return {
            "id": a.id,
            "code": a.code or "",
            "name": a.name or "",
            "description": a.description or "",
            "icon_url": a.icon_url or "",
            "category": a.category or "",
            "difficulty": a.difficulty or "",
            "points_reward": a.points_reward or 0,
            "is_secret": a.is_secret or False,
            "requirements": a.requirements,
            "star_wars_title": a.star_wars_title or "",
            "is_active": a.is_active if a.is_active is not None else True,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }

    @staticmethod
    def _validate_badge_requirements(req: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Délègue à badge_requirement_validation (cluster E4)."""
        return validate_badge_requirements(req)

    @staticmethod
    def list_badges_for_admin(db: Session) -> Dict[str, Any]:
        badges = (
            db.query(Achievement).order_by(Achievement.category, Achievement.code).all()
        )
        counts = (
            db.query(UserAchievement.achievement_id, func.count(UserAchievement.id))
            .group_by(UserAchievement.achievement_id)
            .all()
        )
        count_map = {aid: c for aid, c in counts}
        items = []
        for a in badges:
            d = AdminContentService._achievement_to_detail(a)
            d["_user_count"] = count_map.get(a.id, 0)
            items.append(d)
        return {"success": True, "data": items}

    @staticmethod
    def create_badge_for_admin(
        db: Session,
        *,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> AdminContentMutationResult:
        """Création badge admin — flux F3 : préparation, validation, persistance, mapping."""
        prepared = prepare_badge_create_data(data)
        err, status = validate_badge_create_pre_persist(prepared, db)
        if err:
            return AdminContentMutationResult(
                data=None, error_message=err, status_code=status
            )
        a = persist_badge_create(db, prepared, admin_user_id)
        return AdminContentMutationResult(
            data=AdminContentService._achievement_to_detail(a),
            error_message=None,
            status_code=201,
        )

    @staticmethod
    def get_badge_for_admin(
        db: Session, badge_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        a = db.query(Achievement).filter(Achievement.id == badge_id).first()
        if not a:
            return None, "Badge non trouvé.", 404
        d = AdminContentService._achievement_to_detail(a)
        user_count = (
            db.query(func.count(UserAchievement.id))
            .filter(UserAchievement.achievement_id == badge_id)
            .scalar()
            or 0
        )
        d["_user_count"] = user_count
        return d, None, 200

    @staticmethod
    def put_badge_for_admin(
        db: Session,
        *,
        badge_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> AdminContentMutationResult:
        a = db.query(Achievement).filter(Achievement.id == badge_id).first()
        if not a:
            return AdminContentMutationResult(
                data=None, error_message="Badge non trouvé.", status_code=404
            )
        if "requirements" in data:
            ok, err = AdminContentService._validate_badge_requirements(
                data.get("requirements")
            )
            if not ok:
                return AdminContentMutationResult(
                    data=None,
                    error_message=err or "Requirements invalides.",
                    status_code=400,
                )
        str_fields = (
            "name",
            "description",
            "icon_url",
            "category",
            "difficulty",
            "star_wars_title",
        )
        for k, v in data.items():
            if k == "code":
                continue
            if k == "points_reward":
                a.points_reward = int(v) if v is not None else 0
            elif k in ("is_secret", "is_active"):
                setattr(a, k, v in (True, "true", "1", 1))
            elif k == "requirements":
                a.requirements = v
            elif k in str_fields and v is not None:
                setattr(a, k, (v or "").strip() or None)
        log_admin_action(
            db,
            admin_user_id,
            "badge_update",
            "achievement",
            badge_id,
            {"fields": list(data.keys())},
        )
        db.commit()
        db.refresh(a)
        return AdminContentMutationResult(
            data=AdminContentService._achievement_to_detail(a),
            error_message=None,
            status_code=200,
        )

    @staticmethod
    def delete_badge_for_admin(
        db: Session,
        *,
        badge_id: int,
        admin_user_id: Optional[int] = None,
    ) -> AdminContentMutationResult:
        a = db.query(Achievement).filter(Achievement.id == badge_id).first()
        if not a:
            return AdminContentMutationResult(
                data=None, error_message="Badge non trouvé.", status_code=404
            )
        user_count = (
            db.query(func.count(UserAchievement.id))
            .filter(UserAchievement.achievement_id == badge_id)
            .scalar()
            or 0
        )
        a.is_active = False
        log_admin_action(
            db,
            admin_user_id,
            "badge_delete",
            "achievement",
            badge_id,
            {"soft": True, "user_count": user_count},
        )
        db.commit()
        db.refresh(a)
        return AdminContentMutationResult(
            data={
                "success": True,
                "id": a.id,
                "code": a.code,
                "name": a.name,
                "is_active": False,
                "message": "Badge désactivé (soft delete).",
            },
            error_message=None,
            status_code=200,
        )

    # ── Exercises ─────────────────────────────────────────────────────────

    @staticmethod
    def _exercise_to_detail(e: Exercise) -> Dict[str, Any]:
        return {
            "id": e.id,
            "title": e.title,
            "exercise_type": e.exercise_type or "",
            "difficulty": e.difficulty or "",
            "age_group": e.age_group or "",
            "tags": e.tags or "",
            "context_theme": e.context_theme or "",
            "complexity": e.complexity,
            "ai_generated": e.ai_generated or False,
            "question": e.question or "",
            "correct_answer": e.correct_answer or "",
            "choices": e.choices,
            "explanation": e.explanation or "",
            "hint": e.hint or "",
            "image_url": e.image_url or "",
            "audio_url": e.audio_url or "",
            "is_active": e.is_active,
            "is_archived": e.is_archived,
            "difficulty_tier": e.difficulty_tier,
            "created_at": e.created_at.isoformat() if e.created_at else None,
            "updated_at": e.updated_at.isoformat() if e.updated_at else None,
        }

    @staticmethod
    def list_exercises_for_admin(
        db: Session,
        *,
        archived: Optional[bool] = None,
        exercise_type: Optional[str] = None,
        search: str = "",
        sort: str = "created_at",
        order: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        sortable = {"title", "exercise_type", "difficulty", "age_group", "created_at"}
        if sort not in sortable:
            sort = "created_at"
        order_fn = "asc" if order == "asc" else "desc"
        sort_col = getattr(Exercise, sort, Exercise.created_at)
        order_by = getattr(sort_col, order_fn)()

        q = db.query(Exercise)
        if archived is not None:
            q = q.filter(Exercise.is_archived == archived)
        if exercise_type:
            q = q.filter(Exercise.exercise_type == exercise_type)
        if search:
            q = q.filter(Exercise.title.ilike(f"%{search}%"))
        total = q.count()
        exercises = q.order_by(order_by).offset(skip).limit(limit).all()
        ex_ids = [e.id for e in exercises]

        attempt_stats: Dict[int, Dict[str, int]] = {}
        if ex_ids:
            rows = (
                db.query(
                    Attempt.exercise_id,
                    func.count(Attempt.id).label("attempt_count"),
                    func.sum(case((Attempt.is_correct == True, 1), else_=0)).label(
                        "correct_count"
                    ),
                )
                .filter(Attempt.exercise_id.in_(ex_ids))
                .group_by(Attempt.exercise_id)
                .all()
            )
            for ex_id, a_count, c_count in rows:
                attempt_stats[ex_id] = {
                    "attempt_count": a_count or 0,
                    "correct_count": c_count or 0,
                }

        items = []
        for e in exercises:
            stats = attempt_stats.get(e.id, {"attempt_count": 0, "correct_count": 0})
            a_count = stats["attempt_count"]
            c_count = stats["correct_count"]
            success_rate = round((c_count / a_count * 100), 1) if a_count > 0 else 0.0
            items.append(
                {
                    "id": e.id,
                    "title": e.title,
                    "exercise_type": e.exercise_type,
                    "difficulty": e.difficulty,
                    "age_group": e.age_group,
                    "difficulty_tier": e.difficulty_tier,
                    "is_archived": e.is_archived,
                    "attempt_count": a_count,
                    "success_rate": success_rate,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
            )
        return {"items": items, "total": total}

    @staticmethod
    def create_exercise_for_admin(
        db: Session,
        *,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """Orchestration : prepare / validate / persist (G3, calqué sur F3)."""
        from app.services.admin.admin_exercise_create_flow import (
            persist_exercise_create,
            prepare_exercise_create_data,
            validate_exercise_create_pre_persist,
        )

        prepared = prepare_exercise_create_data(data)
        err, status = validate_exercise_create_pre_persist(prepared, db)
        if err:
            return None, err, status
        ex = persist_exercise_create(db, prepared, admin_user_id)
        return AdminContentService._exercise_to_detail(ex), None, 201

    @staticmethod
    def get_exercise_for_admin(
        db: Session, exercise_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return None, "Exercice non trouvé.", 404
        return AdminContentService._exercise_to_detail(ex), None, 200

    @staticmethod
    def put_exercise_for_admin(
        db: Session,
        *,
        exercise_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return None, "Exercice non trouvé.", 404
        allowed_str = {
            "title",
            "exercise_type",
            "difficulty",
            "age_group",
            "tags",
            "context_theme",
            "complexity",
            "question",
            "correct_answer",
            "explanation",
            "hint",
            "image_url",
            "audio_url",
        }
        allowed_bool = {"is_active", "is_archived"}
        allowed_json = {"choices"}
        for k, v in data.items():
            if k in allowed_str and v is not None:
                setattr(ex, k, str(v) if not isinstance(v, str) else v)
            elif k in allowed_bool and v is not None:
                setattr(ex, k, v in (True, "true", "1", 1))
            elif k in allowed_json:
                setattr(ex, k, v)
        if any(k in data for k in ("difficulty", "age_group")):
            from app.core.difficulty_tier import assign_exercise_difficulty_tier

            assign_exercise_difficulty_tier(ex)
        log_admin_action(
            db,
            admin_user_id,
            "exercise_update",
            "exercise",
            exercise_id,
            {"fields": list(data.keys())},
        )
        db.commit()
        db.refresh(ex)
        return AdminContentService._exercise_to_detail(ex), None, 200

    @staticmethod
    def duplicate_exercise_for_admin(
        db: Session,
        *,
        exercise_id: int,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        orig = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not orig:
            return None, "Exercice non trouvé.", 404
        copy = Exercise(
            title=f"{orig.title} (copie)",
            exercise_type=orig.exercise_type,
            difficulty=orig.difficulty,
            age_group=orig.age_group,
            tags=orig.tags,
            context_theme=orig.context_theme,
            complexity=orig.complexity,
            ai_generated=orig.ai_generated,
            question=orig.question,
            correct_answer=orig.correct_answer,
            choices=orig.choices,
            explanation=orig.explanation,
            hint=orig.hint,
            image_url=orig.image_url,
            audio_url=orig.audio_url,
            is_active=orig.is_active,
            is_archived=False,
        )
        from app.core.difficulty_tier import assign_exercise_difficulty_tier

        assign_exercise_difficulty_tier(copy)
        db.add(copy)
        db.flush()
        log_admin_action(
            db,
            admin_user_id,
            "exercise_duplicate",
            "exercise",
            copy.id,
            {"from_id": exercise_id, "title": copy.title},
        )
        db.commit()
        db.refresh(copy)
        return AdminContentService._exercise_to_detail(copy), None, 201

    @staticmethod
    def patch_exercise_for_admin(
        db: Session,
        *,
        exercise_id: int,
        is_archived: bool,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not ex:
            return None, "Exercice non trouvé.", 404
        ex.is_archived = is_archived
        log_admin_action(
            db,
            admin_user_id,
            "exercise_archive",
            "exercise",
            exercise_id,
            {"is_archived": is_archived},
        )
        db.commit()
        db.refresh(ex)
        return (
            {"id": ex.id, "title": ex.title, "is_archived": ex.is_archived},
            None,
            200,
        )

    # ── Challenges ────────────────────────────────────────────────────────

    @staticmethod
    def _challenge_to_detail(c: LogicChallenge) -> Dict[str, Any]:
        ct_val = (
            c.challenge_type.value
            if hasattr(c.challenge_type, "value")
            else str(c.challenge_type)
        )
        ag_val = (
            c.age_group.value if hasattr(c.age_group, "value") else str(c.age_group)
        )
        return {
            "id": c.id,
            "title": c.title,
            "description": c.description or "",
            "challenge_type": ct_val,
            "age_group": ag_val,
            "difficulty": c.difficulty or "",
            "content": c.content or "",
            "question": c.question or "",
            "solution": c.solution or "",
            "correct_answer": c.correct_answer or "",
            "choices": c.choices,
            "solution_explanation": c.solution_explanation or "",
            "visual_data": c.visual_data,
            "hints": c.hints,
            "image_url": c.image_url or "",
            "tags": c.tags or "",
            "is_active": c.is_active,
            "is_archived": c.is_archived,
            "difficulty_rating": c.difficulty_rating,
            "estimated_time_minutes": c.estimated_time_minutes,
            "difficulty_tier": c.difficulty_tier,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }

    @staticmethod
    def list_challenges_for_admin(
        db: Session,
        *,
        archived: Optional[bool] = None,
        challenge_type: Optional[str] = None,
        search: str = "",
        sort: str = "created_at",
        order: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        from sqlalchemy import or_

        sortable = {"title", "challenge_type", "age_group", "created_at"}
        if sort not in sortable:
            sort = "created_at"
        order_fn = "asc" if order == "asc" else "desc"
        sort_col = getattr(LogicChallenge, sort, LogicChallenge.created_at)
        order_by = getattr(sort_col, order_fn)()

        q = db.query(LogicChallenge)
        if archived is not None:
            q = q.filter(LogicChallenge.is_archived == archived)
        if challenge_type:
            try:
                ct = LogicChallengeType(challenge_type)
                q = q.filter(LogicChallenge.challenge_type == ct)
            except ValueError:
                pass
        if search:
            pattern = f"%{search}%"
            q = q.filter(
                or_(
                    LogicChallenge.title.ilike(pattern),
                    LogicChallenge.description.ilike(pattern),
                )
            )
        total = q.count()
        challenges = q.order_by(order_by).offset(skip).limit(limit).all()
        ch_ids = [c.id for c in challenges]

        attempt_stats: Dict[int, Dict[str, int]] = {}
        if ch_ids:
            rows = (
                db.query(
                    LogicChallengeAttempt.challenge_id,
                    func.count(LogicChallengeAttempt.id).label("attempt_count"),
                    func.sum(
                        case((LogicChallengeAttempt.is_correct == True, 1), else_=0)
                    ).label("correct_count"),
                )
                .filter(LogicChallengeAttempt.challenge_id.in_(ch_ids))
                .group_by(LogicChallengeAttempt.challenge_id)
                .all()
            )
            for ch_id, a_count, c_count in rows:
                attempt_stats[ch_id] = {
                    "attempt_count": a_count or 0,
                    "correct_count": c_count or 0,
                }

        items = []
        for c in challenges:
            stats = attempt_stats.get(c.id, {"attempt_count": 0, "correct_count": 0})
            a_count = stats["attempt_count"]
            c_count = stats["correct_count"]
            success_rate = round((c_count / a_count * 100), 1) if a_count > 0 else 0.0
            ct_val = (
                c.challenge_type.value
                if hasattr(c.challenge_type, "value")
                else str(c.challenge_type)
            )
            ag_val = (
                c.age_group.value if hasattr(c.age_group, "value") else str(c.age_group)
            )
            items.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "challenge_type": ct_val,
                    "age_group": ag_val,
                    "difficulty_rating": c.difficulty_rating,
                    "difficulty_tier": c.difficulty_tier,
                    "is_archived": c.is_archived,
                    "attempt_count": a_count,
                    "success_rate": success_rate,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
            )
        return {"items": items, "total": total}

    @staticmethod
    def create_challenge_for_admin(
        db: Session,
        *,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        title = (data.get("title") or "").strip()
        description = (data.get("description") or "").strip()
        challenge_type_raw = (data.get("challenge_type") or "puzzle").strip().lower()
        age_group_raw = (data.get("age_group") or "GROUP_10_12").strip()

        if not title:
            return None, "Le titre est obligatoire.", 400
        if not description:
            return None, "La description est obligatoire.", 400

        try:
            ct = LogicChallengeType(challenge_type_raw)
        except ValueError:
            ct = LogicChallengeType.PUZZLE
        try:
            ag = AgeGroup(age_group_raw)
        except ValueError:
            ag = AgeGroup.GROUP_10_12

        difficulty_rating = (
            AdminContentService._coerce_challenge_difficulty_rating_value(
                data.get("difficulty_rating")
            )
        )

        ch = LogicChallenge(
            title=title,
            description=description,
            challenge_type=ct,
            age_group=ag,
            question=(data.get("question") or "").strip() or None,
            content=(data.get("content") or "").strip() or None,
            solution=(data.get("solution") or "").strip() or None,
            correct_answer=(data.get("correct_answer") or "").strip() or None,
            solution_explanation=(data.get("solution_explanation") or "").strip()
            or None,
            visual_data=data.get("visual_data"),
            hints=data.get("hints"),
            difficulty_rating=difficulty_rating,
        )
        from app.core.difficulty_tier import assign_logic_challenge_difficulty_tier

        assign_logic_challenge_difficulty_tier(ch)
        db.add(ch)
        db.flush()
        log_admin_action(
            db,
            admin_user_id,
            "challenge_create",
            "challenge",
            ch.id,
            {"title": ch.title},
        )
        db.commit()
        db.refresh(ch)
        return AdminContentService._challenge_to_detail(ch), None, 201

    @staticmethod
    def get_challenge_for_admin(
        db: Session, challenge_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return None, "Défi non trouvé.", 404
        return AdminContentService._challenge_to_detail(ch), None, 200

    @staticmethod
    def put_challenge_for_admin(
        db: Session,
        *,
        challenge_id: int,
        data: Dict[str, Any],
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return None, "Défi non trouvé.", 404
        allowed_str = {
            "title",
            "description",
            "difficulty",
            "content",
            "question",
            "solution",
            "correct_answer",
            "solution_explanation",
            "image_url",
            "tags",
        }
        allowed_bool = {"is_active", "is_archived"}
        allowed_int = {"estimated_time_minutes"}
        allowed_json = {"choices", "visual_data", "hints"}
        for k, v in data.items():
            if k in allowed_str and v is not None:
                setattr(ch, k, str(v) if not isinstance(v, str) else v)
            elif k in allowed_bool and v is not None:
                setattr(ch, k, v in (True, "true", "1", 1))
            elif k == "difficulty_rating" and v is not None:
                setattr(
                    ch,
                    "difficulty_rating",
                    AdminContentService._coerce_challenge_difficulty_rating_value(v),
                )
            elif k in allowed_int and v is not None:
                setattr(ch, k, int(v) if isinstance(v, (int, float)) else v)
            elif k in allowed_json:
                setattr(ch, k, v)
            elif k == "challenge_type" and v is not None:
                try:
                    setattr(ch, k, LogicChallengeType(str(v).lower()))
                except ValueError:
                    pass
            elif k == "age_group" and v is not None:
                try:
                    setattr(ch, k, AgeGroup(str(v).strip()))
                except ValueError:
                    pass
        if any(k in data for k in ("difficulty", "age_group", "difficulty_rating")):
            from app.core.difficulty_tier import assign_logic_challenge_difficulty_tier

            assign_logic_challenge_difficulty_tier(ch)
        log_admin_action(
            db,
            admin_user_id,
            "challenge_update",
            "challenge",
            challenge_id,
            {"fields": list(data.keys())},
        )
        db.commit()
        db.refresh(ch)
        return AdminContentService._challenge_to_detail(ch), None, 200

    @staticmethod
    def duplicate_challenge_for_admin(
        db: Session,
        *,
        challenge_id: int,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        orig = (
            db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        )
        if not orig:
            return None, "Défi non trouvé.", 404
        copy = LogicChallenge(
            title=f"{orig.title} (copie)",
            description=orig.description,
            challenge_type=orig.challenge_type,
            age_group=orig.age_group,
            difficulty=orig.difficulty,
            content=orig.content,
            question=orig.question,
            solution=orig.solution,
            correct_answer=orig.correct_answer,
            choices=orig.choices,
            solution_explanation=orig.solution_explanation,
            visual_data=orig.visual_data,
            hints=orig.hints,
            image_url=orig.image_url,
            tags=orig.tags,
            is_active=orig.is_active,
            is_archived=False,
            difficulty_rating=orig.difficulty_rating,
            estimated_time_minutes=orig.estimated_time_minutes,
        )
        from app.core.difficulty_tier import assign_logic_challenge_difficulty_tier

        assign_logic_challenge_difficulty_tier(copy)
        db.add(copy)
        db.flush()
        log_admin_action(
            db,
            admin_user_id,
            "challenge_duplicate",
            "challenge",
            copy.id,
            {"from_id": challenge_id, "title": copy.title},
        )
        db.commit()
        db.refresh(copy)
        return AdminContentService._challenge_to_detail(copy), None, 201

    @staticmethod
    def patch_challenge_for_admin(
        db: Session,
        *,
        challenge_id: int,
        is_archived: bool,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        ch = db.query(LogicChallenge).filter(LogicChallenge.id == challenge_id).first()
        if not ch:
            return None, "Défi non trouvé.", 404
        ch.is_archived = is_archived
        log_admin_action(
            db,
            admin_user_id,
            "challenge_archive",
            "challenge",
            challenge_id,
            {"is_archived": is_archived},
        )
        db.commit()
        db.refresh(ch)
        return (
            {"id": ch.id, "title": ch.title, "is_archived": ch.is_archived},
            None,
            200,
        )

    # ── Export CSV ─────────────────────────────────────────────────────────

    @staticmethod
    def export_csv_data_for_admin(
        db: Session,
        *,
        export_type: str,
        period: str,
        admin_user_id: Optional[int] = None,
    ) -> Tuple[List[str], List[List[Any]]]:
        since = None
        if period == "7d":
            since = datetime.now(timezone.utc) - timedelta(days=7)
        elif period == "30d":
            since = datetime.now(timezone.utc) - timedelta(days=30)

        MAX_ROWS = 10_000
        log_admin_action(
            db,
            admin_user_id,
            "export_csv",
            None,
            None,
            {"type": export_type, "period": period},
        )
        db.commit()

        if export_type == "users":
            q = db.query(User)
            if since:
                q = q.filter(User.created_at >= since)
            rows = q.order_by(User.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    u.id,
                    u.username or "",
                    u.email or "",
                    u.full_name or "",
                    serialize_user_role(getattr(u, "role", None)) or "",
                    u.is_active,
                    u.created_at.isoformat() if u.created_at else "",
                ]
                for u in rows
            ]
            headers = [
                "id",
                "username",
                "email",
                "full_name",
                "role",
                "is_active",
                "created_at",
            ]
        elif export_type == "exercises":
            q = db.query(Exercise)
            if since:
                q = q.filter(Exercise.created_at >= since)
            rows = q.order_by(Exercise.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    e.id,
                    (e.title or "").replace("\n", " "),
                    e.exercise_type or "",
                    e.difficulty or "",
                    e.age_group or "",
                    e.is_archived,
                    e.created_at.isoformat() if e.created_at else "",
                ]
                for e in rows
            ]
            headers = [
                "id",
                "title",
                "exercise_type",
                "difficulty",
                "age_group",
                "is_archived",
                "created_at",
            ]
        elif export_type == "attempts":
            q = db.query(Attempt)
            if since:
                q = q.filter(Attempt.created_at >= since)
            rows = q.order_by(Attempt.created_at.desc()).limit(MAX_ROWS).all()
            rows_data = [
                [
                    a.id,
                    a.user_id,
                    a.exercise_id,
                    a.is_correct,
                    a.time_spent or "",
                    a.created_at.isoformat() if a.created_at else "",
                ]
                for a in rows
            ]
            headers = [
                "id",
                "user_id",
                "exercise_id",
                "is_correct",
                "time_spent",
                "created_at",
            ]
        else:
            total_users = db.query(func.count(User.id)).scalar() or 0
            total_exercises = db.query(func.count(Exercise.id)).scalar() or 0
            total_challenges = db.query(func.count(LogicChallenge.id)).scalar() or 0
            total_attempts = db.query(func.count(Attempt.id)).scalar() or 0
            headers = ["metric", "value", "period"]
            rows_data = [
                ["total_users", total_users, period],
                ["total_exercises", total_exercises, period],
                ["total_challenges", total_challenges, period],
                ["total_attempts", total_attempts, period],
            ]
        return headers, rows_data
