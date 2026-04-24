"""Lot M étape 1 — contrat d'affichage unifié backend.

``item_label`` doit refuser de produire :
- une repr Python ``"{'id': 'A', ...}"``
- la chaîne ``"[object Object]"`` (pas prod par Python mais on garantit que
  le helper ne laisse passer aucune repr bruyante).

Fail-open ``""`` quand aucun champ reconnu ; l'appelant décide du fallback.
"""

from __future__ import annotations

import pytest

from app.services.challenges.challenge_ordering_utils import (
    DEFAULT_ITEM_LABEL_FIELDS,
    _parse_python_dict_like_label_str,
    item_label,
    parse_numeric_order,
    piece_label,
    piece_order_key,
)


def test_item_label_plain_string_trimmed() -> None:
    assert item_label("  cercle rouge  ") == "cercle rouge"


def test_item_label_dict_label_priority() -> None:
    assert item_label({"label": "Alpha", "id": "A"}) == "Alpha"


def test_item_label_dict_id_fallback() -> None:
    # Contrat LLM puzzle (cas défi 4070-bis) : {id, left, right}.
    assert item_label({"id": "P1", "left": "11", "right": "13"}) == "P1"


def test_item_label_dict_numeric_value() -> None:
    assert item_label({"value": 42}) == "42"


def test_item_label_numeric_direct() -> None:
    assert item_label(7) == "7"
    assert item_label(3.14) == "3.14"


def test_item_label_bool_ignored() -> None:
    assert item_label(True) == ""
    assert item_label(False, fallback="nope") == "nope"


def test_item_label_none_fallback() -> None:
    assert item_label(None) == ""
    assert item_label(None, fallback="#1") == "#1"


def test_item_label_unknown_dict_never_leaks_python_repr() -> None:
    raw = {"pattern": ["x"], "payload": 1}
    out = item_label(raw)
    assert out == ""
    assert "{'pattern'" not in out


def test_item_label_python_dict_like_string_reparsed() -> None:
    assert item_label("{'name': 'cercle rouge', 'size': 'petit'}") == "cercle rouge"
    assert item_label('{"id": "P1", "left": "11"}') == "P1"


def test_item_label_does_not_reparse_real_strings() -> None:
    # Fail-open : ne touche pas les vraies chaînes de forme.
    assert item_label("cercle rouge") == "cercle rouge"
    assert item_label("no brace text") == "no brace text"


def test_item_label_fields_override_priority() -> None:
    raw = {"token": "T1", "id": "fallback"}
    assert item_label(raw, fields=("token", "id")) == "T1"
    # Sans override : ``token`` n'est pas dans la liste officielle → id gagne.
    assert item_label(raw) == "fallback"


def test_item_label_array_returns_fallback_not_repr() -> None:
    # Pas de ``str([1, 2, 3])`` silencieux.
    assert item_label([1, 2, 3]) == ""


def test_parse_python_dict_like_label_str_fail_open_on_regular_strings() -> None:
    assert _parse_python_dict_like_label_str("cercle rouge") is None
    assert _parse_python_dict_like_label_str("") is None
    assert _parse_python_dict_like_label_str("{pas un dict}") is None


def test_default_field_order_matches_contract() -> None:
    # Source de vérité lue par le frontend — verrouiller l'ordre évite les
    # divergences silencieuses entre back et front.
    assert DEFAULT_ITEM_LABEL_FIELDS == (
        "label",
        "value",
        "name",
        "text",
        "description",
        "id",
        "piece_id",
        "tag",
    )


def test_piece_label_delegates_to_item_label_with_puzzle_fields() -> None:
    assert piece_label({"id": "A"}) == "A"
    assert piece_label("Alpha") == "Alpha"
    assert piece_label({"label": "Beta", "id": "Z"}) == "Beta"
    assert piece_label({"pattern": ["x"]}) == ""


def test_piece_order_key_prefers_stable_ids_over_editorial_labels() -> None:
    assert piece_order_key({"label": "paire 11↔13", "id": "P1"}) == "P1"
    assert piece_order_key({"piece_id": "P2", "name": "tuile 2"}) == "P2"
    assert piece_order_key({"label": "Beta"}) == "Beta"


def test_parse_numeric_order_unchanged_by_refactor() -> None:
    # Sanity check : le refactor n'a rien cassé côté API publique existante.
    assert parse_numeric_order(["1", "2", "3"]) == [1.0, 2.0, 3.0]
    assert parse_numeric_order(["1", "abc"]) is None


@pytest.mark.parametrize(
    "raw,expected",
    [
        ({"id": "X"}, "X"),
        ({"name": "Y"}, "Y"),
        ({"text": "Z"}, "Z"),
        ({"description": "D"}, "D"),
        ({"piece_id": "PID"}, "PID"),
        ({"tag": "T"}, "T"),
    ],
)
def test_item_label_reads_all_official_fields(raw: dict, expected: str) -> None:
    assert item_label(raw) == expected
