"""One-shot audit for exercise generation calibration before beta invitations.

The script is intentionally read-only for the application: it builds prompts
through the production helpers, measures the authorized type x difficulty
matrix, and emits a JSON report to stdout or --output.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_AGE_GROUP = "15-17"
DEFAULT_THEME = "spatial/galactique (vaisseaux, planetes, etoiles)"
DEFAULT_USER_PROMPT = ""
REPORT_SCHEMA_VERSION = 1

NUMBER_RE = re.compile(r"-?\d+(?:[,.]\d+)?")
MULTI_STEP_RE = re.compile(
    r"(\betapes?\b|\bétapes?\b|\n\s*1[.)].*\n\s*2[.)])",
    flags=re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class GenerationDeps:
    build_exercise_ai_stream_kwargs: Callable[..., dict[str, Any]]
    build_exercise_difficulty_info: Callable[[str, str], dict[str, Any]]
    build_exercise_generation_profile: Callable[..., dict[str, Any]]
    build_exercise_system_prompt: Callable[..., str]
    build_exercise_user_prompt: Callable[[Optional[str], str, str], str]
    difficulty_order: tuple[str, ...]
    difficulty_rank: dict[str, int]
    extract_json_from_text: Callable[[str], dict[str, Any]]
    resolve_exercise_ai_model: Callable[[], str]
    settings: Any
    type_difficulty_bounds: dict[str, tuple[str, str]]


@dataclass(frozen=True)
class TokenCounter:
    count: Callable[[str], int]
    name: str
    exact: bool
    reason: Optional[str] = None


def _load_generation_deps() -> GenerationDeps:
    """Import app helpers while keeping stdout reserved for the JSON report."""
    with contextlib.redirect_stdout(sys.stderr):
        from app.core.ai_generation_policy import (  # noqa: PLC0415
            build_exercise_ai_stream_kwargs,
            resolve_exercise_ai_model,
        )
        from app.core.config import settings  # noqa: PLC0415
        from app.core.difficulty_tier import (  # noqa: PLC0415
            _DIFFICULTY_ORDER,
            _DIFFICULTY_RANK,
            _TYPE_DIFFICULTY_BOUNDS,
            build_exercise_generation_profile,
        )
        from app.services.exercises.exercise_ai_service import (  # noqa: PLC0415
            build_exercise_difficulty_info,
            build_exercise_system_prompt,
            build_exercise_user_prompt,
        )
        from app.utils.json_utils import extract_json_from_text  # noqa: PLC0415

    return GenerationDeps(
        build_exercise_ai_stream_kwargs=build_exercise_ai_stream_kwargs,
        build_exercise_difficulty_info=build_exercise_difficulty_info,
        build_exercise_generation_profile=build_exercise_generation_profile,
        build_exercise_system_prompt=build_exercise_system_prompt,
        build_exercise_user_prompt=build_exercise_user_prompt,
        difficulty_order=_DIFFICULTY_ORDER,
        difficulty_rank=_DIFFICULTY_RANK,
        extract_json_from_text=extract_json_from_text,
        resolve_exercise_ai_model=resolve_exercise_ai_model,
        settings=settings,
        type_difficulty_bounds=_TYPE_DIFFICULTY_BOUNDS,
    )


def _load_token_counter(model: str) -> TokenCounter:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        return TokenCounter(
            count=lambda text: math.ceil(len(text) / 4),
            name="fallback_char_estimate",
            exact=False,
            reason=f"tiktoken unavailable: {exc.__class__.__name__}",
        )

    try:
        encoding = tiktoken.encoding_for_model(model)
        name = f"tiktoken:{encoding.name}:model:{model}"
    except KeyError:
        try:
            encoding = tiktoken.get_encoding("o200k_base")
        except Exception:  # pragma: no cover - defensive for old tiktoken builds
            encoding = tiktoken.get_encoding("cl100k_base")
        name = f"tiktoken:{encoding.name}:fallback_for:{model}"

    return TokenCounter(
        count=lambda text: len(encoding.encode(text)),
        name=name,
        exact=True,
    )


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _allowed_cells(deps: GenerationDeps) -> Iterable[tuple[str, str]]:
    for exercise_type, (floor, ceiling) in deps.type_difficulty_bounds.items():
        floor_rank = deps.difficulty_rank[floor]
        ceiling_rank = deps.difficulty_rank[ceiling]
        for difficulty in deps.difficulty_order[floor_rank : ceiling_rank + 1]:
            yield exercise_type, difficulty


def _percentile(values: list[float], percentile: float) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 2)
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[int(position)], 2)
    weight = position - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 2)


def _numeric_magnitude(value: Any) -> Optional[float]:
    matches = NUMBER_RE.findall(str(value or "").replace(" ", ""))
    if not matches:
        return None
    numbers = [abs(float(match.replace(",", "."))) for match in matches]
    return max(numbers) if numbers else None


def _max_operand_magnitude(*texts: str) -> Optional[float]:
    numbers: list[float] = []
    for text in texts:
        numbers.extend(
            abs(float(match.replace(",", ".")))
            for match in NUMBER_RE.findall((text or "").replace(" ", ""))
        )
    return max(numbers) if numbers else None


def _detect_multi_step(explanation: str) -> bool:
    return bool(MULTI_STEP_RE.search(explanation or ""))


def _extract_json_object(raw_text: str, deps: GenerationDeps) -> dict[str, Any]:
    return deps.extract_json_from_text(raw_text)


def _collect_stream_content(stream: Any) -> str:
    chunks: list[str] = []
    for chunk in stream:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            continue
        delta = getattr(choices[0], "delta", None)
        content = getattr(delta, "content", None)
        if content:
            chunks.append(content)
    return "".join(chunks)


def _generate_sample(
    *,
    deps: GenerationDeps,
    model: str,
    exercise_type: str,
    system_prompt: str,
    user_prompt: str,
) -> dict[str, Any]:
    from openai import OpenAI  # noqa: PLC0415

    kwargs = deps.build_exercise_ai_stream_kwargs(
        model=model,
        exercise_type=exercise_type,
        system_content=system_prompt,
        user_content=user_prompt,
    )
    client = OpenAI(api_key=deps.settings.OPENAI_API_KEY)
    raw_text = _collect_stream_content(client.chat.completions.create(**kwargs))
    payload = _extract_json_object(raw_text, deps)
    question = str(payload.get("question") or "")
    explanation = str(payload.get("explanation") or "")
    correct_answer = str(payload.get("correct_answer") or "")
    return {
        "correct_answer": correct_answer,
        "correct_answer_magnitude": _numeric_magnitude(correct_answer),
        "max_operand_magnitude": _max_operand_magnitude(question, explanation),
        "multi_step_detected": _detect_multi_step(explanation),
        "raw_response_sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
    }


def _build_cell(
    *,
    deps: GenerationDeps,
    token_counter: TokenCounter,
    model: str,
    exercise_type: str,
    difficulty: str,
    age_group: str,
    generate: bool,
    samples_per_cell: int,
) -> dict[str, Any]:
    diff_info = deps.build_exercise_difficulty_info(exercise_type, difficulty)
    profile = deps.build_exercise_generation_profile(
        exercise_type,
        age_group,
        difficulty,
    )
    system_prompt = deps.build_exercise_system_prompt(
        exercise_type,
        difficulty,
        profile["age_group"],
        diff_info,
        DEFAULT_THEME,
        calibration_desc=profile.get("calibration_desc", ""),
        cognitive_hint=profile.get("cognitive_hint", ""),
    )
    user_prompt = deps.build_exercise_user_prompt(
        DEFAULT_USER_PROMPT,
        exercise_type,
        difficulty,
    )
    cell: dict[str, Any] = {
        "exercise_type": exercise_type,
        "difficulty": difficulty,
        "age_group": profile["age_group"],
        "difficulty_tier": profile.get("difficulty_tier"),
        "pedagogical_band": profile.get("pedagogical_band"),
        "cognitive_intensity": profile.get("cognitive_intensity"),
        "system_prompt_tokens": token_counter.count(system_prompt),
        "system_prompt_sha256": hashlib.sha256(
            system_prompt.encode("utf-8")
        ).hexdigest(),
        "difficulty_desc": diff_info.get("desc"),
    }
    if generate:
        cell["samples"] = [
            _generate_sample(
                deps=deps,
                model=model,
                exercise_type=exercise_type,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            for _ in range(samples_per_cell)
        ]
    return cell


def _build_aggregates(matrix: dict[str, dict[str, Any]]) -> dict[str, Any]:
    token_values = [
        float(cell["system_prompt_tokens"])
        for cell in matrix.values()
        if isinstance(cell.get("system_prompt_tokens"), int)
    ]
    magnitudes_by_difficulty: dict[str, list[float]] = {}
    for cell in matrix.values():
        for sample in cell.get("samples", []):
            magnitude = sample.get("max_operand_magnitude")
            if isinstance(magnitude, (int, float)):
                magnitudes_by_difficulty.setdefault(cell["difficulty"], []).append(
                    float(magnitude)
                )
    return {
        "authorized_cells": len(matrix),
        "tokens_p50": _percentile(token_values, 0.50),
        "tokens_p95": _percentile(token_values, 0.95),
        "magnitude_p50_per_difficulty": {
            difficulty: _percentile(values, 0.50)
            for difficulty, values in sorted(magnitudes_by_difficulty.items())
        },
    }


def build_report(args: argparse.Namespace, deps: GenerationDeps) -> dict[str, Any]:
    model = deps.resolve_exercise_ai_model()
    token_counter = _load_token_counter(model)
    matrix: dict[str, dict[str, Any]] = {}
    for exercise_type, difficulty in _allowed_cells(deps):
        key = f"{exercise_type}_{difficulty}"
        matrix[key] = _build_cell(
            deps=deps,
            token_counter=token_counter,
            model=model,
            exercise_type=exercise_type,
            difficulty=difficulty,
            age_group=args.age_group,
            generate=args.generate,
            samples_per_cell=args.n,
        )

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(),
        "mode": "generate" if args.generate else "dry_run",
        "model": model,
        "age_group": args.age_group,
        "samples_per_cell": args.n if args.generate else 0,
        "tokenizer": {
            "name": token_counter.name,
            "exact": token_counter.exact,
            "reason": token_counter.reason,
        },
        "matrix": matrix,
        "aggregates": _build_aggregates(matrix),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a pre-invitations calibration baseline for exercise generation."
        )
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Call OpenAI and collect generated samples. Default is dry-run only.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compatibility flag; dry-run is already the default unless --generate is set.",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=3,
        help="Number of OpenAI samples per authorized cell when --generate is used.",
    )
    parser.add_argument(
        "--age-group",
        default=DEFAULT_AGE_GROUP,
        help=f"Age group used to build F42 profiles. Default: {DEFAULT_AGE_GROUP}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path. Defaults to stdout.",
    )
    args = parser.parse_args()
    if args.n < 1:
        parser.error("--n must be >= 1")
    return args


def main() -> int:
    args = parse_args()
    deps = _load_generation_deps()
    if args.generate and not deps.settings.OPENAI_API_KEY:
        raise SystemExit("--generate requires settings.OPENAI_API_KEY")

    report = build_report(args, deps)
    output = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
