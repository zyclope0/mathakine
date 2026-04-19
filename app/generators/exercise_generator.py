"""
Module de génération d'exercices pour enhanced_server.py
"""

import random

from app.core.constants import DifficultyLevels, ExerciseTypes, Messages, Tags
from app.core.logging_config import get_logger
from app.core.messages import ExerciseMessages, SpatialNarratives
from app.generators.exercise_generation_policy import (
    SIMPLE_TITLE_ADDITION,
    SIMPLE_TITLE_DIVERS,
    SIMPLE_TITLE_DIVISION,
    SIMPLE_TITLE_FRACTIONS,
    SIMPLE_TITLE_GEOMETRIE,
    SIMPLE_TITLE_MIXTE,
    SIMPLE_TITLE_MULTIPLICATION,
    SIMPLE_TITLE_SUBTRACTION,
    SIMPLE_TITLE_TEXTE,
    pick_title_variant,
)
from app.utils.exercise_generator_helpers import (
    apply_test_title,
    build_base_exercise_data,
    default_addition_fallback,
    ensure_four_distinct_str_choices,
    generate_smart_choices,
    init_exercise_context,
)
from app.utils.exercise_generator_validators import (
    normalize_and_validate_exercise_params,
)

logger = get_logger(__name__)


def _ai_prefix() -> str:
    """Préfixe optionnel pour titres/explications (vide = pas d'affichage utilisateur)."""
    p = Messages.AI_EXERCISE_PREFIX
    return f"[{p}] " if p else ""


# Fonctions de génération d'exercices
def generate_ai_exercise(
    exercise_type,
    age_group,
    *,
    difficulty_override=None,
    pedagogical_band_override=None,
):
    """
    Génère un exercice avec thème spatial neutre et calibrage F42.
    Le profil F42 (difficulty_tier, pedagogical_band, calibration_desc) est
    calculé avant la génération et influence le calibrage des bornes.

    ``pedagogical_band_override`` (keyword-only): quand fourni par
    :func:`exercise_generation_service.generate_exercise_sync`, il injecte la
    bande résolue depuis les données de maîtrise (second axe F42) plutôt que
    de la dériver depuis ``derived_difficulty``.
    """
    (
        normalized_type,
        normalized_age_group,
        derived_difficulty,
        type_limits,
        f42_profile,
    ) = init_exercise_context(
        exercise_type,
        age_group,
        difficulty_override=difficulty_override,
        pedagogical_band_override=pedagogical_band_override,
    )
    exercise_data = build_base_exercise_data(
        normalized_type, normalized_age_group, derived_difficulty, ai_generated=True
    )
    # Store F42 profile in the exercise dict so it survives to persistance helpers.
    exercise_data["difficulty_tier"] = f42_profile["difficulty_tier"]

    explanation_prefix = SpatialNarratives.get_explanation_prefix(derived_difficulty)
    explanation_suffix = SpatialNarratives.get_explanation_suffix(derived_difficulty)

    if normalized_type == ExerciseTypes.ADDITION:
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)

        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)
        result = num1 + num2

        if derived_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice(
                [
                    f"Tu as trouvé {num1} cristaux sur la planète et ton équipier en a trouvé {num2}. Combien avez-vous de cristaux au total ?",
                    f"Il y a {num1} robots dans le hangar et {num2} robots dans l'atelier. Combien y a-t-il de robots en tout ?",
                    f"Tu as parcouru {num1} kilomètres hier et {num2} kilomètres aujourd'hui. Quelle distance as-tu parcourue en tout ?",
                ]
            )
            explanation_template = f"Pour trouver la réponse, tu dois additionner {num1} et {num2}, ce qui donne {result}."
        else:
            question_template = random.choice(
                [
                    f"Une escadre de {num1} vaisseaux et une flottille de {num2} navettes se préparent pour la mission. Combien de vaisseaux y a-t-il au total ?",
                    f"La base Alpha a reçu {num1} caisses de ravitaillement et la base Bêta en a reçu {num2}. Combien de caisses au total ?",
                    f"Un cargo spatial contient {num1} conteneurs et {num2} modules. Combien d'éléments sont à bord au total ?",
                ]
            )
            explanation_template = f"Pour calculer le total, on additionne les deux nombres : {num1} + {num2} = {result}."

        choices = generate_smart_choices(
            "ADDITION",
            num1,
            num2,
            result,
            normalized_age_group,
            derived_difficulty=derived_difficulty,
        )

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Mission spatiale - Addition pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "num1": num1,
                "num2": num2,
                "explanation": f"{_ai_prefix()}{explanation_prefix} {explanation_template} {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.SUBTRACTION:
        # Paramètres pour la soustraction avec des limites adaptatives
        min1 = type_limits.get("min1", 5)
        max1 = type_limits.get("max1", 20)
        min2 = type_limits.get("min2", 1)
        max2 = type_limits.get("max2", 5)

        num1 = random.randint(min1, max1)
        num2 = random.randint(
            min2, min(num1 - 1, max2)
        )  # Eviter les soustractions avec résultat négatif
        result = num1 - num2

        if derived_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice(
                [
                    f"Tu as {num1} rations de voyage, mais tu en as utilisé {num2}. Combien te reste-t-il ?",
                    f"Il y avait {num1} robots dans le hangar, mais {num2} sont partis en mission. Combien en reste-t-il ?",
                    f"Tu as parcouru {num1} kilomètres, mais il te reste encore {num2} kilomètres à faire. Quelle distance as-tu déjà parcourue ?",
                ]
            )
            explanation_template = f"Pour trouver la réponse, tu dois soustraire {num2} de {num1}, ce qui donne {result}."
        else:
            question_template = random.choice(
                [
                    f"La flotte comptait {num1} vaisseaux, mais {num2} ont été endommagés. Combien de vaisseaux restent opérationnels ?",
                    f"La station disposait de {num1} modules, mais {num2} sont hors service. Combien sont encore actifs ?",
                    f"Un cargo transportait {num1} conteneurs, mais {num2} ont été livrés. Combien en reste-t-il à bord ?",
                ]
            )
            explanation_template = (
                f"Pour calculer ce qui reste, on soustrait: {num1} - {num2} = {result}."
            )

        # Générer des choix proches mais différents
        # Guard: result // 2 peut être 0 si result == 1 → random.randint(1, 0) crash
        wrong_offset = min(3, max(1, result // 2))
        choices = [
            str(result),
            str(result + random.randint(1, min(5, max2))),
            str(result - random.randint(1, wrong_offset)),
            str(num2 - num1),  # Erreur commune: inverser l'ordre de la soustraction
        ]
        random.shuffle(choices)

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Mission spatiale - Soustraction pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "num1": num1,
                "num2": num2,
                "explanation": f"{_ai_prefix()}{explanation_prefix} {explanation_template} {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        # Utiliser des limites adaptées pour la multiplication
        min_val = type_limits.get("min", 2)
        max_val = type_limits.get("max", 10)

        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)
        result = num1 * num2

        if derived_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice(
                [
                    f"Chaque astronaute a {num2} cristaux. S'il y a {num1} astronautes, combien de cristaux y a-t-il au total ?",
                    f"Chaque robot a {num2} capteurs. Combien de capteurs ont {num1} robots au total ?",
                    f"Chaque module de formation a {num2} exercices. Combien d'exercices y a-t-il dans {num1} modules ?",
                ]
            )
            explanation_template = f"Pour trouver le total, tu dois multiplier {num1} par {num2}, ce qui donne {result}."
        else:
            question_template = random.choice(
                [
                    f"Chaque escadre comprend {num2} vaisseaux. Combien de vaisseaux y a-t-il dans {num1} escadres ?",
                    f"Chaque station spatiale héberge {num2} équipages. Combien d'équipages pour {num1} stations ?",
                    f"Chaque secteur contient {num2} systèmes stellaires. Combien de systèmes y a-t-il dans {num1} secteurs ?",
                ]
            )
            explanation_template = (
                f"Pour calculer le total, on multiplie: {num1} × {num2} = {result}."
            )

        # Générer des choix proches mais différents
        choices = [
            str(result),
            str(result + num1),  # Erreur: une fois de trop
            str(result - num2),  # Erreur: une fois de moins
            str(num1 + num2),  # Erreur: addition au lieu de multiplication
        ]
        random.shuffle(choices)

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Mission spatiale - Multiplication pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "num1": num1,
                "num2": num2,
                "explanation": f"{_ai_prefix()}{explanation_prefix} {explanation_template} {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.DIVISION:
        # Générer une division avec reste nul
        min_divisor = type_limits.get("min_divisor", 2)
        max_divisor = type_limits.get("max_divisor", 10)
        min_result = type_limits.get("min_result", 1)
        max_result = type_limits.get("max_result", 10)

        # Pour assurer une division sans reste, on génère d'abord le diviseur et le quotient
        num2 = random.randint(min_divisor, max_divisor)  # diviseur
        result = random.randint(min_result, max_result)  # quotient
        num1 = num2 * result  # dividende

        if derived_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice(
                [
                    f"Tu as {num1} cristaux à distribuer équitablement entre {num2} explorateurs. Combien de cristaux chacun recevra-t-il ?",
                    f"Il y a {num1} robots à répartir dans {num2} hangars. Combien de robots y aura-t-il dans chaque hangar ?",
                    f"Tu dois parcourir {num1} kilomètres en {num2} jours. Combien de kilomètres dois-tu parcourir chaque jour ?",
                ]
            )
            explanation_template = f"Pour trouver la réponse, tu dois diviser {num1} par {num2}, ce qui donne {result}."
        else:
            question_template = random.choice(
                [
                    f"La base spatiale a {num1} membres d'équipage à répartir dans {num2} sections. Combien par section ?",
                    f"Un entrepôt orbital contient {num1} pièces à distribuer à {num2} ateliers. Combien chaque atelier recevra-t-il ?",
                    f"Un convoi de {num1} conteneurs doit être réparti sur {num2} cargos. Combien de conteneurs par cargo ?",
                ]
            )
            explanation_template = (
                f"Pour calculer le résultat, on divise: {num1} ÷ {num2} = {result}."
            )

        # Générer des choix proches mais différents (avec déduplication)
        choices = generate_smart_choices(
            "DIVISION",
            num1,
            num2,
            result,
            normalized_age_group,
            derived_difficulty=derived_difficulty,
        )

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Mission spatiale - Division pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "num1": num1,
                "num2": num2,
                "explanation": f"{_ai_prefix()}{explanation_prefix} {explanation_template} {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.FRACTIONS:
        # Génération IA d'un exercice sur les fractions avec thème Star Wars
        from fractions import Fraction

        # Paramètres selon la difficulté
        if derived_difficulty == DifficultyLevels.INITIE:  # Use derived_difficulty
            denom1, denom2 = random.choice([2, 3, 4]), random.choice([2, 3, 4])
            num1, num2 = random.randint(1, denom1 - 1), random.randint(1, denom2 - 1)
            operation = "+"
        elif derived_difficulty == DifficultyLevels.PADAWAN:  # Use derived_difficulty
            denom1, denom2 = random.choice([2, 3, 4, 5, 6]), random.choice(
                [2, 3, 4, 5, 6]
            )
            num1, num2 = random.randint(1, denom1 - 1), random.randint(1, denom2 - 1)
            operation = random.choice(["+", "-"])
        elif derived_difficulty == DifficultyLevels.CHEVALIER:  # Use derived_difficulty
            denom1, denom2 = random.randint(2, 8), random.randint(2, 8)
            num1, num2 = random.randint(1, denom1), random.randint(1, denom2)
            operation = random.choice(["+", "-", "×"])
        else:  # MAITRE
            denom1, denom2 = random.randint(2, 12), random.randint(2, 12)
            num1, num2 = random.randint(1, denom1 * 2), random.randint(1, denom2 * 2)
            operation = random.choice(["+", "-", "×", "÷"])

        # Calcul du résultat
        frac1, frac2 = Fraction(num1, denom1), Fraction(num2, denom2)
        if operation == "+":
            result = frac1 + frac2
            op_word = "additionner"
        elif operation == "-":
            if frac1 < frac2:
                frac1, frac2 = frac2, frac1  # Éviter les négatifs
            result = frac1 - frac2
            op_word = "soustraire"
        elif operation == "×":
            result = frac1 * frac2
            op_word = "multiplier"
        else:  # "÷"
            if num2 == 0:
                num2 = 1
            result = frac1 / frac2
            op_word = "diviser"

        # Format du résultat
        if result.denominator == 1:
            formatted_result = str(result.numerator)
        else:
            formatted_result = f"{result.numerator}/{result.denominator}"

        if derived_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice(
                [
                    f"Un explorateur boit {num1}/{denom1} de sa gourde et son équipier en boit {num2}/{denom2} de la sienne. Quelle fraction ont-ils bue ensemble ?",
                    f"Le robot A a réparé {num1}/{denom1} des systèmes et le robot B {num2}/{denom2}. Quelle fraction totale ont-ils réparée ?",
                    f"Dans le vaisseau, {num1}/{denom1} des moteurs fonctionnent et {num2}/{denom2} des boucliers. Quelle fraction totale est opérationnelle ?",
                ]
            )
        else:
            question_template = random.choice(
                [
                    f"Une flotte a perdu {num1}/{denom1} de ses appareils, puis {num2}/{denom2} de plus. Quelle fraction totale a été perdue ?",
                    f"Un navigateur maîtrise {num1}/{denom1} des trajets et enseigne {num2}/{denom2} de ses connaissances. Quelle fraction a-t-il transmise ?",
                    f"La station contrôle {num1}/{denom1} du réseau et étend sa portée de {num2}/{denom2}. Quelle fraction contrôle-t-elle maintenant ?",
                ]
            )

        # Choix avec erreurs typiques
        incorrect1 = f"{num1+num2}/{denom1+denom2}"  # Erreur: additionner num et denom
        incorrect2 = f"{num1}/{denom2}"  # Confusion des dénominateurs
        incorrect3 = f"{num2}/{denom1}"  # Inversion

        choices = [formatted_result, incorrect1, incorrect2, incorrect3]
        random.shuffle(choices)

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Fractions spatiales - pour les {age_group}",
                "question": f"Problème de navigation : {question_template}",
                "correct_answer": formatted_result,
                "choices": choices,
                "explanation": f"{_ai_prefix()}{explanation_prefix} Pour {op_word} les fractions {num1}/{denom1} et {num2}/{denom2}, le résultat est {formatted_result}. {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.GEOMETRIE:
        # Génération IA d'un exercice de géométrie avec thème Star Wars
        import math

        # Formes et propriétés selon la difficulté
        if derived_difficulty == DifficultyLevels.INITIE:  # Use derived_difficulty
            shape = random.choice(["carré", "rectangle"])
            property = random.choice(["périmètre", "aire"])
        elif derived_difficulty == DifficultyLevels.PADAWAN:  # Use derived_difficulty
            shape = random.choice(["carré", "rectangle", "triangle"])
            property = random.choice(["périmètre", "aire"])
        elif derived_difficulty == DifficultyLevels.CHEVALIER:  # Use derived_difficulty
            shape = random.choice(["carré", "rectangle", "triangle", "cercle"])
            property = random.choice(["périmètre", "aire"])
        else:  # MAITRE
            shape = random.choice(["carré", "rectangle", "triangle", "cercle"])
            property = random.choice(["périmètre", "aire", "volume"])

        # Génération des valeurs et calculs
        if shape == "carré":
            side = random.randint(type_limits.get("min", 3), type_limits.get("max", 15))
            if property == "périmètre":
                result = 4 * side
                formula = f"4 \\times {side}"
            else:  # aire
                result = side * side
                formula = f"{side}^2"

            question_template = random.choice(
                [
                    f"Une station orbitale a une section carrée de côté {side} km. Quel est son {property} ?",
                    f"Un hangar spatial est carré avec {side} m de côté. Calcule son {property}.",
                    f"Un module de la base lunaire est une salle carrée de {side} m de côté. Quel est son {property} ?",
                ]
            )

        elif shape == "rectangle":
            length = random.randint(
                type_limits.get("min", 4), type_limits.get("max", 20)
            )
            width = random.randint(type_limits.get("min", 3), length - 1)
            if property == "périmètre":
                result = 2 * (length + width)
                formula = f"2 \\times ({length} + {width})"
            else:  # aire
                result = length * width
                formula = f"{length} \\times {width}"

            question_template = random.choice(
                [
                    f"Un cargo spatial a une soute rectangulaire de {length}m × {width}m. Quel est son {property} ?",
                    f"Un vaisseau de transport a un hangar de {length} km sur {width} km. Calcule son {property}.",
                    f"Le centre de commandement mesure {length}m × {width}m. Quel est son {property} ?",
                ]
            )

        elif shape == "triangle":
            base = random.randint(type_limits.get("min", 4), type_limits.get("max", 15))
            height = random.randint(
                type_limits.get("min", 3), type_limits.get("max", 12)
            )
            if property == "aire":
                result = (base * height) / 2
                formula = f"\\frac{{{base} \\times {height}}}{{2}}"
            else:  # périmètre approximatif
                hypotenuse = round(math.sqrt(base * base + height * height), 1)
                result = base + height + hypotenuse
                formula = f"{base} + {height} + {hypotenuse}"

            question_template = random.choice(
                [
                    f"Un voilier spatial a des ailes triangulaires de base {base}m et hauteur {height}m. Quelle est leur {property} ?",
                    f"Une antenne de relais forme un triangle de base {base} cm et hauteur {height} cm. Calcule son {property}.",
                    f"Une voile solaire triangulaire mesure {base}km × {height}km. Quel est son {property} ?",
                ]
            )

        else:  # cercle
            radius = random.randint(
                type_limits.get("min", 2), type_limits.get("max", 10)
            )
            if property == "périmètre":
                result = round(2 * math.pi * radius, 2)
                formula = f"2 \\times \\pi \\times {radius}"
            else:  # aire
                result = round(math.pi * radius * radius, 2)
                formula = f"\\pi \\times {radius}^2"

            question_template = random.choice(
                [
                    f"Un astéroïde sphérique a un rayon de {radius} km. Quel est son {property} ?",
                    f"Une planète de la ceinture d'astéroïdes a un rayon de {radius} milliers de km. Calcule son {property}.",
                    f"Un bouclier déflecteur circulaire a un rayon de {radius}m. Quel est son {property} ?",
                ]
            )

        # Choix avec erreurs typiques
        choices = [
            str(result),
            str(round(result * 0.5, 2)),  # Moitié
            str(round(result * 2, 2)),  # Double
            str(round(result * 1.5, 2)),  # 1.5 fois
        ]
        random.shuffle(choices)

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Géométrie spatiale - pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "explanation": f"{_ai_prefix()}{explanation_prefix} Pour calculer le {property} d'un {shape}, on utilise : $${formula} = {result}$$. {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.DIVERS:
        # Génération IA d'exercices divers avec thème Star Wars

        # Types de problèmes selon la difficulté
        if derived_difficulty == DifficultyLevels.INITIE:  # Use derived_difficulty
            problem_type = random.choice(["age", "monnaie", "temps"])
        elif derived_difficulty == DifficultyLevels.PADAWAN:  # Use derived_difficulty
            problem_type = random.choice(
                ["age", "monnaie", "vitesse", "pourcentage_simple"]
            )
        elif derived_difficulty == DifficultyLevels.CHEVALIER:  # Use derived_difficulty
            problem_type = random.choice(["vitesse", "pourcentage", "probabilité"])
        else:  # MAITRE
            problem_type = random.choice(["probabilité", "séquence", "logique_avancée"])

        # Génération selon le type
        if problem_type == "age":
            age_actuel = random.randint(
                type_limits.get("min", 8), type_limits.get("max", 25)
            )
            années = random.randint(1, 10)
            result = age_actuel + années

            question_template = random.choice(
                [
                    f"Un astronaute a {age_actuel} ans. Dans {années} ans, quel âge aura-t-il ?",
                    f"Une exploratrice a {age_actuel} ans aujourd'hui. Quel âge aura-t-elle dans {années} ans ?",
                    f"Un navigateur a {age_actuel} ans. Dans combien d'années aura-t-il {result} ans ?",
                ]
            )
            explanation_template = (
                f"Pour trouver l'âge futur: {age_actuel} + {années} = {result} ans."
            )

        elif problem_type == "monnaie":
            prix = random.randint(type_limits.get("min", 5), type_limits.get("max", 50))
            payé = random.randint(prix + 1, prix + 20)
            result = payé - prix

            question_template = random.choice(
                [
                    f"Tu achètes un équipement à {prix} crédits. Tu paies {payé} crédits. Combien de monnaie ?",
                    f"Un module coûte {prix} crédits. Tu donnes {payé} crédits. Quelle est la monnaie ?",
                    f"Des provisions coûtent {prix} crédits. Tu paies avec {payé} crédits. Combien récupères-tu ?",
                ]
            )
            explanation_template = (
                f"Monnaie = montant payé - prix: {payé} - {prix} = {result} crédits."
            )

        elif problem_type == "vitesse":
            distance = random.randint(
                type_limits.get("min", 10), type_limits.get("max", 100)
            )
            temps = random.randint(2, 10)
            result = distance // temps

            question_template = random.choice(
                [
                    f"Un vaisseau parcourt {distance} km en {temps} heures. Quelle est sa vitesse ?",
                    f"Une sonde explore {distance} km en {temps} minutes. Quelle est sa vitesse par minute ?",
                    f"Un cargo voyage {distance} années-lumière en {temps} jours. Vitesse par jour ?",
                ]
            )
            explanation_template = (
                f"Vitesse = distance ÷ temps: {distance} ÷ {temps} = {result}."
            )

        elif problem_type == "pourcentage" or problem_type == "pourcentage_simple":
            initial = random.randint(
                type_limits.get("min", 20), type_limits.get("max", 100)
            )
            pourcentage = random.choice([10, 20, 25, 50])
            result = initial + (initial * pourcentage // 100)

            question_template = random.choice(
                [
                    f"La flotte compte {initial} appareils. Leur nombre augmente de {pourcentage}%. Nouveau total ?",
                    f"La base a {initial} membres. Elle recrute {pourcentage}% de plus. Combien maintenant ?",
                    f"Un entrepôt contient {initial} caisses. Le stock augmente de {pourcentage}%. Nouveau total ?",
                ]
            )
            explanation_template = (
                f"Augmentation: {initial} + ({initial} × {pourcentage}%) = {result}."
            )

        elif problem_type == "probabilité":
            total = random.randint(10, 30)
            favorables = random.randint(1, total // 3)
            result = f"{favorables}/{total}"

            question_template = random.choice(
                [
                    f"Dans un sac, {total} pierres dont {favorables} sont brillantes. Probabilité d'une pierre brillante ?",
                    f"Sur {total} planètes explorées, {favorables} sont habitables. Quelle est la probabilité ?",
                    f"Parmi {total} capteurs, {favorables} sont défaillants. Probabilité d'un capteur défaillant ?",
                ]
            )
            explanation_template = f"Probabilité = cas favorables ÷ total: {favorables} ÷ {total} = {result}."

        elif problem_type == "séquence":
            start = random.randint(2, 8)
            diff = random.randint(2, 5)
            sequence = [start + diff * i for i in range(4)]
            result = sequence[-1] + diff

            question_template = f"Suite numérique : {', '.join(map(str, sequence))}, … Quel est le terme suivant ?"
            explanation_template = (
                f"La suite augmente de {diff}: {sequence[-1]} + {diff} = {result}."
            )

        else:  # logique_avancée
            a, b = random.randint(5, 15), random.randint(2, 8)
            result = a * b

            question_template = random.choice(
                [
                    f"Si {a} équipages s'entraînent {b} heures chacun, combien d'heures au total ?",
                    f"La base déploie {a} escadres de {b} appareils. Combien d'appareils au total ?",
                    f"Dans {a} secteurs, il y a {b} stations chacun. Combien de stations au total ?",
                ]
            )
            explanation_template = f"Total = {a} × {b} = {result}."

        # Choix appropriés selon le type de résultat
        if isinstance(result, str) and "/" in result:
            # Pour les fractions (probabilités)
            num, denom = map(int, result.split("/"))
            choices = [result, f"{num+1}/{denom}", f"{num}/{denom+1}", f"{denom}/{num}"]
        else:
            # Pour les entiers
            choices = [
                str(result),
                str(result + random.randint(1, 5)),
                str(max(1, result - random.randint(1, 3))),
                str(result * 2),
            ]
        random.shuffle(choices)

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Défis numériques - pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "explanation": f"{_ai_prefix()}{explanation_prefix} {explanation_template} {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.MIXTE:
        # Génération IA d'un exercice mixte avec PLUSIEURS opérations et thème Star Wars
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)

        # Choisir un pattern de calcul mixte selon la difficulté avec contexte Star Wars
        if derived_difficulty == DifficultyLevels.INITIE:
            # Pour les débutants: 2 opérations simples
            a = random.randint(min_val, max_val)
            b = random.randint(2, 6)
            c = random.randint(1, 4)

            patterns = [
                (
                    lambda: a + b - c,
                    f"{a} + {b} - {c}",
                    f"Un explorateur a trouvé {a} cristaux, puis {b} de plus, mais il en a échangé {c}.",
                    f"On calcule étape par étape: {a} + {b} = {a+b}, puis {a+b} - {c} = {a+b-c}.",
                ),
                (
                    lambda: a * b + c,
                    f"{a} × {b} + {c}",
                    f"Chaque astronaute a {b} outils et il y a {a} astronautes, plus {c} outils de réserve.",
                    f"D'abord la multiplication: {a} × {b} = {a*b}, puis on ajoute {c}: {a*b} + {c} = {a*b+c}.",
                ),
            ]
        elif derived_difficulty == DifficultyLevels.PADAWAN:
            # Intermédiaire: priorité des opérations
            a = random.randint(min_val, max_val)
            b = random.randint(2, 8)
            c = random.randint(2, 6)

            patterns = [
                (
                    lambda: a + b * c,
                    f"{a} + {b} × {c}",
                    f"La flotte a {a} vaisseaux, plus {b} escadres de {c} appareils chacune.",
                    f"Attention à la priorité ! D'abord {b} × {c} = {b*c}, puis {a} + {b*c} = {a + b*c}.",
                ),
                (
                    lambda: a * b - c,
                    f"{a} × {b} - {c}",
                    f"La base a {a} escouades de {b} membres, mais {c} sont en mission.",
                    f"D'abord {a} × {b} = {a*b}, puis on soustrait {c}: {a*b} - {c} = {a*b - c}.",
                ),
            ]
        else:
            # Avancé: parenthèses et opérations complexes
            a = random.randint(min_val, max_val)
            b = random.randint(2, 8)
            c = random.randint(2, 6)

            # S'assurer que a > b pour éviter les résultats négatifs
            if a <= b:
                a, b = b + 2, a

            patterns = [
                (
                    lambda: (a + b) * c,
                    f"({a} + {b}) × {c}",
                    f"Deux équipes ont ensemble {a} + {b} minerais, chaque minerai vaut {c} crédits.",
                    f"D'abord les parenthèses: ({a} + {b}) = {a+b}, puis × {c} = {(a+b)*c}.",
                ),
                (
                    lambda: (a - b) * c,
                    f"({a} - {b}) × {c}",
                    f"La station avait {a} appareils, {b} sont en révision, les {a-b} restants ont {c} équipages chacun.",
                    f"D'abord ({a} - {b}) = {a-b}, puis × {c} = {(a-b)*c}.",
                ),
                (
                    lambda: a * (b + c),
                    f"{a} × ({b} + {c})",
                    f"Chaque avant-poste ({a} au total) a {b} + {c} membres d'équipage.",
                    f"D'abord ({b} + {c}) = {b+c}, puis {a} × {b+c} = {a*(b+c)}.",
                ),
            ]

        calc_func, formula, context, explain = random.choice(patterns)
        result = calc_func()

        question_template = f"{context} Combien au total? (Calcul: {formula})"
        explanation_template = explain

        # Générer des choix avec erreurs typiques
        choices = [
            str(result),
            str(result + random.randint(1, 5)),
            str(max(1, result - random.randint(1, 5))),
            str(a + b + c),  # Erreur courante: additionner tout
        ]
        choices = list(set(choices))
        while len(choices) < 4:
            choices.append(str(result + random.randint(-10, 10)))
        choices = list(set(choices))[:4]
        random.shuffle(choices)

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Opération mixte - pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "formula": formula,
                "explanation": f"{_ai_prefix()}{explanation_prefix} {explanation_template} {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.TEXTE:
        # Génération IA d'exercices textuels avec thème Star Wars

        # Générer des nombres aléatoirement selon la difficulté
        if derived_difficulty == DifficultyLevels.INITIE:  # Use derived_difficulty
            base_num = random.randint(3, 8)
            modifier = random.randint(2, 5)
            large_num = random.randint(10, 20)
        elif derived_difficulty == DifficultyLevels.PADAWAN:  # Use derived_difficulty
            base_num = random.randint(5, 12)
            modifier = random.randint(3, 7)
            large_num = random.randint(15, 30)
        elif derived_difficulty == DifficultyLevels.CHEVALIER:  # Use derived_difficulty
            base_num = random.randint(8, 15)
            modifier = random.randint(4, 9)
            large_num = random.randint(20, 50)
        else:  # MAITRE
            base_num = random.randint(10, 25)
            modifier = random.randint(5, 12)
            large_num = random.randint(30, 100)

        # Choisir un type de problème selon la difficulté
        if derived_difficulty == DifficultyLevels.INITIE:  # Use derived_difficulty
            problem_types = [
                "simple_addition",
                "simple_subtraction",
                "simple_multiplication",
            ]
        elif derived_difficulty == DifficultyLevels.PADAWAN:  # Use derived_difficulty
            problem_types = ["two_step", "sequence", "comparison"]
        elif derived_difficulty == DifficultyLevels.CHEVALIER:  # Use derived_difficulty
            problem_types = ["multi_step", "ratio", "logic_puzzle"]
        else:  # MAITRE
            problem_types = ["complex_multi_step", "algebraic", "advanced_logic"]

        problem_type = random.choice(problem_types)

        # Générer le problème selon le type
        if problem_type == "simple_addition":
            result = base_num + modifier
            question_template = random.choice(
                [
                    f"Un robot a {base_num} capteurs. Un autre en a {modifier} de plus. Combien le second en a-t-il ?",
                    f"Un astronaute a {base_num} outils. Il en trouve {modifier} autres dans la réserve. Combien en a-t-il maintenant ?",
                    f"Dans le hangar, il y a {base_num} techniciens et {modifier} pilotes arrivent. Combien de personnes au total ?",
                ]
            )

        elif problem_type == "simple_subtraction":
            result = large_num - base_num
            question_template = random.choice(
                [
                    f"Un entrepôt avait {large_num} pièces. On en utilise {base_num}. Combien en reste-t-il ?",
                    f"La flotte avait {large_num} appareils. {base_num} ont été mis en révision. Combien restent opérationnels ?",
                    f"Un stock contenait {large_num} composants. {base_num} ont été distribués. Combien en reste-t-il ?",
                ]
            )

        elif problem_type == "simple_multiplication":
            result = base_num * modifier
            question_template = random.choice(
                [
                    f"Dans le hangar, il y a {base_num} tables d'atelier. Chaque table a {modifier} outils. Combien d'outils au total ?",
                    f"Chaque navette a {modifier} sièges. Combien de sièges ont {base_num} navettes ?",
                    f"Chaque technicien travaille {modifier} heures par jour. Combien d'heures pour {base_num} techniciens ?",
                ]
            )

        elif problem_type == "two_step":
            step1_result = base_num * modifier
            result = step1_result - base_num
            question_template = random.choice(
                [
                    f"Un pilote a {base_num} crédits. Il achète {modifier} pièces à {base_num} crédits chacune. Combien lui reste-t-il ?",
                    f"Un vaisseau consomme {modifier} unités de carburant par trajet. Pour {base_num} trajets, combien d'unités faut-il ?",
                    f"Un chef d'équipe supervise {base_num} techniciens. Chacun a {modifier} outils. Combien d'outils au total ?",
                ]
            )
            if "reste-t-il" in question_template:
                result = (
                    base_num - step1_result
                    if base_num > step1_result
                    else step1_result - base_num
                )
            else:
                result = step1_result

        elif problem_type == "sequence":
            # Séquence arithmétique
            start = base_num
            step = modifier
            result = start + (3 * step)  # 4ème terme
            sequence = f"{start}, {start + step}, {start + 2*step}, {start + 3*step}"
            question_template = random.choice(
                [
                    f"Une suite de coordonnées : {start}, {start + step}, {start + 2*step}… Quel est le terme suivant ?",
                    f"Les capteurs enregistrent ces valeurs : {start}, {start + step}, {start + 2*step}… Quelle est la prochaine valeur ?",
                    f"Le code d'accès suit ce motif : {start}, {start + step}, {start + 2*step}… Quel est le nombre suivant ?",
                ]
            )

        elif problem_type == "comparison":
            multiplier = random.randint(2, 4)
            result = base_num * multiplier
            question_template = random.choice(
                [
                    f"La flotte A a {multiplier} fois plus d'appareils que la flotte B. Si la flotte B a {base_num} appareils, combien la flotte A en a-t-elle ?",
                    f"Un croiseur transporte {multiplier} fois plus de membres d'équipage qu'une frégate. Si la frégate a {base_num} membres, combien le croiseur en a-t-il ?",
                    f"Une grande base a {multiplier} fois plus de réserves qu'un avant-poste. Si l'avant-poste a {base_num} unités, combien la base en a-t-elle ?",
                ]
            )

        else:  # Types plus complexes pour niveaux élevés
            result = base_num + modifier
            question_template = f"Problème de logique : La somme de deux nombres consécutifs est {result + result - 1}. Quel est le plus petit nombre ?"
            result = base_num  # Pour les problèmes algébriques

        # Générer des choix incorrects plausibles
        choices = [
            str(result),
            str(result + random.randint(1, 5)),
            str(max(1, result - random.randint(1, 3))),
            str(result * 2) if result < 50 else str(result // 2),
        ]
        random.shuffle(choices)

        exercise_data.update(
            {
                "title": f"{_ai_prefix()}Problème textuel - pour les {age_group}",
                "question": question_template,
                "correct_answer": str(result),
                "choices": choices,
                "explanation": f"{_ai_prefix()}{explanation_prefix} Pour résoudre ce problème, il faut analyser les données et appliquer les bonnes opérations mathématiques. {explanation_suffix}",
            }
        )
        return apply_test_title(exercise_data)
    return default_addition_fallback(exercise_data, type_limits, ai_generated=True)


def ensure_explanation(exercise_dict):
    """S'assure qu'un exercice a une explication valide et enrichit le dict."""
    # S'assurer que l'explication est définie et n'est pas None
    if (
        "explanation" not in exercise_dict
        or exercise_dict["explanation"] is None
        or exercise_dict["explanation"] == "None"
        or exercise_dict["explanation"] == ""
    ):
        if exercise_dict["exercise_type"] == ExerciseTypes.ADDITION:
            exercise_dict["explanation"] = (
                f"Pour additionner {exercise_dict.get('num1', '?')} et {exercise_dict.get('num2', '?')}, il faut calculer leur somme: {exercise_dict['correct_answer']}"
            )
        elif exercise_dict["exercise_type"] == ExerciseTypes.SUBTRACTION:
            exercise_dict["explanation"] = (
                f"Pour soustraire {exercise_dict.get('num2', '?')} de {exercise_dict.get('num1', '?')}, il faut calculer leur différence: {exercise_dict['correct_answer']}"
            )
        elif exercise_dict["exercise_type"] == ExerciseTypes.MULTIPLICATION:
            exercise_dict["explanation"] = (
                f"Pour multiplier {exercise_dict.get('num1', '?')} par {exercise_dict.get('num2', '?')}, il faut calculer leur produit: {exercise_dict['correct_answer']}"
            )
        elif exercise_dict["exercise_type"] == ExerciseTypes.DIVISION:
            exercise_dict["explanation"] = (
                f"Pour diviser {exercise_dict.get('num1', '?')} par {exercise_dict.get('num2', '?')}, il faut calculer leur quotient: {exercise_dict['correct_answer']}"
            )
        else:
            exercise_dict["explanation"] = (
                f"La réponse correcte est {exercise_dict['correct_answer']}"
            )

    # Flag is_open_answer : les niveaux MAITRE et GRAND_MAITRE utilisent
    # une saisie libre plutôt que des choix QCM (réduction de l'aide QCM).
    if "is_open_answer" not in exercise_dict:
        difficulty = exercise_dict.get("difficulty", "")
        exercise_dict["is_open_answer"] = difficulty in (
            DifficultyLevels.MAITRE,
            DifficultyLevels.GRAND_MAITRE,
        )

    return exercise_dict


def generate_simple_exercise(
    exercise_type,
    age_group,
    *,
    difficulty_override=None,
    pedagogical_band_override=None,
):
    """Génère un exercice simple sans IA avec calibrage F42.

    ``pedagogical_band_override`` (keyword-only): injecte la bande résolue depuis
    les données de maîtrise (second axe F42) quand disponible.
    """
    (
        normalized_type,
        normalized_age_group,
        derived_difficulty,
        type_limits,
        f42_profile,
    ) = init_exercise_context(
        exercise_type,
        age_group,
        difficulty_override=difficulty_override,
        pedagogical_band_override=pedagogical_band_override,
    )
    exercise_data = build_base_exercise_data(
        normalized_type, normalized_age_group, derived_difficulty, ai_generated=False
    )
    exercise_data["difficulty_tier"] = f42_profile["difficulty_tier"]

    if normalized_type == ExerciseTypes.ADDITION:
        # Génération d'une addition
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)

        result = num1 + num2
        question = ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2)
        correct_answer = str(result)

        choices = generate_smart_choices(
            "ADDITION",
            num1,
            num2,
            result,
            normalized_age_group,
            derived_difficulty=derived_difficulty,
        )
        title_salt = num1 + num2 + result

        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_ADDITION, salt=title_salt),
                "question": question,
                "correct_answer": correct_answer,
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
                "num1": num1,
                "num2": num2,
                "explanation": f"Pour additionner {num1} et {num2}, il faut calculer leur somme, donc {num1} + {num2} = {result}.",
            }
        )
        return apply_test_title(exercise_data)

    elif normalized_type == ExerciseTypes.SUBTRACTION:
        # Génération d'une soustraction
        limits = type_limits
        num1 = random.randint(limits.get("min1", 5), limits.get("max1", 20))
        num2 = random.randint(
            limits.get("min2", 1), min(num1 - 1, limits.get("max2", 5))
        )  # Assurer num2 < num1

        result = num1 - num2
        question = ExerciseMessages.QUESTION_SUBTRACTION.format(num1=num1, num2=num2)
        correct_answer = str(result)

        choices = generate_smart_choices(
            "SOUSTRACTION",
            num1,
            num2,
            result,
            normalized_age_group,
            derived_difficulty=derived_difficulty,
        )
        title_salt = num1 + num2 + result

        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_SUBTRACTION, salt=title_salt),
                "question": question,
                "correct_answer": correct_answer,
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
                "num1": num1,
                "num2": num2,
                "explanation": f"Pour soustraire {num2} de {num1}, il faut calculer leur différence, donc {num1} - {num2} = {result}.",
            }
        )
        return apply_test_title(exercise_data)

    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        # Génération d'une multiplication
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)

        result = num1 * num2
        question = ExerciseMessages.QUESTION_MULTIPLICATION.format(num1=num1, num2=num2)
        correct_answer = str(result)

        choices = generate_smart_choices(
            "MULTIPLICATION",
            num1,
            num2,
            result,
            normalized_age_group,
            derived_difficulty=derived_difficulty,
        )
        title_salt = num1 + num2 + result

        exercise_data.update(
            {
                "title": pick_title_variant(
                    SIMPLE_TITLE_MULTIPLICATION, salt=title_salt
                ),
                "question": question,
                "correct_answer": correct_answer,
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
                "num1": num1,
                "num2": num2,
                "explanation": f"Pour multiplier {num1} par {num2}, il faut calculer leur produit, donc {num1} × {num2} = {result}.",
            }
        )
        return apply_test_title(exercise_data)

    elif normalized_type == ExerciseTypes.DIVISION:
        # Génération d'une division
        limits = type_limits
        min_divisor = limits.get("min_divisor", 2)
        max_divisor = limits.get("max_divisor", 5)
        min_result = limits.get("min_result", 1)
        max_result = limits.get("max_result", 5)

        # Générer d'abord le diviseur et le résultat pour assurer une division exacte
        num2 = random.randint(min_divisor, max_divisor)  # diviseur
        result = random.randint(min_result, max_result)  # quotient
        num1 = num2 * result  # dividende

        question = ExerciseMessages.QUESTION_DIVISION.format(num1=num1, num2=num2)
        correct_answer = str(result)

        choices = generate_smart_choices(
            "DIVISION",
            num1,
            num2,
            result,
            normalized_age_group,
            derived_difficulty=derived_difficulty,
        )
        title_salt = num1 + num2 + result

        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_DIVISION, salt=title_salt),
                "question": question,
                "correct_answer": correct_answer,
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
                "num1": num1,
                "num2": num2,
                "explanation": f"Pour diviser {num1} par {num2}, il faut calculer leur quotient, donc {num1} ÷ {num2} = {result}.",
            }
        )
        return apply_test_title(exercise_data)

    elif normalized_type == ExerciseTypes.TEXTE:
        # Génération d'un exercice textuel (problèmes logiques, énigmes, etc.)
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)

        # Choisir un type de problème textuel en fonction du groupe d'âge (via la difficulté dérivée)
        if derived_difficulty == DifficultyLevels.INITIE:
            # Problèmes textuels simples pour débutants
            problem_type = random.choice(
                ["logique_simple", "devinette_nombre", "probleme_concret"]
            )
        elif derived_difficulty == DifficultyLevels.PADAWAN:
            problem_type = random.choice(
                [
                    "logique_simple",
                    "devinette_nombre",
                    "probleme_concret",
                    "sequence_simple",
                ]
            )
        elif derived_difficulty == DifficultyLevels.CHEVALIER:
            problem_type = random.choice(
                ["logique_avance", "enigme_math", "probleme_etapes", "sequence_avance"]
            )
        else:  # MAITRE
            problem_type = random.choice(
                [
                    "logique_complexe",
                    "enigme_complexe",
                    "probleme_multi_etapes",
                    "code_secret",
                ]
            )

        # Logique pour chaque type de problème textuel
        if problem_type == "logique_simple":
            # Problème logique simple
            objets = random.choice(
                [
                    ("capteurs", "l'équipe"),
                    ("robots", "la station"),
                    ("vaisseaux", "la flotte"),
                    ("cristaux", "l'explorateur"),
                ]
            )
            objet, personnage = objets

            initial = random.randint(min_val, max_val)
            donnés = random.randint(1, initial - 1)
            result = initial - donnés

            problem = f"{personnage} a {initial} {objet}. Elle/il en distribue {donnés}. Combien en reste-t-il ?"
            explanation = f"Pour trouver ce qui reste, on soustrait ce qui a été distribué du total initial. Donc {initial} - {donnés} = {result}."
            answer_type = "number"

        elif problem_type == "devinette_nombre":
            # Devinette sur un nombre
            if derived_difficulty == DifficultyLevels.INITIE:
                # Devinette simple
                nombre = random.randint(1, 10)
                indices = []
                if nombre % 2 == 0:
                    indices.append("pair")
                else:
                    indices.append("impair")

                if nombre < 5:
                    indices.append("plus petit que 5")
                else:
                    indices.append("plus grand que 4")

                problem = f"Je pense à un nombre entre 1 et 10. Il est {indices[0]} et {indices[1]}. Quel est ce nombre ?"
                explanation = f"En cherchant un nombre {indices[0]} et {indices[1]}, on trouve {nombre}."
                result = nombre
            else:
                # Devinette plus complexe
                nombre = random.randint(10, 50)
                operation = random.choice(["addition", "multiplication"])

                if operation == "addition":
                    ajout = random.randint(5, 15)
                    resultat_op = nombre + ajout
                    problem = f"Je pense à un nombre. Si j'ajoute {ajout}, j'obtiens {resultat_op}. Quel est mon nombre ?"
                    explanation = f"Pour trouver le nombre, on soustrait {ajout} de {resultat_op}. Donc {resultat_op} - {ajout} = {nombre}."
                else:
                    facteur = random.randint(2, 5)
                    resultat_op = nombre * facteur
                    problem = f"Je pense à un nombre. Si je le multiplie par {facteur}, j'obtiens {resultat_op}. Quel est mon nombre ?"
                    explanation = f"Pour trouver le nombre, on divise {resultat_op} par {facteur}. Donc {resultat_op} ÷ {facteur} = {nombre}."

                result = nombre
            answer_type = "number"

        elif problem_type == "probleme_concret":
            scenarios = [
                {
                    "context": "À la cantine de la station orbitale",
                    "action": "Un astronaute commande {nb1} repas à {prix} crédits chacun",
                    "question": "Combien paie-t-il au total ?",
                    "calc": lambda nb1, prix: nb1 * prix,
                    "explanation": "Pour calculer le total, on multiplie le nombre de repas par le prix unitaire. Donc {nb1} × {prix} = {result}.",
                },
                {
                    "context": "Sur la lune de la base",
                    "action": "Un explorateur trouve {nb1} minerais. Il en perd {nb2} dans la tempête",
                    "question": "Combien lui en reste-t-il ?",
                    "calc": lambda nb1, nb2: nb1 - nb2,
                    "explanation": "Pour trouver ce qui reste, on soustrait ce qui est perdu du total initial. Donc {nb1} - {nb2} = {result}.",
                },
                {
                    "context": "Dans l'escadre de navettes",
                    "action": "Il y a {nb1} pilotes répartis équitablement dans {nb2} escouades",
                    "question": "Combien de pilotes par escouade ?",
                    "calc": lambda nb1, nb2: nb1 // nb2,
                    "explanation": "Pour répartir équitablement, on divise le nombre total par le nombre d'escouades. Donc {nb1} ÷ {nb2} = {result}.",
                },
            ]

            scenario = random.choice(scenarios)
            nb1 = random.randint(min_val, max_val)
            nb2 = (
                random.randint(2, min(nb1, 5))
                if "divise" in scenario["explanation"]
                else random.randint(1, min_val)
            )

            # Ajuster pour éviter les divisions impossibles
            if "÷" in scenario["explanation"] and nb1 % nb2 != 0:
                nb1 = nb2 * random.randint(2, 5)  # Assurer une division exacte

            result = scenario["calc"](nb1, nb2)

            problem = f"{scenario['context']}, {scenario['action'].format(nb1=nb1, nb2=nb2, prix=nb2)}. {scenario['question']}"
            explanation = scenario["explanation"].format(
                nb1=nb1, nb2=nb2, prix=nb2, result=result
            )
            answer_type = "number"

        elif problem_type == "sequence_simple":
            # Séquence simple
            start = random.randint(1, 5)
            step = random.randint(1, 3)
            sequence = [start + step * i for i in range(4)]
            result = sequence[-1] + step

            problem = f"Quelle est la suite logique : {sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, ... ?"
            explanation = f"Cette séquence augmente de {step} à chaque terme. Le terme suivant est donc {sequence[3]} + {step} = {result}."
            answer_type = "number"

        else:
            # Problème par défaut pour les types non implémentés
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            result = a + b

            problem = f"Un astronaute a {a} outils. Son équipier lui en donne {b} de plus. Combien en a-t-il maintenant ?"
            explanation = f"Pour trouver le total, on additionne les deux quantités. Donc {a} + {b} = {result}."
            answer_type = "number"

        # Créer des choix appropriés
        if answer_type == "number":
            choices = [
                str(result),
                str(result + random.randint(1, 3)),
                str(max(1, result - random.randint(1, 3))),
                str(result + random.randint(4, 6)),
            ]
        else:
            # Pour les réponses textuelles (si nécessaire)
            choices = [
                str(result),
                "Autre réponse 1",
                "Autre réponse 2",
                "Autre réponse 3",
            ]

        random.shuffle(choices)

        # Construire l'exercice
        text_salt = result + len(problem)
        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_TEXTE, salt=text_salt),
                "question": problem,
                "correct_answer": str(result),
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + "texte",
                "explanation": explanation,
                "answer_type": answer_type,  # Métadonnée pour l'interface
            }
        )

        return apply_test_title(exercise_data)

    elif normalized_type == ExerciseTypes.FRACTIONS:
        # Génération d'un exercice sur les fractions
        from fractions import Fraction

        if derived_difficulty == DifficultyLevels.INITIE:  # Use derived_difficulty
            denominator = random.choice([2, 3, 4])
            numerator = 1
        elif derived_difficulty == DifficultyLevels.PADAWAN:  # Use derived_difficulty
            denominator = random.choice([2, 3, 4, 5])
            numerator = random.randint(1, denominator - 1)
        elif derived_difficulty == DifficultyLevels.CHEVALIER:  # Use derived_difficulty
            denominator = random.choice([4, 5, 6, 8])
            numerator = random.randint(1, denominator - 1)
        else:  # MAITRE
            denominator = random.choice([6, 8, 9, 12])
            numerator = random.randint(1, denominator - 1)

        question = f"Quelle fraction représente {numerator} part{'s' if numerator > 1 else ''} sur {denominator} ?"
        correct_answer = f"{numerator}/{denominator}"

        pool = [
            f"{denominator}/{numerator}",
            f"{numerator}/{denominator + 1}",
            f"{numerator + 1}/{denominator}",
        ]
        choices = ensure_four_distinct_str_choices(correct_answer, pool)
        frac_salt = numerator + denominator

        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_FRACTIONS, salt=frac_salt),
                "question": question,
                "correct_answer": correct_answer,
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.FRACTIONS,
                "explanation": f"Une fraction représente une partie d'un tout. {numerator} part{'s' if numerator > 1 else ''} sur {denominator} s'écrit {correct_answer}.",
            }
        )
        return apply_test_title(exercise_data)

    elif normalized_type == ExerciseTypes.GEOMETRIE:
        # Génération d'un exercice de géométrie
        import math

        if derived_difficulty == DifficultyLevels.INITIE:  # Use derived_difficulty
            shape = random.choice(["carré", "rectangle"])
            if shape == "carré":
                side = random.randint(3, 10)
                property_type = random.choice(["périmètre", "aire"])
                if property_type == "périmètre":
                    result = 4 * side
                    question = (
                        f"Un carré a un côté de {side} cm. Quel est son périmètre ?"
                    )
                    explanation = f"Le périmètre d'un carré = 4 × côté = 4 × {side} = {result} cm."
                else:
                    result = side * side
                    question = f"Un carré a un côté de {side} cm. Quelle est son aire ?"
                    explanation = f"L'aire d'un carré = côté × côté = {side} × {side} = {result} cm²."
            else:  # rectangle
                length = random.randint(4, 10)
                width = random.randint(3, length - 1)
                property_type = random.choice(["périmètre", "aire"])
                if property_type == "périmètre":
                    result = 2 * (length + width)
                    question = f"Un rectangle mesure {length} cm de longueur et {width} cm de largeur. Quel est son périmètre ?"
                    explanation = f"Le périmètre d'un rectangle = 2 × (longueur + largeur) = 2 × ({length} + {width}) = {result} cm."
                else:
                    result = length * width
                    question = f"Un rectangle mesure {length} cm de longueur et {width} cm de largeur. Quelle est son aire ?"
                    explanation = f"L'aire d'un rectangle = longueur × largeur = {length} × {width} = {result} cm²."
        else:
            shape = random.choice(["carré", "rectangle", "triangle", "cercle"])
            property_type = random.choice(["périmètre", "aire"])

            if shape == "carré":
                side = random.randint(5, 15)
                if property_type == "périmètre":
                    result = 4 * side
                    question = (
                        f"Un carré a un côté de {side} cm. Quel est son périmètre ?"
                    )
                    explanation = f"Le périmètre d'un carré = 4 × côté = 4 × {side} = {result} cm."
                else:
                    result = side * side
                    question = f"Un carré a un côté de {side} cm. Quelle est son aire ?"
                    explanation = f"L'aire d'un carré = côté² = {side}² = {result} cm²."
            elif shape == "rectangle":
                length = random.randint(6, 20)
                width = random.randint(4, length - 1)
                if property_type == "périmètre":
                    result = 2 * (length + width)
                    question = f"Un rectangle mesure {length} cm × {width} cm. Quel est son périmètre ?"
                    explanation = f"Le périmètre = 2 × (longueur + largeur) = 2 × ({length} + {width}) = {result} cm."
                else:
                    result = length * width
                    question = f"Un rectangle mesure {length} cm × {width} cm. Quelle est son aire ?"
                    explanation = f"L'aire = longueur × largeur = {length} × {width} = {result} cm²."
            elif shape == "triangle":
                base = random.randint(5, 15)
                height = random.randint(4, 12)
                if property_type == "aire":
                    result = (base * height) / 2
                    question = f"Un triangle a une base de {base} cm et une hauteur de {height} cm. Quelle est son aire ?"
                    explanation = f"L'aire d'un triangle $= \\frac{{base \\times hauteur}}{{2}} = \\frac{{{base} \\times {height}}}{{2}} = {result}$ cm²."
                else:
                    hypotenuse = round(math.sqrt(base * base + height * height), 1)
                    result = round(base + height + hypotenuse, 1)
                    question = f"Un triangle rectangle a une base de {base} cm et une hauteur de {height} cm. Quel est son périmètre approximatif ?"
                    explanation = f"Le périmètre $\\approx {base} + {height} + {hypotenuse} \\approx {result}$ cm."
            else:  # cercle
                radius = random.randint(3, 10)
                if property_type == "périmètre":
                    result = round(2 * math.pi * radius, 2)
                    question = f"Un cercle a un rayon de {radius} cm. Quel est son périmètre ? (Utilise $\\pi \\approx 3.14$)"
                    explanation = f"Le périmètre d'un cercle $= 2 \\times \\pi \\times {radius} \\approx {result}$ cm."
                else:
                    result = round(math.pi * radius * radius, 2)
                    question = f"Un cercle a un rayon de {radius} cm. Quelle est son aire ? (Utilise $\\pi \\approx 3.14$)"
                    explanation = f"L'aire d'un cercle $= \\pi \\times {radius}^2 \\approx {result}$ cm²."

        geo_extras = [
            str(round(result * 0.5, 2)),
            str(round(result * 2, 2)),
            str(round(result * 1.5, 2)),
        ]
        choices = ensure_four_distinct_str_choices(str(result), geo_extras)
        try:
            _r_num = float(result)
        except (TypeError, ValueError):
            _r_num = 0.0
        geo_salt = len(question) + int(abs(_r_num * 100)) % 9_901

        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_GEOMETRIE, salt=geo_salt),
                "question": question,
                "correct_answer": str(result),
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.GEOMETRY,
                "explanation": explanation,
            }
        )
        return apply_test_title(exercise_data)
    elif normalized_type == ExerciseTypes.MIXTE:
        # Génération d'un exercice mixte avec PLUSIEURS opérations combinées
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        num_operations = type_limits.get("operations", 2)

        # Choisir un pattern de calcul mixte selon la difficulté
        if derived_difficulty == DifficultyLevels.INITIE:
            # Pour les débutants: 2 opérations simples sans priorité complexe
            patterns = [
                ("add_sub", lambda a, b, c: a + b - c, "{a} + {b} - {c}"),
                ("sub_add", lambda a, b, c: a - b + c, "{a} - {b} + {c}"),
                ("mult_add", lambda a, b, c: a * b + c, "{a} × {b} + {c}"),
            ]
        elif derived_difficulty == DifficultyLevels.PADAWAN:
            # Intermédiaire: priorité des opérations
            patterns = [
                ("add_mult", lambda a, b, c: a + b * c, "{a} + {b} × {c}"),
                ("sub_mult", lambda a, b, c: a - b * c, "{a} - {b} × {c}"),
                ("mult_sub", lambda a, b, c: a * b - c, "{a} × {b} - {c}"),
                ("div_add", lambda a, b, c: a // b + c, "{a} ÷ {b} + {c}"),
            ]
        else:
            # Avancé: parenthèses et opérations complexes
            patterns = [
                ("paren_add_mult", lambda a, b, c: (a + b) * c, "({a} + {b}) × {c}"),
                ("paren_sub_mult", lambda a, b, c: (a - b) * c, "({a} - {b}) × {c}"),
                ("mult_paren_add", lambda a, b, c: a * (b + c), "{a} × ({b} + {c})"),
                ("div_paren", lambda a, b, c: (a * b) // c, "({a} × {b}) ÷ {c}"),
            ]

        pattern_name, calc_func, template = random.choice(patterns)

        # Générer des nombres appropriés
        a = random.randint(min_val, max_val)
        b = random.randint(
            2, min(max_val, 10)
        )  # Garder b petit pour éviter les grands résultats
        c = random.randint(2, min(max_val, 10))

        # Ajustements pour éviter les résultats négatifs ou les divisions impossibles
        if "sub" in pattern_name and "paren" not in pattern_name:
            # Pour a - b * c, s'assurer que a > b * c
            if a <= b * c:
                a = b * c + random.randint(1, 10)
        if "div" in pattern_name:
            # S'assurer que la division est exacte
            if "paren" in pattern_name:
                # (a * b) ÷ c doit être exact
                temp = a * b
                if temp % c != 0:
                    c = random.choice([d for d in range(2, 6) if temp % d == 0] or [1])
            else:
                # a ÷ b doit être exact
                if a % b != 0:
                    a = b * random.randint(2, 5)

        result = calc_func(a, b, c)
        question = f"Calcule : {template.format(a=a, b=b, c=c)} = ?"

        # Explication détaillée
        if "paren" in pattern_name:
            explanation = f"Avec les parenthèses, on calcule d'abord l'intérieur, puis le reste. Résultat : {result}."
        else:
            explanation = f"Attention à la priorité des opérations ! La multiplication/division se fait avant l'addition/soustraction. Résultat : {result}."

        mix_pool = [
            str(result + random.randint(1, 5)),
            str(max(1, result - random.randint(1, 5))),
            str(a + b + c),
        ]
        choices = ensure_four_distinct_str_choices(str(result), mix_pool)
        mix_salt = a + b + c + result

        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_MIXTE, salt=mix_salt),
                "question": question,
                "correct_answer": str(result),
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.ADVANCED,
                "explanation": explanation,
            }
        )
        return apply_test_title(exercise_data)

    elif normalized_type == ExerciseTypes.DIVERS:
        # Génération d'un exercice divers (logique, conversions, probabilités, etc.)
        # Différent de TEXTE qui est orienté problèmes concrets avec contexte
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        problem_types = [
            "sequence",
            "conversion",
            "comparaison",
            "pourcentage",
            "moyenne",
        ]

        if derived_difficulty == DifficultyLevels.INITIE:
            problem_type = random.choice(["sequence", "comparaison"])
        elif derived_difficulty == DifficultyLevels.PADAWAN:
            problem_type = random.choice(["sequence", "conversion", "comparaison"])
        else:
            problem_type = random.choice(problem_types)

        if problem_type == "sequence":
            # Séquence logique (plus variée selon difficulté)
            if derived_difficulty in [
                DifficultyLevels.INITIE,
                DifficultyLevels.PADAWAN,
            ]:
                start = random.randint(1, 10)
                step = random.randint(1, 5)
                sequence = [start + step * i for i in range(4)]
                result = sequence[-1] + step
                question = f"Trouve le nombre suivant : {sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, ?"
                explanation = f"C'est une suite arithmétique où on ajoute {step} à chaque fois. Donc {sequence[3]} + {step} = {result}."
            else:
                # Séquence géométrique
                start = random.randint(2, 4)
                factor = random.randint(2, 3)
                sequence = [start * (factor**i) for i in range(4)]
                result = sequence[-1] * factor
                question = f"Trouve le nombre suivant : {sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, ?"
                explanation = f"C'est une suite géométrique où on multiplie par {factor} à chaque fois. Donc {sequence[3]} × {factor} = {result}."

        elif problem_type == "conversion":
            # Conversion d'unités
            conversions = [
                (
                    60,
                    "minutes",
                    "heure",
                    "Combien y a-t-il de minutes dans {n} heure(s) ?",
                    "{n} × 60 = {r} minutes",
                ),
                (
                    100,
                    "centimètres",
                    "mètre",
                    "Combien y a-t-il de centimètres dans {n} mètre(s) ?",
                    "{n} × 100 = {r} centimètres",
                ),
                (
                    1000,
                    "grammes",
                    "kilogramme",
                    "Combien y a-t-il de grammes dans {n} kilogramme(s) ?",
                    "{n} × 1000 = {r} grammes",
                ),
                (
                    24,
                    "heures",
                    "jour",
                    "Combien y a-t-il d'heures dans {n} jour(s) ?",
                    "{n} × 24 = {r} heures",
                ),
            ]
            factor, unit_small, unit_big, q_template, exp_template = random.choice(
                conversions
            )
            n = random.randint(1, 5)
            result = n * factor
            question = q_template.format(n=n)
            explanation = exp_template.format(n=n, r=result)

        elif problem_type == "comparaison":
            # Comparaison de nombres
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            if a == b:
                b = a + random.choice([-1, 1])
            result = max(a, b)
            question = f"Quel est le plus grand nombre : {a} ou {b} ?"
            explanation = f"En comparant {a} et {b}, le plus grand est {result}."

        elif problem_type == "pourcentage":
            # Pourcentage simple
            base = random.choice([10, 20, 50, 100])
            pct = random.choice([10, 20, 25, 50])
            result = base * pct // 100
            question = f"Combien font {pct}% de {base} ?"
            explanation = f"Pour calculer {pct}% de {base}, on fait {base} × {pct} ÷ 100 = {result}."

        else:  # moyenne
            # Moyenne entière exacte : on choisit le dernier terme pour que la somme soit
            # divisible par count (pas de troncature silencieuse avec //).
            numbers: list[int] = []
            count = 3
            for _gen in range(100):
                count = random.randint(3, 5)
                partial = 0
                nums: list[int] = []
                for _ in range(count - 1):
                    n = random.randint(min_val, max_val)
                    nums.append(n)
                    partial += n
                valid_last = [
                    x for x in range(min_val, max_val + 1) if (partial + x) % count == 0
                ]
                if valid_last:
                    nums.append(random.choice(valid_last))
                    numbers = nums
                    break
            if not numbers:
                count = random.randint(3, 5)
                K = random.randint(min_val, max_val)
                numbers = [K] * count

            total = sum(numbers)
            # total % count == 0 par construction (dernier terme ou [K]*count)
            result = total // count
            numbers_str = ", ".join(map(str, numbers))
            question = f"Quelle est la moyenne de ces nombres : {numbers_str} ?"
            explanation = f"La moyenne = somme ÷ nombre de valeurs = {total} ÷ {count} = {result}."

        div_pool = [str(result + k) for k in (-3, -1, 1, 2, 4, 7) if result + k > 0]
        choices = ensure_four_distinct_str_choices(str(result), div_pool)
        div_salt = result + len(question)

        exercise_data.update(
            {
                "title": pick_title_variant(SIMPLE_TITLE_DIVERS, salt=div_salt),
                "question": question,
                "correct_answer": str(result),
                "choices": choices,
                "tags": Tags.ALGORITHMIC + "," + Tags.LOGIC,
                "explanation": explanation,
            }
        )
        return apply_test_title(exercise_data)
    logger.info(
        "⚠️ Type d'exercice non géré dans generate_simple_exercise: %s, utilisation de ADDITION par défaut",
        normalized_type,
    )
    return default_addition_fallback(exercise_data, type_limits, ai_generated=False)
