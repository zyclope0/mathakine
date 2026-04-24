"""IA5 - difficulty, distractors, and deduction validator."""

from __future__ import annotations

from app.services.challenges.challenge_answer_quality import validate_challenge_choices
from app.services.challenges.challenge_difficulty_policy import (
    calibrate_challenge_difficulty,
    estimate_structure_signals,
    sanitize_leaky_title,
    title_suggests_rule_leak,
    validate_difficulty_structural_coherence,
    validate_title_difficulty_coherence,
)
from app.services.challenges.challenge_validator import (
    auto_correct_challenge,
    validate_challenge_logic,
    validate_deduction_challenge,
    validate_graph_challenge,
    validate_probability_challenge,
    validate_puzzle_challenge,
)


def test_title_suggests_rule_leak_detects_explicit_pattern() -> None:
    assert title_suggests_rule_leak("Le cycle x3 puis +1")
    assert title_suggests_rule_leak("Bits a l'envers !")
    assert title_suggests_rule_leak("Le nombre qui descend en rythme")
    assert not title_suggests_rule_leak("Le mystere des cases")


def test_sanitize_leaky_title_for_high_difficulty_coding() -> None:
    assert (
        sanitize_leaky_title("coding", "Bits a l'envers !", 4.0)
        == "Le message sous scellés"
    )


def test_sanitize_leaky_title_for_coding_even_when_rating_is_medium() -> None:
    assert (
        sanitize_leaky_title("coding", "Le cadenas César du professeur distrait", 3.0)
        == "Le message sous scellés"
    )


def test_sanitize_leaky_title_for_coding_keyword_in_title() -> None:
    assert (
        sanitize_leaky_title(
            "coding",
            "Cryptogramme « Galileo » : citation masquée",
            3.2,
            {
                "type": "substitution",
                "partial_key": {"keyword_length": 7},
            },
        )
        == "Le message sous scellés"
    )


def test_sanitize_leaky_title_for_coding_theme_clue_in_title() -> None:
    assert (
        sanitize_leaky_title(
            "coding",
            "Le message caché du triangle",
            4.0,
            {
                "type": "substitution",
                "encoded_message": "X",
                "partial_key": {
                    "keyword_length": 6,
                    "theme_clue": "triangle",
                    "mapping_known": {"T": "A"},
                },
            },
        )
        == "Le message sous scellés"
    )


def test_validate_title_difficulty_coherence_errors_when_high_rating() -> None:
    err = validate_title_difficulty_coherence("Suite x2 a chaque pas", 4.5)
    assert err and "titre" in err[0].lower()


def test_validate_difficulty_pattern_single_question_cell() -> None:
    vd = {"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]]}
    err = validate_difficulty_structural_coherence("PATTERN", vd, 4.2)
    assert err


def test_validate_difficulty_sequence_pattern_vs_rating() -> None:
    vd = {"sequence": [1, 2, 3], "pattern": "n+1"}
    err = validate_difficulty_structural_coherence("SEQUENCE", vd, 4.5)
    assert err


def test_validate_difficulty_sequence_short_single_unknown_vs_rating() -> None:
    vd = {"sequence": [3, 8, 19, 40, 75, "?"]}
    err = validate_difficulty_structural_coherence("SEQUENCE", vd, 4.0)
    assert err and "suite courte" in err[0].lower()


def test_validate_difficulty_sequence_simple_arithmetic_vs_rating() -> None:
    # Une suite arithmétique de 6 éléments avec une seule inconnue déclenche
    # légitimement DEUX contrôles : « suite courte » et « progression simple ».
    # L'ordre d'empilement n'est pas l'objet du test ; on valide que le contrôle
    # « arithmétique » fait bien partie des erreurs remontées.
    vd = {"sequence": [5, 10, 15, 20, 25, "?"]}
    err = validate_difficulty_structural_coherence("SEQUENCE", vd, 4.2)
    assert err and any("arithm" in e.lower() for e in err)


def test_validate_difficulty_coding_binary_short_payload_vs_rating() -> None:
    vd = {
        "type": "binary",
        "encoded_message": "10100010 10101010 01001010 10100010 11010010 10000010",
    }
    err = validate_difficulty_structural_coherence("CODING", vd, 4.0)
    assert err and "binary" in err[0].lower()


def test_validate_difficulty_coding_substitution_string_key_vs_rating() -> None:
    vd = {
        "type": "substitution",
        "encoded_message": "KGTCEKGTDLS DS TCE JGMBUGBE",
        "full_key": "GALIEOBCDFHJKMNPQRSTUVWXYZ",
    }

    err = validate_difficulty_structural_coherence("CODING", vd, 4.0)

    assert err and any("substitution" in e.lower() for e in err)


def test_validate_difficulty_riddle_direct_numeric_clues_vs_rating() -> None:
    vd = {
        "clues": [
            "Je suis divisible par 9.",
            "Le produit de mes trois chiffres vaut $2^3 \\times 3$.",
            "Mes chiffres forment une suite arithmetique decroissante.",
            "Mon chiffre des centaines est egal au nombre de lettres du mot math.",
        ],
        "key_elements": ["suite arithmetique", "divisibilite par 9", "produit"],
    }
    err = validate_difficulty_structural_coherence("RIDDLE", vd, 4.0)
    assert err and "riddle" in err[0].lower()


def test_validate_puzzle_rejects_numeric_ascending_sort_solution() -> None:
    vd = {"pieces": ["610", "144", "2584", "987", "377", "1597", "233"]}
    err = validate_puzzle_challenge(
        vd,
        "144, 233, 377, 610, 987, 1597, 2584",
        "Chaque terme est la somme des deux precedents.",
    )
    assert err and any("tri numerique" in e.lower() for e in err)


def test_validate_puzzle_allows_non_sort_numeric_order() -> None:
    vd = {"pieces": ["5", "2", "8", "3"], "description": "ordre par contrainte"}
    err = validate_puzzle_challenge(
        vd,
        "2, 3, 5, 8",
        "Les pieces suivent une contrainte additive.",
    )
    assert any("tri numerique" in e.lower() for e in err)

    non_sort_err = validate_puzzle_challenge(
        vd,
        "2, 5, 3, 8",
        "Les pieces suivent une contrainte additive.",
    )
    assert not any("tri numerique" in e.lower() for e in non_sort_err)


def test_validate_puzzle_accepts_pieces_with_id_field() -> None:
    """Contrat LLM fréquent : ``pieces: [{"id": "A", "pattern": [...]}]``.

    ``piece_label`` doit lire ``id`` et ne jamais sortir la repr Python
    du dict — sinon la validation bloque alors que correct_answer "A, B, C, ..."
    est parfaitement cohérent avec les pièces.
    """
    vd = {
        "pieces": [
            {"id": "A", "pattern": ["NW: rouge"]},
            {"id": "B", "pattern": ["NW: bleu", "NE: rouge"]},
            {"id": "C", "pattern": ["NW: rouge", "NE: rouge", "SW: rouge"]},
            {"id": "D", "pattern": ["NW: bleu", "NE: rouge", "SW: rouge", "SE: rouge"]},
            {"id": "E", "pattern": ["NW: rouge", "SW: rouge", "SE: rouge"]},
            {"id": "F", "pattern": ["NW: bleu", "SE: rouge"]},
        ],
        "hints": [
            "Compare le nombre de points rouges sur chaque tuile.",
            "Regarde la couleur du quadrant NW.",
            "Observe l'alternance rouge/bleu sur NW.",
        ],
    }
    errors = validate_puzzle_challenge(
        vd,
        "A, B, C, D, E, F",
        "On compte les points rouges sur A, B, C, D, E, F puis l'alternance NW.",
    )
    assert errors == []
    # Sanity : aucune repr Python dict ne doit apparaître dans les messages.
    for err in errors:
        assert "{'id'" not in err
        assert '{"id"' not in err


def test_validate_puzzle_matches_answer_on_stable_piece_ids_not_labels() -> None:
    vd = {
        "pieces": [
            {"id": "P1", "label": "paire 11-13"},
            {"id": "P2", "label": "paire 13-17"},
            {"id": "P3", "label": "paire 17-19"},
        ],
        "hints": [
            "Observe les ecarts entre les paires.",
            "La paire centrale touche les deux autres.",
        ],
    }

    errors = validate_puzzle_challenge(
        vd,
        "P1, P2, P3",
        "Les pieces 'paire 11-13', 'paire 13-17' et 'paire 17-19' s'ordonnent par chevauchement progressif.",
    )

    assert errors == []


def test_piece_label_ignores_non_label_dict_without_python_repr() -> None:
    from app.services.challenges.challenge_ordering_utils import piece_label

    assert piece_label({"id": "A", "pattern": ["x"]}) == "A"
    assert piece_label({"label": "Alpha"}) == "Alpha"
    assert piece_label({"value": 3}) == "3"
    # Dict sans clé label-compatible : fail-open chaîne vide, pas de repr Python.
    assert piece_label({"pattern": ["x"]}) == ""


def test_validate_challenge_choices_min_three_and_no_duplicates() -> None:
    assert not validate_challenge_choices("SEQUENCE", "10", None)
    assert validate_challenge_choices("SEQUENCE", "10", ["10", "11"])
    dup_err = validate_challenge_choices("SEQUENCE", "10", ["10", "10", "11"])
    assert dup_err and "doublon" in dup_err[0].lower()
    assert not validate_challenge_choices("SEQUENCE", "10", ["8", "9", "10", "11"])


def test_validate_challenge_choices_correct_must_match() -> None:
    assert validate_challenge_choices("PROBABILITY", "1/2", ["1/3", "1/4", "2/3"])


def test_validate_challenge_choices_rejects_equivalent_probability_options() -> None:
    err = validate_challenge_choices(
        "PROBABILITY",
        "10/27",
        ["5/18", "16/45", "10/27", "50/135"],
    )

    assert err and any("equivalentes" in e.lower() for e in err)


def test_validate_difficulty_probability_direct_urn_vs_high_rating() -> None:
    vd = {
        "urns": {
            "A": {"red": 5, "blue": 5},
            "B": {"red": 8, "blue": 2},
            "C": {"red": 1, "blue": 9},
        },
        "total_per_urn": 10,
        "urn_selection": "equiprobable",
        "draws_without_replacement": 2,
        "question": "Probabilite d'obtenir deux couleurs differentes.",
    }

    err = validate_difficulty_structural_coherence("PROBABILITY", vd, 4.4)

    assert err and any("tirage direct" in e.lower() for e in err)


def test_validate_difficulty_probability_direct_flat_draw_vs_high_rating() -> None:
    vd = {
        "red_marbles": 15,
        "blue_marbles": 10,
        "green_marbles": 5,
        "total_marbles": 30,
        "draws_without_replacement": 2,
        "question": "Probability that two marbles drawn without replacement are of different colors",
    }

    err = validate_difficulty_structural_coherence("PROBABILITY", vd, 4.0)

    assert err and any("tirage direct" in e.lower() for e in err)


def test_calibrate_probability_direct_flat_draw_caps_rating() -> None:
    rating, meta = calibrate_challenge_difficulty(
        challenge_type="probability",
        age_group="15-17",
        visual_data={
            "red_marbles": 15,
            "blue_marbles": 10,
            "green_marbles": 5,
            "total_marbles": 30,
            "draws_without_replacement": 2,
            "question": "probabilite que deux billes soient de couleurs differentes",
        },
        title="Tirages colores",
        ai_difficulty=4.0,
    )

    assert rating == 3.8
    assert "probability_direct_total_cap_3_8" in meta["caps_applied"]


def test_validate_probability_rejects_wrong_weighted_urn_answer() -> None:
    vd = {
        "box_A": {
            "red": 40,
            "blue": 60,
            "total": 100,
            "selection_probability": 0.7,
        },
        "box_B": {
            "red": 30,
            "blue": 20,
            "total": 50,
            "selection_probability": 0.3,
        },
        "draws": "2 marbles without replacement",
        "event": "two marbles of different colors",
    }

    err = validate_probability_challenge(vd, "48.67%", "")

    assert err and any("48.63%" in e for e in err)


def test_validate_probability_accepts_weighted_urn_answer_rounded_to_centième() -> None:
    vd = {
        "box_A": {
            "red": 40,
            "blue": 60,
            "total": 100,
            "selection_probability": 0.7,
        },
        "box_B": {
            "red": 30,
            "blue": 20,
            "total": 50,
            "selection_probability": 0.3,
        },
        "draws": "2 marbles without replacement",
        "event": "two marbles of different colors",
    }

    err = validate_probability_challenge(vd, "48.63%", "")

    assert not err


def _mst_graph_visual_data() -> dict:
    return {
        "nodes": ["A", "B", "C", "D", "E", "F", "G", "H"],
        "edges": [
            ["F", "G", 1],
            ["F", "D", 3],
            ["A", "B", 4],
            ["B", "C", 5],
            ["A", "C", 6],
            ["E", "F", 7],
            ["C", "D", 8],
            ["B", "E", 9],
            ["H", "E", 10],
            ["H", "G", 11],
            ["C", "F", 12],
            ["H", "F", 13],
            ["G", "D", 14],
            ["A", "D", 16],
        ],
        "objective": "minimum_spanning_tree",
    }


def test_validate_graph_challenge_accepts_minimum_spanning_tree_total() -> None:
    err = validate_graph_challenge(
        _mst_graph_visual_data(),
        "38",
        "On trie les arêtes par coût puis on évite les cycles.",
    )

    assert not err


def test_validate_graph_challenge_rejects_wrong_minimum_spanning_tree_total() -> None:
    err = validate_graph_challenge(
        _mst_graph_visual_data(),
        "36",
        "On trie les arêtes par coût puis on évite les cycles.",
    )

    assert err and any("Attendu 38" in e for e in err)


def _shortest_path_graph_visual_data() -> dict:
    return {
        "nodes": ["A", "B", "C", "D", "E", "F", "G"],
        "edges": [
            {"route": "A-B", "cost": 4},
            {"route": "A-C", "cost": 2},
            {"route": "B-C", "cost": 1},
            {"route": "B-D", "cost": 5},
            {"route": "C-G", "cost": 9},
            {"route": "C-D", "cost": 8},
            {"route": "C-E", "cost": 10},
            {"route": "D-E", "cost": 2},
            {"route": "D-F", "cost": 6},
            {"route": "E-F", "cost": 3},
            {"route": "E-G", "cost": 7},
            {"route": "F-G", "cost": 1},
        ],
        "objective": "shortest_path",
        "source": "A",
        "target": "G",
    }


def test_validate_graph_challenge_accepts_shortest_path_total() -> None:
    err = validate_graph_challenge(
        _shortest_path_graph_visual_data(),
        "11",
        "Le chemin minimal de A à G passe par C.",
    )

    assert not err


def test_validate_graph_challenge_rejects_wrong_shortest_path_total() -> None:
    err = validate_graph_challenge(
        _shortest_path_graph_visual_data(),
        "12",
        "Le chemin minimal de A à G passe par C.",
    )

    assert err and any("Attendu 11" in e for e in err)


def test_validate_deduction_challenge_happy_path() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["the", "cafe"],
        },
        "clues": ["Alice ne boit pas le cafe", "Bob aime le the"],
        "description": "test",
    }
    ca = "Alice:the,Bob:cafe"
    assert not validate_deduction_challenge(vd, ca, "explanation")


def test_validate_deduction_challenge_rejects_duplicate_secondary_category() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["the", "cafe"],
        },
        "clues": ["c1", "c2"],
        "description": "test",
    }
    err = validate_deduction_challenge(vd, "Alice:the,Bob:the", "")
    assert err and any("one-to-one" in e or "bijection" in e.lower() for e in err)


def test_validate_deduction_challenge_rejects_duplicate_tertiary_category() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {
            "personnes": ["Alice", "Bob"],
            "boisson": ["the", "cafe"],
            "ville": ["Paris", "Lyon"],
        },
        "clues": ["c1", "c2"],
        "description": "test",
    }
    err = validate_deduction_challenge(vd, "Alice:the:Paris,Bob:cafe:Paris", "")
    assert err and any("one-to-one" in e for e in err)


def test_validate_deduction_challenge_wrong_type() -> None:
    vd = {"type": "other", "entities": {"a": [1], "b": [2]}, "clues": ["x", "y"]}
    err = validate_deduction_challenge(vd, "1:2", "")
    assert any("logic_grid" in e for e in err)


def test_validate_deduction_challenge_bad_association_count() -> None:
    vd = {
        "type": "logic_grid",
        "entities": {"p": ["A", "B"], "x": [1, 2], "y": [3, 4]},
        "clues": ["c1", "c2"],
    }
    err = validate_deduction_challenge(vd, "A:1,B:2", "")
    assert err


def _terminal_schedule_deduction_data() -> dict:
    return {
        "type": "logic_grid",
        "entities": {
            "Étudiants": ["Camille", "Damien", "Lise", "Marc"],
            "Thèmes": [
                "Énergie solaire",
                "Robotique",
                "Cryptographie",
                "Intelligence artificielle",
            ],
            "Jours": ["Lundi", "Mardi", "Jeudi", "Vendredi"],
        },
        "clues": [
            "Le sujet de Cryptographie est programmé le Mardi.",
            "Camille présente exactement un créneau avant Lise "
            "(dans l'ordre Lundi → Mardi → Jeudi → Vendredi).",
            "Marc n'intervient ni le jour immédiatement avant ni le jour "
            "immédiatement après la Cryptographie.",
            "Le sujet d'Énergie solaire est programmé avant celui de Robotique "
            "dans la semaine.",
            "Damien ne travaille pas sur la Robotique.",
            "L'exposé sur l'Intelligence artificielle a lieu le même jour que "
            "l'intervention de Damien.",
        ],
    }


def test_validate_deduction_challenge_rejects_non_unique_schedule() -> None:
    vd = _terminal_schedule_deduction_data()
    ca = (
        "Camille:Énergie solaire:Lundi,"
        "Lise:Cryptographie:Mardi,"
        "Damien:Intelligence artificielle:Jeudi,"
        "Marc:Robotique:Vendredi"
    )

    err = validate_deduction_challenge(vd, ca, "explication")

    assert err and any("solution unique" in e.lower() for e in err)


def test_validate_deduction_challenge_accepts_discriminated_schedule() -> None:
    vd = _terminal_schedule_deduction_data()
    vd["clues"] = [*vd["clues"], "Damien présente après Lise."]
    ca = (
        "Camille:Énergie solaire:Lundi,"
        "Lise:Cryptographie:Mardi,"
        "Damien:Intelligence artificielle:Jeudi,"
        "Marc:Robotique:Vendredi"
    )

    assert not validate_deduction_challenge(vd, ca, "explication")


def test_validate_deduction_challenge_rejects_wrong_answer_for_unique_schedule() -> (
    None
):
    vd = _terminal_schedule_deduction_data()
    vd["clues"] = [*vd["clues"], "Damien présente après Lise."]
    wrong = (
        "Camille:Énergie solaire:Lundi,"
        "Lise:Cryptographie:Mardi,"
        "Damien:Robotique:Jeudi,"
        "Marc:Intelligence artificielle:Vendredi"
    )

    err = validate_deduction_challenge(vd, wrong, "explication")

    assert err and any("correct_answer" in e for e in err)


def test_validate_challenge_logic_runs_deduction_validator() -> None:
    data = {
        "challenge_type": "DEDUCTION",
        "title": "Grille",
        "difficulty_rating": 3.0,
        "correct_answer": "A:1",
        "solution_explanation": "ok",
        "visual_data": {
            "type": "logic_grid",
            "entities": {"p": ["A", "B"], "x": [1, 2]},
            "clues": ["c1", "c2"],
        },
    }
    ok, errors = validate_challenge_logic(data)
    assert not ok
    assert any("DEDUCTION" in e for e in errors)


def test_calibrate_challenge_difficulty_caps_on_title_leak() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="sequence",
        age_group="9-11",
        visual_data={"sequence": [1, 2, 3]},
        title="La suite x2 magique",
        ai_difficulty=3.2,
    )
    assert final <= 3.0
    assert "title_rule_leak_cap_3_0" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_caps_short_binary_coding() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="coding",
        age_group="15-17",
        visual_data={
            "type": "binary",
            "encoded_message": "10100010 10101010 01001010 10100010 11010010 10000010",
        },
        title="Le mot du laboratoire",
        ai_difficulty=4.0,
    )
    assert final <= 3.2
    assert "coding_binary_short_payload_cap_3_2" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_caps_string_full_key_coding() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="coding",
        age_group="15-17",
        visual_data={
            "type": "substitution",
            "encoded_message": "KGTCEKGTDLS DS TCE JGMBUGBE",
            "full_key": "GALIEOBCDFHJKMNPQRSTUVWXYZ",
        },
        title="Le message sous scellés",
        ai_difficulty=4.3,
    )

    assert final <= 3.2
    assert "coding_substitution_full_key_cap_3_2" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_caps_keyword_quoted_in_title() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="coding",
        age_group="15-17",
        visual_data={
            "type": "substitution",
            "encoded_message": "HMNWJEIBE DS PNWER AUT",
            "partial_key": {
                "keyword_length": 7,
                "theme_clue": "astronomer",
                "mapping_known": {"G": "A", "A": "B"},
                "rule_type": "keyword",
            },
        },
        title="Cryptogramme « Galileo » : citation masquée",
        ai_difficulty=4.3,
    )

    assert final <= 3.2
    assert "coding_keyword_in_title_cap_3_2" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_raises_complex_pattern_floor() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="pattern",
        age_group="9-11",
        visual_data={
            "grid": [
                ["A", "B", "C", "D", "E"],
                ["B", "C", "D", "E", "?"],
                ["C", "D", "E", "?", "?"],
                ["D", "E", "?", "B", "C"],
                ["?", "?", "B", "C", "D"],
            ],
            "size": 5,
        },
        title="Le motif caché",
        ai_difficulty=2.6,
    )
    assert final == 4.0
    assert "pattern_large_multi_unknown_floor_4_0" in meta.get("floors_applied", [])


def test_calibrate_challenge_difficulty_raises_long_sequence_floor() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="sequence",
        age_group="9-11",
        visual_data={"sequence": [3, 4, 8, 12, 36, 45, "?", "?"]},
        title="La suite cachée",
        ai_difficulty=2.6,
    )
    assert final == 4.0
    assert "sequence_long_multi_unknown_floor_4_0" in meta.get("floors_applied", [])


def test_calibrate_challenge_difficulty_does_not_floor_deduction() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="deduction",
        age_group="9-11",
        visual_data={
            "type": "logic_grid",
            "entities": {
                "personnes": ["A", "B", "C", "D"],
                "villes": ["Lyon", "Paris", "Rome", "Oslo"],
                "metiers": ["Pilote", "Chef", "Juge", "Mage"],
                "objets": ["Cle", "Carte", "Livre", "Bague"],
            },
            "clues": ["c1", "c2", "c3", "c4", "c5", "c6"],
        },
        title="Les indices croisés",
        ai_difficulty=2.6,
    )
    assert final == 2.6
    assert meta.get("floors_applied") == []


def test_calibrate_challenge_difficulty_title_cap_overrides_structure_floor() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="pattern",
        age_group="9-11",
        visual_data={
            "grid": [
                ["A", "B", "C", "D", "E"],
                ["B", "C", "D", "E", "?"],
                ["C", "D", "E", "?", "?"],
                ["D", "E", "?", "B", "C"],
                ["?", "?", "B", "C", "D"],
            ],
            "size": 5,
        },
        title="Décalage cyclique caché",
        ai_difficulty=2.6,
    )
    assert final == 3.0
    assert "pattern_large_multi_unknown_floor_4_0" in meta.get("floors_applied", [])
    assert "title_rule_leak_cap_3_0" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_caps_direct_numeric_riddle() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="riddle",
        age_group="15-17",
        visual_data={
            "clues": [
                "Je suis divisible par 9.",
                "Le produit de mes trois chiffres vaut $2^3 \\times 3$.",
                "Mes chiffres forment une suite arithmetique decroissante.",
                "Mon chiffre des centaines est egal au nombre de lettres du mot math.",
            ],
            "key_elements": ["suite arithmetique", "divisibilite par 9", "produit"],
        },
        title="Le nombre cache",
        ai_difficulty=4.0,
    )
    assert final == 3.0
    assert "riddle_direct_numeric_clues_cap_3_0" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_caps_coding_theme_clue_unquoted_in_title() -> (
    None
):
    final, meta = calibrate_challenge_difficulty(
        challenge_type="coding",
        age_group="15-17",
        visual_data={
            "type": "substitution",
            "encoded_message": "IT BEMJERPDE KMUQ PEKQEDBKE QUP I UKDVEPQ",
            "partial_key": {
                "keyword_length": 6,
                "theme_clue": "triangle",
                "mapping_known": {"T": "A", "P": "R"},
                "rule_type": "keyword",
            },
        },
        title="Le message caché du triangle",
        ai_difficulty=4.0,
    )
    assert final <= 3.2
    assert "coding_theme_clue_in_title_cap_3_2" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_ignores_theme_clue_when_not_in_title() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="coding",
        age_group="15-17",
        visual_data={
            "type": "substitution",
            "encoded_message": "IT BEMJERPDE KMUQ",
            "partial_key": {
                "keyword_length": 6,
                "theme_clue": "triangle",
                "mapping_known": {"T": "A"},
                "rule_type": "keyword",
            },
        },
        title="Le manuscrit oublié",
        ai_difficulty=4.0,
    )
    assert "coding_theme_clue_in_title_cap_3_2" not in meta.get("caps_applied", [])
    assert final >= 3.3


def test_calibrate_challenge_difficulty_caps_magic_square_riddle() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="riddle",
        age_group="15-17",
        visual_data={
            "description": (
                "Chaque ligne, chaque colonne et chacune des deux diagonales "
                "vérifient une même somme constante."
            ),
            "clues": [
                "La somme des trois nombres de la première ligne est 8 + 1 + 6.",
                "La somme des trois nombres de la troisième colonne est identique "
                "à celle de la première ligne.",
                "La diagonale principale part du coin supérieur gauche.",
                "La diagonale secondaire part du coin supérieur droit.",
                "La somme constante est égale à celle de la première ligne.",
            ],
            "key_elements": [
                "Propriété de somme constante (magie du carré)",
                "Somme à trouver",
                "Emplacement (2,2) à calculer",
            ],
            "grid": [["8", "1", "6"], ["3", "?", "7"], ["4", "9", "2"]],
        },
        title="Le carré aux sommes cachées",
        ai_difficulty=4.0,
    )
    assert final == 3.0
    assert "riddle_magic_square_explicit_cap_3_0" in meta.get("caps_applied", [])


def test_calibrate_challenge_difficulty_caps_direct_urn_probability() -> None:
    final, meta = calibrate_challenge_difficulty(
        challenge_type="probability",
        age_group="adulte",
        visual_data={
            "urns": {
                "A": {"red": 5, "blue": 5},
                "B": {"red": 8, "blue": 2},
                "C": {"red": 1, "blue": 9},
            },
            "total_per_urn": 10,
            "urn_selection": "equiprobable",
            "draws_without_replacement": 2,
            "question": "Probabilite d'obtenir deux couleurs differentes.",
        },
        title="Le tirage incertain",
        ai_difficulty=4.4,
    )

    assert final == 3.8
    assert "probability_direct_total_cap_3_8" in meta.get("caps_applied", [])


def test_estimate_structure_signals_includes_rule_visibility() -> None:
    sig = estimate_structure_signals(
        "sequence",
        {"sequence": [1, 2, 3], "pattern": "n+1"},
        "Sans indice",
    )
    assert sig.rule_visibility == "partial"


def test_auto_correct_challenge_sanitizes_leaky_high_difficulty_title() -> None:
    corrected = auto_correct_challenge(
        {
            "challenge_type": "CODING",
            "title": "Bits a l'envers !",
            "difficulty_rating": 4.0,
            "visual_data": {
                "type": "binary",
                "encoded_message": "10100010 10101010 01001010 10100010 11010010 10000010",
            },
        }
    )
    assert corrected["title"] == "Le message sous scellés"
