"""
Handlers pour le système de challenges hybrides.
"""

from starlette.responses import JSONResponse, RedirectResponse
from server.views import get_current_user, render_template, render_error
from app.services.enhanced_server_adapter import EnhancedServerAdapter


async def hybrid_challenges_page(request):
    """
    Page principale des challenges hybrides avec les 3 sections.
    
    URL: /challenges-hybrid
    """
    print("=== DEBUT HYBRID_CHALLENGES_PAGE HANDLER ===")
    print("=== DEBUT HYBRID_CHALLENGES_PAGE HANDLER ===")
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        adapter = EnhancedServerAdapter()
        
        # === SECTION 1: CHALLENGES D'EXERCICES ===
        exercise_challenges = [
            {
                "id": 1,
                "type": "EXERCISE",
                "name": "Sommes de Tatooine",
                "icon": "🌅",
                "story": "Aide Luke Skywalker à compter ses crédits avant son départ pour l'aventure !",
                "target": "5 exercices d'addition niveau Initié",
                "reward": "50 ⭐ + Badge Compteur de Tatooine",
                "redirect_url": "/exercises?exercise_type=addition&difficulty=initie",
                "progress": 80,  # En pourcentage
                "progress_text": "4/5 exercices"
            },
            {
                "id": 2, 
                "type": "EXERCISE",
                "name": "Calculs Hyperspatiaux",
                "icon": "⚡",
                "story": "Calcule les vitesses des vaisseaux rebelles pour échapper à l'Empire !",
                "target": "8 exercices de multiplication niveau Padawan",
                "reward": "120 ⭐ + Badge Pilote Hyperespace",
                "redirect_url": "/exercises?exercise_type=multiplication&difficulty=padawan",
                "progress": 25,
                "progress_text": "2/8 exercices"
            },
            {
                "id": 3,
                "type": "EXERCISE", 
                "name": "Partage des Rations",
                "icon": "🍞",
                "story": "Distribue équitablement les provisions aux soldats de l'Alliance Rebelle !",
                "target": "6 exercices de fractions niveau Chevalier",
                "reward": "200 ⭐ + Badge Maître des Rations",
                "redirect_url": "/exercises?exercise_type=fractions&difficulty=chevalier",
                "progress": 0,
                "progress_text": "0/6 exercices"
            },
            {
                "id": 4,
                "type": "EXERCISE",
                "name": "Architecture Étoile Noire", 
                "icon": "🔧",
                "story": "Analyse les plans secrets pour trouver les points faibles de l'Étoile Noire !",
                "target": "10 exercices de géométrie niveau Maître",
                "reward": "500 ⭐ + Badge Architecte Impérial",
                "redirect_url": "/exercises?exercise_type=geometrie&difficulty=maitre",
                "progress": 0,
                "progress_text": "0/10 exercices"
            }
        ]
        
        # === SECTION 2: LOGIC CHALLENGES ===
        try:
            logic_challenges_raw = adapter.get_logic_challenges(limit=6)
            logic_challenges = []
            
            print(f"DEBUG: Récupéré {len(logic_challenges_raw) if logic_challenges_raw else 0} énigmes de la base")
            
            # Créer les challenges dynamiquement basés sur les vraies énigmes
            for i, challenge in enumerate(logic_challenges_raw or []):
                # Utiliser les vraies données de l'énigme
                real_title = challenge.get("title", f"Énigme Logique #{i+1}")
                real_description = challenge.get("description", "Énigme de logique spatiale")
                real_type = challenge.get("challenge_type", "SEQUENCE")
                
                # Choisir une icône basée sur le type
                type_icons = {
                    "SEQUENCE": "🚀",
                    "PATTERN": "🌌", 
                    "PUZZLE": "🔧",
                    "DEDUCTION": "🕵️",
                    "VISUAL": "🔺",
                    "SPATIAL": "🛸",
                    "PROBABILITY": "🎲",
                    "GRAPH": "📊",
                    "CODING": "💻",
                    "CHESS": "♛"
                }
                icon = type_icons.get(real_type, "🧠")
                
                logic_challenges.append({
                    "id": 100 + i,  # Offset pour éviter conflits avec exercise challenges
                    "type": "LOGIC",
                    "name": real_title,  # Utiliser le vrai titre
                    "icon": icon,        # Icône basée sur le type
                    "story": real_description,  # Utiliser la vraie description
                    "target": f"Résoudre cette énigme de type {real_type.lower()}",
                    "reward": f"{int(150 + (i * 25))} ⭐ + Badge {real_type.title()}",
                    "logic_id": challenge.get("id"),  # Vrai ID de l'énigme
                    "challenge_type": real_type,
                    "difficulty_rating": challenge.get("difficulty_rating", 3.0),
                    "estimated_time": challenge.get("estimated_time_minutes", 15)
                })
                
        except Exception as e:
            print(f"Erreur récupération logic_challenges: {e}")
            # Fallback avec vos nouvelles énigmes (IDs 2292-2296)
            logic_challenges = [
                {
                    "id": 100,
                    "type": "LOGIC",
                    "name": "🚀 Code de Navigation Spatiale",
                    "icon": "🚀",
                    "story": "L'ordinateur de bord d'un vaisseau spatial affiche une séquence de navigation. Déchiffrez le code !",
                    "target": "Résoudre la séquence géométrique",
                    "reward": "150 ⭐ + Badge Navigation",
                    "logic_id": 2292,
                    "challenge_type": "SEQUENCE"
                },
                {
                    "id": 101,
                    "type": "LOGIC", 
                    "name": "🌌 Formation de Constellation",
                    "icon": "🌌",
                    "story": "Les étoiles d'une constellation forment un pattern géométrique. Identifiez la règle !",
                    "target": "Reconnaître le pattern stellaire",
                    "reward": "175 ⭐ + Badge Constellation",
                    "logic_id": 2293,
                    "challenge_type": "PATTERN"
                },
                {
                    "id": 102,
                    "type": "LOGIC",
                    "name": "🔧 Réparation Station Spatiale",
                    "icon": "🔧", 
                    "story": "Un système de la station spatiale est défaillant. Utilisez la logique pour réparer !",
                    "target": "Résoudre le puzzle de dépendances",
                    "reward": "200 ⭐ + Badge Ingénieur",
                    "logic_id": 2294,
                    "challenge_type": "PUZZLE"
                },
                {
                    "id": 103,
                    "type": "LOGIC",
                    "name": "🔺 Géométrie des Astéroïdes",
                    "icon": "🔺", 
                    "story": "Un champ d'astéroïdes présente des formes géométriques. Identifiez le pattern !",
                    "target": "Analyser les formes géométriques",
                    "reward": "175 ⭐ + Badge Géomètre",
                    "logic_id": 2295,
                    "challenge_type": "PATTERN"
                },
                {
                    "id": 104,
                    "type": "LOGIC",
                    "name": "🕵️ Mystère du Cargo Spatial",
                    "icon": "🕵️", 
                    "story": "Un cargo spatial a disparu. Analysez les indices pour déterminer sa destination !",
                    "target": "Résoudre l'enquête par déduction",
                    "reward": "225 ⭐ + Badge Enquêteur",
                    "logic_id": 2296,
                    "challenge_type": "DEDUCTION"
                }
            ]
        
        # === SECTION 3: MISSIONS HYBRIDES ===
        hybrid_missions = [
            {
                "id": 999,
                "type": "HYBRID",
                "name": "Mission Alderaan",
                "icon": "🏆",
                "story": "Mission complète : exercices + énigmes logiques pour sauver Alderaan !",
                "target": "15 exercices géométrie + 3 énigmes logiques",
                "reward": "500 ⭐ + Badge Héros d'Alderaan + Accès Maître Jedi",
                "parts": [
                    {"type": "exercises", "count": 15, "exercise_type": "geometrie", "difficulty": "chevalier"},
                    {"type": "logic", "count": 3, "challenge_types": ["SEQUENCE", "PUZZLE", "PATTERN"]}
                ],
                "progress": 35,
                "progress_text": "7/20 parties terminées",
                "time_remaining": "4j 12h 33m",
                "is_weekly": True
            }
        ]
        
        # === STATISTIQUES UTILISATEUR ===
        user_stats = {
            "total_stars": 1250,
            "challenges_completed": 7,
            "total_challenges": 10,
            "current_rank": "Chevalier Jedi",
            "next_rank": "Maître Jedi",
            "stars_to_next_rank": 750
        }
        
        return render_template("challenges-hybrid.html", request, {
            "current_user": current_user,
            "exercise_challenges": exercise_challenges,
            "logic_challenges": logic_challenges,
            "hybrid_missions": hybrid_missions,
            "user_stats": user_stats,
            "page_title": "Défis Galactiques Hybrides"
        })
        
    except Exception as e:
        return render_error(
            request=request,
            error="Erreur système",
            message=f"Impossible de charger les challenges: {str(e)}",
            status_code=500
        )


async def api_hybrid_start_challenge(request):
    """
    API pour démarrer un challenge hybride.
    
    URL: POST /api/hybrid-challenges/start/{challenge_id}
    """
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return JSONResponse(
            {"success": False, "error": "Non authentifié"},
            status_code=401
        )
    
    try:
        challenge_id = int(request.path_params["challenge_id"])
        
        # Mapping dynamique des challenges vers leurs redirections
        redirect_map = {
            # Challenges d'exercices (1-99)
            1: "/exercises?exercise_type=addition&difficulty=initie",
            2: "/exercises?exercise_type=multiplication&difficulty=padawan", 
            3: "/exercises?exercise_type=fractions&difficulty=chevalier",
            4: "/exercises?exercise_type=geometrie&difficulty=maitre",
            
            # Missions hybrides (999+)
            999: "/hybrid-mission/999"     # Mission Alderaan
        }
        
        # Logic challenges (100-199) - Récupération dynamique
        if 100 <= challenge_id <= 199:
            try:
                from app.services.enhanced_server_adapter import EnhancedServerAdapter
                adapter = EnhancedServerAdapter()
                logic_challenges_raw = adapter.get_logic_challenges(limit=10)
                
                # Calculer l'index dans la liste des énigmes réelles
                logic_index = challenge_id - 100
                if logic_index < len(logic_challenges_raw):
                    real_logic_id = logic_challenges_raw[logic_index].get("id")
                    redirect_url = f"/logic-challenge/{real_logic_id}"
                else:
                    # Fallback vers les énigmes connues
                    fallback_ids = [2292, 2293, 2294, 2295, 2296]
                    if logic_index < len(fallback_ids):
                        redirect_url = f"/logic-challenge/{fallback_ids[logic_index]}"
                    else:
                        redirect_url = None
            except Exception as e:
                print(f"Erreur mapping dynamique logic challenge: {e}")
                # Fallback vers les énigmes connues
                fallback_ids = [2292, 2293, 2294, 2295, 2296]
                logic_index = challenge_id - 100
                if logic_index < len(fallback_ids):
                    redirect_url = f"/logic-challenge/{fallback_ids[logic_index]}"
                else:
                    redirect_url = None
        else:
            redirect_url = redirect_map.get(challenge_id)
        
        if not redirect_url:
            return JSONResponse({
                "success": False,
                "error": "Challenge introuvable",
                "message": f"Le challenge #{challenge_id} n'existe pas."
            }, status_code=404)
        
        # TODO: Enregistrer le début du challenge en DB
        # TODO: Initialiser le suivi de progression
        # TODO: Mettre à jour les statistiques utilisateur
        
        return JSONResponse({
            "success": True,
            "message": f"Challenge #{challenge_id} démarré avec succès !",
            "redirect_url": redirect_url,
            "challenge_id": challenge_id
        })
        
    except ValueError:
        return JSONResponse({
            "success": False,
            "error": "ID invalide"
        }, status_code=400)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": "Erreur système",
            "message": str(e)
        }, status_code=500) 