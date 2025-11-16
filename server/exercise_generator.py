"""
Module de génération d'exercices pour enhanced_server.py
"""
import random
import json
from typing import Dict, List, Any, Optional

from app.core.constants import ExerciseTypes, DifficultyLevels, DIFFICULTY_LIMITS, Messages, Tags
from app.core.messages import ExerciseMessages, StarWarsNarratives
from app.services.enhanced_server_adapter import EnhancedServerAdapter

# Fonctions de normalisation
def normalize_exercise_type(exercise_type):
    """Normalise le type d'exercice"""
    if not exercise_type:
        return ExerciseTypes.ADDITION

    exercise_type = exercise_type.lower()

    # Parcourir tous les types d'exercices et leurs alias
    for type_key, aliases in ExerciseTypes.TYPE_ALIASES.items():
        if exercise_type in aliases:
            return type_key
    
    # Si aucune correspondance trouvée, logger un avertissement et retourner ADDITION par défaut
    print(f"⚠️ Type d'exercice non reconnu: {exercise_type}, utilisation de ADDITION par défaut")
    return ExerciseTypes.ADDITION

def normalize_difficulty(difficulty):
    """Normalise le niveau de difficulté"""
    if not difficulty:
        return DifficultyLevels.PADAWAN

    difficulty = difficulty.lower()

    # Parcourir tous les niveaux de difficulté et leurs alias
    for level_key, aliases in DifficultyLevels.LEVEL_ALIASES.items():
        if difficulty in aliases:
            return level_key
            
    # Si aucune correspondance trouvée, retourner la difficulté telle quelle
    return difficulty


def normalize_and_validate_exercise_params(exercise_type_raw: Optional[str], difficulty_raw: Optional[str]) -> tuple:
    """
    Normalise et valide les paramètres d'exercice de manière centralisée.
    
    Args:
        exercise_type_raw: Type d'exercice brut (peut être None)
        difficulty_raw: Difficulté brute (peut être None)
    
    Returns:
        Tuple (exercise_type, difficulty) normalisés et validés
    
    Raises:
        ValueError: Si les paramètres sont invalides après normalisation
    """
    from app.core.constants import ExerciseTypes
    
    # Normaliser les paramètres
    exercise_type = normalize_exercise_type(exercise_type_raw)
    difficulty = normalize_difficulty(difficulty_raw)
    
    # Valider que le type normalisé est valide
    if exercise_type not in ExerciseTypes.ALL_TYPES:
        print(f"⚠️ Type normalisé invalide: {exercise_type}, utilisation de ADDITION par défaut")
        exercise_type = ExerciseTypes.ADDITION
    
    return exercise_type, difficulty

# Fonctions de génération d'exercices
def generate_ai_exercise(exercise_type, difficulty):
    """
    Génère un exercice avec IA en utilisant des prompts et contextes Star Wars
    """
    normalized_type = normalize_exercise_type(exercise_type)
    normalized_difficulty = normalize_difficulty(difficulty)
    
    # Récupérer les limites pour ce type d'exercice et cette difficulté
    difficulty_config = DIFFICULTY_LIMITS.get(normalized_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN])
    type_limits = difficulty_config.get(normalized_type, difficulty_config.get("default", {"min": 1, "max": 10}))
    
    # Structure de base commune pour tous les types d'exercices générés par IA
    exercise_data = {
        "exercise_type": normalized_type,
        "difficulty": normalized_difficulty,
        "ai_generated": True,
        "tags": Tags.AI + "," + Tags.GENERATIVE + "," + Tags.STARWARS
    }
    
    # Préfixe et suffixe pour enrichir l'explication
    explanation_prefix = StarWarsNarratives.get_explanation_prefix(normalized_difficulty)
    explanation_suffix = StarWarsNarratives.get_explanation_suffix(normalized_difficulty)
    
    if normalized_type == ExerciseTypes.ADDITION:
        # Utiliser les limites de difficulté pour déterminer les plages de nombres
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        
        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)
        result = num1 + num2
        
        # Thème Star Wars pour l'addition
        if normalized_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice([
                f"Tu as trouvé {num1} cristaux Kyber et ton ami en a trouvé {num2}. Combien avez-vous de cristaux au total?",
                f"Il y a {num1} droïdes dans le hangar et {num2} droïdes dans l'atelier. Combien y a-t-il de droïdes en tout?",
                f"Tu as parcouru {num1} parsecs hier et {num2} parsecs aujourd'hui. Quelle distance as-tu parcourue en tout?"
            ])
            explanation_template = f"Pour trouver la réponse, tu dois additionner {num1} et {num2}, ce qui donne {result}."
        else:
            question_template = random.choice([
                f"Un escadron de {num1} X-wings et un escadron de {num2} Y-wings se préparent pour attaquer l'Étoile de la Mort. Combien de vaisseaux y a-t-il au total?",
                f"L'Empire a envoyé {num1} stormtroopers sur Endor et {num2} stormtroopers sur Hoth. Combien de stormtroopers ont été déployés en tout?",
                f"Un destroyer stellaire contient {num1} TIE fighters et {num2} navettes. Combien de vaisseaux sont à bord au total?"
            ])
            explanation_template = f"Pour calculer le total, on additionne les deux nombres: {num1} + {num2} = {result}."
        
        # Générer des choix intelligents avec erreurs typiques
        choices = generate_smart_choices("ADDITION", num1, num2, result, normalized_difficulty)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Alliance Rebelle - Addition niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        return exercise_data
        
    elif normalized_type == ExerciseTypes.SUBTRACTION:
        # Paramètres pour la soustraction avec des limites adaptatives
        min1 = type_limits.get("min1", 5)
        max1 = type_limits.get("max1", 20)
        min2 = type_limits.get("min2", 1)
        max2 = type_limits.get("max2", 5)
        
        num1 = random.randint(min1, max1)
        num2 = random.randint(min2, min(num1-1, max2))  # Eviter les soustractions avec résultat négatif
        result = num1 - num2
        
        # Thème Star Wars pour la soustraction
        if normalized_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice([
                f"Tu as {num1} portions de rations, mais tu en as utilisé {num2}. Combien te reste-t-il?",
                f"Il y avait {num1} droïdes dans le hangar, mais {num2} sont partis en mission. Combien reste-t-il de droïdes?",
                f"Tu as parcouru {num1} années-lumière, mais il te reste encore {num2} années-lumière à faire. Quelle distance as-tu déjà parcourue?"
            ])
            explanation_template = f"Pour trouver la réponse, tu dois soustraire {num2} de {num1}, ce qui donne {result}."
        else:
            question_template = random.choice([
                f"La flotte rebelle comptait {num1} vaisseaux, mais {num2} ont été détruits dans la bataille. Combien de vaisseaux reste-t-il?",
                f"L'Empire avait {num1} planètes sous son contrôle, mais {num2} se sont rebellées. Combien de planètes restent loyales?",
                f"Le Faucon Millenium a {num1} pièces de contrebande, mais {num2} sont confisquées par les Impériaux. Combien de pièces reste-t-il?"
            ])
            explanation_template = f"Pour calculer ce qui reste, on soustrait: {num1} - {num2} = {result}."
        
        # Générer des choix proches mais différents
        choices = [
            str(result),
            str(result + random.randint(1, min(5, max2))),
            str(result - random.randint(1, min(3, result//2))),
            str(num2 - num1)  # Erreur commune: inverser l'ordre de la soustraction
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Conflit galactique - Soustraction niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        return exercise_data
        
    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        # Utiliser des limites adaptées pour la multiplication
        min_val = type_limits.get("min", 2)
        max_val = type_limits.get("max", 10)
        
        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)
        result = num1 * num2
        
        # Thème Star Wars pour la multiplication
        if normalized_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice([
                f"Chaque Padawan a {num2} cristaux Kyber. S'il y a {num1} Padawans, combien de cristaux y a-t-il au total?",
                f"Chaque droïde astromech a {num2} outils. Combien d'outils ont {num1} droïdes au total?",
                f"Chaque module de formation a {num2} exercices. Combien d'exercices y a-t-il dans {num1} modules?"
            ])
            explanation_template = f"Pour trouver le total, tu dois multiplier le nombre de {num1} par {num2}, ce qui donne {result}."
        else:
            question_template = random.choice([
                f"Chaque escadron comprend {num2} X-wings. Combien de X-wings y a-t-il dans {num1} escadrons?",
                f"Chaque Star Destroyer transporte {num2} TIE Fighters. Combien de TIE Fighters y a-t-il sur {num1} Star Destroyers?",
                f"Chaque secteur contient {num2} systèmes stellaires. Combien de systèmes y a-t-il dans {num1} secteurs?"
            ])
            explanation_template = f"Pour calculer le total, on multiplie: {num1} × {num2} = {result}."
        
        # Générer des choix proches mais différents
        choices = [
            str(result),
            str(result + num1),  # Erreur: une fois de trop
            str(result - num2),  # Erreur: une fois de moins
            str(num1 + num2)  # Erreur: addition au lieu de multiplication
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Forces galactiques - Multiplication niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        return exercise_data
        
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
        
        # Thème Star Wars pour la division
        if normalized_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice([
                f"Tu as {num1} cristaux Kyber à distribuer équitablement entre {num2} Padawans. Combien de cristaux chaque Padawan recevra-t-il?",
                f"Il y a {num1} droïdes à répartir dans {num2} hangars. Combien de droïdes y aura-t-il dans chaque hangar?",
                f"Tu dois parcourir {num1} parsecs en {num2} jours. Combien de parsecs dois-tu parcourir chaque jour?"
            ])
            explanation_template = f"Pour trouver la réponse, tu dois diviser {num1} par {num2}, ce qui donne {result}."
        else:
            question_template = random.choice([
                f"L'Alliance a {num1} soldats à répartir équitablement dans {num2} bases. Combien de soldats seront affectés à chaque base?",
                f"L'Empire a fabriqué {num1} blasters qui doivent être distribués à {num2} escouades. Combien de blasters chaque escouade recevra-t-elle?",
                f"Un convoi de {num1} containers doit être réparti sur {num2} vaisseaux de transport. Combien de containers chaque vaisseau transportera-t-il?"
            ])
            explanation_template = f"Pour calculer le résultat, on divise: {num1} ÷ {num2} = {result}."
        
        # Générer des choix proches mais différents
        choices = [
            str(result),
            str(result + random.randint(1, min(5, result))),
            str(result - random.randint(1, min(3, result - 1) if result > 1 else 1)),
            str(num1 // (num2 + random.randint(1, 3)))  # Diviseur légèrement différent
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Stratégie galactique - Division niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.FRACTIONS:
        # Génération IA d'un exercice sur les fractions avec thème Star Wars
        from fractions import Fraction
        
        # Paramètres selon la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            denom1, denom2 = random.choice([2, 3, 4]), random.choice([2, 3, 4])
            num1, num2 = random.randint(1, denom1-1), random.randint(1, denom2-1)
            operation = "+"
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            denom1, denom2 = random.choice([2, 3, 4, 5, 6]), random.choice([2, 3, 4, 5, 6])
            num1, num2 = random.randint(1, denom1-1), random.randint(1, denom2-1)
            operation = random.choice(["+", "-"])
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            denom1, denom2 = random.randint(2, 8), random.randint(2, 8)
            num1, num2 = random.randint(1, denom1), random.randint(1, denom2)
            operation = random.choice(["+", "-", "×"])
        else:  # MAITRE
            denom1, denom2 = random.randint(2, 12), random.randint(2, 12)
            num1, num2 = random.randint(1, denom1*2), random.randint(1, denom2*2)
            operation = random.choice(["+", "-", "×", "÷"])
        
        # Calcul du résultat
        frac1, frac2 = Fraction(num1, denom1), Fraction(num2, denom2)
        if operation == "+":
            result = frac1 + frac2
            op_word = "additionner"
        elif operation == "-":
            if frac1 < frac2: frac1, frac2 = frac2, frac1  # Éviter les négatifs
            result = frac1 - frac2
            op_word = "soustraire"
        elif operation == "×":
            result = frac1 * frac2
            op_word = "multiplier"
        else:  # "÷"
            if num2 == 0: num2 = 1
            result = frac1 / frac2
            op_word = "diviser"
        
        # Format du résultat
        if result.denominator == 1:
            formatted_result = str(result.numerator)
        else:
            formatted_result = f"{result.numerator}/{result.denominator}"
        
        # Questions Star Wars selon la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            question_template = random.choice([
                f"Luke mange {num1}/{denom1} de sa ration et Leia mange {num2}/{denom2} de la sienne. Quelle fraction ont-ils mangée ensemble?",
                f"R2-D2 a réparé {num1}/{denom1} des systèmes et C-3PO {num2}/{denom2}. Quelle fraction totale ont-ils réparée?",
                f"Dans le Faucon Millenium, {num1}/{denom1} des moteurs fonctionnent et {num2}/{denom2} des boucliers. Quelle fraction totale est opérationnelle?"
            ])
        else:
            question_template = random.choice([
                f"L'Étoile de la Mort a détruit {num1}/{denom1} de la flotte rebelle, puis {num2}/{denom2} de plus. Quelle fraction totale a été détruite?",
                f"Yoda maîtrise {num1}/{denom1} de la Force et enseigne {num2}/{denom2} de ses connaissances. Quelle fraction a-t-il transmise?",
                f"L'Empire contrôle {num1}/{denom1} de la galaxie et conquiert {num2}/{denom2} de plus. Quelle fraction contrôle-t-il maintenant?"
            ])
        
        # Choix avec erreurs typiques
        incorrect1 = f"{num1+num2}/{denom1+denom2}"  # Erreur: additionner num et denom
        incorrect2 = f"{num1}/{denom2}"  # Confusion des dénominateurs
        incorrect3 = f"{num2}/{denom1}"  # Inversion
        
        choices = [formatted_result, incorrect1, incorrect2, incorrect3]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Fractions Jedi - Niveau {difficulty}",
            "question": f"Problème galactique: {question_template.replace(f'{num1}/{denom1} {operation} {num2}/{denom2}', f'{num1}/{denom1} {operation} {num2}/{denom2}')}",
            "correct_answer": formatted_result,
            "choices": choices,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} Pour {op_word} les fractions {num1}/{denom1} et {num2}/{denom2}, le résultat est {formatted_result}. {explanation_suffix}"
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.GEOMETRIE:
        # Génération IA d'un exercice de géométrie avec thème Star Wars
        import math
        
        # Formes et propriétés selon la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            shape = random.choice(["carré", "rectangle"])
            property = random.choice(["périmètre", "aire"])
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            shape = random.choice(["carré", "rectangle", "triangle"])
            property = random.choice(["périmètre", "aire"])
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
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
                formula = f"4 × {side}"
            else:  # aire
                result = side * side
                formula = f"{side}²"
            
            question_template = random.choice([
                f"L'Étoile de la Mort a une section carrée de côté {side} km. Quel est son {property}?",
                f"La base rebelle a un hangar carré de {side} m de côté. Calcule son {property}.",
                f"Le Temple Jedi a une salle carrée de {side} m de côté. Quel est son {property}?"
            ])
            
        elif shape == "rectangle":
            length = random.randint(type_limits.get("min", 4), type_limits.get("max", 20))
            width = random.randint(type_limits.get("min", 3), length-1)
            if property == "périmètre":
                result = 2 * (length + width)
                formula = f"2 × ({length} + {width})"
            else:  # aire
                result = length * width
                formula = f"{length} × {width}"
            
            question_template = random.choice([
                f"Le Faucon Millenium a une soute rectangulaire de {length}m × {width}m. Quel est son {property}?",
                f"Un Star Destroyer a un hangar de {length} km sur {width} km. Calcule son {property}.",
                f"La cantina de Mos Eisley mesure {length}m × {width}m. Quel est son {property}?"
            ])
            
        elif shape == "triangle":
            base = random.randint(type_limits.get("min", 4), type_limits.get("max", 15))
            height = random.randint(type_limits.get("min", 3), type_limits.get("max", 12))
            if property == "aire":
                result = (base * height) / 2
                formula = f"({base} × {height}) ÷ 2"
            else:  # périmètre approximatif
                hypotenuse = round(math.sqrt(base*base + height*height), 1)
                result = base + height + hypotenuse
                formula = f"{base} + {height} + {hypotenuse}"
            
            question_template = random.choice([
                f"Un X-wing a des ailes triangulaires de base {base}m et hauteur {height}m. Quelle est leur {property}?",
                f"Le sabre laser de Yoda forme un triangle de base {base} cm et hauteur {height} cm. Calcule son {property}.",
                f"Une voile solaire triangulaire mesure {base}km × {height}km. Quel est son {property}?"
            ])
            
        else:  # cercle
            radius = random.randint(type_limits.get("min", 2), type_limits.get("max", 10))
            if property == "périmètre":
                result = round(2 * math.pi * radius, 2)
                formula = f"2 × π × {radius}"
            else:  # aire
                result = round(math.pi * radius * radius, 2)
                formula = f"π × {radius}²"
            
            question_template = random.choice([
                f"L'Étoile de la Mort a un rayon de {radius} km. Quel est son {property}?",
                f"La planète Tatooine a un rayon de {radius} milliers de km. Calcule son {property}.",
                f"Un bouclier déflecteur circulaire a un rayon de {radius}m. Quel est son {property}?"
            ])
        
        # Choix avec erreurs typiques
        choices = [
            str(result),
            str(round(result * 0.5, 2)),  # Moitié
            str(round(result * 2, 2)),    # Double
            str(round(result * 1.5, 2))   # 1.5 fois
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Géométrie Galactique - Niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} Pour calculer le {property} d'un {shape}, on utilise: {formula} = {result}. {explanation_suffix}"
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.DIVERS:
        # Génération IA d'exercices divers avec thème Star Wars
        
        # Types de problèmes selon la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            problem_type = random.choice(["age", "monnaie", "temps"])
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            problem_type = random.choice(["age", "monnaie", "vitesse", "pourcentage_simple"])
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            problem_type = random.choice(["vitesse", "pourcentage", "probabilité"])
        else:  # MAITRE
            problem_type = random.choice(["probabilité", "séquence", "logique_avancée"])
        
        # Génération selon le type
        if problem_type == "age":
            age_actuel = random.randint(type_limits.get("min", 8), type_limits.get("max", 25))
            années = random.randint(1, 10)
            result = age_actuel + années
            
            question_template = random.choice([
                f"Luke a {age_actuel} ans. Dans {années} ans, quel âge aura-t-il?",
                f"Leia a {age_actuel} ans aujourd'hui. Quel âge aura-t-elle dans {années} ans?",
                f"Anakin a {age_actuel} ans. Dans combien d'années aura-t-il {result} ans?"
            ])
            explanation_template = f"Pour trouver l'âge futur: {age_actuel} + {années} = {result} ans."
            
        elif problem_type == "monnaie":
            prix = random.randint(type_limits.get("min", 5), type_limits.get("max", 50))
            payé = random.randint(prix + 1, prix + 20)
            result = payé - prix
            
            question_template = random.choice([
                f"Tu achètes un sabre laser à {prix} crédits. Tu paies {payé} crédits. Combien de monnaie?",
                f"Un droïde coûte {prix} crédits. Tu donnes {payé} crédits. Quelle est la monnaie?",
                f"Des rations coûtent {prix} crédits. Tu paies avec {payé} crédits. Combien récupères-tu?"
            ])
            explanation_template = f"Monnaie = montant payé - prix: {payé} - {prix} = {result} crédits."
            
        elif problem_type == "vitesse":
            distance = random.randint(type_limits.get("min", 10), type_limits.get("max", 100))
            temps = random.randint(2, 10)
            result = distance // temps
            
            question_template = random.choice([
                f"Le Faucon Millenium parcourt {distance} parsecs en {temps} heures. Quelle est sa vitesse?",
                f"Un X-wing vole {distance} km en {temps} minutes. Quelle est sa vitesse par minute?",
                f"Un Star Destroyer voyage {distance} années-lumière en {temps} jours. Vitesse par jour?"
            ])
            explanation_template = f"Vitesse = distance ÷ temps: {distance} ÷ {temps} = {result}."
            
        elif problem_type == "pourcentage" or problem_type == "pourcentage_simple":
            initial = random.randint(type_limits.get("min", 20), type_limits.get("max", 100))
            pourcentage = random.choice([10, 20, 25, 50])
            result = initial + (initial * pourcentage // 100)
            
            question_template = random.choice([
                f"L'Empire a {initial} vaisseaux. Leur nombre augmente de {pourcentage}%. Nouveau total?",
                f"La Rébellion a {initial} soldats. Ils recrutent {pourcentage}% de plus. Combien maintenant?",
                f"Jabba possède {initial} crédits. Il gagne {pourcentage}% de plus. Nouveau montant?"
            ])
            explanation_template = f"Augmentation: {initial} + ({initial} × {pourcentage}%) = {result}."
            
        elif problem_type == "probabilité":
            total = random.randint(10, 30)
            favorables = random.randint(1, total // 3)
            result = f"{favorables}/{total}"
            
            question_template = random.choice([
                f"Dans un sac, {total} cristaux dont {favorables} sont bleus. Probabilité d'un cristal bleu?",
                f"Sur {total} planètes, {favorables} sont habitées. Probabilité qu'une planète soit habitée?",
                f"Parmi {total} droïdes, {favorables} sont défaillants. Probabilité d'un droïde défaillant?"
            ])
            explanation_template = f"Probabilité = cas favorables ÷ total: {favorables} ÷ {total} = {result}."
            
        elif problem_type == "séquence":
            start = random.randint(2, 8)
            diff = random.randint(2, 5)
            sequence = [start + diff*i for i in range(4)]
            result = sequence[-1] + diff
            
            question_template = f"Séquence Jedi: {', '.join(map(str, sequence))}, ... Quel est le terme suivant?"
            explanation_template = f"La séquence augmente de {diff}: {sequence[-1]} + {diff} = {result}."
            
        else:  # logique_avancée
            a, b = random.randint(5, 15), random.randint(2, 8)
            result = a * b
            
            question_template = random.choice([
                f"Yoda dit: 'Si {a} Padawans s'entraînent {b} heures chacun, combien d'heures au total?'",
                f"L'Empire déploie {a} escadrons de {b} TIE Fighters. Combien de TIE Fighters?",
                f"Dans {a} systèmes, il y a {b} planètes chacun. Combien de planètes au total?"
            ])
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
                str(result * 2)
            ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Défis Galactiques - Niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.MIXTE:
        # Génération IA d'un exercice mixte avec thème Star Wars
        operation_types = [ExerciseTypes.ADDITION, ExerciseTypes.SUBTRACTION, 
                          ExerciseTypes.MULTIPLICATION, ExerciseTypes.DIVISION]
        chosen_operation = random.choice(operation_types)
        
        # Générer un exercice du type choisi avec contexte Star Wars enrichi
        if chosen_operation == ExerciseTypes.ADDITION:
            min_val = type_limits.get("min", 1)
            max_val = type_limits.get("max", 10)
            num1 = random.randint(min_val, max_val)
            num2 = random.randint(min_val, max_val)
            result = num1 + num2
            
            if normalized_difficulty == DifficultyLevels.INITIE:
                question_template = random.choice([
                    f"Dans la cantina de Mos Eisley, {num1} contrebandiers rejoignent {num2} pilotes rebelles. Combien de personnes y a-t-il maintenant?",
                    f"Luke a collecté {num1} cristaux Kyber et Leia en a trouvé {num2} autres. Combien ont-ils de cristaux ensemble?",
                    f"R2-D2 a {num1} outils et C-3PO en a {num2}. Combien d'outils ont-ils au total?"
                ])
            else:
                question_template = random.choice([
                    f"L'escadron Rouge compte {num1} X-wings et reçoit {num2} renforts. Combien de vaisseaux ont-ils au total?",
                    f"Un destroyer stellaire transporte {num1} TIE Fighters et {num2} navettes impériales. Combien de vaisseaux au total?",
                    f"La base rebelle a {num1} soldats et reçoit {num2} nouvelles recrues. Combien de soldats maintenant?"
                ])
            explanation_template = f"Pour cette addition galactique: {num1} + {num2} = {result}."
            
        elif chosen_operation == ExerciseTypes.SUBTRACTION:
            num1 = random.randint(type_limits.get("min1", 10), type_limits.get("max1", 25))
            num2 = random.randint(type_limits.get("min2", 1), min(num1-1, type_limits.get("max2", 8)))
            result = num1 - num2
            
            if normalized_difficulty == DifficultyLevels.INITIE:
                question_template = random.choice([
                    f"Tu as {num1} portions de rations, mais tu en as utilisé {num2}. Combien te reste-t-il?",
                    f"Il y avait {num1} droïdes dans le hangar, mais {num2} sont partis en mission. Combien restent?",
                    f"Yoda avait {num1} sabres laser, mais {num2} ont été perdus. Combien lui reste-t-il?"
                ])
            else:
                question_template = random.choice([
                    f"L'Empire avait {num1} TIE Fighters, mais {num2} ont été détruits par la Rébellion. Combien en reste-t-il?",
                    f"Jabba possédait {num1} crédits, mais il en a perdu {num2} au sabacc. Combien lui reste-t-il?",
                    f"La flotte impériale comptait {num1} vaisseaux, mais {num2} ont déserté. Combien restent loyaux?"
                ])
            explanation_template = f"Pour cette soustraction stratégique: {num1} - {num2} = {result}."
            
        elif chosen_operation == ExerciseTypes.MULTIPLICATION:
            min_val = type_limits.get("min", 2)
            max_val = type_limits.get("max", 8)
            num1 = random.randint(min_val, max_val)
            num2 = random.randint(min_val, max_val)
            result = num1 * num2
            
            if normalized_difficulty == DifficultyLevels.INITIE:
                question_template = random.choice([
                    f"Chaque Padawan a {num2} cristaux Kyber. S'il y a {num1} Padawans, combien de cristaux au total?",
                    f"Chaque droïde a {num2} outils. Combien d'outils ont {num1} droïdes?",
                    f"Chaque X-wing a {num2} missiles. Combien de missiles pour {num1} X-wings?"
                ])
            else:
                question_template = random.choice([
                    f"Chaque Star Destroyer transporte {num2} escadrons de {num1} TIE Fighters chacun. Combien de TIE Fighters au total?",
                    f"Dans {num1} systèmes stellaires, il y a {num2} planètes habitées chacun. Combien de planètes au total?",
                    f"Chaque base rebelle a {num2} hangars avec {num1} vaisseaux chacun. Combien de vaisseaux au total?"
                ])
            explanation_template = f"Pour cette multiplication tactique: {num1} × {num2} = {result}."
            
        else:  # DIVISION
            num2 = random.randint(type_limits.get("min_divisor", 2), type_limits.get("max_divisor", 6))
            result = random.randint(type_limits.get("min_result", 2), type_limits.get("max_result", 8))
            num1 = num2 * result
            
            if normalized_difficulty == DifficultyLevels.INITIE:
                question_template = random.choice([
                    f"Tu as {num1} cristaux Kyber à distribuer entre {num2} Padawans. Combien chacun en recevra-t-il?",
                    f"Il y a {num1} droïdes à répartir dans {num2} hangars. Combien par hangar?",
                    f"Yoda a {num1} sabres laser à donner à {num2} Jedi. Combien chacun en aura-t-il?"
                ])
            else:
                question_template = random.choice([
                    f"L'Alliance doit répartir {num1} soldats équitablement dans {num2} bases. Combien de soldats par base?",
                    f"Un convoi de {num1} containers doit être chargé sur {num2} vaisseaux. Combien de containers par vaisseau?",
                    f"L'Empire a {num1} stormtroopers à déployer sur {num2} planètes. Combien par planète?"
                ])
            explanation_template = f"Pour cette division logistique: {num1} ÷ {num2} = {result}."
        
        # Générer des choix avec erreurs typiques
        choices = [
            str(result),
            str(result + random.randint(1, 5)),
            str(max(1, result - random.randint(1, 3))),
            str(result + random.randint(6, 10))
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Opération Mixte - {chosen_operation.title()} niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "num1": num1,
            "num2": num2,
            "operation": chosen_operation,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        return exercise_data
        
    elif normalized_type == ExerciseTypes.TEXTE:
        # Génération IA d'exercices textuels avec thème Star Wars
        
        # Générer des nombres aléatoirement selon la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            base_num = random.randint(3, 8)
            modifier = random.randint(2, 5)
            large_num = random.randint(10, 20)
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            base_num = random.randint(5, 12)
            modifier = random.randint(3, 7)
            large_num = random.randint(15, 30)
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            base_num = random.randint(8, 15)
            modifier = random.randint(4, 9)
            large_num = random.randint(20, 50)
        else:  # MAITRE
            base_num = random.randint(10, 25)
            modifier = random.randint(5, 12)
            large_num = random.randint(30, 100)
        
        # Choisir un type de problème selon la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            problem_types = ["simple_addition", "simple_subtraction", "simple_multiplication"]
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            problem_types = ["two_step", "sequence", "comparison"]
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            problem_types = ["multi_step", "ratio", "logic_puzzle"]
        else:  # MAITRE
            problem_types = ["complex_multi_step", "algebraic", "advanced_logic"]
        
        problem_type = random.choice(problem_types)
        
        # Générer le problème selon le type
        if problem_type == "simple_addition":
            result = base_num + modifier
            question_template = random.choice([
                f"R2-D2 a {base_num} droïdes amis. C-3PO en a {modifier} de plus que R2-D2. Combien C-3PO a-t-il d'amis droïdes?",
                f"Luke a {base_num} sabres laser. Il en trouve {modifier} autres dans un temple Jedi. Combien en a-t-il maintenant?",
                f"Dans la cantina, il y a {base_num} contrebandiers et {modifier} pilotes rebelles arrivent. Combien de personnes au total?"
            ])
            
        elif problem_type == "simple_subtraction":
            result = large_num - base_num
            question_template = random.choice([
                f"Luke avait {large_num} sabres laser. Il en donne {base_num} à ses Padawans. Combien lui en reste-t-il?",
                f"L'Empire avait {large_num} TIE Fighters. {base_num} ont été détruits par la Rébellion. Combien en reste-t-il?",
                f"Yoda possédait {large_num} cristaux Kyber. Il en utilise {base_num} pour l'entraînement. Combien lui reste-t-il?"
            ])
            
        elif problem_type == "simple_multiplication":
            result = base_num * modifier
            question_template = random.choice([
                f"Dans la cantina, il y a {base_num} tables. Chaque table peut accueillir {modifier} personnes. Combien de personnes peuvent s'asseoir au total?",
                f"Chaque X-wing a {modifier} missiles. Combien de missiles ont {base_num} X-wings?",
                f"Chaque Padawan s'entraîne {modifier} heures par jour. Combien d'heures pour {base_num} Padawans?"
            ])
            
        elif problem_type == "two_step":
            step1_result = base_num * modifier
            result = step1_result - base_num
            question_template = random.choice([
                f"Leia a {base_num} crédits. Elle achète {modifier} blasters à {base_num} crédits chacun. Combien lui reste-t-il?",
                f"Un X-wing consomme {modifier} unités de carburant par parsec. Pour un voyage de {base_num} parsecs, combien d'unités faut-il?",
                f"Obi-Wan a {base_num} Padawans. Chacun a {modifier} sabres laser. Combien de sabres au total?"
            ])
            if "reste-t-il" in question_template:
                result = base_num - step1_result if base_num > step1_result else step1_result - base_num
            else:
                result = step1_result
                
        elif problem_type == "sequence":
            # Séquence arithmétique
            start = base_num
            step = modifier
            result = start + (3 * step)  # 4ème terme
            sequence = f"{start}, {start + step}, {start + 2*step}, {start + 3*step}"
            question_template = random.choice([
                f"Yoda entraîne ses Padawans en séquence: {start}, {start + step}, {start + 2*step}... Quel est le prochain nombre dans cette séquence de la Force?",
                f"Les coordonnées galactiques suivent cette séquence: {start}, {start + step}, {start + 2*step}... Quelle est la prochaine coordonnée?",
                f"Le code d'accès Jedi suit ce motif: {start}, {start + step}, {start + 2*step}... Quel est le nombre suivant?"
            ])
            
        elif problem_type == "comparison":
            multiplier = random.randint(2, 4)
            result = base_num * multiplier
            question_template = random.choice([
                f"Dans une bataille, l'Alliance a {multiplier} fois plus de X-wings que l'Empire a de TIE Fighters. Si l'Empire a {base_num} TIE Fighters, combien l'Alliance a-t-elle de X-wings?",
                f"Un destroyer stellaire transporte {multiplier} fois plus de soldats qu'une corvette. Si une corvette a {base_num} soldats, combien le destroyer en a-t-il?",
                f"Jabba a {multiplier} fois plus de crédits que Han Solo. Si Han a {base_num} crédits, combien Jabba en a-t-il?"
            ])
            
        else:  # Types plus complexes pour niveaux élevés
            result = base_num + modifier
            question_template = f"Problème Jedi complexe: La somme de deux nombres consécutifs est {result + result - 1}. Quel est le plus petit nombre?"
            result = base_num  # Pour les problèmes algébriques
        
        # Générer des choix incorrects plausibles
        choices = [
            str(result),
            str(result + random.randint(1, 5)),
            str(max(1, result - random.randint(1, 3))),
            str(result * 2) if result < 50 else str(result // 2)
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Énigme Jedi - Niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} Pour résoudre ce problème, il faut analyser les données et appliquer les bonnes opérations mathématiques. {explanation_suffix}"
        })
        return exercise_data

    # Si aucun type correspondant, retourner un exercice d'addition par défaut
    min_val = type_limits.get("min", 1)
    max_val = type_limits.get("max", 10)
    num1 = random.randint(min_val, max_val)
    num2 = random.randint(min_val, max_val)
    result = num1 + num2
    
    exercise_data.update({
        "title": ExerciseMessages.TITLE_DEFAULT,
        "question": ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2),
        "correct_answer": str(result),
        "choices": [str(result), str(result-1), str(result+1), str(result+2)],
        "num1": num1,
        "num2": num2,
        "explanation": f"Pour additionner {num1} et {num2}, il faut calculer leur somme, donc {num1} + {num2} = {result}."
    })
    
    return exercise_data 

def ensure_explanation(exercise_dict):
    """S'assure qu'un exercice a une explication valide"""
    # S'assurer que l'explication est définie et n'est pas None
    if 'explanation' not in exercise_dict or exercise_dict['explanation'] is None or exercise_dict['explanation'] == "None" or exercise_dict['explanation'] == "":
        if exercise_dict['exercise_type'] == ExerciseTypes.ADDITION:
            exercise_dict['explanation'] = f"Pour additionner {exercise_dict.get('num1', '?')} et {exercise_dict.get('num2', '?')}, il faut calculer leur somme: {exercise_dict['correct_answer']}"
        elif exercise_dict['exercise_type'] == ExerciseTypes.SUBTRACTION:
            exercise_dict['explanation'] = f"Pour soustraire {exercise_dict.get('num2', '?')} de {exercise_dict.get('num1', '?')}, il faut calculer leur différence: {exercise_dict['correct_answer']}"
        elif exercise_dict['exercise_type'] == ExerciseTypes.MULTIPLICATION:
            exercise_dict['explanation'] = f"Pour multiplier {exercise_dict.get('num1', '?')} par {exercise_dict.get('num2', '?')}, il faut calculer leur produit: {exercise_dict['correct_answer']}"
        elif exercise_dict['exercise_type'] == ExerciseTypes.DIVISION:
            exercise_dict['explanation'] = f"Pour diviser {exercise_dict.get('num1', '?')} par {exercise_dict.get('num2', '?')}, il faut calculer leur quotient: {exercise_dict['correct_answer']}"
        else:
            exercise_dict['explanation'] = f"La réponse correcte est {exercise_dict['correct_answer']}"
    
    return exercise_dict 

def generate_simple_exercise(exercise_type, difficulty):
    """Génère un exercice simple sans IA"""
    
    normalized_type = normalize_exercise_type(exercise_type)
    normalized_difficulty = normalize_difficulty(difficulty)
    
    # Récupérer les limites pour ce type d'exercice et cette difficulté
    difficulty_config = DIFFICULTY_LIMITS.get(normalized_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN])
    type_limits = difficulty_config.get(normalized_type, difficulty_config.get("default", {"min": 1, "max": 10}))
    
    # Structure de base commune pour tous les types d'exercices
    exercise_data = {
        "exercise_type": normalized_type,
        "difficulty": normalized_difficulty,
        "ai_generated": False,
        "tags": Tags.ALGORITHMIC
    }
    
    if normalized_type == ExerciseTypes.ADDITION:
        # Génération d'une addition
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        
        result = num1 + num2
        question = ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        
        # Générer des choix proches mais différents selon la difficulté
        error_margin = max(1, min(int(max_val * 0.1), 10))  # Marge d'erreur proportionnelle à la difficulté
        
        choices = [
            str(result),  # Bonne réponse
            str(result + random.randint(1, error_margin)),
            str(result - random.randint(1, error_margin)),
            str(num1 * num2) if num1 * num2 != result else str(result + error_margin + 1)  # Distraction: multiplication
        ]
        random.shuffle(choices)

        exercise_data.update({
            "title": ExerciseMessages.TITLE_ADDITION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour additionner {num1} et {num2}, il faut calculer leur somme, donc {num1} + {num2} = {result}."
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.SUBTRACTION:
        # Génération d'une soustraction
        limits = type_limits
        num1 = random.randint(limits.get("min1", 5), limits.get("max1", 20))
        num2 = random.randint(limits.get("min2", 1), min(num1-1, limits.get("max2", 5)))  # Assurer num2 < num1
        
        result = num1 - num2
        question = ExerciseMessages.QUESTION_SUBTRACTION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        
        # Générer des choix proches mais différents selon la difficulté
        error_margin = max(1, min(int(limits.get("max2", 5) * 0.2), 10))
        
        choices = [
            str(result),  # Bonne réponse
            str(result + random.randint(1, error_margin)),
            str(result - random.randint(1, min(error_margin, result-1) if result > 1 else 1)),
            str(num2 - num1) if num2 > num1 else str(result + error_margin + 2)  # Erreur: inversion de l'ordre
        ]
        random.shuffle(choices)

        exercise_data.update({
            "title": ExerciseMessages.TITLE_SUBTRACTION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour soustraire {num2} de {num1}, il faut calculer leur différence, donc {num1} - {num2} = {result}."
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.MULTIPLICATION:
        # Génération d'une multiplication
        min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
        num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
        
        result = num1 * num2
        question = ExerciseMessages.QUESTION_MULTIPLICATION.format(num1=num1, num2=num2)
        correct_answer = str(result)
        
        # Générer des choix proches mais différents selon la difficulté
        choices = [
            str(result),  # Bonne réponse
            str(result + num1),  # Erreur: une fois de trop
            str(result - num2),  # Erreur: une fois de moins
            str(num1 + num2)  # Erreur: addition au lieu de multiplication
        ]
        random.shuffle(choices)

        exercise_data.update({
            "title": ExerciseMessages.TITLE_MULTIPLICATION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour multiplier {num1} par {num2}, il faut calculer leur produit, donc {num1} × {num2} = {result}."
        })
        return exercise_data

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
        
        # Générer des choix proches mais différents selon la difficulté
        choices = [
            str(result),  # Bonne réponse
            str(result + 1),  # Une de plus
            str(max(1, result - 1)),  # Une de moins (minimum 1)
            str(num1 // (num2 + 1)) if num2 < 9 else str(result + 2)  # Diviseur légèrement différent
        ]
        random.shuffle(choices)

        exercise_data.update({
            "title": ExerciseMessages.TITLE_DIVISION,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": f"Pour diviser {num1} par {num2}, il faut calculer leur quotient, donc {num1} ÷ {num2} = {result}."
        })
        return exercise_data
    
    elif normalized_type == ExerciseTypes.TEXTE:
        # Génération d'un exercice textuel (problèmes logiques, énigmes, etc.)
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        
        # Choisir un type de problème textuel en fonction de la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            # Problèmes textuels simples pour débutants
            problem_type = random.choice(["logique_simple", "devinette_nombre", "probleme_concret"])
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            problem_type = random.choice(["logique_simple", "devinette_nombre", "probleme_concret", "sequence_simple"])
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            problem_type = random.choice(["logique_avance", "enigme_math", "probleme_etapes", "sequence_avance"])
        else:  # MAITRE
            problem_type = random.choice(["logique_complexe", "enigme_complexe", "probleme_multi_etapes", "code_secret"])
        
        # Logique pour chaque type de problème textuel
        if problem_type == "logique_simple":
            # Problème logique simple
            objets = random.choice([
                ("sabres laser", "Luke"),
                ("droïdes", "R2-D2"),
                ("vaisseaux", "l'Alliance"),
                ("cristaux", "Yoda")
            ])
            objet, personnage = objets
            
            initial = random.randint(min_val, max_val)
            donnés = random.randint(1, initial-1)
            result = initial - donnés
            
            problem = f"{personnage} a {initial} {objet}. Il en donne {donnés} à ses amis. Combien lui en reste-t-il ?"
            explanation = f"Pour trouver ce qui reste, on soustrait ce qui a été donné du total initial. Donc {initial} - {donnés} = {result}."
            answer_type = "number"
            
        elif problem_type == "devinette_nombre":
            # Devinette sur un nombre
            if normalized_difficulty == DifficultyLevels.INITIE:
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
            # Problème concret avec contexte Star Wars
            scenarios = [
                {
                    "context": "Dans la cantina de Mos Eisley",
                    "action": "Luke commande {nb1} boissons à {prix} crédits chacune",
                    "question": "Combien paie-t-il au total ?",
                    "calc": lambda nb1, prix: nb1 * prix,
                    "explanation": "Pour calculer le total, on multiplie le nombre de boissons par le prix unitaire. Donc {nb1} × {prix} = {result}."
                },
                {
                    "context": "Sur la planète Tatooine",
                    "action": "Anakin trouve {nb1} pièces. Il en perd {nb2} dans le désert",
                    "question": "Combien lui en reste-t-il ?",
                    "calc": lambda nb1, nb2: nb1 - nb2,
                    "explanation": "Pour trouver ce qui reste, on soustrait ce qui est perdu du total initial. Donc {nb1} - {nb2} = {result}."
                },
                {
                    "context": "Dans l'escadron de X-Wings",
                    "action": "Il y a {nb1} pilotes répartis équitablement dans {nb2} escouades",
                    "question": "Combien de pilotes par escouade ?",
                    "calc": lambda nb1, nb2: nb1 // nb2,
                    "explanation": "Pour répartir équitablement, on divise le nombre total par le nombre d'escouades. Donc {nb1} ÷ {nb2} = {result}."
                }
            ]
            
            scenario = random.choice(scenarios)
            nb1 = random.randint(min_val, max_val)
            nb2 = random.randint(2, min(nb1, 5)) if "divise" in scenario["explanation"] else random.randint(1, min_val)
            
            # Ajuster pour éviter les divisions impossibles
            if "÷" in scenario["explanation"] and nb1 % nb2 != 0:
                nb1 = nb2 * random.randint(2, 5)  # Assurer une division exacte
            
            result = scenario["calc"](nb1, nb2)
            
            problem = f"{scenario['context']}, {scenario['action'].format(nb1=nb1, nb2=nb2, prix=nb2)}. {scenario['question']}"
            explanation = scenario["explanation"].format(nb1=nb1, nb2=nb2, result=result)
            answer_type = "number"
            
        elif problem_type == "sequence_simple":
            # Séquence simple
            start = random.randint(1, 5)
            step = random.randint(1, 3)
            sequence = [start + step*i for i in range(4)]
            result = sequence[-1] + step
            
            problem = f"Quelle est la suite logique : {sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, ... ?"
            explanation = f"Cette séquence augmente de {step} à chaque terme. Le terme suivant est donc {sequence[3]} + {step} = {result}."
            answer_type = "number"
            
        else:
            # Problème par défaut pour les types non implémentés
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            result = a + b
            
            problem = f"Luke a {a} sabres laser. Leia lui en donne {b} de plus. Combien Luke a-t-il de sabres laser maintenant ?"
            explanation = f"Pour trouver le total, on additionne les sabres laser de Luke et ceux de Leia. Donc {a} + {b} = {result}."
            answer_type = "number"
        
        # Créer des choix appropriés
        if answer_type == "number":
            choices = [
                str(result),
                str(result + random.randint(1, 3)),
                str(max(1, result - random.randint(1, 3))),
                str(result + random.randint(4, 6))
            ]
        else:
            # Pour les réponses textuelles (si nécessaire)
            choices = [str(result), "Autre réponse 1", "Autre réponse 2", "Autre réponse 3"]
            
        random.shuffle(choices)
        
        # Construire l'exercice
        exercise_data.update({
            "title": "Problème textuel",
            "question": problem,
            "correct_answer": str(result),
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + "texte",
            "explanation": explanation,
            "answer_type": answer_type  # Métadonnée pour l'interface
        })
        
        return exercise_data

    elif normalized_type == ExerciseTypes.FRACTIONS:
        # Génération d'un exercice sur les fractions
        from fractions import Fraction
        
        if normalized_difficulty == DifficultyLevels.INITIE:
            denominator = random.choice([2, 3, 4])
            numerator = 1
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            denominator = random.choice([2, 3, 4, 5])
            numerator = random.randint(1, denominator - 1)
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            denominator = random.choice([4, 5, 6, 8])
            numerator = random.randint(1, denominator - 1)
        else:  # MAITRE
            denominator = random.choice([6, 8, 9, 12])
            numerator = random.randint(1, denominator - 1)
        
        question = f"Quelle fraction représente {numerator} part{'s' if numerator > 1 else ''} sur {denominator} ?"
        correct_answer = f"{numerator}/{denominator}"
        
        choices = [
            correct_answer,
            f"{denominator}/{numerator}",  # Inversion
            f"{numerator}/{denominator + 1}",  # Dénominateur incorrect
            f"{numerator + 1}/{denominator}"  # Numérateur incorrect
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": "Exercice sur les fractions",
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.FRACTIONS,
            "explanation": f"Une fraction représente une partie d'un tout. {numerator} part{'s' if numerator > 1 else ''} sur {denominator} s'écrit {correct_answer}."
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.GEOMETRIE:
        # Génération d'un exercice de géométrie
        import math
        
        if normalized_difficulty == DifficultyLevels.INITIE:
            shape = random.choice(["carré", "rectangle"])
            if shape == "carré":
                side = random.randint(3, 10)
                property_type = random.choice(["périmètre", "aire"])
                if property_type == "périmètre":
                    result = 4 * side
                    question = f"Un carré a un côté de {side} cm. Quel est son périmètre ?"
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
                    question = f"Un carré a un côté de {side} cm. Quel est son périmètre ?"
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
                    explanation = f"L'aire d'un triangle = (base × hauteur) ÷ 2 = ({base} × {height}) ÷ 2 = {result} cm²."
                else:
                    hypotenuse = round(math.sqrt(base*base + height*height), 1)
                    result = round(base + height + hypotenuse, 1)
                    question = f"Un triangle rectangle a une base de {base} cm et une hauteur de {height} cm. Quel est son périmètre approximatif ?"
                    explanation = f"Le périmètre ≈ base + hauteur + hypoténuse ≈ {base} + {height} + {hypotenuse} ≈ {result} cm."
            else:  # cercle
                radius = random.randint(3, 10)
                if property_type == "périmètre":
                    result = round(2 * math.pi * radius, 2)
                    question = f"Un cercle a un rayon de {radius} cm. Quel est son périmètre ? (Utilise π ≈ 3.14)"
                    explanation = f"Le périmètre d'un cercle = 2 × π × rayon = 2 × 3.14 × {radius} ≈ {result} cm."
                else:
                    result = round(math.pi * radius * radius, 2)
                    question = f"Un cercle a un rayon de {radius} cm. Quelle est son aire ? (Utilise π ≈ 3.14)"
                    explanation = f"L'aire d'un cercle = π × rayon² = 3.14 × {radius}² ≈ {result} cm²."
        
        choices = [
            str(result),
            str(round(result * 0.5, 2)),
            str(round(result * 2, 2)),
            str(round(result * 1.5, 2))
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": "Exercice de géométrie",
            "question": question,
            "correct_answer": str(result),
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.GEOMETRY,
            "explanation": explanation
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.MIXTE:
        # Génération d'un exercice mixte (combinaison d'opérations)
        operation_types = [ExerciseTypes.ADDITION, ExerciseTypes.SUBTRACTION, 
                          ExerciseTypes.MULTIPLICATION, ExerciseTypes.DIVISION]
        chosen_operation = random.choice(operation_types)
        
        if chosen_operation == ExerciseTypes.ADDITION:
            min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
            num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
            result = num1 + num2
            question = f"Calcule : {num1} + {num2} = ?"
            explanation = f"Pour additionner, on calcule {num1} + {num2} = {result}."
        elif chosen_operation == ExerciseTypes.SUBTRACTION:
            num1 = random.randint(type_limits.get("min1", 10), type_limits.get("max1", 20))
            num2 = random.randint(type_limits.get("min2", 1), min(num1-1, type_limits.get("max2", 5)))
            result = num1 - num2
            question = f"Calcule : {num1} - {num2} = ?"
            explanation = f"Pour soustraire, on calcule {num1} - {num2} = {result}."
        elif chosen_operation == ExerciseTypes.MULTIPLICATION:
            min_val, max_val = type_limits.get("min", 1), type_limits.get("max", 10)
            num1, num2 = random.randint(min_val, max_val), random.randint(min_val, max_val)
            result = num1 * num2
            question = f"Calcule : {num1} × {num2} = ?"
            explanation = f"Pour multiplier, on calcule {num1} × {num2} = {result}."
        else:  # DIVISION
            num2 = random.randint(type_limits.get("min_divisor", 2), type_limits.get("max_divisor", 5))
            result = random.randint(type_limits.get("min_result", 1), type_limits.get("max_result", 5))
            num1 = num2 * result
            question = f"Calcule : {num1} ÷ {num2} = ?"
            explanation = f"Pour diviser, on calcule {num1} ÷ {num2} = {result}."
        
        choices = [
            str(result),
            str(result + random.randint(1, 3)),
            str(max(1, result - random.randint(1, 3))),
            str(result + random.randint(4, 6))
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": "Exercice mixte",
            "question": question,
            "correct_answer": str(result),
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "explanation": explanation
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.DIVERS:
        # Génération d'un exercice divers (probabilités, séquences, etc.)
        problem_type = random.choice(["sequence", "age", "monnaie"])
        
        if problem_type == "sequence":
            start = random.randint(1, 5)
            step = random.randint(1, 3)
            sequence = [start + step*i for i in range(4)]
            result = sequence[-1] + step
            question = f"Quelle est la suite logique : {sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, ... ?"
            explanation = f"Cette séquence augmente de {step} à chaque terme. Le terme suivant est donc {sequence[3]} + {step} = {result}."
        elif problem_type == "age":
            age_actuel = random.randint(8, 20)
            années = random.randint(1, 10)
            result = age_actuel + années
            question = f"Si tu as {age_actuel} ans maintenant, quel âge auras-tu dans {années} ans ?"
            explanation = f"Pour trouver l'âge futur, on additionne l'âge actuel et les années : {age_actuel} + {années} = {result} ans."
        else:  # monnaie
            pieces = random.randint(5, 20)
            valeur_piece = random.randint(1, 5)
            result = pieces * valeur_piece
            question = f"Si tu as {pieces} pièces de {valeur_piece} crédits chacune, combien de crédits as-tu en tout ?"
            explanation = f"Pour trouver le total, on multiplie le nombre de pièces par leur valeur : {pieces} × {valeur_piece} = {result} crédits."
        
        choices = [
            str(result),
            str(result + random.randint(1, 3)),
            str(max(1, result - random.randint(1, 3))),
            str(result + random.randint(4, 6))
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": "Exercice divers",
            "question": question,
            "correct_answer": str(result),
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.LOGIC,
            "explanation": explanation
        })
        return exercise_data

    # Si aucun type correspondant, retourner un exercice d'addition par défaut
    print(f"⚠️ Type d'exercice non géré dans generate_simple_exercise: {normalized_type}, utilisation de ADDITION par défaut")
    min_val = type_limits.get("min", 1)
    max_val = type_limits.get("max", 10)
    num1 = random.randint(min_val, max_val)
    num2 = random.randint(min_val, max_val)
    result = num1 + num2
    
    exercise_data.update({
        "title": ExerciseMessages.TITLE_DEFAULT if hasattr(ExerciseMessages, 'TITLE_DEFAULT') else "Exercice par défaut",
        "question": ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2),
        "correct_answer": str(result),
        "choices": [str(result), str(result-1), str(result+1), str(result+2)],
        "num1": num1,
        "num2": num2,
        "explanation": f"Pour additionner {num1} et {num2}, il faut calculer leur somme, donc {num1} + {num2} = {result}."
    })
    
    return exercise_data 

def generate_contextual_question(operation_type, num1, num2, result, difficulty):
    """Génère une question contextualisée selon le type d'opération et la difficulté"""
    contexts = StarWarsNarratives.CONTEXTS_BY_TYPE.get(operation_type.upper(), {})
    
    if not contexts:
        # Fallback vers les questions de base
        if operation_type.upper() == "ADDITION":
            return f"Calcule {num1} + {num2}"
        elif operation_type.upper() == "SUBTRACTION":
            return f"Calcule {num1} - {num2}"
        elif operation_type.upper() == "MULTIPLICATION":
            return f"Calcule {num1} × {num2}"
        elif operation_type.upper() == "DIVISION":
            return f"Calcule {num1} ÷ {num2}"
    
    objects = contexts.get("objects", ["éléments"])
    actions = contexts.get("actions", ["se combinent"])
    locations = contexts.get("locations", ["dans la galaxie"])
    
    obj = random.choice(objects)
    action = random.choice(actions)
    location = random.choice(locations)
    
    # Templates selon la difficulté et l'opération
    if operation_type.upper() == "ADDITION":
        if difficulty.upper() == "INITIE":
            templates = [
                f"Dans {location}, tu trouves {num1} {obj} et ton ami en trouve {num2}. Combien en avez-vous ensemble?",
                f"R2-D2 compte {num1} {obj} et C-3PO en compte {num2}. Quel est le total?",
                f"Luke a {num1} {obj} et Leia en a {num2}. Combien ont-ils au total?"
            ]
        else:
            templates = [
                f"Dans {location}, {num1} {obj} {action} avec {num2} autres. Quel est le total?",
                f"L'Alliance déploie {num1} {obj} qui {action} avec {num2} renforts. Combien au total?",
                f"Sur {location}, {num1} {obj} {action} et {num2} autres arrivent. Total?"
            ]
    
    elif operation_type.upper() == "SUBTRACTION":
        if difficulty.upper() == "INITIE":
            templates = [
                f"Tu avais {num1} {obj}, mais {num2} {action}. Combien te reste-t-il?",
                f"Dans {location}, il y avait {num1} {obj}, mais {num2} {action}. Combien restent?",
                f"Yoda possédait {num1} {obj}, mais {num2} {action}. Combien lui reste-t-il?"
            ]
        else:
            templates = [
                f"L'Empire avait {num1} {obj}, mais {num2} {action} lors de {location}. Combien restent?",
                f"Dans {location}, {num1} {obj} étaient présents, mais {num2} {action}. Reste?",
                f"La flotte comptait {num1} {obj}, mais {num2} {action} pendant {location}. Combien survivent?"
            ]
    
    elif operation_type.upper() == "MULTIPLICATION":
        if difficulty.upper() == "INITIE":
            templates = [
                f"Chaque Padawan a {num2} {obj}. S'il y a {num1} Padawans, combien de {obj} au total?",
                f"Dans chaque {location}, il y a {num2} {obj}. Combien dans {num1} {location}?",
                f"Chaque droïde transporte {num2} {obj}. Combien pour {num1} droïdes?"
            ]
        else:
            templates = [
                f"Chaque {location} déploie {num2} {obj}. Combien pour {num1} {location}?",
                f"Dans {location}, chaque unité a {num2} {obj}. Total pour {num1} unités?",
                f"L'Empire organise {num1} {location} avec {num2} {obj} chacun. Combien au total?"
            ]
    
    elif operation_type.upper() == "DIVISION":
        if difficulty.upper() == "INITIE":
            templates = [
                f"Tu as {num1} {obj} à distribuer entre {num2} Padawans. Combien chacun en aura?",
                f"Il faut répartir {num1} {obj} dans {num2} {location}. Combien par {location}?",
                f"Yoda doit partager {num1} {obj} entre {num2} élèves. Combien chacun?"
            ]
        else:
            templates = [
                f"L'Alliance doit répartir {num1} {obj} dans {num2} {location}. Combien par {location}?",
                f"Un convoi de {num1} {obj} doit être distribué sur {num2} {location}. Combien par site?",
                f"L'Empire divise {num1} {obj} entre {num2} {location}. Répartition par zone?"
            ]
    
    return random.choice(templates) if 'templates' in locals() else f"Calcule {num1} {operation_type.lower()} {num2}" 

def generate_smart_choices(operation_type, num1, num2, correct_result, difficulty):
    """Génère des choix de réponses avec des erreurs typiques selon l'opération"""
    choices = [str(correct_result)]
    
    if operation_type.upper() == "ADDITION":
        # Erreurs typiques en addition
        choices.extend([
            str(correct_result + random.randint(1, 3)),  # Erreur de calcul simple
            str(correct_result - random.randint(1, 2)),  # Oubli d'une unité
            str(num1 * num2) if num1 * num2 != correct_result else str(correct_result + 5)  # Confusion avec multiplication
        ])
    
    elif operation_type.upper() == "SUBTRACTION":
        # Erreurs typiques en soustraction
        choices.extend([
            str(num2 - num1) if num2 != num1 else str(correct_result + 3),  # Inversion de l'ordre
            str(correct_result + random.randint(1, 3)),  # Erreur de calcul
            str(num1 + num2) if num1 + num2 != correct_result else str(correct_result - 2)  # Addition au lieu de soustraction
        ])
    
    elif operation_type.upper() == "MULTIPLICATION":
        # Erreurs typiques en multiplication
        choices.extend([
            str(num1 + num2),  # Addition au lieu de multiplication
            str(correct_result + num1),  # Une fois de trop
            str(max(1, correct_result - num2))  # Une fois de moins
        ])
    
    elif operation_type.upper() == "DIVISION":
        # Erreurs typiques en division
        choices.extend([
            str(correct_result + 1),  # Erreur de calcul simple
            str(max(1, correct_result - 1)),  # Erreur de calcul simple
            str(num1 - num2) if num1 > num2 else str(correct_result + 2)  # Soustraction au lieu de division
        ])
    
    # Ajuster selon la difficulté
    if difficulty.upper() in ["CHEVALIER", "MAITRE"]:
        # Pour les niveaux avancés, ajouter des erreurs plus subtiles
        margin = max(1, int(correct_result * 0.1))
        choices[1] = str(correct_result + margin)
        choices[2] = str(max(1, correct_result - margin))
    
    # S'assurer qu'il n'y a pas de doublons et que tous les choix sont positifs
    unique_choices = []
    for choice in choices:
        if choice not in unique_choices and int(choice) > 0:
            unique_choices.append(choice)
    
    # Compléter si nécessaire
    while len(unique_choices) < 4:
        new_choice = str(correct_result + random.randint(-3, 5))
        if new_choice not in unique_choices and int(new_choice) > 0:
            unique_choices.append(new_choice)
    
    # Mélanger et retourner les 4 premiers
    random.shuffle(unique_choices)
    return unique_choices[:4]