"""
Helpers pour la génération d'exercices : choix de réponses et questions contextualisées.

Extrait de exercise_generator.py (PR découpage #2) — fonctions pures pour MCQ et templates.
"""
import random

from app.core.constants import DifficultyLevels
from server.exercise_generator_validators import get_difficulty_from_age_group


def generate_smart_choices(
    operation_type: str, num1: int, num2: int, correct_result: int, age_group_or_difficulty: str
) -> list[str]:
    """Génère des choix de réponses avec des erreurs typiques selon l'opération."""
    choices = [str(correct_result)]

    op = operation_type.upper()
    if op == "ADDITION":
        choices.extend([
            str(correct_result + random.randint(1, 3)),
            str(correct_result - random.randint(1, 2)),
            str(num1 * num2) if num1 * num2 != correct_result else str(correct_result + 5),
        ])
    elif op == "SUBTRACTION":
        choices.extend([
            str(num2 - num1) if num2 != num1 else str(correct_result + 3),
            str(correct_result + random.randint(1, 3)),
            str(num1 + num2) if num1 + num2 != correct_result else str(correct_result - 2),
        ])
    elif op == "MULTIPLICATION":
        choices.extend([
            str(num1 + num2),
            str(correct_result + num1),
            str(max(1, correct_result - num2)),
        ])
    elif op == "DIVISION":
        choices.extend([
            str(correct_result + 1),
            str(max(1, correct_result - 1)),
            str(num1 - num2) if num1 > num2 else str(correct_result + 2),
        ])

    derived = get_difficulty_from_age_group(age_group_or_difficulty)
    if derived in [DifficultyLevels.CHEVALIER, DifficultyLevels.MAITRE]:
        margin = max(1, int(correct_result * 0.1))
        if len(choices) > 1:
            choices[1] = str(correct_result + margin)
        if len(choices) > 2:
            choices[2] = str(max(1, correct_result - margin))

    unique = []
    for c in choices:
        try:
            if c not in unique and int(c) > 0:
                unique.append(c)
        except (ValueError, TypeError):
            pass

    while len(unique) < 4:
        new = str(correct_result + random.randint(-3, 5))
        if new not in unique:
            try:
                if int(new) > 0:
                    unique.append(new)
            except (ValueError, TypeError):
                pass

    random.shuffle(unique)
    return unique[:4]


def generate_contextual_question(
    operation_type: str, num1: int, num2: int, result: int, age_group: str
) -> str:
    """Génère une question contextualisée selon le type d'opération et le groupe d'âge."""
    from app.core.messages import StarWarsNarratives

    contexts = StarWarsNarratives.CONTEXTS_BY_TYPE.get(operation_type.upper(), {})

    if not contexts:
        fallbacks = {
            "ADDITION": f"Calcule {num1} + {num2}",
            "SUBTRACTION": f"Calcule {num1} - {num2}",
            "MULTIPLICATION": f"Calcule {num1} × {num2}",
            "DIVISION": f"Calcule {num1} ÷ {num2}",
        }
        return fallbacks.get(operation_type.upper(), f"Calcule {num1} {operation_type.lower()} {num2}")

    objects = contexts.get("objects", ["éléments"])
    actions = contexts.get("actions", ["se combinent"])
    locations = contexts.get("locations", ["dans la galaxie"])

    obj = random.choice(objects)
    action = random.choice(actions)
    location = random.choice(locations)

    derived = get_difficulty_from_age_group(age_group)
    templates = []

    op = operation_type.upper()
    if op == "ADDITION":
        if derived == DifficultyLevels.INITIE:
            templates = [
                f"Dans {location}, tu trouves {num1} {obj} et ton ami en trouve {num2}. Combien en avez-vous ensemble?",
                f"R2-D2 compte {num1} {obj} et C-3PO en compte {num2}. Quel est le total?",
                f"Luke a {num1} {obj} et Leia en a {num2}. Combien ont-ils au total?",
            ]
        else:
            templates = [
                f"Dans {location}, {num1} {obj} {action} avec {num2} autres. Quel est le total?",
                f"L'Alliance déploie {num1} {obj} qui {action} avec {num2} renforts. Combien au total?",
                f"Sur {location}, {num1} {obj} {action} et {num2} autres arrivent. Total?",
            ]
    elif op == "SUBTRACTION":
        if derived == DifficultyLevels.INITIE:
            templates = [
                f"Tu avais {num1} {obj}, mais {num2} {action}. Combien te reste-t-il?",
                f"Dans {location}, il y avait {num1} {obj}, mais {num2} {action}. Combien restent?",
                f"Yoda possédait {num1} {obj}, mais {num2} {action}. Combien lui reste-t-il?",
            ]
        else:
            templates = [
                f"L'Empire avait {num1} {obj}, mais {num2} {action} lors de {location}. Combien restent?",
                f"Dans {location}, {num1} {obj} étaient présents, mais {num2} {action}. Reste?",
                f"La flotte comptait {num1} {obj}, mais {num2} {action} pendant {location}. Combien survivent?",
            ]
    elif op == "MULTIPLICATION":
        if derived == DifficultyLevels.INITIE:
            templates = [
                f"Chaque Padawan a {num2} {obj}. S'il y a {num1} Padawans, combien de {obj} au total?",
                f"Dans chaque {location}, il y a {num2} {obj}. Combien dans {num1} {location}?",
                f"Chaque droïde transporte {num2} {obj}. Combien pour {num1} droïdes?",
            ]
        else:
            templates = [
                f"Chaque {location} déploie {num2} {obj}. Combien pour {num1} {location}?",
                f"Dans {location}, chaque unité a {num2} {obj}. Total pour {num1} unités?",
                f"L'Empire organise {num1} {location} avec {num2} {obj} chacun. Combien au total?",
            ]
    elif op == "DIVISION":
        if derived == DifficultyLevels.INITIE:
            templates = [
                f"Tu as {num1} {obj} à distribuer entre {num2} Padawans. Combien chacun en aura?",
                f"Il faut répartir {num1} {obj} dans {num2} {location}. Combien par {location}?",
                f"Yoda doit partager {num1} {obj} entre {num2} élèves. Combien chacun?",
            ]
        else:
            templates = [
                f"L'Alliance doit répartir {num1} {obj} dans {num2} {location}. Combien par {location}?",
                f"Un convoi de {num1} {obj} doit être distribué sur {num2} {location}. Combien par site?",
                f"L'Empire divise {num1} {obj} entre {num2} {location}. Répartition par zone?",
            ]

    return random.choice(templates) if templates else f"Calcule {num1} {operation_type.lower()} {num2}"
