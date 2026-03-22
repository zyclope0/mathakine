"""Chargement du corpus versionné (JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def default_corpus_path() -> Path:
    """Corpus relatif à la racine du dépôt."""
    return (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "ai_eval"
        / "corpus.json"
    )


def load_corpus(path: Path | None = None) -> Dict[str, Any]:
    p = path or default_corpus_path()
    if not p.is_file():
        raise FileNotFoundError(f"Corpus introuvable: {p}")
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def iter_cases(
    data: Dict[str, Any],
    *,
    target: str,
    mode: str,
) -> List[Dict[str, Any]]:
    """
    Filtre les cas selon la cible et le mode.

    target: all | simple | template_exercises | fixtures | openai_exercises |
            openai_challenges | exercises_ai (fixtures + template + openai exercise)
    """
    cases: List[Dict[str, Any]] = list(data.get("cases") or [])
    out: List[Dict[str, Any]] = []
    for c in cases:
        if c.get("live_only") and mode != "live":
            continue
        pipe = str(c.get("pipeline", ""))
        if target == "all":
            if mode == "offline" and c.get("live_only"):
                continue
            out.append(c)
            continue
        if target == "simple":
            if pipe == "simple_generator":
                out.append(c)
        elif target == "template_exercises":
            if pipe == "template_exercise_generator":
                out.append(c)
        elif target == "fixtures":
            if pipe in ("fixture_exercise_openai_shape", "fixture_challenge"):
                out.append(c)
        elif target == "openai_exercises":
            if pipe == "openai_exercise_stream":
                out.append(c)
        elif target == "openai_challenges":
            if pipe == "openai_challenge_stream":
                out.append(c)
        elif target == "exercises_ai":
            if pipe in (
                "template_exercise_generator",
                "fixture_exercise_openai_shape",
                "openai_exercise_stream",
            ):
                if mode == "offline" and pipe == "openai_exercise_stream":
                    continue
                out.append(c)
        elif target == "challenges_ai":
            if pipe in ("fixture_challenge", "openai_challenge_stream"):
                if mode == "offline" and pipe == "openai_challenge_stream":
                    continue
                out.append(c)
    return out
