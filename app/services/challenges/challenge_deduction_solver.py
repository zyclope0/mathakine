"""Conservative uniqueness checks for small DEDUCTION logic grids.

The solver intentionally supports only machine-checkable constraints. If a clue
cannot be parsed safely, callers should fail open and keep the existing
structural validation behavior.

Structured ``entity_value`` / ``entity_not_value`` are interpreted as
same-(first-category) row: the left and right label refs may be the primary
entity category or any secondary category, with pairwise "same person" / negation
semantics.
"""

from __future__ import annotations

import itertools
import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

MAX_DEDUCTION_SOLVER_COMBINATIONS = 50_000
UNIQUE_SOLUTION_TARGET = 1

CONSTRAINT_ENTITY_VALUE = "entity_value"
CONSTRAINT_ENTITY_NOT_VALUE = "entity_not_value"
CONSTRAINT_SAME_ROW = "same_row"
CONSTRAINT_ENTITY_BEFORE_ENTITY = "entity_before_entity"
CONSTRAINT_ENTITY_AFTER_ENTITY = "entity_after_entity"
CONSTRAINT_ENTITY_IMMEDIATELY_BEFORE_ENTITY = "entity_immediately_before_entity"
CONSTRAINT_VALUE_BEFORE_VALUE = "value_before_value"
CONSTRAINT_ENTITY_NOT_ADJACENT_VALUE = "entity_not_adjacent_value"

_NEGATIVE_CLUE_RE = re.compile(
    r"(?:\bne\b|\bn['’][a-z]+)\b.*\bpas\b|\b(?:jamais|aucun|aucune)\b"
)

WEEKDAY_ORDER = (
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
)


@dataclass(frozen=True)
class DeductionUniquenessResult:
    checked: bool
    solution_count: int
    reason: str
    expected_answer_matches: Optional[bool] = None


@dataclass(frozen=True)
class _Mention:
    category: str
    value: str
    start: int


@dataclass(frozen=True)
class _LabelRef:
    category: str
    value: str


@dataclass(frozen=True)
class _Constraint:
    kind: str
    left: _LabelRef
    right: Optional[_LabelRef] = None


@dataclass(frozen=True)
class _DeductionModel:
    category_order: Tuple[str, ...]
    values_by_category: Dict[str, Tuple[str, ...]]
    first_category: str
    first_values: Tuple[str, ...]
    secondary_categories: Tuple[str, ...]
    day_category: Optional[str]
    day_rank: Dict[str, int]


def _norm(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", " ", without_accents.lower()).strip()


def _is_day_category(category: str, values: Sequence[str]) -> bool:
    category_key = _norm(category)
    if "jour" in category_key or "day" in category_key:
        return True
    normalized_values = {_norm(v) for v in values}
    return len(normalized_values.intersection(WEEKDAY_ORDER)) >= 2


def _build_model(visual_data: Dict[str, Any]) -> Optional[_DeductionModel]:
    entities = visual_data.get("entities")
    if not isinstance(entities, dict) or len(entities) < 2:
        return None

    category_order = tuple(str(category) for category in entities.keys())
    values_by_category: Dict[str, Tuple[str, ...]] = {}
    for category in category_order:
        raw_values = entities.get(category)
        if not isinstance(raw_values, list) or not raw_values:
            return None
        values = tuple(str(value).strip() for value in raw_values if str(value).strip())
        if len(values) != len(raw_values):
            return None
        if len({_norm(value) for value in values}) != len(values):
            return None
        values_by_category[category] = values

    first_category = category_order[0]
    first_values = values_by_category[first_category]
    secondary_categories = category_order[1:]
    expected_size = len(first_values)
    if expected_size < 2:
        return None
    if any(
        len(values_by_category[category]) != expected_size
        for category in category_order
    ):
        return None

    day_category = next(
        (
            category
            for category in secondary_categories
            if _is_day_category(category, values_by_category[category])
        ),
        None,
    )
    day_rank: Dict[str, int] = {}
    if day_category is not None:
        raw_days = values_by_category[day_category]
        # The generated grid defines the pedagogical order. This matters for
        # partial schedules such as Lundi -> Mardi -> Jeudi -> Vendredi, where
        # "immediately after Mardi" means Jeudi in the presented list.
        day_rank = {day: idx for idx, day in enumerate(raw_days)}

    return _DeductionModel(
        category_order=category_order,
        values_by_category=values_by_category,
        first_category=first_category,
        first_values=first_values,
        secondary_categories=secondary_categories,
        day_category=day_category,
        day_rank=day_rank,
    )


def _mentions_for_text(text: str, model: _DeductionModel) -> List[_Mention]:
    normalized_text = _norm(text)
    mentions: List[_Mention] = []
    for category in model.category_order:
        for value in model.values_by_category[category]:
            label = _norm(value)
            if not label:
                continue
            pattern = re.compile(rf"(?<!\w){re.escape(label)}(?!\w)")
            for match in pattern.finditer(normalized_text):
                mentions.append(
                    _Mention(category=category, value=value, start=match.start())
                )
    return sorted(mentions, key=lambda mention: mention.start)


def _mentions_by_category(
    mentions: Iterable[_Mention], category: str
) -> List[_Mention]:
    return [mention for mention in mentions if mention.category == category]


def _secondary_mentions(
    mentions: Iterable[_Mention], model: _DeductionModel
) -> List[_Mention]:
    return [mention for mention in mentions if mention.category != model.first_category]


def _contains_any(text: str, needles: Sequence[str]) -> bool:
    normalized = _norm(text)
    return any(needle in normalized for needle in needles)


def _is_negative_clue(normalized_text: str) -> bool:
    return bool(_NEGATIVE_CLUE_RE.search(normalized_text))


def _parse_natural_clue(text: str, model: _DeductionModel) -> Optional[_Constraint]:
    normalized = _norm(text)
    mentions = _mentions_for_text(text, model)
    first_mentions = _mentions_by_category(mentions, model.first_category)
    secondary_mentions = _secondary_mentions(mentions, model)

    if model.day_category:
        day_mentions = _mentions_by_category(mentions, model.day_category)
        non_day_secondary = [
            mention
            for mention in secondary_mentions
            if mention.category != model.day_category
        ]
    else:
        day_mentions = []
        non_day_secondary = secondary_mentions

    if len(first_mentions) == 2 and "avant" in normalized:
        first, second = first_mentions[0], first_mentions[1]
        if _contains_any(normalized, ("exactement", "creneau", "immediat")):
            return _Constraint(
                CONSTRAINT_ENTITY_IMMEDIATELY_BEFORE_ENTITY,
                _LabelRef(first.category, first.value),
                _LabelRef(second.category, second.value),
            )
        return _Constraint(
            CONSTRAINT_ENTITY_BEFORE_ENTITY,
            _LabelRef(first.category, first.value),
            _LabelRef(second.category, second.value),
        )

    if len(first_mentions) == 2 and "apres" in normalized:
        first, second = first_mentions[0], first_mentions[1]
        return _Constraint(
            CONSTRAINT_ENTITY_AFTER_ENTITY,
            _LabelRef(first.category, first.value),
            _LabelRef(second.category, second.value),
        )

    if (
        len(first_mentions) == 1
        and len(non_day_secondary) == 1
        and _contains_any(normalized, ("immediatement avant", "immediatement apres"))
        and "avant" in normalized
        and "apres" in normalized
    ):
        entity = first_mentions[0]
        value = non_day_secondary[0]
        return _Constraint(
            CONSTRAINT_ENTITY_NOT_ADJACENT_VALUE,
            _LabelRef(entity.category, entity.value),
            _LabelRef(value.category, value.value),
        )

    if len(first_mentions) == 1 and len(non_day_secondary) == 1:
        entity = first_mentions[0]
        value = non_day_secondary[0]
        if _is_negative_clue(normalized) or _contains_any(normalized, ("pas sur",)):
            return _Constraint(
                CONSTRAINT_ENTITY_NOT_VALUE,
                _LabelRef(entity.category, entity.value),
                _LabelRef(value.category, value.value),
            )
        if _contains_any(normalized, ("meme jour", "même jour")):
            return _Constraint(
                CONSTRAINT_ENTITY_VALUE,
                _LabelRef(entity.category, entity.value),
                _LabelRef(value.category, value.value),
            )

    if len(non_day_secondary) == 2 and "avant" in normalized:
        first, second = non_day_secondary[0], non_day_secondary[1]
        if first.category == second.category:
            return _Constraint(
                CONSTRAINT_VALUE_BEFORE_VALUE,
                _LabelRef(first.category, first.value),
                _LabelRef(second.category, second.value),
            )

    if len(non_day_secondary) == 1 and len(day_mentions) == 1:
        value = non_day_secondary[0]
        day = day_mentions[0]
        if _contains_any(normalized, ("programme", "programmé", "a lieu")):
            return _Constraint(
                CONSTRAINT_SAME_ROW,
                _LabelRef(value.category, value.value),
                _LabelRef(day.category, day.value),
            )

    return None


def _label_ref_from_structured(raw: Any, model: _DeductionModel) -> Optional[_LabelRef]:
    if not isinstance(raw, dict):
        return None
    category_key = _norm(raw.get("category"))
    value_key = _norm(raw.get("value"))
    for category in model.category_order:
        if _norm(category) != category_key:
            continue
        for value in model.values_by_category[category]:
            if _norm(value) == value_key:
                return _LabelRef(category, value)
    return None


def _parse_structured_constraints(
    raw_constraints: Any, model: _DeductionModel
) -> Optional[List[_Constraint]]:
    if not isinstance(raw_constraints, list) or not raw_constraints:
        return None
    constraints: List[_Constraint] = []
    for raw in raw_constraints:
        if not isinstance(raw, dict):
            return None
        kind = str(raw.get("type", "")).strip()
        left = _label_ref_from_structured(raw.get("left"), model)
        right = _label_ref_from_structured(raw.get("right"), model)
        if kind in {
            CONSTRAINT_ENTITY_VALUE,
            CONSTRAINT_ENTITY_NOT_VALUE,
            CONSTRAINT_SAME_ROW,
            CONSTRAINT_ENTITY_BEFORE_ENTITY,
            CONSTRAINT_ENTITY_AFTER_ENTITY,
            CONSTRAINT_ENTITY_IMMEDIATELY_BEFORE_ENTITY,
            CONSTRAINT_VALUE_BEFORE_VALUE,
            CONSTRAINT_ENTITY_NOT_ADJACENT_VALUE,
        }:
            if left is None or right is None:
                return None
            constraints.append(_Constraint(kind, left, right))
            continue
        return None
    return constraints


def _parse_constraints(
    visual_data: Dict[str, Any], model: _DeductionModel
) -> Tuple[Optional[List[_Constraint]], str]:
    structured = _parse_structured_constraints(visual_data.get("constraints"), model)
    if structured is not None:
        return structured, "structured"

    raw_clues = visual_data.get("clues", [])
    if not isinstance(raw_clues, list) or not raw_clues:
        return None, "no_clues"

    constraints: List[_Constraint] = []
    for raw_clue in raw_clues:
        parsed = _parse_natural_clue(str(raw_clue), model)
        if parsed is None:
            return None, "unparsed_natural_clue"
        constraints.append(parsed)
    return constraints, "natural"


def _row_has_ref(
    assignment: Dict[str, Dict[str, str]],
    model: _DeductionModel,
    entity: str,
    ref: _LabelRef,
) -> bool:
    if ref.category == model.first_category:
        return entity == ref.value
    return assignment[entity].get(ref.category) == ref.value


def _refs_co_same_row(
    assignment: Dict[str, Dict[str, str]],
    model: _DeductionModel,
    left: _LabelRef,
    right: _LabelRef,
) -> bool:
    """True if left and right refer to the same first-category row (Zebra / logic grid)."""
    if left.category == model.first_category and right.category == model.first_category:
        return left.value == right.value
    if left.category == model.first_category:
        return _row_has_ref(assignment, model, left.value, right)
    if right.category == model.first_category:
        return _row_has_ref(assignment, model, right.value, left)
    le = _find_entity_for_ref(assignment, model, left)
    re = _find_entity_for_ref(assignment, model, right)
    return le is not None and re is not None and le == re


def _find_entity_for_ref(
    assignment: Dict[str, Dict[str, str]], model: _DeductionModel, ref: _LabelRef
) -> Optional[str]:
    if ref.category == model.first_category:
        return ref.value
    for entity in model.first_values:
        if assignment[entity].get(ref.category) == ref.value:
            return entity
    return None


def _day_index_for_ref(
    assignment: Dict[str, Dict[str, str]], model: _DeductionModel, ref: _LabelRef
) -> Optional[int]:
    if model.day_category is None:
        return None
    entity = _find_entity_for_ref(assignment, model, ref)
    if entity is None:
        return None
    day = assignment[entity].get(model.day_category)
    if day is None:
        return None
    return model.day_rank.get(day)


def _constraint_matches(
    assignment: Dict[str, Dict[str, str]],
    model: _DeductionModel,
    constraint: _Constraint,
) -> bool:
    left = constraint.left
    right = constraint.right
    if right is None:
        return False

    if constraint.kind == CONSTRAINT_ENTITY_VALUE:
        return _refs_co_same_row(assignment, model, left, right)
    if constraint.kind == CONSTRAINT_ENTITY_NOT_VALUE:
        return not _refs_co_same_row(assignment, model, left, right)
    if constraint.kind == CONSTRAINT_SAME_ROW:
        left_entity = _find_entity_for_ref(assignment, model, left)
        right_entity = _find_entity_for_ref(assignment, model, right)
        return left_entity is not None and left_entity == right_entity

    left_day = _day_index_for_ref(assignment, model, left)
    right_day = _day_index_for_ref(assignment, model, right)
    if left_day is None or right_day is None:
        return False

    if constraint.kind == CONSTRAINT_ENTITY_BEFORE_ENTITY:
        return (
            left.category == model.first_category
            and right.category == model.first_category
            and left_day < right_day
        )
    if constraint.kind == CONSTRAINT_ENTITY_AFTER_ENTITY:
        return (
            left.category == model.first_category
            and right.category == model.first_category
            and left_day > right_day
        )
    if constraint.kind == CONSTRAINT_ENTITY_IMMEDIATELY_BEFORE_ENTITY:
        return (
            left.category == model.first_category
            and right.category == model.first_category
            and right_day - left_day == 1
        )
    if constraint.kind == CONSTRAINT_VALUE_BEFORE_VALUE:
        return left_day < right_day
    if constraint.kind == CONSTRAINT_ENTITY_NOT_ADJACENT_VALUE:
        return left.category == model.first_category and abs(left_day - right_day) != 1
    return False


def _assignment_signature(
    assignment: Dict[str, Dict[str, str]], model: _DeductionModel
) -> str:
    rows = []
    for entity in model.first_values:
        row_values = [entity] + [
            assignment[entity][category] for category in model.secondary_categories
        ]
        rows.append(":".join(_norm(value) for value in row_values))
    return ",".join(rows)


def _expected_answer_signature(
    correct_answer: str, model: _DeductionModel
) -> Optional[str]:
    rows_by_entity: Dict[str, List[str]] = {}
    by_category_value = {
        category: {_norm(value): value for value in values}
        for category, values in model.values_by_category.items()
    }
    for raw_part in str(correct_answer or "").split(","):
        part = raw_part.strip()
        if not part:
            continue
        segments = [segment.strip() for segment in part.split(":")]
        if len(segments) != len(model.category_order):
            return None
        canonical_segments: List[str] = []
        for category, segment in zip(model.category_order, segments):
            value = by_category_value[category].get(_norm(segment))
            if value is None:
                return None
            canonical_segments.append(value)
        entity = canonical_segments[0]
        rows_by_entity[entity] = canonical_segments

    if set(rows_by_entity) != set(model.first_values):
        return None

    return ",".join(
        ":".join(_norm(value) for value in rows_by_entity[entity])
        for entity in model.first_values
    )


def _total_search_space(model: _DeductionModel) -> int:
    per_category = math.factorial(len(model.first_values))
    return per_category ** len(model.secondary_categories)


def analyze_deduction_uniqueness(
    visual_data: Dict[str, Any], correct_answer: str
) -> DeductionUniquenessResult:
    """Return a uniqueness verdict when the grid is small and constraints are parseable."""
    model = _build_model(visual_data)
    if model is None:
        return DeductionUniquenessResult(False, 0, "unsupported_model")

    constraints, constraint_source = _parse_constraints(visual_data, model)
    if constraints is None or not constraints:
        return DeductionUniquenessResult(False, 0, constraint_source)

    search_space = _total_search_space(model)
    if search_space > MAX_DEDUCTION_SOLVER_COMBINATIONS:
        return DeductionUniquenessResult(False, 0, "search_space_too_large")

    permutations_by_category = [
        tuple(itertools.permutations(model.values_by_category[category]))
        for category in model.secondary_categories
    ]

    solution_signatures: List[str] = []
    for permutation_combo in itertools.product(*permutations_by_category):
        assignment: Dict[str, Dict[str, str]] = {
            entity: {} for entity in model.first_values
        }
        for category, permutation in zip(model.secondary_categories, permutation_combo):
            for entity, value in zip(model.first_values, permutation):
                assignment[entity][category] = value
        if all(
            _constraint_matches(assignment, model, constraint)
            for constraint in constraints
        ):
            solution_signatures.append(_assignment_signature(assignment, model))
            if len(solution_signatures) > UNIQUE_SOLUTION_TARGET:
                break

    expected_signature = _expected_answer_signature(correct_answer, model)
    expected_matches: Optional[bool] = None
    if (
        len(solution_signatures) == UNIQUE_SOLUTION_TARGET
        and expected_signature is not None
    ):
        expected_matches = expected_signature == solution_signatures[0]

    return DeductionUniquenessResult(
        checked=True,
        solution_count=len(solution_signatures),
        reason=f"{constraint_source}_constraints",
        expected_answer_matches=expected_matches,
    )
