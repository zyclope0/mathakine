"""
Politique de contrat par type de défi (lot IA9).

Source de vérité runtime pour :
- modalité de réponse (`response_mode`) ;
- présence / persistance des `choices` (QCM) ;
- normalisation minimale du contrat VISUAL / symétrie.

Principes EdTech :
- QCM vs réponse libre vs interaction changent la charge cognitive (reconnaissance vs production).
- Un défi « plausible » mais hors contrat machine reste produit-invalide : fail-closed côté validation.
- Le frontend ne doit pas inférer un QCM depuis la seule présence de `choices` : décision portée par `response_mode`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from app.services.challenges.challenge_answer_quality import validate_challenge_choices

# Seuil strict : QCM autorisé pour types « interaction-first » seulement si difficulté < 2.0.
EASY_QCM_MAX_DIFFICULTY_EXCLUSIVE: float = 2.0

# Valeurs exposées API / frontend (contrat stable).
RESPONSE_MODE_OPEN_TEXT = "open_text"
RESPONSE_MODE_SINGLE_CHOICE = "single_choice"
RESPONSE_MODE_INTERACTIVE_VISUAL = "interactive_visual"
RESPONSE_MODE_INTERACTIVE_ORDER = "interactive_order"
RESPONSE_MODE_INTERACTIVE_GRID = "interactive_grid"

RESPONSE_MODES: Tuple[str, ...] = (
    RESPONSE_MODE_OPEN_TEXT,
    RESPONSE_MODE_SINGLE_CHOICE,
    RESPONSE_MODE_INTERACTIVE_VISUAL,
    RESPONSE_MODE_INTERACTIVE_ORDER,
    RESPONSE_MODE_INTERACTIVE_GRID,
)


class ChoicesDisposition(str, Enum):
    """Politique de persistance / validation des listes `choices`."""

    OPTIONAL = "optional"
    """QCM possible si la liste est valide (règles ``validate_challenge_choices``)."""

    FORBIDDEN = "forbidden"
    """Ne jamais conserver ni valider un QCM pour ce type."""

    RESTRICTED_EASY_ONLY = "restricted_easy_only"
    """
    QCM seulement si ``difficulty_rating < EASY_QCM_MAX_DIFFICULTY_EXCLUSIVE`` ;
    au-delà : interaction ou texte libre selon le type.
    """


@dataclass(frozen=True)
class ChallengeTypeContract:
    """Ligne de la matrice contrat (documentation + comportement)."""

    choices_disposition: ChoicesDisposition
    default_response_mode: str
    visual_contract_hint: str
    frontend_renderer: str


def _upper_type(challenge_type: str) -> str:
    return (challenge_type or "").strip().upper()


# Matrice source de vérité (types DB/API normalisés en majuscules).
TYPE_CONTRACTS: Dict[str, ChallengeTypeContract] = {
    "SEQUENCE": ChallengeTypeContract(
        ChoicesDisposition.OPTIONAL,
        RESPONSE_MODE_INTERACTIVE_GRID,
        "visual_data.sequence ou items ; pas de QCM imposé.",
        "SequenceRenderer",
    ),
    "PATTERN": ChallengeTypeContract(
        ChoicesDisposition.OPTIONAL,
        RESPONSE_MODE_INTERACTIVE_GRID,
        "visual_data.grid avec ? ; réponse alignée grille.",
        "PatternRenderer",
    ),
    "VISUAL": ChallengeTypeContract(
        ChoicesDisposition.RESTRICTED_EASY_ONLY,
        RESPONSE_MODE_INTERACTIVE_VISUAL,
        'symétrie : type "symmetry", symmetry_line vertical|horizontal, layout[{side,shape,...}].',
        "VisualRenderer",
    ),
    "PUZZLE": ChallengeTypeContract(
        ChoicesDisposition.RESTRICTED_EASY_ONLY,
        RESPONSE_MODE_INTERACTIVE_ORDER,
        "visual_data.pieces + hints ; correct_answer ordre.",
        "PuzzleRenderer",
    ),
    "GRAPH": ChallengeTypeContract(
        ChoicesDisposition.OPTIONAL,
        RESPONSE_MODE_OPEN_TEXT,
        "nodes/edges cohérents ; réponse texte courte.",
        "GraphRenderer",
    ),
    "RIDDLE": ChallengeTypeContract(
        ChoicesDisposition.OPTIONAL,
        RESPONSE_MODE_OPEN_TEXT,
        "clues/context/riddle/grid au choix.",
        "RiddleRenderer",
    ),
    "DEDUCTION": ChallengeTypeContract(
        ChoicesDisposition.FORBIDDEN,
        RESPONSE_MODE_INTERACTIVE_GRID,
        "type logic_grid, entities, clues ; réponse associations.",
        "DeductionRenderer",
    ),
    "PROBABILITY": ChallengeTypeContract(
        ChoicesDisposition.OPTIONAL,
        RESPONSE_MODE_OPEN_TEXT,
        "quantités numériques dans visual_data.",
        "ProbabilityRenderer",
    ),
    "CODING": ChallengeTypeContract(
        ChoicesDisposition.OPTIONAL,
        RESPONSE_MODE_OPEN_TEXT,
        "sous-type crypto / maze selon validateur coding ; choices possibles pour assistance diff\u00e9r\u00e9e, r\u00e9ponse libre par d\u00e9faut.",
        "CodingRenderer",
    ),
    "CHESS": ChallengeTypeContract(
        ChoicesDisposition.FORBIDDEN,
        RESPONSE_MODE_OPEN_TEXT,
        "board 8x8, turn, objective ; notation algébrique.",
        "ChessRenderer",
    ),
}


def get_type_contract(challenge_type: str) -> ChallengeTypeContract:
    """Contrat pour un type ; CUSTOM / inconnu → défaut fail-safe (pas de QCM forcé)."""
    key = _upper_type(challenge_type)
    if key not in TYPE_CONTRACTS:
        return ChallengeTypeContract(
            ChoicesDisposition.OPTIONAL,
            RESPONSE_MODE_OPEN_TEXT,
            "Type générique : réponse libre par défaut.",
            "DefaultRenderer",
        )
    return TYPE_CONTRACTS[key]


def _as_float_difficulty(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    try:
        f = float(raw)
    except (TypeError, ValueError):
        return None
    if 1.0 <= f <= 5.0:
        return f
    return None


def validate_choices_policy(
    challenge_type: str,
    difficulty_rating: Optional[float],
    choices: Any,
) -> List[str]:
    """
    Erreurs métier si ``choices`` est présent alors que la politique l'interdit.

    Une liste vide ou null ne pose pas problème.
    """
    errors: List[str] = []
    contract = get_type_contract(challenge_type)

    if choices is None:
        return errors
    if isinstance(choices, str):
        return errors
    if not isinstance(choices, list):
        return errors
    if len(choices) == 0:
        return errors

    dr = difficulty_rating

    if contract.choices_disposition == ChoicesDisposition.FORBIDDEN:
        errors.append(
            f"Le type {_upper_type(challenge_type)} n'accepte pas de champ choices (QCM interdit). "
            "Omettre choices ou utiliser la réponse structurée attendue."
        )
        return errors

    if contract.choices_disposition == ChoicesDisposition.RESTRICTED_EASY_ONLY:
        if dr is None or dr >= EASY_QCM_MAX_DIFFICULTY_EXCLUSIVE:
            errors.append(
                f"QCM (choices) pour le type {_upper_type(challenge_type)} uniquement si "
                f"difficulty_rating < {EASY_QCM_MAX_DIFFICULTY_EXCLUSIVE} ; sinon omettre choices "
                "et utiliser l'interaction prévue (symétrie, ordre des pièces, etc.)."
            )

    if _upper_type(challenge_type) == "SEQUENCE" and dr is not None and dr >= 4.0:
        errors.append(
            "SEQUENCE : omettre choices pour difficulty_rating >= 4.0. "
            "À ce niveau, la réponse doit rester en production libre plutôt qu'en reconnaissance QCM."
        )

    return errors


def filter_choices_for_persistence(
    challenge_type: str,
    difficulty_rating: Optional[float],
    choices: Any,
) -> Optional[List[str]]:
    """
    Retourne la liste à persister (ou None si aucun QCM actif).

    Défense en profondeur après validation : ne jamais persister des choices interdits.
    """
    if choices is None:
        return None
    if not isinstance(choices, list) or len(choices) == 0:
        return None

    errs = validate_choices_policy(challenge_type, difficulty_rating, choices)
    if errs:
        return None

    out = [str(c).strip() for c in choices if c is not None and str(c).strip()]
    return out if len(out) > 0 else None


def sanitize_choices_for_delivery(
    challenge_type: str,
    difficulty_rating: Optional[float],
    choices: Any,
    correct_answer: Optional[str],
) -> List[str]:
    """
    IA9b — Choix exposés API et utilisés pour ``response_mode`` : policy type/difficulté
    **et** cohérence QCM métier (``validate_challenge_choices``).

    Retourne ``[]`` si la liste est absente, interdite, ou invalide (legacy / manuel /
    distracteurs incohérents) : pas de QCM actif côté produit.
    """
    filtered = filter_choices_for_persistence(
        challenge_type, difficulty_rating, choices
    )
    if not filtered:
        return []
    ca = str(correct_answer or "").strip()
    errs = validate_challenge_choices(challenge_type, ca, filtered)
    if errs:
        return []
    return filtered


def _has_nonempty_choices(choices: Any) -> bool:
    if not isinstance(choices, list) or len(choices) == 0:
        return False
    return any(c is not None and str(c).strip() for c in choices)


def compute_response_mode(
    challenge_type: str,
    visual_data: Any,
    difficulty_rating: Optional[float],
    choices_after_policy: Any,
) -> str:
    """
    Modalité d'interaction utilisateur (champ exposé API).

    Priorité : QCM seulement si choices autorisés **et** liste non vide après policy.
    """
    ct = _upper_type(challenge_type)

    if ct == "CODING":
        return RESPONSE_MODE_OPEN_TEXT

    if _has_nonempty_choices(choices_after_policy):
        return RESPONSE_MODE_SINGLE_CHOICE

    vd = visual_data if isinstance(visual_data, dict) else {}

    if ct == "PUZZLE" and (vd.get("pieces") or vd.get("items")):
        return RESPONSE_MODE_INTERACTIVE_ORDER

    if ct == "VISUAL" and vd:
        return RESPONSE_MODE_INTERACTIVE_VISUAL

    if ct == "PATTERN" and (vd.get("grid") or vd.get("matrix") or vd.get("pattern")):
        return RESPONSE_MODE_INTERACTIVE_GRID

    seq = vd.get("sequence")
    items = vd.get("items")
    if ct == "SEQUENCE" and (
        (isinstance(seq, list) and len(seq) > 0)
        or (isinstance(items, list) and len(items) > 0)
    ):
        return RESPONSE_MODE_INTERACTIVE_GRID

    if ct == "DEDUCTION" and str(vd.get("type", "")).lower() == "logic_grid":
        return RESPONSE_MODE_INTERACTIVE_GRID

    contract = get_type_contract(challenge_type)
    return contract.default_response_mode


def normalize_symmetry_visual_data(visual_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forme canonique VISUAL / symétrie pour prompt ↔ validateur ↔ VisualRenderer.

    - ``type``: \"symmetry\"
    - ``symmetry_line``: \"vertical\" | \"horizontal\"
    - ``layout`` : éléments avec ``side`` en minuscules.
    """
    if not isinstance(visual_data, dict):
        return {}

    out = dict(visual_data)
    layout = out.get("layout")
    sym_line = out.get("symmetry_line") or out.get("symmetryLine") or out.get("axis")

    is_symmetry_candidate = (
        isinstance(layout, list)
        and len(layout) > 0
        and (out.get("type") == "symmetry" or sym_line is not None)
    )

    if is_symmetry_candidate:
        out["type"] = "symmetry"
        if sym_line is not None:
            sl = str(sym_line).lower().strip()
            if sl in ("vertical", "horizontal", "v", "h"):
                out["symmetry_line"] = (
                    "vertical" if sl in ("vertical", "v") else "horizontal"
                )
            else:
                out["symmetry_line"] = "vertical"
        elif "symmetry_line" not in out:
            out["symmetry_line"] = "vertical"

        for k in ("symmetryLine", "axis"):
            out.pop(k, None)

        # Detect row-based format: [{"row": N, "left": [...], "right": [...]}]
        # OpenAI sometimes generates this instead of the canonical flat format.
        # Convert to canonical: [{"side": "left"|"right", "shape": "..."[, "question": true]}]
        if (
            isinstance(layout, list)
            and layout
            and isinstance(layout[0], dict)
            and "row" in layout[0]
            and ("left" in layout[0] or "right" in layout[0])
        ):
            flat_items: List[Any] = []
            for row_item in layout:
                if not isinstance(row_item, dict):
                    continue
                for shape_str in row_item.get("left") or []:
                    flat_items.append({"side": "left", "shape": str(shape_str)})
                for shape_str in row_item.get("right") or []:
                    s = str(shape_str)
                    cell: Dict[str, Any] = {"side": "right", "shape": s}
                    if s == "?":
                        cell["question"] = True
                    flat_items.append(cell)
            layout = flat_items
            out["layout"] = flat_items

        new_layout: List[Any] = []
        if isinstance(layout, list):
            for item in layout:
                if isinstance(item, dict):
                    cell = dict(item)
                    if "side" in cell:
                        cell["side"] = str(cell["side"]).lower().strip()
                    new_layout.append(cell)
                else:
                    new_layout.append(item)
            out["layout"] = new_layout

    return out


def apply_visual_contract_normalization(
    challenge_type: str, visual_data: Any
) -> Dict[str, Any]:
    """Normalisation légère par type avant validation IA."""
    if not isinstance(visual_data, dict):
        return {}

    vd = dict(visual_data)
    ct = _upper_type(challenge_type)

    if ct == "VISUAL":
        vd = normalize_symmetry_visual_data(vd)

    return vd


def validate_symmetry_canonical(visual_data: Dict[str, Any]) -> List[str]:
    """
    Invariants symétrie (fail-closed) une fois la branche symétrie détectée.
    Complète ``validate_spatial_challenge`` sans casser les grilles VISUAL non-symétrie.
    """
    errors: List[str] = []
    if not visual_data or visual_data.get("type") != "symmetry":
        return errors

    line = visual_data.get("symmetry_line")
    if line not in ("vertical", "horizontal"):
        errors.append(
            'VISUAL symmetry: symmetry_line doit être "vertical" ou "horizontal" (contrat canonique).'
        )

    layout = visual_data.get("layout")
    if not layout or not isinstance(layout, list):
        errors.append("VISUAL symmetry: layout[] requis.")
        return errors

    for i, item in enumerate(layout):
        if not isinstance(item, dict):
            errors.append(
                f"VISUAL symmetry: layout[{i}] doit être un objet avec au moins side/shape."
            )
            continue
        side = item.get("side")
        if side is not None and str(side).lower() not in ("left", "right"):
            errors.append(
                f'VISUAL symmetry: layout[{i}].side doit être "left" ou "right".'
            )

    return errors
