"""
Endpoints API pour la gestion des exercices
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Any, List, Dict, Optional
from fastapi.responses import RedirectResponse
import random
import logging
import uuid
import json
import os
import time
from datetime import datetime, timezone

from app.api.deps import get_db_session, get_current_gardien_or_archiviste, get_current_user
from app.schemas.exercise import Exercise, ExerciseCreate, ExerciseUpdate
from app.models.user import User
from app.models.exercise import DifficultyLevel, ExerciseType
from app.schemas.common import PaginationParams
from app.core.constants import ExerciseTypes, DifficultyLevels, Messages, Tags
from app.core.messages import SystemMessages, ExerciseMessages, InterfaceTexts
from app.core.logging_config import get_logger

# Logger pour ce module
logger = get_logger(__name__)

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
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Créer un nouvel exercice.
    """
    from app.models.exercise import Exercise as ExerciseModel
    
    # Créer un nouvel exercice dans la base de données
    try:
        # Créer l'objet modèle
        new_exercise = ExerciseModel(
            title=exercise_in.title,
            exercise_type=exercise_in.exercise_type,
            difficulty=exercise_in.difficulty,
            question=exercise_in.question,
            correct_answer=exercise_in.correct_answer,
            choices=exercise_in.choices,
            creator_id=current_user.id if current_user else None,
            is_active=True,
            is_archived=False,
            view_count=0
        )
        
        # Ajouter les champs optionnels s'ils sont présents
        if hasattr(exercise_in, "explanation") and exercise_in.explanation:
            new_exercise.explanation = exercise_in.explanation
        
        if hasattr(exercise_in, "hint") and exercise_in.hint:
            new_exercise.hint = exercise_in.hint
            
        if hasattr(exercise_in, "image_url") and exercise_in.image_url:
            new_exercise.image_url = exercise_in.image_url
            
        if hasattr(exercise_in, "audio_url") and exercise_in.audio_url:
            new_exercise.audio_url = exercise_in.audio_url
            
        # Ajouter et valider en base de données
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        
        # Convertir en dictionnaire pour correspondre au schéma de réponse
        return {
            "id": new_exercise.id,
            "title": new_exercise.title,
            "exercise_type": new_exercise.exercise_type,
            "difficulty": new_exercise.difficulty,
            "question": new_exercise.question,
            "correct_answer": new_exercise.correct_answer,
            "choices": new_exercise.choices,
            "is_active": new_exercise.is_active,
            "is_archived": new_exercise.is_archived,
            "view_count": new_exercise.view_count,
            "creator_id": new_exercise.creator_id,
            "created_at": new_exercise.created_at.isoformat() if new_exercise.created_at else None,
            "updated_at": new_exercise.updated_at.isoformat() if new_exercise.updated_at else None,
            "explanation": new_exercise.explanation,
            "hint": new_exercise.hint,
            "image_url": new_exercise.image_url,
            "audio_url": new_exercise.audio_url
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la création de l'exercice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'exercice: {str(e)}"
        )


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
    Générer un exercice mathématique avec des paramètres aléatoires adaptés au niveau.
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
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        result = num1 + num2
        question = f"[{Messages.AI_EXERCISE_PREFIX}] Si tu as {num1} cristaux Kyber et que tu en trouves {num2} autres, combien de cristaux as-tu au total?"
        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 10)), str(result+random.randint(1, 10)), str(result+random.randint(11, 20))]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Tu avais {num1} puis tu en as ajouté {num2}. Ainsi, {num1} + {num2} = {result}."

    elif exercise_type == ExerciseType.SOUSTRACTION.value:
        num1 = random.randint(5, 15)
        num2 = random.randint(1, 5)
        result = num1 - num2
        question = f"[{Messages.AI_EXERCISE_PREFIX}] Tu as {num1} portions de rations et tu en consommes {num2}. Combien de portions te reste-t-il?"
        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 5)), str(result+random.randint(1, 5)), str(num2)]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Tu avais {num1} au départ et tu en as perdu {num2}. Donc, {num1} - {num2} = {result}."

    elif exercise_type == ExerciseType.MULTIPLICATION.value:
        num1 = random.randint(1, 5)
        num2 = random.randint(1, 5)
        result = num1 * num2
        question = f"[{Messages.AI_EXERCISE_PREFIX}] Chaque Padawan a {num2} cristaux Kyber. S'il y a {num1} Padawans, combien de cristaux y a-t-il au total?"
        correct_answer = str(result)
        choices = [str(result), str(result-num2), str(result+num1), str(num1+num2)]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Il y a {num1} groupes de {num2} éléments chacun. Donc, {num1} × {num2} = {result}."

    elif exercise_type == ExerciseType.DIVISION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            result = num1 + num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Si tu as {num1} cristaux Kyber et que tu en trouves {num2} autres, combien de cristaux as-tu au total?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num1 = random.randint(10, 30)
            num2 = random.randint(10, 30)
            result = num1 + num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Ton escadron de {num1} chasseurs TIE est rejoint par {num2} autres. Combien de vaisseaux forment maintenant ton escadron?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num1 = random.randint(30, 100)
            num2 = random.randint(30, 100)
            result = num1 + num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] La République dispose de {num1} destroyers et en construit {num2} supplémentaires. Quelle est la taille de la flotte?"
        else:  # Maître
            num1 = random.randint(100, 500)
            num2 = random.randint(100, 500)
            result = num1 + num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] L'Empire compte {num1} systèmes sous son contrôle et en conquiert {num2} de plus. Combien de systèmes sont maintenant sous contrôle impérial?"

        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 10)), str(result+random.randint(1, 10)), str(result+random.randint(11, 20))]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Tu avais {num1} puis tu en as ajouté {num2}. Ainsi, {num1} + {num2} = {result}."

    elif exercise_type == ExerciseType.SOUSTRACTION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num1 = random.randint(5, 15)
            num2 = random.randint(1, 5)
            result = num1 - num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Tu as {num1} portions de rations et tu en consommes {num2}. Combien de portions te reste-t-il?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num1 = random.randint(20, 50)
            num2 = random.randint(5, 20)
            result = num1 - num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Tu commandais {num1} stormtroopers mais {num2} ont été capturés par la Résistance. Combien de stormtroopers te reste-t-il?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num1 = random.randint(50, 150)
            num2 = random.randint(20, 50)
            result = num1 - num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Ta flotte a {num1} vaisseaux mais {num2} sont endommagés après la bataille. Combien de vaisseaux sont encore opérationnels?"
        else:  # Maître
            num1 = random.randint(200, 500)
            num2 = random.randint(50, 200)
            result = num1 - num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] L'Empire contrôle {num1} planètes, mais {num2} se rebellent et rejoignent l'Alliance. Combien de planètes restent fidèles à l'Empire?"

        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 5)), str(result+random.randint(1, 5)), str(num2)]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Tu avais {num1} au départ et tu en as perdu {num2}. Donc, {num1} - {num2} = {result}."

    elif exercise_type == ExerciseType.MULTIPLICATION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num1 = random.randint(1, 5)
            num2 = random.randint(1, 5)
            result = num1 * num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Chaque Padawan a {num2} cristaux Kyber. S'il y a {num1} Padawans, combien de cristaux y a-t-il au total?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num1 = random.randint(2, 10)
            num2 = random.randint(2, 10)
            result = num1 * num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Chaque escadron compte {num2} vaisseaux. Combien de vaisseaux y a-t-il dans {num1} escadrons?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num1 = random.randint(5, 12)
            num2 = random.randint(5, 12)
            result = num1 * num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Chaque Star Destroyer transporte {num2} TIE Fighters. Combien de TIE Fighters y a-t-il sur {num1} Star Destroyers?"
        else:  # Maître
            num1 = random.randint(10, 20)
            num2 = random.randint(10, 20)
            result = num1 * num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Un bataillon compte {num2} régiments de clones. Si l'armée de la République déploie {num1} bataillons, combien de régiments sont mobilisés au total?"

        correct_answer = str(result)
        choices = [str(result), str(result-num2), str(result+num1), str(num1+num2)]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Il y a {num1} groupes de {num2} éléments chacun. Donc, {num1} × {num2} = {result}."

    elif exercise_type == ExerciseType.DIVISION.value:
        if difficulty == DifficultyLevel.INITIE.value:
            num2 = random.choice([2, 5, 10])
            num1 = num2 * random.randint(1, 5)
            result = num1 // num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Tu dois partager équitablement {num1} portions de rations entre {num2} Padawans. Combien chaque Padawan recevra-t-il?"
        elif difficulty == DifficultyLevel.PADAWAN.value:
            num2 = random.randint(2, 10)
            num1 = num2 * random.randint(2, 10)
            result = num1 // num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Tu as {num1} stormtroopers à répartir également dans {num2} transports. Combien de stormtroopers embarqueront dans chaque transport?"
        elif difficulty == DifficultyLevel.CHEVALIER.value:
            num2 = random.randint(5, 15)
            num1 = num2 * random.randint(5, 15)
            result = num1 // num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] La flotte impériale de {num1} TIE Fighters doit être répartie équitablement entre {num2} Star Destroyers. Combien de TIE Fighters seront affectés à chaque vaisseau?"
        else:  # Maître
            num2 = random.randint(10, 20)
            remainder = random.randint(0, num2-1)
            num1 = num2 * random.randint(10, 20) + remainder
            result = num1 // num2
            if remainder > 0:
                question = f"[{Messages.AI_EXERCISE_PREFIX}] L'Empire doit diviser {num1} troupes en {num2} garnisons égales. Combien de soldats y aura-t-il dans chaque garnison? (Donne le quotient sans le reste)"
            else:
                question = f"[{Messages.AI_EXERCISE_PREFIX}] L'Empire doit diviser {num1} troupes en {num2} garnisons égales. Combien de soldats y aura-t-il dans chaque garnison?"

        correct_answer = str(result)
        choices = [str(result), str(result-1), str(result+1), str(result*2)]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Pour répartir {num1} éléments en {num2} groupes égaux, chaque groupe contient {result} éléments car {num1} ÷ {num2} = {result}."

    else:
        # Ce bloc ne devrait jamais être exécuté grâce à la normalisation précédente
        # Par précaution, on fait une addition sur le thème Star Wars
        num1 = random.randint(5, 25)
        num2 = random.randint(5, 25)
        result = num1 + num2
        question = f"[{Messages.AI_EXERCISE_PREFIX}] Si tu as {num1} crédits galactiques et que tu en gagnes {num2} de plus dans une mission, combien de crédits possèdes-tu maintenant?"
        correct_answer = str(result)
        choices = [str(result), str(result-random.randint(1, 5)), str(result+random.randint(1, 5)), str(result+random.randint(6, 10))]
        explanation = f"[{Messages.AI_EXERCISE_PREFIX}] Tu avais {num1} crédits et tu en as gagné {num2} de plus. Donc {num1} + {num2} = {result} crédits au total."

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
        # Utiliser les mappings centralisés des types d'exercices
        for type_key, aliases in ExerciseTypes.TYPE_ALIASES.items():
            if exercise_type in aliases:
                selected_type = type_key
                break
        else:
            selected_type = ExerciseType.ADDITION.value

    # Si la difficulté n'est pas spécifiée, en choisir une au hasard
    if not difficulty:
        # Choisir une difficulté aléatoire
        selected_difficulty = random.choice([d.value for d in DifficultyLevel])
    else:
        # Normaliser la difficulté fournie
        difficulty = difficulty.lower()
        # Utiliser les mappings centralisés pour les niveaux de difficulté
        for level_key, aliases in DifficultyLevels.LEVEL_ALIASES.items():
            if difficulty in aliases:
                selected_difficulty = level_key
                break
        else:
            selected_difficulty = DifficultyLevel.PADAWAN.value

    # Déterminer les limites de nombres en fonction de la difficulté
    if selected_difficulty == DifficultyLevel.INITIE.value:
        min_range, max_range = 1, 10  # Nombres simples pour les débutants
    elif selected_difficulty == DifficultyLevel.PADAWAN.value:
        min_range, max_range = 10, 50  # Nombres intermédiaires
    elif selected_difficulty == DifficultyLevel.CHEVALIER.value:
        min_range, max_range = 20, 100  # Nombres plus grands
    else:  # DifficultyLevel.MAITRE.value
        min_range, max_range = 50, 200  # Nombres avancés

    # Variables pour suivre si l'exercice est généré par IA
    is_ai_generated = False
    
    # Si l'utilisateur a demandé de générer avec IA
    if ai:
        ai_exercise = generate_ai_exercise(selected_type, selected_difficulty)
        question = ai_exercise["question"]
        correct_answer = ai_exercise["correct_answer"]
        choices = ai_exercise["choices"]
        # S'assurer qu'une explication existe toujours
        explanation = ai_exercise.get("explanation", "")
        if explanation is None or explanation == "" or explanation == "None":
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] La réponse est {correct_answer}. Dans cet exercice de {selected_type}, tu dois trouver le résultat de l'opération."
        is_ai_generated = True

        # Utiliser les valeurs normalisées retournées par generate_ai_exercise pour assurer la cohérence
        if "exercise_type" in ai_exercise:
            selected_type = ai_exercise["exercise_type"]

        if "difficulty" in ai_exercise:
            selected_difficulty = ai_exercise["difficulty"]

        # Utiliser les noms d'affichage des constantes centralisées
        type_label = DISPLAY_NAMES.get(selected_type, selected_type.capitalize())
        difficulty_label = DISPLAY_NAMES.get(selected_difficulty, selected_difficulty.capitalize())

        title = f"[{Messages.AI_EXERCISE_PREFIX}] Épreuve de {type_label} - Niveau {difficulty_label}"
    else:
        # Génération algorithmique standard
        if selected_type == ExerciseType.ADDITION.value:
            # Génération d'une addition basée sur la difficulté
            num1 = random.randint(min_range, max_range)
            num2 = random.randint(min_range, max_range)
            result = num1 + num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} + {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + random.randint(1, 10)),
                str(result - random.randint(1, 10)),
                str(result + random.randint(11, 20))
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} + {num2} = {result}"
            title = f"[{Messages.AI_EXERCISE_PREFIX}] Exercice de {selected_type.lower()}"
            is_ai_generated = False

        elif selected_type == ExerciseType.SOUSTRACTION.value:
            # Génération d'une soustraction
            num1 = random.randint(min_range + 10, max_range)
            num2 = random.randint(min_range, num1 - 1)  # S'assurer que num2 < num1
            result = num1 - num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} - {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + random.randint(1, 5)),
                str(result - random.randint(1, 5)),
                str(num2 - num1)  # Erreur courante: inverser l'ordre
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} - {num2} = {result}"

        elif selected_type == ExerciseType.MULTIPLICATION.value:
            # Génération d'une multiplication
            num1 = random.randint(5, min(20, max_range // 5))
            num2 = random.randint(5, min(20, max_range // num1))

            result = num1 * num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} × {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + num1),  # Erreur: une fois de trop
                str(result - num2),  # Erreur: une fois de moins
                str(num1 + num2)  # Erreur: addition au lieu de multiplication
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} × {num2} = {result}"

        elif selected_type == ExerciseType.DIVISION.value:
            # Génération d'une division (s'assurer que le résultat est un entier)
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
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} ÷ {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + 1),  # Erreur d'arrondi vers le haut
                str(result - 1),  # Erreur d'arrondi vers le bas
                str(num2 // num1 if num1 != 0 else 0)  # Erreur: inverser l'ordre
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} ÷ {num2} = {result}"

        else:
            # Par défaut, faire une addition
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            result = num1 + num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} + {num2}?"
            correct_answer = str(result)
            choices = [str(result), str(result-1), str(result+1), str(result+2)]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} + {num2} = {result}"
            title = f"[{Messages.AI_EXERCISE_PREFIX}] Exercice de {selected_type.lower()}"
            is_ai_generated = False

    try:
        # S'assurer que l'explication n'est jamais NULL
        if explanation is None or explanation == "" or explanation == "None":
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] La réponse est {correct_answer}."
            
        print(f"Création d'un nouvel exercice avec explication: {explanation}")
            
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
            explanation=explanation,  # Assurer que l'explication est définie et non-nulle
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
        db.refresh(new_exercise)
        
        print(f"Exercice créé avec ID {new_exercise.id}, explication: {new_exercise.explanation}")

    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la création de l'exercice: {str(e)}")
        import traceback
        traceback.print_exc()
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
            "explanation": "70 + 89 = 159. On additionne les dizaines (7 + 8 = 15) et les unités (0 + 9 = 9) pour obtenir 159.",
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
            "explanation": "12 × 5 = 60. On peut calculer 10 × 5 = 50, puis 2 × 5 = 10, et enfin 50 + 10 = 60.",
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
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} + {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + random.randint(1, 10)),
                str(result - random.randint(1, 10)),
                str(result + random.randint(11, 20))
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} + {num2} = {result}"

        elif selected_type == ExerciseType.SOUSTRACTION.value:
            # Génération d'une soustraction (s'assurer que le résultat est positif)
            num1 = random.randint(min_range + 10, max_range)
            num2 = random.randint(min_range, num1 - 1)  # S'assurer que num2 < num1
            result = num1 - num2
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} - {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + random.randint(1, 5)),
                str(result - random.randint(1, 5)),
                str(num2 - num1)  # Erreur courante: inverser l'ordre
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} - {num2} = {result}"

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
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} × {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + num1),  # Erreur: une fois de trop
                str(result - num2),  # Erreur: une fois de moins
                str(num1 + num2)  # Erreur: addition au lieu de multiplication
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} × {num2} = {result}"

        else:  # Division
            # Génération d'une division (s'assurer que le résultat est un entier)
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
            question = f"[{Messages.AI_EXERCISE_PREFIX}] Combien font {num1} ÷ {num2}?"
            correct_answer = str(result)

            # Générer des choix proches mais différents
            choices = [
                str(result),  # Bonne réponse
                str(result + 1),  # Erreur d'arrondi vers le haut
                str(result - 1),  # Erreur d'arrondi vers le bas
                str(num2 // num1 if num1 != 0 else 0)  # Erreur: inverser l'ordre
            ]
            random.shuffle(choices)
            explanation = f"[{Messages.AI_EXERCISE_PREFIX}] {num1} ÷ {num2} = {result}"

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
            "explanation": explanation if explanation is not None else "",
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


@router.post("/{exercise_id}/submit", response_model=dict)
async def submit_exercise(
    exercise_id: int,
    data: dict,
    db: Session = Depends(get_db_session)
):
    """
    Soumettre une réponse à un exercice et recevoir un feedback.
    
    - Vérifie si la réponse est correcte
    - Enregistre la tentative dans la base de données (si authentifié)
    - Retourne un feedback approprié
    """
    
    # Récupérer l'exercice
    exercise_data = None
    try:
        exercise_data = get_exercise(db=db, exercise_id=exercise_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercice non trouvé"
        )

    # Si nous trouvons l'exercice
    if exercise_data:
        # Vérifier si la réponse est correcte
        selected_answer = data.get("selected_answer", "")
        is_correct = selected_answer == exercise_data["correct_answer"]
        
        # Préparation des données de réponse
        explanation = exercise_data.get("explanation", "")
        if explanation is None or explanation == "" or explanation == "None":
            # Créer une explication de secours basée sur le type d'exercice et la réponse
            exercise_type = exercise_data.get("exercise_type", "")
            if "addition" in exercise_type.lower():
                explanation = f"La somme des nombres est {exercise_data['correct_answer']}."
            elif "soustraction" in exercise_type.lower():
                explanation = f"La différence entre les nombres est {exercise_data['correct_answer']}."
            elif "multiplication" in exercise_type.lower():
                explanation = f"Le produit des nombres est {exercise_data['correct_answer']}."
            elif "division" in exercise_type.lower():
                explanation = f"Le quotient des nombres est {exercise_data['correct_answer']}."
            else:
                explanation = f"La réponse correcte est {exercise_data['correct_answer']}."
            
        response_data = {
            "is_correct": is_correct,
            "correct_answer": exercise_data["correct_answer"],
            "explanation": explanation
        }
        
        # TODO: Enregistrer la tentative dans la base de données
        # Si un utilisateur est authentifié
        
        return response_data
    
    # Si l'exercice n'est pas trouvé
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Exercice non trouvé"
    )


@router.delete("/{exercise_id}", status_code=204,
               summary="Archiver un exercice",
               description="Archive un exercice et conserve toutes ses données associées. Nécessite les droits de Gardien ou d'Archiviste.")


def delete_exercise(
    *,
    db: Session = Depends(get_db_session),
    exercise_id: int,
    current_user: User = Depends(get_current_gardien_or_archiviste)
) -> None:
    """
    Archive un exercice par ID (marque comme supprimé sans suppression physique).
    
    Cette opération marque l'exercice comme archivé (is_archived = true) mais conserve 
    toutes les données associées dans la base de données. L'exercice n'apparaîtra plus
    dans les résultats de recherche standard mais peut être récupéré si nécessaire.
    
    Nécessite un utilisateur avec le rôle Gardien ou Archiviste.
    
    - **exercise_id**: ID de l'exercice à archiver
    
    Retourne un code 204 (No Content) en cas de succès.
    
    Génère une erreur 404 si l'exercice n'existe pas.
    Génère une erreur 500 en cas de problème lors de l'archivage.
    """
    from app.models.exercise import Exercise as ExerciseModel
    from sqlalchemy.exc import SQLAlchemyError
    import logging
    import traceback

    logger = logging.getLogger(__name__)
    logger.info(f"Tentative d'archivage de l'exercice {exercise_id}")

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

        # Marquer l'exercice comme archivé au lieu de le supprimer physiquement
        exercise.is_archived = True
        exercise.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Vérifier que l'exercice a bien été marqué comme archivé
        db.refresh(exercise)
        if not exercise.is_archived:
            db.rollback()
            logger.error(f"Exercice {exercise_id} n'a pas été correctement archivé")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="L'exercice n'a pas été correctement archivé"
            )
        
        logger.info(f"Exercice {exercise_id} archivé avec succès")
        return None

    except SQLAlchemyError as sqla_error:
        db.rollback()
        error_msg = str(sqla_error)
        stack_trace = traceback.format_exc()
        logger.error(f"Erreur SQL lors de l'archivage: {error_msg}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de base de données: {error_msg}"
        )
    except Exception as e:
        db.rollback()
        stack_trace = traceback.format_exc()
        logger.error(f"Erreur lors de l'archivage de l'exercice {exercise_id}: {str(e)}")
        logger.error(f"Stack trace: {stack_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'archivage de l'exercice: {str(e)}"
        )


@router.post("/{exercise_id}/attempt", response_model=dict)
def attempt_exercise(
    exercise_id: int,
    attempt_data: dict,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Enregistrer une tentative pour un exercice spécifique.
    
    - **exercise_id**: ID de l'exercice
    - **attempt_data**: Données de la tentative (user_answer, time_spent)
    
    Retourne les informations sur la tentative, notamment si la réponse est correcte.
    """
    from app.models.exercise import Exercise as ExerciseModel
    from app.models.attempt import Attempt as AttemptModel
    
    # Vérifier si l'exercice existe
    exercise = db.query(ExerciseModel).filter(
        ExerciseModel.id == exercise_id
    ).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercice non trouvé"
        )
    
    # Extraire les données de la tentative
    user_answer = attempt_data.get("user_answer", "")
    time_spent = attempt_data.get("time_spent", None)
    
    # Vérifier si la réponse est correcte
    is_correct = user_answer == exercise.correct_answer
    
    # Créer une nouvelle tentative en base de données
    try:
        attempt = AttemptModel(
            user_id=current_user.id,
            exercise_id=exercise_id,
            user_answer=user_answer,
            is_correct=is_correct,
            time_spent=time_spent
        )
        
        db.add(attempt)
        db.commit()
        
        # Préparer la réponse
        response = {
            "id": attempt.id,
            "is_correct": is_correct,
            "correct_answer": exercise.correct_answer,
            "user_answer": user_answer,
            "time_spent": time_spent,
            "exercise_id": exercise_id,
            "user_id": current_user.id,
            "created_at": attempt.created_at.isoformat() if attempt.created_at else None
        }
        
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'enregistrement de la tentative: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'enregistrement de la tentative: {str(e)}"
        )
