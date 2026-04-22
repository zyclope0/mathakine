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

import re
import unicodedata
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


_SYMMETRY_SIDE_ALIASES: Dict[str, str] = {
    "left": "left",
    "l": "left",
    "gauche": "left",
    "cote gauche": "left",
    "cotes gauche": "left",
    "colonne gauche": "left",
    "partie gauche": "left",
    "left side": "left",
    "left column": "left",
    "right": "right",
    "r": "right",
    "droite": "right",
    "droit": "right",
    "cote droit": "right",
    "cote droite": "right",
    "cotes droit": "right",
    "cotes droite": "right",
    "colonne droite": "right",
    "partie droite": "right",
    "right side": "right",
    "right column": "right",
}

_SYMMETRY_AXIS_SIDE_VALUES = {
    "axis",
    "axe",
    "center",
    "centre",
    "milieu",
    "ligne",
    "symmetry line",
    "ligne de symetrie",
}


def _normalize_label(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    text = "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )
    return " ".join(text.replace("_", " ").replace("-", " ").split())


def _normalize_symmetry_side(raw_side: Any) -> Optional[str]:
    normalized = _normalize_label(raw_side)
    if not normalized:
        return None
    if normalized in _SYMMETRY_SIDE_ALIASES:
        return _SYMMETRY_SIDE_ALIASES[normalized]
    if "gauche" in normalized or "left" in normalized:
        return "left"
    if "droite" in normalized or "droit" in normalized or "right" in normalized:
        return "right"
    return None


def _is_symmetry_axis_side(raw_side: Any) -> bool:
    normalized = _normalize_label(raw_side)
    return normalized in _SYMMETRY_AXIS_SIDE_VALUES or "axe" in normalized


def _flatten_grouped_symmetry_layout(
    layout: List[Any],
) -> Optional[List[Dict[str, Any]]]:
    """Convertit [{side, elements|shapes|items:[...]}] en layout canonique par cellule."""
    grouped: Dict[str, List[Any]] = {}
    for item in layout:
        if not isinstance(item, dict):
            continue
        side = _normalize_symmetry_side(item.get("side"))
        elements = item.get("elements")
        if not isinstance(elements, list):
            elements = item.get("shapes")
        if not isinstance(elements, list):
            elements = item.get("items")
        if side in ("left", "right") and isinstance(elements, list):
            grouped[side] = elements

    if not grouped:
        return None

    row_count = max((len(elements) for elements in grouped.values()), default=0)
    if row_count == 0:
        return None

    flat_items: List[Dict[str, Any]] = []
    for row_idx in range(row_count):
        for side in ("left", "right"):
            elements = grouped.get(side, [])
            if row_idx >= len(elements):
                continue
            raw_element = elements[row_idx]
            shape, extras = _canonicalize_symmetry_shape_element(raw_element)
            cell: Dict[str, Any] = {
                "side": side,
                "shape": shape,
                "position": row_idx + 1,
            }
            if extras:
                for k, v in extras.items():
                    if k not in cell:
                        cell[k] = v
            if "?" in shape or shape == "":
                cell["question"] = True
            flat_items.append(cell)
    return flat_items


_PYTHON_DICT_SHAPE_FIELD_RE = re.compile(
    r"""['"](?P<field>name|label|value|size|orientation|color)['"]\s*:\s*['"](?P<val>[^'"]*)['"]""",
    re.IGNORECASE,
)


def _parse_python_dict_like_shape_str(
    text: str,
) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Si ``text`` ressemble à ``"{'name': 'cercle rouge', 'size': 'petit'}"`` (repr
    Python-like parfois persistée par l'ancien code), extrait ``name``/``label``/
    ``value`` comme shape plat et ``size``/``orientation``/``color`` en extras.

    Renvoie ``None`` si ce n'est pas une repr dict reconnaissable, pour rester
    fail-open sur les vraies chaînes de forme.
    """
    s = text.strip()
    if not (s.startswith("{") and s.endswith("}")):
        return None
    fields: Dict[str, str] = {}
    for m in _PYTHON_DICT_SHAPE_FIELD_RE.finditer(s):
        fields.setdefault(m.group("field").lower(), m.group("val").strip())
    if not fields:
        return None
    shape_text = fields.get("name") or fields.get("label") or fields.get("value") or ""
    if not shape_text:
        return None
    extras: Dict[str, Any] = {}
    for k in ("size", "orientation", "color"):
        v = fields.get(k)
        if v and v != "?":
            extras[k] = v
    return shape_text, extras


def _canonicalize_symmetry_shape_element(
    raw: Any,
) -> tuple:
    """
    Extrait un libellé de forme texte (`shape`) + métadonnées associées.

    Le LLM sort parfois ``shapes: [{"name": "cercle rouge", "size": "petit"}]``
    au lieu de chaînes plates. ``str(dict)`` produirait ``{'name': ...}`` avec
    guillemets simples côté front — inacceptable pour le renderer.
    """
    if raw is None:
        return ("", {})
    if isinstance(raw, str):
        parsed = _parse_python_dict_like_shape_str(raw)
        if parsed is not None:
            shape_text, extras = parsed
            if shape_text == "?":
                extras = dict(extras)
                extras["question"] = True
            return (shape_text, extras)
        return (raw.strip(), {})
    if isinstance(raw, dict):
        label_candidates = ("name", "label", "value", "shape")
        shape_text = ""
        for key in label_candidates:
            v = raw.get(key)
            if isinstance(v, str) and v.strip():
                shape_text = v.strip()
                break
        dict_extras: Dict[str, Any] = {}
        for meta in ("size", "orientation", "color"):
            mv = raw.get(meta)
            if isinstance(mv, str) and mv.strip():
                dict_extras[meta] = mv.strip()
        if raw.get("question") is True:
            dict_extras["question"] = True
        if not shape_text and raw.get("question") is True:
            shape_text = "?"
        return (shape_text, dict_extras)
    return (str(raw).strip(), {})


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

    if _upper_type(challenge_type) == "RIDDLE" and dr is not None and dr >= 4.0:
        errors.append(
            "RIDDLE : omettre choices pour difficulty_rating >= 4.0. "
            "À ce niveau, l'énigme doit se résoudre en production libre plutôt qu'en reconnaissance QCM."
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

        grouped_layout = (
            _flatten_grouped_symmetry_layout(layout)
            if isinstance(layout, list)
            else None
        )
        if grouped_layout is not None:
            layout = grouped_layout
            out["layout"] = grouped_layout

        # Detect row-based format: [{"row": N, "left": [...], "right": [...]}]
        # OpenAI sometimes generates this instead of the canonical flat format.
        # Convert to canonical: [{"side": "left"|"right", "shape": "..."[, "question": true]}]
        elif (
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
                for raw_shape in row_item.get("left") or []:
                    shape, extras = _canonicalize_symmetry_shape_element(raw_shape)
                    cell: Dict[str, Any] = {"side": "left", "shape": shape}
                    for k, v in extras.items():
                        cell.setdefault(k, v)
                    flat_items.append(cell)
                for raw_shape in row_item.get("right") or []:
                    shape, extras = _canonicalize_symmetry_shape_element(raw_shape)
                    cell = {"side": "right", "shape": shape}
                    for k, v in extras.items():
                        cell.setdefault(k, v)
                    if shape == "?" or shape == "":
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
                        normalized_side = _normalize_symmetry_side(cell.get("side"))
                        if normalized_side:
                            cell["side"] = normalized_side
                        elif _is_symmetry_axis_side(cell.get("side")):
                            continue
                        else:
                            cell["side"] = str(cell["side"]).lower().strip()
                    raw_shape = cell.get("shape")
                    if isinstance(raw_shape, dict):
                        shape_text, extras = _canonicalize_symmetry_shape_element(
                            raw_shape
                        )
                        cell["shape"] = shape_text
                        for k, v in extras.items():
                            cell.setdefault(k, v)
                        if (
                            shape_text == "?" or shape_text == ""
                        ) and "question" not in cell:
                            cell["question"] = True
                    elif isinstance(raw_shape, str):
                        # Répare les défis persistés avant le fix :
                        # ``shape`` y est stocké comme repr Python
                        # ``"{'name': 'cercle rouge', ...}"``.
                        parsed = _parse_python_dict_like_shape_str(raw_shape)
                        if parsed is not None:
                            shape_text, extras = parsed
                            cell["shape"] = shape_text
                            for k, v in extras.items():
                                cell.setdefault(k, v)
                            if (
                                shape_text == "?" or shape_text == ""
                            ) and "question" not in cell:
                                cell["question"] = True
                    elif raw_shape is not None:
                        cell["shape"] = str(raw_shape)
                    new_layout.append(cell)
                else:
                    new_layout.append(item)
            out["layout"] = new_layout

    return out


_CODING_ENCODED_MESSAGE_ALIASES = (
    "cipher_text",
    "ciphertext",
    "coded_message",
    "encrypted_message",
)
_CODING_PARTIAL_KEY_ROOT_FIELDS = (
    "keyword_length",
    "theme_clue",
    "mapping_known",
    "rule_type",
)

_CHESS_BOARD_PIECE_ALIASES: Dict[str, str] = {
    # Alias français fréquents produits par le LLM dans visual_data.board.
    # Le renderer et le validateur attendent la notation FEN anglaise.
    "D": "Q",
    "T": "R",
    "F": "B",
    "C": "N",
    "d": "q",
    "t": "r",
    "f": "b",
    "c": "n",
}
_CHESS_VALID_BOARD_PIECES = frozenset(
    {"K", "k", "Q", "q", "R", "r", "B", "b", "N", "n", "P", "p"}
)


def _normalize_chess_piece_token(raw_piece: Any) -> str:
    piece = str(raw_piece or "").strip()
    if piece in ("", ".", " "):
        return ""
    return _CHESS_BOARD_PIECE_ALIASES.get(piece, piece)


def _normalize_chess_board(
    board: Any, *, infer_missing_kings_from_rook_aliases: bool = False
) -> List[List[Any]]:
    if not isinstance(board, list):
        return []

    normalized: List[List[Any]] = []
    for raw_row in board:
        if not isinstance(raw_row, list):
            normalized.append([])
            continue
        row: List[Any] = []
        for raw_cell in raw_row:
            if isinstance(raw_cell, dict):
                cell = dict(raw_cell)
                if "piece" in cell:
                    cell["piece"] = _normalize_chess_piece_token(cell.get("piece"))
                row.append(cell)
            else:
                row.append(_normalize_chess_piece_token(raw_cell))
        normalized.append(row)

    if infer_missing_kings_from_rook_aliases:
        return _infer_missing_kings_from_french_rook_aliases(normalized)
    return normalized


def _infer_missing_kings_from_french_rook_aliases(
    board: List[List[Any]],
) -> List[List[Any]]:
    """
    Corrige un cas LLM courant en français : R/r utilisé pour roi au lieu de K/k.

    Si le roi attendu existe déjà, R/r reste une tour. Si aucun roi n'existe et
    qu'une seule tour de cette couleur est présente, la position était déjà invalide ;
    l'hypothèse la plus conservatrice pour un défi de mat est que la pièce désigne
    le roi dans la notation française.
    """
    king_count_by_piece: Dict[str, int] = {"K": 0, "k": 0}
    rook_positions_by_piece: Dict[str, List[Tuple[int, int]]] = {"R": [], "r": []}
    for row_index, row in enumerate(board):
        if not isinstance(row, list):
            continue
        for col_index, cell in enumerate(row):
            piece = cell.get("piece") if isinstance(cell, dict) else cell
            if piece in king_count_by_piece:
                king_count_by_piece[piece] += 1
            elif piece in rook_positions_by_piece:
                rook_positions_by_piece[piece].append((row_index, col_index))

    for rook_piece, king_piece in (("R", "K"), ("r", "k")):
        if (
            king_count_by_piece[king_piece] == 0
            and len(rook_positions_by_piece[rook_piece]) == 1
        ):
            row_index, col_index = rook_positions_by_piece[rook_piece][0]
            cell = board[row_index][col_index]
            if isinstance(cell, dict):
                cell["piece"] = king_piece
            else:
                board[row_index][col_index] = king_piece
    return board


def _normalize_chess_highlight_position(raw_position: Any) -> Optional[Tuple[int, int]]:
    if isinstance(raw_position, dict):
        raw_row = raw_position.get("row")
        raw_col = raw_position.get("col")
    elif isinstance(raw_position, (list, tuple)) and len(raw_position) >= 2:
        raw_row, raw_col = raw_position[0], raw_position[1]
    elif isinstance(raw_position, str) and len(raw_position.strip()) >= 2:
        text = raw_position.strip().lower()
        file_char, rank_char = text[0], text[1]
        if file_char < "a" or file_char > "h" or not rank_char.isdigit():
            return None
        raw_row = 8 - int(rank_char)
        raw_col = ord(file_char) - ord("a")
    else:
        return None

    try:
        row = int(raw_row)
        col = int(raw_col)
    except (TypeError, ValueError):
        return None
    if not (0 <= row <= 7 and 0 <= col <= 7):
        return None
    return row, col


def normalize_chess_visual_data(visual_data: Dict[str, Any]) -> Dict[str, Any]:
    """Canonicalise les symboles d'échecs pour le validateur et le renderer."""
    if not isinstance(visual_data, dict):
        return {}

    out = dict(visual_data)
    objective = str(out.get("objective", "")).strip().lower()
    board = _normalize_chess_board(
        out.get("board"),
        infer_missing_kings_from_rook_aliases=objective.startswith("mat_en_"),
    )
    if board:
        out["board"] = board

    raw_highlights = out.get("highlight_positions")
    if isinstance(raw_highlights, list) and board:
        normalized_highlights: List[Dict[str, int]] = []
        for raw_position in raw_highlights:
            coords = _normalize_chess_highlight_position(raw_position)
            if coords is None:
                continue
            row, col = coords
            normalized_highlights.append({"row": row, "col": col})
        out["highlight_positions"] = normalized_highlights

    return out


def normalize_coding_visual_data(visual_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forme canonique CODING pour prompt ↔ validateur ↔ CodingRenderer.

    Le contrat public est ``encoded_message``. Certains modèles produisent
    spontanément ``cipher_text`` ; on le canonicalise pour ne pas persister un
    défi impossible à résoudre visuellement.
    """
    if not isinstance(visual_data, dict):
        return {}

    out = dict(visual_data)
    if not out.get("encoded_message"):
        for alias in _CODING_ENCODED_MESSAGE_ALIASES:
            candidate = out.get(alias)
            if candidate is not None and str(candidate).strip():
                out["encoded_message"] = str(candidate)
                break

    for alias in _CODING_ENCODED_MESSAGE_ALIASES:
        out.pop(alias, None)

    if str(out.get("type", "")).strip().lower() == "substitution":
        partial_key = out.get("partial_key")
        canonical_partial_key = (
            dict(partial_key) if isinstance(partial_key, dict) else {}
        )
        for field in _CODING_PARTIAL_KEY_ROOT_FIELDS:
            if field not in canonical_partial_key and out.get(field) is not None:
                canonical_partial_key[field] = out[field]

        if canonical_partial_key:
            out["partial_key"] = canonical_partial_key
            if not out.get("rule_type") and canonical_partial_key.get("rule_type"):
                out["rule_type"] = canonical_partial_key["rule_type"]

        for field in ("keyword_length", "theme_clue", "mapping_known"):
            out.pop(field, None)

    return out


def apply_visual_contract_normalization(
    challenge_type: str, visual_data: Any
) -> Dict[str, Any]:
    """Normalisation légère par type avant validation IA."""
    if not isinstance(visual_data, dict):
        return {}

    vd = dict(visual_data)
    ct = _upper_type(challenge_type)

    if ct in ("VISUAL", "SPATIAL"):
        vd = normalize_symmetry_visual_data(vd)
    elif ct == "CODING":
        vd = normalize_coding_visual_data(vd)
    elif ct == "CHESS":
        vd = normalize_chess_visual_data(vd)

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
