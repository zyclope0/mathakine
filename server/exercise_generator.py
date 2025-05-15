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
            
    # Si aucune correspondance trouvée, retourner le type tel quel
    return exercise_type

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

# Fonctions de génération d'exercices
def generate_ai_exercise(exercise_type, difficulty):
    """Génère un exercice avec contexte Star Wars pour simuler une génération par IA"""
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
    explanation_prefix = random.choice(StarWarsNarratives.EXPLANATION_PREFIXES)
    explanation_suffix = random.choice(StarWarsNarratives.EXPLANATION_SUFFIXES)
    
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
        
        # Générer des choix proches mais différents
        choices = [
            str(result),
            str(result + random.randint(1, min(10, max_val//2))),
            str(result - random.randint(1, min(5, max_val//3))),
            str(num1 * num2)  # Distraction: multiplication au lieu d'addition
        ]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": f"[{Messages.AI_EXERCISE_PREFIX}] Alliance Rebelle - Addition niveau {difficulty}",
            "question": question_template,
            "correct_answer": str(result),
            "choices": choices,
            "num1": num1,
            "num2": num2,
            "explanation": f"[{Messages.AI_EXERCISE_PREFIX}] {explanation_prefix} {explanation_template} {explanation_suffix}"
        })
        
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
                f"Tu as {num1} portions de rations, mais tu en as utilisé {num2}. Combien de portions te reste-t-il?",
                f"Il y avait {num1} droïdes dans le hangar, mais {num2} ont été envoyés en mission. Combien reste-t-il de droïdes?",
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
        
    else:
        # Par défaut, générer une addition si le type n'est pas reconnu
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        
        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)
        result = num1 + num2
        
        question = ExerciseMessages.QUESTION_ADDITION.format(num1=num1, num2=num2)
        explanation = f"Pour additionner {num1} et {num2}, il faut calculer leur somme, donc {num1} + {num2} = {result}."
        
        choices = [str(result), str(result-1), str(result+1), str(result+2)]
        random.shuffle(choices)
        
        exercise_data.update({
            "title": ExerciseMessages.TITLE_DEFAULT,
            "question": question,
            "correct_answer": str(result),
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + Tags.SIMPLE,
            "num1": num1,
            "num2": num2,
            "explanation": explanation
        })
        return exercise_data

    # S'assurer que tous les choix sont uniques
    choices = list(set(exercise_data.get("choices", [])))
    while len(choices) < 4:
        new_choice = str(int(exercise_data["correct_answer"]) + random.randint(-10, 10))
        if new_choice != exercise_data["correct_answer"] and new_choice not in choices and int(new_choice) > 0:
            choices.append(new_choice)
    
    # Limiter à 4 choix maximum
    if len(choices) > 4:
        # S'assurer que la bonne réponse est incluse
        if exercise_data["correct_answer"] not in choices[:4]:
            choices[3] = exercise_data["correct_answer"]
        choices = choices[:4]
    
    exercise_data["choices"] = choices
    return exercise_data

def generate_simple_exercise(exercise_type, difficulty):
    """Génère un exercice simple de manière algorithmique"""
    normalized_type = normalize_exercise_type(exercise_type)
    normalized_difficulty = normalize_difficulty(difficulty)
    
    # Récupérer les limites pour ce type et cette difficulté
    difficulty_config = DIFFICULTY_LIMITS.get(normalized_difficulty, DIFFICULTY_LIMITS[DifficultyLevels.PADAWAN])
    
    # Limites par défaut si le type n'est pas trouvé
    type_limits = difficulty_config.get(normalized_type, difficulty_config.get("default", {"min": 1, "max": 10}))
    
    # Structure de base commune pour tous les types d'exercices
    exercise_data = {
        "exercise_type": normalized_type,
        "difficulty": normalized_difficulty
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
    
    # Autres types d'exercices...
    
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