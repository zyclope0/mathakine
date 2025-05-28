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
        
    elif normalized_type == ExerciseTypes.FRACTIONS:
        # Génération d'un exercice sur les fractions
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        
        # Dénominateurs et numérateurs en fonction de la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            # Fractions simples avec dénominateurs faciles (2, 3, 4, 5)
            denom1 = random.choice([2, 3, 4, 5])
            denom2 = random.choice([2, 3, 4, 5])
            num1 = random.randint(1, denom1-1)
            num2 = random.randint(1, denom2-1)
            operation = "+"  # Addition simple pour les débutants
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            # Fractions avec dénominateurs intermédiaires
            denom1 = random.choice([2, 3, 4, 5, 6, 8, 10])
            denom2 = random.choice([2, 3, 4, 5, 6, 8, 10])
            num1 = random.randint(1, denom1-1)
            num2 = random.randint(1, denom2-1)
            operation = random.choice(["+", "-"])  # Addition ou soustraction
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            # Fractions plus complexes
            denom1 = random.randint(2, 12)
            denom2 = random.randint(2, 12)
            num1 = random.randint(1, denom1)
            num2 = random.randint(1, denom2)
            operation = random.choice(["+", "-", "×"])  # +, - ou ×
        else:  # MAITRE
            # Fractions avancées
            denom1 = random.randint(2, 20)
            denom2 = random.randint(2, 20)
            num1 = random.randint(1, denom1*2)  # Fractions impropres
            num2 = random.randint(1, denom2*2)
            operation = random.choice(["+", "-", "×", "÷"])  # Toutes les opérations
        
        # Calculer le résultat
        from fractions import Fraction
        frac1 = Fraction(num1, denom1)
        frac2 = Fraction(num2, denom2)
        
        if operation == "+":
            result = frac1 + frac2
            op_text = "addition"
            steps = f"trouver un dénominateur commun ({denom1*denom2})"
        elif operation == "-":
            # S'assurer que le résultat n'est pas négatif pour les niveaux faciles
            if normalized_difficulty in [DifficultyLevels.INITIE, DifficultyLevels.PADAWAN] and frac1 < frac2:
                frac1, frac2 = frac2, frac1  # Échanger les fractions
            result = frac1 - frac2
            op_text = "soustraction"
            steps = f"trouver un dénominateur commun ({denom1*denom2})"
        elif operation == "×":
            result = frac1 * frac2
            op_text = "multiplication"
            steps = f"multiplier les numérateurs ({num1}×{num2}) et les dénominateurs ({denom1}×{denom2})"
        else:  # "÷"
            # Éviter division par zéro
            if num2 == 0:
                num2 = 1
            result = frac1 / frac2
            op_text = "division"
            steps = f"inverser la deuxième fraction et multiplier ({num1}/{denom1} × {denom2}/{num2})"
        
        # Formatage du résultat
        if result.denominator == 1:
            formatted_result = str(result.numerator)
        else:
            formatted_result = f"{result.numerator}/{result.denominator}"
        
        # Générer la question
        question = f"Calcule {num1}/{denom1} {operation} {num2}/{denom2}"
        
        # Générer des choix
        # Pour les fractions simples, on propose des variantes proches
        incorrect1 = Fraction(num1, denom2)  # Confusion des dénominateurs
        incorrect2 = Fraction(num2, denom1)  # Inversion
        
        if operation == "+":
            incorrect3 = Fraction(num1 + num2, denom1 + denom2)  # Erreur commune: additionner num et denom
        elif operation == "-":
            incorrect3 = Fraction(abs(num1 - num2), abs(denom1 - denom2))  # Erreur: soustraire num et denom
        elif operation == "×":
            incorrect3 = Fraction(num1 + num2, denom1 * denom2)  # Erreur: addition des numérateurs
        else:  # "÷"
            incorrect3 = Fraction(num1 * num2, denom1 * denom2)  # Erreur: multiplication au lieu de division
        
        # Formater les choix
        choices = [
            formatted_result,  # Bonne réponse
            f"{incorrect1.numerator}/{incorrect1.denominator}",
            f"{incorrect2.numerator}/{incorrect2.denominator}",
            f"{incorrect3.numerator}/{incorrect3.denominator}"
        ]
        random.shuffle(choices)
        
        explanation = f"Pour calculer {num1}/{denom1} {operation} {num2}/{denom2}, il faut {steps}. Le résultat est {formatted_result}."
        
        exercise_data.update({
            "title": "Calcul de fractions",
            "question": question,
            "correct_answer": formatted_result,
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + "fractions",
            "explanation": explanation
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.GEOMETRIE:
        # Génération d'un exercice de géométrie
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        
        # Choisir une forme géométrique et une propriété à calculer en fonction de la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            # Formes simples: carré ou rectangle, périmètre ou aire
            shape = random.choice(["carré", "rectangle"])
            property = random.choice(["périmètre", "aire"])
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            # Ajout de triangle et trapèze
            shape = random.choice(["carré", "rectangle", "triangle"])
            property = random.choice(["périmètre", "aire"])
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            # Formes plus complexes
            shape = random.choice(["carré", "rectangle", "triangle", "cercle"])
            property = random.choice(["périmètre", "aire"])
        else:  # MAITRE
            # Toutes les formes et propriétés
            shape = random.choice(["carré", "rectangle", "triangle", "cercle", "trapèze"])
            property = random.choice(["périmètre", "aire", "diagonale"])
        
        # Variables pour la question et l'explication
        formula = ""
        parameter1 = ""
        parameter2 = ""
        value1 = 0
        value2 = 0
        result = 0
        
        # Logique spécifique par forme
        if shape == "carré":
            parameter1 = "côté"
            value1 = random.randint(min_val, max_val)
            
            if property == "périmètre":
                result = 4 * value1
                formula = "4 × côté"
            elif property == "aire":
                result = value1 * value1
                formula = "côté²"
            elif property == "diagonale":
                import math
                result = round(value1 * math.sqrt(2), 2)
                formula = "côté × √2"
            
            parameter2 = ""
            value2 = 0
            
        elif shape == "rectangle":
            parameter1 = "longueur"
            parameter2 = "largeur"
            value1 = random.randint(min_val+1, max_val)
            value2 = random.randint(min_val, value1-1)  # Largeur < Longueur
            
            if property == "périmètre":
                result = 2 * (value1 + value2)
                formula = "2 × (longueur + largeur)"
            elif property == "aire":
                result = value1 * value2
                formula = "longueur × largeur"
            elif property == "diagonale":
                import math
                result = round(math.sqrt(value1*value1 + value2*value2), 2)
                formula = "√(longueur² + largeur²)"
            
        elif shape == "triangle":
            # Triangle rectangle pour simplifier
            parameter1 = "base"
            parameter2 = "hauteur"
            value1 = random.randint(min_val, max_val)
            value2 = random.randint(min_val, max_val)
            
            if property == "aire":
                result = (value1 * value2) / 2
                formula = "(base × hauteur) / 2"
            elif property == "périmètre":
                # Utiliser le théorème de Pythagore pour calculer l'hypoténuse
                import math
                hypotenuse = math.sqrt(value1*value1 + value2*value2)
                result = round(value1 + value2 + hypotenuse, 2)
                formula = "base + hauteur + hypoténuse"
        
        elif shape == "cercle":
            parameter1 = "rayon"
            value1 = random.randint(min_val, max_val)
            
            if property == "périmètre":
                import math
                result = round(2 * math.pi * value1, 2)
                formula = "2 × π × rayon"
            elif property == "aire":
                import math
                result = round(math.pi * value1 * value1, 2)
                formula = "π × rayon²"
            
            parameter2 = ""
            value2 = 0
        
        # Générer la question
        if parameter2:
            question = f"Calcule le {property} d'un {shape} avec {parameter1}={value1} et {parameter2}={value2}"
        else:
            question = f"Calcule le {property} d'un {shape} avec {parameter1}={value1}"
        
        # Générer des choix
        # Erreurs communes
        if property == "périmètre" and shape in ["carré", "rectangle"]:
            incorrect1 = round(result * 0.5, 2)  # Oubli du facteur 2
            incorrect2 = round(result * 2, 2)     # Double du périmètre
            incorrect3 = value1 * value2 if shape == "rectangle" else value1 * value1  # Confusion avec l'aire
        elif property == "aire" and shape in ["carré", "rectangle", "triangle"]:
            incorrect1 = round(result * 2, 2)  # Double de l'aire
            incorrect2 = round(result / 2, 2)  # Moitié de l'aire
            if shape == "triangle":
                incorrect3 = value1 * value2  # Oubli du facteur 1/2
            else:
                incorrect3 = 2 * (value1 + (value2 if value2 else value1))  # Confusion avec le périmètre
        else:
            # Valeurs proches pour les autres cas
            incorrect1 = round(result * 0.9, 2)  # 10% de moins
            incorrect2 = round(result * 1.1, 2)  # 10% de plus
            incorrect3 = round(result * 1.5, 2)  # 50% de plus
        
        # Formater les choix
        choices = [
            str(result),
            str(incorrect1),
            str(incorrect2),
            str(incorrect3)
        ]
        random.shuffle(choices)
        
        explanation = f"Pour calculer le {property} d'un {shape}, on utilise la formule: {formula}. Donc le résultat est {result}."
        
        exercise_data.update({
            "title": "Géométrie",
            "question": question,
            "correct_answer": str(result),
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + "geometrie",
            "explanation": explanation
        })
        return exercise_data

    elif normalized_type == ExerciseTypes.DIVERS:
        # Génération d'un exercice divers (problèmes, défis logiques, etc.)
        min_val = type_limits.get("min", 1)
        max_val = type_limits.get("max", 10)
        
        # Choisir un type de problème en fonction de la difficulté
        if normalized_difficulty == DifficultyLevels.INITIE:
            # Problèmes simples pour débutants
            problem_type = random.choice(["monnaie", "age", "vitesse_simple"])
        elif normalized_difficulty == DifficultyLevels.PADAWAN:
            problem_type = random.choice(["monnaie", "age", "vitesse", "pourcentage"])
        elif normalized_difficulty == DifficultyLevels.CHEVALIER:
            problem_type = random.choice(["vitesse", "pourcentage", "probabilité"])
        else:  # MAITRE
            problem_type = random.choice(["probabilité", "pourcentage", "séquence"])
        
        # Logique pour chaque type de problème
        if problem_type == "monnaie":
            # Problème simple de monnaie: rendre la monnaie
            prix = random.randint(min_val, max_val)
            payé = random.randint(prix, prix + 20)
            result = payé - prix
            
            problem = f"Tu achètes un jouet qui coûte {prix} euros. Tu paies avec un billet de {payé} euros. Combien d'euros le vendeur doit-il te rendre?"
            explanation = f"Pour calculer la monnaie, tu dois soustraire le prix ({prix} euros) du montant payé ({payé} euros). Donc {payé} - {prix} = {result} euros."
            
        elif problem_type == "age":
            # Problème d'âge
            age_actuel = random.randint(min_val, max_val)
            années = random.randint(1, 5)
            result = age_actuel + années
            
            problem = f"Luke a {age_actuel} ans aujourd'hui. Quel âge aura-t-il dans {années} ans?"
            explanation = f"Pour trouver l'âge futur, tu ajoutes le nombre d'années à l'âge actuel. Donc {age_actuel} + {années} = {result} ans."
            
        elif problem_type == "vitesse_simple":
            # Problème de vitesse simple
            distance = random.randint(min_val, max_val) * 5  # multiple de 5 pour des distances réalistes
            heures = random.randint(1, 5)
            result = distance // heures  # vitesse horaire simplement arrondie
            
            problem = f"Une voiture parcourt {distance} kilomètres en {heures} heures à une vitesse constante. Quelle est sa vitesse en kilomètres par heure?"
            explanation = f"La vitesse se calcule en divisant la distance par le temps. Donc {distance} ÷ {heures} = {result} km/h."
            
        elif problem_type == "vitesse":
            # Problème de vitesse plus avancé
            vitesse = random.randint(min_val, max_val) * 5  # en km/h
            heures = random.randint(1, 5)
            result = vitesse * heures  # distance
            
            problem = f"Un train roule à {vitesse} km/h pendant {heures} heures. Quelle distance parcourt-il?"
            explanation = f"Pour calculer la distance, tu multiplies la vitesse par le temps. Donc {vitesse} × {heures} = {result} km."
            
        elif problem_type == "pourcentage":
            # Problème de pourcentage
            initial = random.randint(min_val, max_val) * 10  # montant initial
            pourcentage = random.choice([5, 10, 15, 20, 25, 50])  # pourcentage courant
            result = initial + (initial * pourcentage // 100)  # montant après augmentation
            
            problem = f"Un produit coûte {initial} euros. Son prix augmente de {pourcentage}%. Quel est son nouveau prix?"
            explanation = f"Pour calculer l'augmentation, tu multiplies le prix initial par le pourcentage et tu divises par 100, puis tu ajoutes au prix initial. Donc {initial} + ({initial} × {pourcentage} ÷ 100) = {initial} + {initial * pourcentage // 100} = {result} euros."
            
        elif problem_type == "probabilité":
            # Problème de probabilité
            total = random.randint(10, 50)  # nombre total d'objets
            favorables = random.randint(1, total // 2)  # cas favorables
            result = favorables / total  # probabilité exacte
            formatted_result = f"{favorables}/{total}"  # format fraction
            
            problem = f"Dans un sac, il y a {total} billes dont {favorables} sont rouges. Quelle est la probabilité de tirer une bille rouge?"
            explanation = f"La probabilité se calcule en divisant le nombre de cas favorables par le nombre total de cas. Donc {favorables} ÷ {total} = {formatted_result}."
            result = formatted_result  # Utiliser le format fraction comme résultat
            
        elif problem_type == "séquence":
            # Problème de séquence
            start = random.randint(1, 5)
            diff = random.randint(1, 5)
            sequence = [start + diff*i for i in range(5)]  # séquence arithmétique
            result = sequence[4] + diff  # terme suivant
            
            problem = f"Trouve le terme suivant dans cette séquence : {sequence[0]}, {sequence[1]}, {sequence[2]}, {sequence[3]}, {sequence[4]}, ..."
            explanation = f"Cette séquence augmente de {diff} à chaque terme. Le terme suivant après {sequence[4]} est donc {sequence[4]} + {diff} = {result}."
        
        else:
            # Problème par défaut
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            result = a + b
            
            problem = f"Combien font {a} + {b}?"
            explanation = f"Pour additionner {a} et {b}, il faut calculer leur somme, donc {a} + {b} = {result}."
        
        # Créer des choix appropriés
        if isinstance(result, float):
            # Pour les résultats décimaux
            choices = [
                str(result),
                str(round(result * 0.9, 2)),  # 10% moins
                str(round(result * 1.1, 2)),  # 10% plus
                str(round(result * 2, 2))      # double
            ]
        elif isinstance(result, str) and "/" in result:
            # Pour les fractions
            num, denom = map(int, result.split("/"))
            choices = [
                result,
                f"{num+1}/{denom}",  # numérateur +1
                f"{num}/{denom+1}",  # dénominateur +1
                f"{denom}/{num}"     # inversé
            ]
        else:
            # Pour les entiers
            choices = [
                str(result),
                str(result + random.randint(1, 5)),
                str(max(1, result - random.randint(1, 5))),
                str(result * 2)  # double
            ]
            
        random.shuffle(choices)
        
        # Construire l'exercice
        exercise_data.update({
            "title": "Problème mathématique",
            "question": problem,
            "correct_answer": str(result),
            "choices": choices,
            "tags": Tags.ALGORITHMIC + "," + "divers",
            "explanation": explanation
        })
        return exercise_data

    # Si aucun type correspondant, retourner un exercice d'addition par défaut avec thème Star Wars
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
    
    # Si aucun type correspondant, retourner un exercice d'addition par défaut avec thème Star Wars
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