"""Tests for canonical_token + integration with puzzle/deduction validators.

Context: Sentry 115344051 (2026-04-26) — false-positive
``"Puzzle: éléments manquants dans correct_answer:
{'\\\\ln(x)', 'e^x', '\\\\sqrt{x}', ...}"`` triggered when the LLM emitted
LaTeX (``\\ln(x)``, ``\\sqrt{x}``, ``x^2``) in ``visual_data.pieces`` and
Unicode (``ln(x)``, ``√x``, ``x²``, ``eˣ``) in ``correct_answer``. These
tests pin the equivalence and guard against regressions.
"""

from __future__ import annotations

import unicodedata

import pytest

from app.services.challenges.challenge_ordering_utils import (
    canonical_piece_key,
    canonical_token,
)
from app.services.challenges.challenge_validator import (
    validate_deduction_challenge,
    validate_puzzle_challenge,
)

# --- canonical_token: pure unit tests -----------------------------------


def test_canonical_token_handles_none_and_empty() -> None:
    assert canonical_token(None) == ""
    assert canonical_token("") == ""
    assert canonical_token("   ") == ""


def test_canonical_token_lowercases_and_nfkc() -> None:
    """NFKC folds compatibility chars (e.g. fullwidth, mathematical italic)."""
    assert canonical_token("ALICE") == "alice"
    nfd = unicodedata.normalize("NFD", "Café")
    nfc = unicodedata.normalize("NFC", "Café")
    assert canonical_token(nfd) == canonical_token(nfc) == "café"
    assert canonical_token("\uff21\uff42") == "ab"


@pytest.mark.parametrize(
    "latex,unicode_,expected",
    [
        ("\\ln(x)", "ln(x)", "lnx"),
        ("\\sqrt{x}", "√x", "sqrtx"),
        ("\\sqrt{2x}", "√(2x)", "sqrt2x"),
        ("e^x", "eˣ", "e^x"),
        ("x^2", "x²", "x^2"),
        ("x^3", "x³", "x^3"),
        ("2x", "2x", "2x"),
    ],
)
def test_canonical_token_collapses_latex_unicode_math(
    latex: str, unicode_: str, expected: str
) -> None:
    """LaTeX and Unicode math equivalents must collapse to the same key."""
    assert canonical_token(latex) == expected
    assert canonical_token(unicode_) == expected


def test_canonical_token_preserves_distinct_tokens() -> None:
    """Things that are NOT equivalent must stay distinct (no false negative)."""
    assert canonical_token("e^x") != canonical_token("e^y")
    assert canonical_token("x^2") != canonical_token("x^3")
    assert canonical_token("\\ln(x)") != canonical_token("\\log(x)")
    assert canonical_token("alice") != canonical_token("bob")


def test_canonical_token_idempotent() -> None:
    """Applying the function twice must yield the same result."""
    samples = ["\\ln(x)", "√x", "x²", "Alice", "  Bob  ", "e^x", "Café"]
    for s in samples:
        once = canonical_token(s)
        twice = canonical_token(once)
        assert once == twice, f"Not idempotent for {s!r}: {once!r} -> {twice!r}"


def test_canonical_token_handles_unicode_math_operators() -> None:
    assert canonical_token("3 × 4") == "3*4"
    assert canonical_token("a · b") == "a*b"
    assert canonical_token("10 ÷ 2") == "10/2"
    assert canonical_token("a ≤ b") == "a<=b"


def test_canonical_piece_key_handles_dict_pieces() -> None:
    """``canonical_piece_key`` doit lire l'``id`` (clé d'ordre) et le canoniser."""
    piece = {"id": "P1", "label": "\\ln(x)"}
    assert canonical_piece_key(piece) == "p1"
    piece_label_first = {"label": "\\sqrt{x}"}
    assert canonical_piece_key(piece_label_first) == "sqrtx"


# --- Integration: PUZZLE validator (Sentry 115344051 case) --------------


_SENTRY_PIECES = ["\\ln(x)", "\\sqrt{x}", "2x", "x^2", "x^3", "e^x"]
_SENTRY_HINTS = [
    "Pour x → +∞, certaines fonctions croissent beaucoup plus vite.",
    "Compare les limites relatives lim f_i / f_j.",
    "Identifie d'abord la plus lente et la plus rapide.",
]


def test_puzzle_accepts_unicode_answer_for_latex_pieces() -> None:
    """Régression Sentry 115344051 : LaTeX dans pieces + Unicode dans answer."""
    vd = {"pieces": _SENTRY_PIECES, "hints": _SENTRY_HINTS}
    answer = "ln(x), √x, 2x, x², x³, eˣ"
    explanation = (
        "On compare les vitesses de croissance : ln(x) plus lent que √x, "
        "puis 2x, x², x³ et enfin eˣ qui domine."
    )
    errors = validate_puzzle_challenge(vd, answer, explanation)
    missing_errors = [e for e in errors if "manquants dans correct_answer" in e]
    assert (
        missing_errors == []
    ), f"Le validateur signale à tort des éléments manquants: {missing_errors}"


def test_puzzle_accepts_latex_answer_for_unicode_pieces() -> None:
    """Symétrie : Unicode dans pieces + LaTeX dans answer doit aussi passer."""
    vd = {
        "pieces": ["ln(x)", "√x", "2x", "x²", "x³", "eˣ"],
        "hints": _SENTRY_HINTS,
    }
    answer = "\\ln(x), \\sqrt{x}, 2x, x^2, x^3, e^x"
    explanation = "On compare ln(x), sqrt(x), 2x, x^2, x^3 et e^x."
    errors = validate_puzzle_challenge(vd, answer, explanation)
    missing_errors = [e for e in errors if "manquants dans correct_answer" in e]
    assert missing_errors == []


def test_puzzle_still_rejects_real_missing_piece() -> None:
    """Garde-fou : une vraie omission doit toujours être détectée."""
    vd = {"pieces": _SENTRY_PIECES, "hints": _SENTRY_HINTS}
    answer = "ln(x), √x, 2x, x², x³"
    errors = validate_puzzle_challenge(vd, answer, "explanation")
    missing_errors = [e for e in errors if "manquants dans correct_answer" in e]
    assert missing_errors, "L'omission de e^x doit toujours produire une erreur"
    assert "e^x" in missing_errors[0]


def test_puzzle_still_rejects_extra_piece() -> None:
    """Garde-fou : une réponse plus longue que pieces doit produire une erreur de longueur."""
    vd = {"pieces": _SENTRY_PIECES, "hints": _SENTRY_HINTS}
    answer = "ln(x), √x, 2x, x², x³, eˣ, log(x)"
    errors = validate_puzzle_challenge(vd, answer, "explanation")
    length_errors = [e for e in errors if "incohérent" in e and "éléments" in e]
    assert length_errors, "Le mismatch de longueur doit toujours être détecté"


def test_puzzle_explanation_check_uses_canonical_form() -> None:
    """Une explanation en LaTeX doit valider des pieces Unicode (et inversement)."""
    vd = {
        "pieces": ["\\ln(x)", "\\sqrt{x}", "x^2", "x^3"],
        "hints": [
            "Une croissance logarithmique reste très lente.",
            "Compare ensuite racine, carré et cube.",
        ],
    }
    answer = "ln(x), √x, x², x³"
    explanation = "On voit que ln(x) < √x, puis x² < x³."
    errors = validate_puzzle_challenge(vd, answer, explanation)
    expl_errors = [e for e in errors if "explication ne mentionne pas assez" in e]
    assert (
        expl_errors == []
    ), f"L'explication doit être reconnue via la forme canonique: {expl_errors}"


# --- Integration: DEDUCTION validator (latent NFKC risk) ----------------


def test_deduction_tolerates_nfd_nfc_accent_variants() -> None:
    """Garde latent : entités équivalentes en NFD/NFC ne doivent plus diverger."""
    # `entities` en NFC, correct_answer composé en NFD : sans canonical_token,
    # le set diff `first_cat_allowed - seen_first` produirait un faux-positif.
    vd = {
        "type": "logic_grid",
        "entities": {
            "Personnes": ["Café", "Thé"],
            "Couleurs": ["Rouge", "Bleu"],
        },
        "clues": [
            "Café boit Rouge.",
            "Thé boit Bleu.",
        ],
    }
    answer_nfd = unicodedata.normalize("NFD", "Café:Rouge, Thé:Bleu")
    errors = validate_deduction_challenge(vd, answer_nfd, "explication")
    missing = [e for e in errors if "entités manquantes" in e]
    assert (
        missing == []
    ), f"NFD ↔ NFC ne doit pas produire d'entités manquantes: {missing}"


def test_deduction_still_rejects_real_missing_entity() -> None:
    """Garde-fou : une vraie omission d'entité reste détectée."""
    vd = {
        "type": "logic_grid",
        "entities": {
            "Personnes": ["Alice", "Bob"],
            "Couleurs": ["Rouge", "Bleu"],
        },
        "clues": ["Alice aime Rouge.", "Bob aime Bleu."],
    }
    errors = validate_deduction_challenge(vd, "Alice:Rouge, Alice:Bleu", "explication")
    missing = [e for e in errors if "entités manquantes" in e]
    duplicate = [e for e in errors if "même entité" in e]
    assert missing or duplicate
