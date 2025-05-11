"""
Endpoints API pour la gestion des exercices
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional, Dict
from fastapi.responses import RedirectResponse
import random
import logging

from app.api.deps import get_db_session
from app.schemas.exercise import Exercise, ExerciseCreate, ExerciseUpdate
from app.schemas.common import PaginationParams
from app.models.exercise import DifficultyLevel, ExerciseType

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])


def get_exercises(
    db: Session = Depends(get_db_session),
    params: PaginationParams = Depends(),
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> Any:
    """
    Récupérer tous les exercices avec filtre optionnel par type et difficulté.
    """
    from app.models.exercise import Exercise as ExerciseModel

    # Créer une requête de base
    query = db.query(ExerciseModel).filter(ExerciseModel.is_archived == False)

    # Appliquer les filtres si nécessaire
    if exercise_type:
        # Essayer de trouver le type d'exercice correspondant
        try:
            # On regarde manuellement quelle valeur d'énumération correspond
            matching_type = None
            for t in ExerciseType:
                if t.value.lower() == exercise_type.lower() or t.name.lower() == exercise_type.lower():
                    matching_type = t
                    break

            if matching_type:
                query = query.filter(ExerciseModel.exercise_type == matching_type.value)
        except:
            # En cas d'erreur, ne pas appliquer de filtre
            pass

    if difficulty:
        # Même approche pour la difficulté
        try:
            matching_difficulty = None
            for d in DifficultyLevel:
                if d.value.lower() == difficulty.lower() or d.name.lower() == difficulty.lower():
                    matching_difficulty = d
                    break

            if matching_difficulty:
                query = query.filter(ExerciseModel.difficulty == matching_difficulty.value)
        except:
            pass

    # Appliquer la pagination
    total = query.count()
    if params.skip:
        query = query.offset(params.skip)
    if params.limit:
        query = query.limit(params.limit)

    # Exécuter la requête et récupérer les résultats
    exercises_db = query.all()

    # Convertir les objets ORM en dictionnaires
    exercises = []
    for ex in exercises_db:
        exercise_dict = {
            "id": ex.id,
            "title": ex.title,
            "exercise_type": ex.exercise_type,
            "difficulty": ex.difficulty,
            "question": ex.question,
            "correct_answer": ex.correct_answer,
            "choices": ex.choices,
            "explanation": ex.explanation,
            "hint": ex.hint,
            "image_url": ex.image_url,
            "audio_url": ex.audio_url,
            "is_active": ex.is_active,
            "is_archived": ex.is_archived,
            "view_count": ex.view_count,
            "creator_id": ex.creator_id,
            "created_at": ex.created_at.isoformat() if ex.created_at else None,
            "updated_at": ex.updated_at.isoformat() if ex.updated_at else None
        }
        exercises.append(exercise_dict)

    # Renvoyer la liste complète pour compatibilité avec le frontend
    return {
        "exercises": exercises,
        "total": total,
        "skip": params.skip or 0,
        "limit": params.limit or len(exercises)
    }


@router.get("/types", response_model=List[str])


def get_exercise_types() -> Any:
    """
    Récupérer tous les types d'exercices disponibles.
    """
    return [t.value for t in ExerciseType]


@router.get("/difficulties", response_model=List[str])


def get_difficulty_levels() -> Any:
    """
    Récupérer tous les niveaux de difficulté disponibles.
    """
    return [d.value for d in DifficultyLevel]


@router.post("/", response_model=Exercise)


def create_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_in: ExerciseCreate,
) -> Any:
    """
    Créer un nouvel exercice.
    """
    # Placeholder function - implement actual exercise creation
    return {
        "id": 0,
        "title": exercise_in.title,
        "exercise_type": exercise_in.exercise_type,
        "difficulty": exercise_in.difficulty,
        "question": exercise_in.question,
        "correct_answer": exercise_in.correct_answer,
        "choices": exercise_in.choices,
        "is_active": True
    }


@router.get("/random", response_model=Exercise)


def get_random_exercise(
    db: Session = Depends(get_db_session),
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> Any:
    """
    Récupérer un exercice aléatoire avec filtre optionnel par type et difficulté.
    """
    # Convertir les paramètres si nécessaire
    if exercise_type:
        exercise_type_lower = exercise_type.lower()
        valid_types = [t.value for t in ExerciseType]
        if exercise_type_lower not in valid_types:
            exercise_type_lower = random.choice(valid_types)
    else:
        exercise_type_lower = random.choice([t.value for t in ExerciseType])

    if difficulty:
        difficulty_lower = difficulty.lower()
        valid_difficulties = [d.value for d in DifficultyLevel]
        if difficulty_lower not in valid_difficulties:
            difficulty_lower = random.choice(valid_difficulties)
    else:
        difficulty_lower = random.choice([d.value for d in DifficultyLevel])

    # Pour l'instant, renvoyer des données statiques
    return {
        "id": 1,
        "title": "Exercice aléatoire",
        "exercise_type": exercise_type_lower,
        "difficulty": difficulty_lower,
        "question": "Combien font 2+2?",
        "correct_answer": "4",
        "choices": ["2", "3", "4", "5"],
        "is_active": True
    }




def generate_ai_exercise(exercise_type, difficulty):
    """
    Génère un exercice de mathématiques avec thématique Star Wars.
    Cette fonction n'utilise pas OpenAI, mais simule une génération
    algorithmique avec contexte Star Wars.

    Args:
        exercise_type: Le type d'exercice (addition, soustraction, etc.)
        difficulty: Le niveau de difficulté

    Returns:
        Un dictionnaire avec les détails de l'exercice généré
    """
    # S'assurer que le type d'exercice est normalisé
    if exercise_type not in [e.value for e in ExerciseType]:
        # Type d'exercice non reconnu, utiliser l'addition par défaut
        exercise_type = ExerciseType.ADDITION.value

    # S'assurer que la difficulté est normalisée
    if difficulty not in [d.value for d in DifficultyLevel]:
        # Difficulté non reconnue, utiliser le niveau Padawan par défaut
        difficulty = DifficultyLevel.PADAWAN.value

    # Ajustement des exercices selon le type et la difficulté
    if exercise_type == ExerciseType.ADDITION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            result = num1 + num2
            question = f"[TEST-ZAXXON] Si tu as {num1} cristaux Kyber et que tu en trouves {num2} autres\
                , combien de cristaux as-tu au total?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num1 = random.randint(10, 30)
            num2 = random.randint(10, 30)
            result = num1 + num2
            question = f"[TEST-ZAXXON] Ton escadron de {num1} chasseurs TIE est rejoint par {num2} autres. Combien de vaisseaux forment maintenant ton escadron?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num1 = random.randint(30, 100)
            num2 = random.randint(30, 100)
            result = num1 + num2
            question = f"[TEST-ZAXXON] La République dispose de {num1} destroyers et en construit {num2} supplémentaires. Quelle est la taille de la flotte?"
        else:  # Maître
            num1 = random.randint(100, 500)
            num2 = random.randint(100, 500)
            result = num1 + num2
            question = f"[TEST-ZAXXON] L'Empire compte {num1} systèmes sous son contrôle et en conquiert {num2} de plus. Combien de systèmes sont maintenant sous contrôle impérial?"

        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 10)), str(result+random.randint(1
            , 10)), str(result+random.randint(11, 20))]
        explanation = f"Tu avais {num1} puis tu en as ajouté {num2}. Ainsi, {num1}\
            + {num2} = {result}."

    elif exercise_type == ExerciseType.SOUSTRACTION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num1 = random.randint(5, 15)
            num2 = random.randint(1, 5)
            result = num1 - num2
            question = f"[TEST-ZAXXON] Tu as {num1} portions de rations et tu en consommes {num2}. Combien de portions te reste-t-il?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num1 = random.randint(20, 50)
            num2 = random.randint(5, 20)
            result = num1 - num2
            question = f"[TEST-ZAXXON] Tu commandais {num1} stormtroopers mais {num2} ont été capturés par la Résistance. Combien de stormtroopers te reste-t-il?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num1 = random.randint(50, 150)
            num2 = random.randint(20, 50)
            result = num1 - num2
            question = f"[TEST-ZAXXON] Ta flotte a {num1} vaisseaux mais {num2} sont endommagés après la bataille. Combien de vaisseaux sont encore opérationnels?"
        else:  # Maître
            num1 = random.randint(200, 500)
            num2 = random.randint(50, 200)
            result = num1 - num2
            question = f"[TEST-ZAXXON] L'Empire contrôle {num1} planètes, mais {num2} se rebellent et rejoignent l'Alliance. Combien de planètes restent fidèles à l'Empire?"

        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 5)), str(result+random.randint(1
            , 5)), str(num2)]
        explanation = f"Tu avais {num1} au départ et tu en as perdu {num2}. Donc\
            , {num1} - {num2} = {result}."

    elif exercise_type == ExerciseType.MULTIPLICATION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num1 = random.randint(1, 5)
            num2 = random.randint(1, 5)
            result = num1 * num2
            question = f"[TEST-ZAXXON] Chaque Padawan a {num2} cristaux Kyber. S'il y a {num1} Padawans\
                , combien de cristaux y a-t-il au total?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num1 = random.randint(2, 10)
            num2 = random.randint(2, 10)
            result = num1 * num2
            question = f"[TEST-ZAXXON] Chaque escadron compte {num2} vaisseaux. Combien de vaisseaux y a-t-il dans {num1} escadrons?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num1 = random.randint(5, 12)
            num2 = random.randint(5, 12)
            result = num1 * num2
            question = f"[TEST-ZAXXON] Chaque Star Destroyer transporte {num2} TIE Fighters. Combien de TIE Fighters y a-t-il sur {num1} Star Destroyers?"
        else:  # Maître
            num1 = random.randint(10, 20)
            num2 = random.randint(10, 20)
            result = num1 * num2
            question = f"[TEST-ZAXXON] Un bataillon compte {num2} régiments de clones. Si l'armée de la République déploie {num1} bataillons\
                , combien de régiments sont mobilisés au total?"

        correct_answer = str(result)
        choices = [str(result), str(result-num2), str(result+num1), str(num1+num2)]
        explanation = f"[TEST-ZAXXON] Il y a {num1} groupes de {num2} éléments chacun. Donc\
            , {num1} × {num2} = {result}."

    elif exercise_type == ExerciseType.DIVISION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num2 = random.choice([2, 5, 10])
            num1 = num2 * random.randint(1, 5)
            result = num1 // num2
            question = f"[TEST-ZAXXON] Tu dois partager équitablement {num1} portions de rations entre {num2} Padawans. Combien chaque Padawan recevra-t-il?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num2 = random.randint(2, 10)
            num1 = num2 * random.randint(2, 10)
            result = num1 // num2
            question = f"[TEST-ZAXXON] Tu as {num1} stormtroopers à répartir également dans {num2} transports. Combien de stormtroopers embarqueront dans chaque transport?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num2 = random.randint(5, 15)
            num1 = num2 * random.randint(5, 15)
            result = num1 // num2
            question = f"[TEST-ZAXXON] La flotte impériale de {num1} TIE Fighters doit être répartie équitablement entre {num2} Star Destroyers. Combien de TIE Fighters seront affectés à chaque vaisseau?"
        else:  # Maître
            num2 = random.randint(10, 20)
            remainder = random.randint(0, num2-1)
            num1 = num2 * random.randint(10, 20) + remainder
            result = num1 // num2
            if remainder > 0:
                question = f"[TEST-ZAXXON] L'Empire doit diviser {num1} troupes en {num2} garnisons égales. Combien de soldats y aura-t-il dans chaque garnison? (Donne le quotient sans le reste)"
            else:
                question = f"[TEST-ZAXXON] L'Empire doit diviser {num1} troupes en {num2} garnisons égales. Combien de soldats y aura-t-il dans chaque garnison?"

        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result*2)]
        explanation = f"[TEST-ZAXXON] Pour répartir {num1} éléments en {num2} groupes égaux\
            , chaque groupe contient {result} éléments car {num1} ÷ {num2} = {result}."

    else:
        # Ce bloc ne devrait jamais être exécuté grâce à la normalisation précédente
        # Par précaution, on fait une addition sur le thème Star Wars
        num1 = random.randint(5, 25)
        num2 = random.randint(5, 25)
        result = num1 + num2
        question = f"[TEST-ZAXXON] Si tu as {num1} crédits galactiques et que tu en gagnes {num2} de plus dans une mission\
            , combien de crédits possèdes-tu maintenant?"
        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 5)), str(result+random.randint(1
            , 5)), str(result+random.randint(6, 10))]
        explanation = f"[TEST-ZAXXON] Tu avais {num1} crédits et tu en as gagné {num2} de plus. Donc {num1}\
            + {num2} = {result} crédits au total."

        # Log pour le débogage
        print(f"Attention: Type d'exercice non géré: {exercise_type}, génération d'une addition par défaut")

    # Mélanger les choix pour éviter que la bonne réponse soit toujours à la même position
    random.shuffle(choices)

    # S'assurer que tous les choix sont uniques
    choices = list(set(choices))
    while len(choices) < 4:
        new_choice = str(int(correct_answer) + random.randint(-10, 10))
        if new_choice != correct_answer and new_choice not in choices and int(new_choice) > 0:
            choices.append(new_choice)

    # Limiter à 4 choix maximum
    if len(choices) > 4:
        # S'assurer que la bonne réponse est incluse
        if correct_answer not in choices[:4]:
            choices[3] = correct_answer
        choices = choices[:4]

    # Renvoyer un dictionnaire avec les informations de l'exercice
    return {
        "question": question,
        "correct_answer": correct_answer,
        "choices": choices,
        "explanation": explanation,
        "exercise_type": exercise_type,  # Ajouter le type normalisé pour référence
        "difficulty": difficulty         # Ajouter la difficulté normalisée
    }


@router.get("/generate", response_model=dict)


def generate_exercise(
    db: Session = Depends(get_db_session),
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    ai: Optional[bool] = Query(False)
) -> Any:
    """
    Génère un exercice de mathématique aléatoire ou selon les critères spécifiés.

    Args:
        db: Session de base de données
        exercise_type: Type d'exercice (addition, soustraction, etc.)
        difficulty: Niveau de difficulté (facile, moyen, difficile, etc.)
        ai: Indicateur pour utiliser la génération IA

    Returns:
        L'exercice généré
    """
    # Normalisation des entrées
    # Si le type n'est pas spécifié, en choisir un au hasard
    if not exercise_type:
        # Choisir un type aléatoire parmi les types disponibles
        selected_type = random.choice([e.value for e in ExerciseType])
    else:
        # Normaliser le type d'exercice fourni
        exercise_type = exercise_type.lower()
        # Correspondance des types d'exercices
        type_mapping = {
            "addition": ExerciseType.ADDITION.value,
            "soustraction": ExerciseType.SOUSTRACTION.value,
            "multiplication": ExerciseType.MULTIPLICATION.value,
            "division": ExerciseType.DIVISION.value,
            "fractions": ExerciseType.FRACTIONS.value,
            "geometrie": ExerciseType.GEOMETRIE.value
        }
        selected_type = type_mapping.get(exercise_type, ExerciseType.ADDITION.value)

    # Si la difficulté n'est pas spécifiée, en choisir une au hasard
    if not difficulty:
        # Choisir une difficulté aléatoire
        selected_difficulty = random.choice([d.value for d in DifficultyLevel])
    else:
        # Normaliser la difficulté fournie
        difficulty = difficulty.lower()
        # Correspondance des niveaux de difficulté
        difficulty_mapping = {
            "facile": DifficultyLevel.INITIE.value,
            "moyen": DifficultyLevel.PADAWAN.value,
            "difficile": DifficultyLevel.CHEVALIER.value,
            "tres_difficile": DifficultyLevel.MAITRE.value,
            "initie": DifficultyLevel.INITIE.value,
            "padawan": DifficultyLevel.PADAWAN.value,
            "chevalier": DifficultyLevel.CHEVALIER.value,
            "maitre": DifficultyLevel.MAITRE.value
        }
        selected_difficulty = difficulty_mapping.get(difficulty, DifficultyLevel.PADAWAN.value)

    # Si l'utilisateur a demandé de générer avec IA
    if ai:
        ai_exercise = generate_ai_exercise(selected_type, selected_difficulty)
        question = ai_exercise["question"]
        correct_answer = ai_exercise["correct_answer"]
        choices = ai_exercise["choices"]
        explanation = ai_exercise["explanation"]
        is_ai_generated = True

        # Utiliser les valeurs normalisées retournées par generate_ai_exercise pour assurer la cohérence
        if "exercise_type" in ai_exercise:
            selected_type = ai_exercise["exercise_type"]

        if "difficulty" in ai_exercise:
            selected_difficulty = ai_exercise["difficulty"]

        # Formater le titre avec thématique Star Wars selon le type et le niveau
        type_names = {
            "addition": "Addition",
            "soustraction": "Soustraction",
            "multiplication": "Multiplication",
            "division": "Division"
        }

        difficulty_labels = {
            "initie": "Initié",
            "padawan": "Padawan",
            "chevalier": "Chevalier",
            "maitre": "Maître"
        }

        type_label = type_names.get(selected_type, selected_type.capitalize())
        difficulty_label = difficulty_labels.get(selected_difficulty, selected_difficulty.capitalize())

        title = f"[TEST-ZAXXON] Épreuve de {type_label} - Niveau {difficulty_label}"
    else:
        # Génération algorithmique standard
        if selected_type == ExerciseType.ADDITION.value:
            # Génération d'une addition basée sur la difficulté
            num1, num2 = 1, 1
            if selected_difficulty == DifficultyLevel.PADAWAN.value:
                num1, num2 = random.randint(1, 10), random.randint(1, 10)
            elif selected_difficulty == DifficultyLevel.INITIE.value:
                num1, num2 = random.randint(10, 50), random.randint(10, 50)
            elif selected_difficulty == DifficultyLevel.CHEVALIER.value:
                num1, num2 = random.randint(50, 100), random.randint(50, 100)
            else:  # Maître et au-delà
                num1, num2 = random.randint(100, 500), random.randint(100, 500)

            result = num1 + num2
            question = f"[TEST-ZAXXON] Combien font {num1} + {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-1), str(result+1), str(result+2)]
            random.shuffle(choices)
            explanation = f"[TEST-ZAXXON] {num1} + {num2} = {result}"
            title = f"[TEST-ZAXXON] Exercice de {selected_type.lower()}"
            is_ai_generated = False

        elif selected_type == ExerciseType.SOUSTRACTION.value:
            # Génération d'une soustraction
            num1, num2 = 1, 1
            if selected_difficulty == DifficultyLevel.PADAWAN.value:
                num1, num2 = random.randint(5, 20), random.randint(1, 5)
            elif selected_difficulty == DifficultyLevel.INITIE.value:
                num1, num2 = random.randint(20, 70), random.randint(10, 20)
            elif selected_difficulty == DifficultyLevel.CHEVALIER.value:
                num1, num2 = random.randint(70, 120), random.randint(20, 70)
            else:  # Maître et au-delà
                num1, num2 = random.randint(120, 500), random.randint(70, 120)

            # Assurer que num1 > num2
            if num1 < num2:
                num1, num2 = num2, num1

            result = num1 - num2
            question = f"[TEST-ZAXXON] Combien font {num1} - {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-1), str(result+1), str(result+2)]
            random.shuffle(choices)
            explanation = f"[TEST-ZAXXON] {num1} - {num2} = {result}"
            title = f"[TEST-ZAXXON] Exercice de {selected_type.lower()}"
            is_ai_generated = False

        elif selected_type == ExerciseType.MULTIPLICATION.value:
            # Génération d'une multiplication
            num1, num2 = 1, 1
            if selected_difficulty == DifficultyLevel.PADAWAN.value:
                num1, num2 = random.randint(1, 5), random.randint(1, 5)
            elif selected_difficulty == DifficultyLevel.INITIE.value:
                num1, num2 = random.randint(5, 10), random.randint(5, 10)
            elif selected_difficulty == DifficultyLevel.CHEVALIER.value:
                num1, num2 = random.randint(10, 15), random.randint(10, 15)
            else:  # Maître et au-delà
                num1, num2 = random.randint(15, 30), random.randint(15, 30)

            result = num1 * num2
            question = f"[TEST-ZAXXON] Combien font {num1} × {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-num1), str(result+num1), str(result+num2)]
            random.shuffle(choices)
            explanation = f"[TEST-ZAXXON] {num1} × {num2} = {result}"
            title = f"[TEST-ZAXXON] Exercice de {selected_type.lower()}"
            is_ai_generated = False

        elif selected_type == ExerciseType.DIVISION.value:
            # Génération d'une division (on crée d'abord des nombres qui sont divisibles)
            if selected_difficulty == DifficultyLevel.PADAWAN.value:
                num2 = random.randint(2, 5)
                num1 = num2 * random.randint(1, 5)
            elif selected_difficulty == DifficultyLevel.INITIE.value:
                num2 = random.randint(2, 10)
                num1 = num2 * random.randint(5, 10)
            elif selected_difficulty == DifficultyLevel.CHEVALIER.value:
                num2 = random.randint(5, 12)
                num1 = num2 * random.randint(10, 15)
            else:  # Maître et au-delà
                num2 = random.randint(10, 20)
                num1 = num2 * random.randint(15, 25)

            result = num1 // num2
            question = f"[TEST-ZAXXON] Combien font {num1} ÷ {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-1), str(result+1), str(num1//max(1, num2-1))]
            random.shuffle(choices)
            explanation = f"[TEST-ZAXXON] {num1} ÷ {num2} = {result}"
            title = f"[TEST-ZAXXON] Exercice de {selected_type.lower()}"
            is_ai_generated = False

        else:
            # Par défaut, faire une addition
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            result = num1 + num2
            question = f"[TEST-ZAXXON] Combien font {num1} + {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-1), str(result+1), str(result+2)]
            random.shuffle(choices)
            explanation = f"[TEST-ZAXXON] {num1} + {num2} = {result}"
            title = f"[TEST-ZAXXON] Exercice de {selected_type.lower()}"
            is_ai_generated = False

    try:
        # Créer l'exercice en utilisant le modèle ORM directement
        from app.models.exercise import Exercise as ExerciseModel
        from datetime import datetime

        new_exercise = ExerciseModel(
            title=title,
            exercise_type=selected_type,
            difficulty=selected_difficulty,
            question=question,
            correct_answer=correct_answer,
            choices=choices,
            explanation=explanation,
            hint="Résolvez le calcul étape par étape",
            is_active=True,
            is_archived=False,
            view_count=0,
            creator_id=1,  # Admin ou système
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Ajouter à la session et commiter pour sauvegarder
        db.add(new_exercise)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'exercice: {str(e)}"
        )

    # Retourner une redirection vers la page des exercices
    return RedirectResponse(url="/exercises?generated=true", status_code=303)


@router.get("/{exercise_id}", response_model=Exercise)


def get_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_id: int,
) -> Any:
    """
    Récupérer un exercice par ID.
    """
    # Exercices prédéfinis
    if exercise_id == 1:
        return {
            "id": 1,
            "title": "Addition simple",
            "exercise_type": ExerciseType.ADDITION.value,
            "difficulty": DifficultyLevel.INITIE.value,
            "question": "Combien font 70 + 89?",
            "correct_answer": "159",
            "choices": ["159", "150", "149", "169"],
            "explanation": "70 + 89 = 159. On additionne les dizaines (7 + 8 = 15) et les unités (0
                + 9 = 9) pour obtenir 159.",
            "hint": "Ajoutez les dizaines puis les unités",
            "image_url": None,
            "audio_url": None,
            "is_active": True,
            "is_archived": False,
            "view_count": 10,
            "creator_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    elif exercise_id == 2:
        return {
            "id": 2,
            "title": "Multiplication simple",
            "exercise_type": ExerciseType.MULTIPLICATION.value,
            "difficulty": DifficultyLevel.PADAWAN.value,
            "question": "Combien font 12 × 5?",
            "correct_answer": "60",
            "choices": ["55", "60", "65", "70"],
            "explanation": "12 × 5 = 60. On peut calculer 10 × 5 = 50, puis 2 × 5\
                = 10, et enfin 50 + 10 = 60.",
            "hint": "Décomposez 12 en 10 + 2 pour faciliter le calcul",
            "image_url": None,
            "audio_url": None,
            "is_active": True,
            "is_archived": False,
            "view_count": 8,
            "creator_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }
    elif exercise_id >= 3 and exercise_id <= 10:
        # Pour les exercices générés dynamiquement, on crée un exercice à la volée
        import random

        # On sélectionne aléatoirement un type d'exercice et une difficulté
        selected_type = random.choice([t.value for t in ExerciseType])
        selected_difficulty = random.choice([d.value for d in DifficultyLevel])

        # Ajuster la plage de nombres en fonction de la difficulté
        if selected_difficulty == DifficultyLevel.INITIE.value:
            # Initié: nombres entre 1 et 20
            min_range, max_range = 1, 20
        elif selected_difficulty == DifficultyLevel.PADAWAN.value:
            # Padawan: nombres entre 10 et 50
            min_range, max_range = 10, 50
        elif selected_difficulty == DifficultyLevel.CHEVALIER.value:
            # Chevalier: nombres entre 20 et 100
            min_range, max_range = 20, 100
        else:  # Maître
            # Maître: nombres entre 50 et 200
            min_range, max_range = 50, 200

        if selected_type == ExerciseType.ADDITION.value:
            # Génération d'une addition basée sur la difficulté
            num1 = random.randint(min_range, max_range)
            num2 = random.randint(min_range, max_range)
            result = num1 + num2
            question = f"Combien font {num1} + {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + random.randint(1, 10)),
                str(result - random.randint(1, 10)),
                str(result + random.randint(11, 20))
            ]
            random.shuffle(choices)
            explanation = f"{num1} + {num2} = {result}"

        elif selected_type == ExerciseType.SOUSTRACTION.value:
            # Génération d'une soustraction (s'assurer que le résultat est positif)
            num1 = random.randint(min_range + 10, max_range)
            num2 = random.randint(min_range, num1 - 1)  # S'assurer que num2 < num1
            result = num1 - num2
            question = f"Combien font {num1} - {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + random.randint(1, 5)),
                str(result - random.randint(1, 5)),
                str(num2 - num1)  # Erreur courante: inverser l'ordre
            ]
            random.shuffle(choices)
            explanation = f"{num1} - {num2} = {result}"

        elif selected_type == ExerciseType.MULTIPLICATION.value:
            # Génération d'une multiplication
            if selected_difficulty == DifficultyLevel.INITIE.value:
                # Tables de multiplication simples pour les initiés
                num1 = random.randint(2, 10)
                num2 = random.randint(2, 10)
            else:
                # Multiplications plus complexes pour les niveaux supérieurs
                num1 = random.randint(5, min(20, max_range // 5))
                num2 = random.randint(5, min(20, max_range // num1))

            result = num1 * num2
            question = f"Combien font {num1} × {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + num1),  # Erreur: une fois de trop
                str(result - num2),  # Erreur: une fois de moins
                str(num1 + num2)  # Erreur: addition au lieu de multiplication
            ]
            random.shuffle(choices)
            explanation = f"{num1} × {num2} = {result}"

        else:  # Division
            # Génération d'une division (s'assurer que le résultat est un entier)
            if selected_difficulty == DifficultyLevel.INITIE.value:
                # Divisions simples pour les initiés
                num2 = random.randint(2, 10)
                multiplicateur = random.randint(1, 10)
            else:
                # Divisions plus complexes pour les niveaux supérieurs
                num2 = random.randint(2, min(12, max_range // 10))
                multiplicateur = random.randint(2, min(20, max_range // num2))

            num1 = num2 * multiplicateur  # Garantir que la division est exacte
            result = num1 // num2
            question = f"Combien font {num1} ÷ {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + 1),  # Erreur d'arrondi vers le haut
                str(result - 1),  # Erreur d'arrondi vers le bas
                str(num2 // num1 if num1 != 0 else 0)  # Erreur: inverser l'ordre
            ]
            random.shuffle(choices)
            explanation = f"{num1} ÷ {num2} = {result}"

        # Assurer qu'il n'y a pas de doublons dans les choix
        choices = list(dict.fromkeys(choices))

        # Si nous avons moins de 4 choix (à cause de la suppression des doublons),
        # ajoutons des choix supplémentaires
        while len(choices) < 4:
            new_choice = str(int(correct_answer) + random.randint(-20, 20))
            if new_choice != correct_answer and new_choice not in choices:
                choices.append(new_choice)

        # S'assurer que la bonne réponse est bien incluse
        if correct_answer not in choices:
            choices[0] = correct_answer

        return {
            "id": exercise_id,
            "title": f"Exercice {exercise_id} de {selected_type.lower()}",
            "exercise_type": selected_type,
            "difficulty": selected_difficulty,
            "question": question,
            "correct_answer": correct_answer,
            "choices": choices,
            "explanation": explanation,
            "hint": "Résolvez le calcul étape par étape",
            "image_url": None,
            "audio_url": None,
            "is_active": True,
            "is_archived": False,
            "view_count": random.randint(0, 20),
            "creator_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00"
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Exercice non trouvé"
    )


@router.post("/{exercise_id}/attempt", response_model=dict)


def attempt_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_id: int,
    attempt_data: dict,
) -> Any:
    """
    Soumettre une tentative pour un exercice.
    """
    # Récupérer l'exercice
    exercise = None
    try:
        exercise = get_exercise(db=db, exercise_id=exercise_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercice non trouvé"
        )

    # Vérifier la réponse
    user_answer = attempt_data.get("user_answer", "")
    is_correct = user_answer == exercise["correct_answer"]

    return {
        "is_correct": is_correct,
        "feedback": "Bravo, c'est correct!" if is_correct else "Ce n'est pas la bonne réponse.",
        "correct_answer": exercise["correct_answer"] if not is_correct else None,
        "explanation": exercise["explanation"]
    }


@router.delete("/{exercise_id}", status_code=204)


def delete_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_id: int,
) -> None:
    """
    Supprimer un exercice par ID.
    """
    from app.models.exercise import Exercise as ExerciseModel
    from app.models.attempt import Attempt as AttemptModel
    from sqlalchemy.exc import SQLAlchemyError
    import logging
    import traceback
    from sqlalchemy import text

    logger = logging.getLogger(__name__)
    logger.info(f"Tentative de suppression de l'exercice {exercise_id}")

    try:
        # Vérifier si l'exercice existe
        exercise = db.query(ExerciseModel).filter(
            ExerciseModel.id == exercise_id
        ).first()

        if not exercise:
            logger.error(f"Exercice {exercise_id} non trouvé")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercice non trouvé"
            )

        # Utiliser des requêtes SQL brutes pour éviter les problèmes de types PostgreSQL
        try:
            # Une transaction est déjà démarrée implicitement par SQLAlchemy

            # 1. Supprimer d'abord les tentatives associées
            logger.info(f"Suppression des tentatives associées à l'exercice {exercise_id}")
            db.execute(text("DELETE FROM attempts WHERE exercise_id = :exercise_id"),
                      {"exercise_id": exercise_id})

            # 2. Supprimer l'exercice
            logger.info(f"Suppression de l'exercice {exercise_id}")
            db.execute(text("DELETE FROM exercises WHERE id = :exercise_id"),
                      {"exercise_id": exercise_id})

            # Valider la transaction
            db.commit()
            logger.info(f"Exercice {exercise_id} supprimé avec succès")

            return None

        except SQLAlchemyError as sqla_error:
            db.rollback()
            error_msg = str(sqla_error)
            stack_trace = traceback.format_exc()
            logger.error(f"Erreur SQL lors de la suppression: {error_msg}")
            logger.error(f"Stack trace: {stack_trace}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur de base de données: {error_msg}"
            )

    except Exception as e:
        db.rollback()
        stack_trace = traceback.format_exc()
        logger.error(f"Erreur lors de la suppression de l'exercice {exercise_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression de l'exercice: {str(e)}"
        )
