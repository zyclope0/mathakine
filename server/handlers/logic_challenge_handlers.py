"""
Handlers pour les logic challenges et missions hybrides.
"""

from starlette.responses import JSONResponse, RedirectResponse

from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.views import get_current_user, render_error, render_template


async def logic_challenge_page(request):
    """
    Page d'interface pour résoudre un logic challenge spécifique.
    
    URL: /logic-challenge/{challenge_id}
    """
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        challenge_id = int(request.path_params["challenge_id"])
        adapter = EnhancedServerAdapter()
        
        # Récupérer le logic challenge spécifique
        challenge = adapter.get_logic_challenge(challenge_id)
        
        if not challenge:
            return render_error(
                request=request,
                error="Challenge introuvable",
                message=f"Le défi logique #{challenge_id} n'existe pas.",
                status_code=404
            )
        
        # Mapper les types de challenges vers des templates appropriés
        challenge_data = {
            "id": challenge.get("id"),
            "title": challenge.get("title", "Défi Logique"),
            "description": challenge.get("description", ""),
            "challenge_type": challenge.get("challenge_type", "SEQUENCE"),
            "question": challenge.get("question") or challenge.get("description"),
            "choices": challenge.get("choices", []),
            "hints": challenge.get("hints", []),
            "estimated_time": challenge.get("estimated_time_minutes", 15),
            "difficulty_rating": challenge.get("difficulty_rating", 3.0),
            "visual_data": challenge.get("visual_data"),
            "correct_answer": challenge.get("correct_answer"),  # Ne pas exposer côté client !
            "hint_level1": challenge.get("hint_level1"),
            "hint_level2": challenge.get("hint_level2"),
            "hint_level3": challenge.get("hint_level3")
        }
        
        # Choisir le template selon le type
        template_map = {
            "SEQUENCE": "logic_challenge_sequence.html",
            "PATTERN": "logic_challenge_pattern.html", 
            "PUZZLE": "logic_challenge_puzzle.html"
        }
        
        template_name = template_map.get(
            challenge.get("challenge_type", "SEQUENCE"), 
            "logic_challenge_generic.html"
        )
        
        from server.template_handler import render_template as rt
        return rt(template_name, request, {
            "current_user": current_user,
            "challenge": challenge_data,
            "page_title": f"Défi Logique: {challenge_data['title']}"
        })
        
    except ValueError:
        return render_error(
            request=request,
            error="ID invalide",
            message="L'identifiant du défi doit être un nombre.",
            status_code=400
        )
    except Exception as challenge_load_error:
        print(f"Erreur lors du chargement du challenge {challenge_id}: {str(challenge_load_error)}")
        import traceback
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur système",
            message=f"Impossible de charger le défi logique: {str(e)}",
            status_code=500
        )


async def hybrid_mission_page(request):
    """
    Page d'interface pour une mission hybride (exercices + logic challenges).
    
    URL: /hybrid-mission/{mission_id}
    """
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        mission_id = int(request.path_params["mission_id"])
        
        # Missions hybrides prédéfinies
        hybrid_missions = {
            999: {
                "id": 999,
                "title": "Mission Alderaan",
                "description": "Mission complète pour sauver Alderaan !",
                "story": "La princesse Leia a besoin de votre aide. Cette mission critique combine exercices mathématiques et énigmes logiques pour calculer les coordonnées de sauvetage.",
                "parts": [
                    {
                        "type": "exercises",
                        "title": "Calculs de Navigation",
                        "description": "15 exercices de géométrie niveau Chevalier",
                        "target": {"exercise_type": "geometrie", "difficulty": "chevalier", "count": 15},
                        "progress": 7,
                        "total": 15,
                        "completed": False
                    },
                    {
                        "type": "logic",
                        "title": "Énigmes de Coordination",
                        "description": "3 énigmes logiques avancées",
                        "target": {"challenge_types": ["SEQUENCE", "PUZZLE", "PATTERN"], "count": 3},
                        "progress": 0,
                        "total": 3,
                        "completed": False,
                        "unlocked": False  # Débloqué après les exercices
                    }
                ],
                "rewards": {
                    "stars": 500,
                    "badges": ["Héros d'Alderaan"],
                    "special": "Accès au rang Maître Jedi",
                    "bonus": "Sabre laser holographique"
                },
                "time_limit": "4j 12h 33m",
                "difficulty": "chevalier",
                "estimated_duration": "45-60 minutes"
            }
        }
        
        mission = hybrid_missions.get(mission_id)
        
        if not mission:
            return render_error(
                request=request,
                error="Mission introuvable",
                message=f"La mission hybride #{mission_id} n'existe pas.",
                status_code=404
            )
        
        return render_template("hybrid_mission.html", request, {
            "current_user": current_user,
            "mission": mission,
            "page_title": f"Mission Hybride: {mission['title']}"
        })
        
    except ValueError:
        return render_error(
            request=request,
            error="ID invalide",
            message="L'identifiant de la mission doit être un nombre.",
            status_code=400
        )
    except Exception as submission_error:
        return render_error(
            request=request,
            error="Erreur système",
            message=f"Impossible de charger la mission hybride: {str(e)}",
            status_code=500
        )


async def submit_logic_challenge_answer(request):
    """
    Soumet une réponse à un logic challenge.
    
    URL: POST /api/logic-challenge/{challenge_id}/submit
    """
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return JSONResponse(
            {"success": False, "error": "Non authentifié"},
            status_code=401
        )
    
    try:
        challenge_id = int(request.path_params["challenge_id"])
        data = await request.json()
        user_answer = data.get("answer", "").strip()
        
        if not user_answer:
            return JSONResponse({
                "success": False,
                "error": "Réponse vide",
                "message": "Veuillez fournir une réponse."
            }, status_code=400)
        
        adapter = EnhancedServerAdapter()
        
        # Récupérer le challenge pour vérifier la réponse
        challenge = adapter.get_logic_challenge(challenge_id)
        
        if not challenge:
            return JSONResponse({
                "success": False,
                "error": "Challenge introuvable"
            }, status_code=404)
        
        # Vérifier la réponse
        correct_answer = challenge.get("correct_answer", "").strip().lower()
        user_answer_normalized = user_answer.lower()
        
        is_correct = user_answer_normalized == correct_answer
        
        # Enregistrer la tentative (TODO: implémenter sauvegarde en DB)
        result = {
            "success": True,
            "is_correct": is_correct,
            "user_answer": user_answer,
            "message": "Correct ! Bien joué !" if is_correct else "Incorrect, essayez encore !",
            "points_earned": 0,
            "explanation": challenge.get("solution_explanation", "") if is_correct else None
        }
        
        if is_correct:
            # Calculer les points selon la difficulté
            difficulty_rating = challenge.get("difficulty_rating", 3.0)
            points_earned = int(50 + (difficulty_rating * 25))
            result["points_earned"] = points_earned
            
            # TODO: Ajouter les points au profil utilisateur
            # TODO: Vérifier si c'est la première fois et donner bonus
            # TODO: Mettre à jour les statistiques
        
        return JSONResponse(result)
        
    except ValueError:
        return JSONResponse({
            "success": False,
            "error": "ID invalide"
        }, status_code=400)
    except Exception as hint_error:
        return JSONResponse({
            "success": False,
            "error": "Erreur système",
            "message": str(e)
        }, status_code=500) 