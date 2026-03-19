"""
Validation métier pour les challenges de type CODING (cryptographie / labyrinthe).

Extrait de challenge_validator (I5) pour réduire la densité du fichier principal
et isoler les règles de cohérence type CODING vs SEQUENCE/VISUAL/PUZZLE.
"""

from typing import Any, Dict, List

from app.services.challenges.maze_validator import validate_maze_path


def validate_coding_challenge(
    visual_data: Dict[str, Any], correct_answer: str, explanation: str
) -> List[str]:
    """
    Valide un challenge de type CODING.
    REJETTE les défis qui ne sont pas de vraie cryptographie.
    """
    errors: List[str] = []

    if not visual_data:
        errors.append(
            "CODING: visual_data est vide - un défi de cryptographie doit avoir des données"
        )
        return errors

    # Types valides pour CODING (cryptographie)
    valid_coding_types = [
        "caesar",
        "substitution",
        "binary",
        "symbols",
        "algorithm",
        "maze",
    ]
    coding_type = visual_data.get("type", "").lower()

    # Détecter si c'est un labyrinthe (même sans "type" explicite)
    maze = (
        visual_data.get("maze")
        or visual_data.get("grid")
        or visual_data.get("labyrinth")
    )
    start = visual_data.get("start") or visual_data.get("start_position")
    end = (
        visual_data.get("end")
        or visual_data.get("end_position")
        or visual_data.get("goal")
    )
    is_maze = maze and start and end

    # Détecter si c'est une SÉQUENCE ou un FAUX LABYRINTHE (INVALIDE pour CODING)
    has_sequence = visual_data.get("sequence") is not None
    has_pattern = visual_data.get("pattern") and not visual_data.get("encoded_message")
    has_shapes = visual_data.get("shapes") is not None

    # Détecter les "labyrinthes de nombres" - CE N'EST PAS DE LA CRYPTOGRAPHIE !
    has_numbers = visual_data.get("numbers") is not None
    has_target = visual_data.get("target") is not None
    has_movement_options = (
        visual_data.get("movement_options") is not None
        or visual_data.get("movement") is not None
    )
    is_fake_number_maze = has_numbers and (has_target or has_movement_options)

    # Rejeter les séquences, patterns, et faux labyrinthes
    if has_sequence:
        errors.append(
            "CODING INVALIDE: 'sequence' détectée - utiliser le type SEQUENCE, pas CODING"
        )
        return errors

    if has_pattern and not is_maze:
        errors.append(
            "CODING INVALIDE: 'pattern' sans cryptographie - utiliser le type PATTERN, pas CODING"
        )
        return errors

    if has_shapes:
        errors.append(
            "CODING INVALIDE: 'shapes' détectées - utiliser le type VISUAL, pas CODING"
        )
        return errors

    if is_fake_number_maze:
        errors.append(
            "CODING INVALIDE: 'numbers' + 'target' détectés - c'est un labyrinthe de nombres, "
            "pas de la cryptographie ! Utiliser le type SEQUENCE ou PUZZLE, pas CODING."
        )
        return errors

    # Rejeter aussi les défis avec uniquement des nombres et pas de message encodé
    if (
        has_numbers
        and not visual_data.get("encoded_message")
        and not visual_data.get("message")
    ):
        errors.append(
            "CODING INVALIDE: 'numbers' sans 'encoded_message' - CODING doit avoir un message secret à décoder, "
            "pas une liste de nombres."
        )
        return errors

    # Vérifier le type ou la présence d'éléments de cryptographie
    has_encoded_message = visual_data.get("encoded_message") or visual_data.get(
        "message"
    )
    has_crypto_key = (
        visual_data.get("key")
        or visual_data.get("partial_key")
        or visual_data.get("shift")
    )
    has_steps = visual_data.get("steps") and isinstance(visual_data.get("steps"), list)

    is_valid_crypto = (
        coding_type in valid_coding_types
        or is_maze
        or has_encoded_message
        or (has_crypto_key and has_encoded_message)
        or has_steps
    )

    if not is_valid_crypto:
        errors.append(
            f"CODING INVALIDE: Le visual_data ne contient pas de cryptographie valide. "
            f"Attendu: type={valid_coding_types}, encoded_message, key/shift, ou maze. "
            f"Reçu: {list(visual_data.keys())}"
        )

    # Si c'est un labyrinthe, valider le chemin
    if is_maze:
        if not validate_maze_path(maze, start, end, correct_answer):
            errors.append(
                f"MAZE: Le chemin '{correct_answer}' ne mène pas du départ {start} à l'arrivée {end}"
            )

    # Substitution : clé complète OU partial_key avec règle déductible (caesar, atbash, keyword)
    if coding_type == "substitution" and has_encoded_message:
        msg = (
            visual_data.get("encoded_message") or visual_data.get("message") or ""
        ).upper()
        decode_key = visual_data.get("key") or visual_data.get("partial_key") or {}
        rule_type = (
            visual_data.get("rule_type") or visual_data.get("deducible_rule") or ""
        ).lower()
        letters_in_msg = set(c for c in msg if c.isalpha())
        keys_upper = set(k.upper() for k in decode_key.keys())
        missing = letters_in_msg - keys_upper
        # Si règle déductible (César, Atbash, clé-mot), partial_key avec 3+ exemples suffit
        is_deducible = rule_type in (
            "caesar",
            "cesar",
            "atbash",
            "reverse",
            "keyword",
            "cle-mot",
        )
        if is_deducible:
            if len(decode_key) < 2:
                errors.append(
                    "SUBSTITUTION: Avec rule_type déductible, fournir au moins 2-3 exemples dans partial_key."
                )
        elif missing:
            errors.append(
                f"SUBSTITUTION INVALIDE: La clé ne couvre pas toutes les lettres du message ({sorted(missing)}). "
                "Fournir une clé complète OU rule_type (caesar/atbash/keyword) avec partial_key déductible."
            )
    return errors
