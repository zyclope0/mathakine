"""
Routes des vues pour Mathakine.

Ce module contient les fonctions de rendu pour les pages web.
"""
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse, Response
import traceback
import json
import os
from datetime import datetime, timezone
from fastapi import HTTPException
from loguru import logger

from app.core.constants import ExerciseTypes, DifficultyLevels, DISPLAY_NAMES, Messages
from app.services.enhanced_server_adapter import EnhancedServerAdapter
from server.template_handler import render_template, render_error

# Fonction pour récupérer l'utilisateur courant
async def get_current_user(request: Request):
    """Récupère l'utilisateur actuellement connecté à partir du token"""
    try:
        access_token = request.cookies.get("access_token")
        if not access_token:
            return None
            
        # Utiliser le service d'authentification pour décoder le token
        from app.core.security import decode_token
        from app.services.auth_service import get_user_by_username
        
        # Décoder le token pour obtenir le nom d'utilisateur
        try:
            payload = decode_token(access_token)
        except (HTTPException, Exception) as decode_error:
            # Token invalide ou expiré, retourner None silencieusement
            # Ne pas logger comme erreur car c'est normal si l'utilisateur n'est pas connecté
            error_msg = str(decode_error)
            if "Signature verification failed" in error_msg or "Token" in type(decode_error).__name__:
                logger.debug(f"Token invalide ou expiré: {error_msg}")
            else:
                logger.debug(f"Erreur lors du décodage du token: {error_msg}")
            return None
        
        username = payload.get("sub")
        
        if not username:
            return None
            
        # Récupérer l'utilisateur depuis la base de données
        db = EnhancedServerAdapter.get_db_session()
        try:
            user = get_user_by_username(db, username)
            if user:
                return {
                    "is_authenticated": True,
                    "id": user.id,
                    "username": user.username,
                    "role": user.role
                }
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        # Ne pas logger les erreurs de token invalide comme des erreurs critiques
        if "Signature verification failed" in error_msg or "Token" in error_type:
            logger.debug(f"Token invalide ou expiré: {error_msg}")
        else:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {error_type}: {error_msg}")
            logger.debug(traceback.format_exc())
        
    return None

# Page d'accueil
async def homepage(request: Request):
    """Rendu de la page d'accueil"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    return render_template("home.html", request, {
        "current_user": current_user
    })

# Page "À propos"
async def about_page(request: Request):
    """Rendu de la page À propos"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    return render_template("about.html", request, {
        "current_user": current_user
    })

# Page de connexion
async def login_page(request: Request):
    """Rendu de la page de connexion"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    if current_user["is_authenticated"]:
        return RedirectResponse(url="/", status_code=302)
    return render_template("login.html", request, {
        "current_user": current_user
    })

# Traitement de l'authentification API
async def api_login(request: Request):
    """API pour l'authentification"""
    try:
        # Récupérer les données JSON du corps de la requête
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return JSONResponse(
                {"detail": "Nom d'utilisateur et mot de passe requis"},
                status_code=400
            )
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser le service d'authentification pour vérifier les identifiants
            from app.services.auth_service import authenticate_user, create_user_token
            
            user = authenticate_user(db, username, password)
            if user:
                # Générer les tokens d'accès et de rafraîchissement
                tokens = create_user_token(user)
                
                # Préparer les données utilisateur pour la réponse JSON
                # Convertir le rôle en string si c'est un enum
                role_value = user.role if isinstance(user.role, str) else user.role.value.lower()
                
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": role_value,
                    "is_active": user.is_active,
                    "total_points": getattr(user, 'total_points', 0) or 0,
                    "current_level": getattr(user, 'current_level', 1) or 1,
                    "jedi_rank": getattr(user, 'jedi_rank', 'youngling') or 'youngling',
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                }
                
                # Importer settings pour la durée de vie du token
                from app.core.config import settings
                access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convertir minutes en secondes
                
                # Créer une réponse JSON avec les données utilisateur et tokens
                response_data = {
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "token_type": tokens.get("token_type", "bearer"),
                    "expires_in": access_token_max_age,  # Aligné avec ACCESS_TOKEN_EXPIRE_MINUTES
                    "user": user_data
                }
                
                response = JSONResponse(response_data, status_code=200)
                
                # Déterminer si on est en production (pour secure cookie)
                is_production = os.getenv("MATH_TRAINER_PROFILE", "dev") == "prod"
                
                # Définir les cookies avec les tokens
                # Pour cross-domain (frontend et backend sur domaines différents), 
                # il FAUT samesite="none" et secure=True
                response.set_cookie(
                    key="access_token",
                    value=tokens["access_token"],
                    httponly=True,
                    secure=True,  # Toujours True pour samesite=none
                    samesite="none",  # Permet cross-domain
                    max_age=access_token_max_age  # Aligné avec ACCESS_TOKEN_EXPIRE_MINUTES
                )
                response.set_cookie(
                    key="refresh_token",
                    value=tokens["refresh_token"],
                    httponly=True,
                    secure=True,  # Toujours True pour samesite=none
                    samesite="none",  # Permet cross-domain
                    max_age=86400 * 30  # 30 jours
                )
                
                return response
            else:
                return JSONResponse(
                    {"detail": "Nom d'utilisateur ou mot de passe incorrect"},
                    status_code=401
                )
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de parsing JSON lors de l'authentification: {str(e)}")
        return JSONResponse(
            {"detail": "Format de requête invalide"},
            status_code=400
        )
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        logger.error(f"Erreur lors de l'authentification API: {error_type}: {error_msg}")
        logger.debug(traceback.format_exc())
        # Retourner un message d'erreur plus informatif en développement
        detail_msg = "Erreur lors de l'authentification"
        if os.getenv("MATH_TRAINER_PROFILE", "dev") == "dev":
            detail_msg = f"Erreur lors de l'authentification: {error_type}: {error_msg}"
        return JSONResponse(
            {"detail": detail_msg},
            status_code=500
        )

# API pour récupérer l'utilisateur actuel
async def api_get_user_me(request: Request):
    """API pour récupérer les informations de l'utilisateur actuellement connecté"""
    try:
        current_user = await get_current_user(request)
        
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse(
                {"detail": "Non authentifié"},
                status_code=401
            )
        
        # Récupérer l'utilisateur complet depuis la base de données
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.services.auth_service import get_user_by_username
            user = get_user_by_username(db, current_user["username"])
            
            if not user:
                return JSONResponse(
                    {"detail": "Utilisateur non trouvé"},
                    status_code=404
                )
            
            # Retourner les informations de l'utilisateur au format JSON
            return JSONResponse({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "grade_level": user.grade_level,
                "learning_style": user.learning_style,
                "preferred_difficulty": user.preferred_difficulty,
                "preferred_theme": user.preferred_theme,
                "accessibility_settings": user.accessibility_settings,
                "language_preference": getattr(user, 'language_preference', None),
                "timezone": getattr(user, 'timezone', None),
                "is_public_profile": getattr(user, 'is_public_profile', None),
                "allow_friend_requests": getattr(user, 'allow_friend_requests', None),
                "show_in_leaderboards": getattr(user, 'show_in_leaderboards', None),
                "data_retention_consent": getattr(user, 'data_retention_consent', None),
                "marketing_consent": getattr(user, 'marketing_consent', None),
            })
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"detail": "Erreur lors de la récupération de l'utilisateur"},
            status_code=500
        )

# API pour mettre à jour le profil utilisateur
async def api_update_user_me(request: Request):
    """API pour mettre à jour les informations de l'utilisateur actuellement connecté"""
    try:
        current_user = await get_current_user(request)
        
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse(
                {"detail": "Non authentifié"},
                status_code=401
            )
        
        # Lire les données JSON de la requête
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                {"detail": "Données JSON invalides"},
                status_code=400
            )
        
        # Valider les données avec le schéma UserUpdate
        from app.schemas.user import UserUpdate
        try:
            user_update = UserUpdate(**body)
        except Exception as e:
            logger.debug(f"Erreur de validation UserUpdate: {str(e)}")
            return JSONResponse(
                {"detail": f"Données invalides: {str(e)}"},
                status_code=400
            )
        
        # Récupérer l'utilisateur depuis la base de données
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.services.auth_service import get_user_by_username, update_user
            user = get_user_by_username(db, current_user["username"])
            
            if not user:
                return JSONResponse(
                    {"detail": "Utilisateur non trouvé"},
                    status_code=404
                )
            
            # Mettre à jour l'utilisateur
            updated_user = update_user(db, user, user_update)
            
            # Gérer notification_preferences (stocké dans accessibility_settings pour MVP)
            if 'notification_preferences' in body:
                if not updated_user.accessibility_settings:
                    updated_user.accessibility_settings = {}
                updated_user.accessibility_settings['notification_preferences'] = body['notification_preferences']
                db.add(updated_user)
                db.commit()
                db.refresh(updated_user)
            
            # Retourner les informations mises à jour
            return JSONResponse({
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "full_name": updated_user.full_name,
                "role": updated_user.role.value if hasattr(updated_user.role, 'value') else str(updated_user.role),
                "is_active": updated_user.is_active,
                "created_at": updated_user.created_at.isoformat() if updated_user.created_at else None,
                "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None,
                "grade_level": updated_user.grade_level,
                "learning_style": updated_user.learning_style,
                "preferred_difficulty": updated_user.preferred_difficulty,
                "preferred_theme": updated_user.preferred_theme,
                "accessibility_settings": updated_user.accessibility_settings,
                "language_preference": getattr(updated_user, 'language_preference', None),
                "timezone": getattr(updated_user, 'timezone', None),
                "is_public_profile": getattr(updated_user, 'is_public_profile', None),
                "allow_friend_requests": getattr(updated_user, 'allow_friend_requests', None),
                "show_in_leaderboards": getattr(updated_user, 'show_in_leaderboards', None),
                "data_retention_consent": getattr(updated_user, 'data_retention_consent', None),
                "marketing_consent": getattr(updated_user, 'marketing_consent', None),
            })
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"detail": "Erreur lors de la mise à jour de l'utilisateur"},
            status_code=500
        )

# API pour changer le mot de passe
async def api_change_password(request: Request):
    """API pour changer le mot de passe de l'utilisateur actuellement connecté"""
    try:
        current_user = await get_current_user(request)
        
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse(
                {"detail": "Non authentifié"},
                status_code=401
            )
        
        # Lire les données JSON de la requête
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                {"detail": "Données JSON invalides"},
                status_code=400
            )
        
        # Valider les données avec le schéma UserPasswordUpdate
        from app.schemas.user import UserPasswordUpdate
        try:
            password_update = UserPasswordUpdate(**body)
        except Exception as e:
            logger.debug(f"Erreur de validation UserPasswordUpdate: {str(e)}")
            return JSONResponse(
                {"detail": f"Données invalides: {str(e)}"},
                status_code=400
            )
        
        # Récupérer l'utilisateur depuis la base de données
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.services.auth_service import get_user_by_username, update_user_password
            user = get_user_by_username(db, current_user["username"])
            
            if not user:
                return JSONResponse(
                    {"detail": "Utilisateur non trouvé"},
                    status_code=404
                )
            
            # Changer le mot de passe
            success = update_user_password(
                db, 
                user, 
                password_update.current_password, 
                password_update.new_password
            )
            
            if success:
                return JSONResponse({
                    "message": "Mot de passe mis à jour avec succès",
                    "success": True
                })
            else:
                return JSONResponse(
                    {"detail": "Erreur lors de la mise à jour du mot de passe"},
                    status_code=500
                )
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except HTTPException:
        # Re-lancer les HTTPException (ex: mot de passe incorrect)
        raise
    except Exception as e:
        logger.error(f"Erreur lors du changement de mot de passe: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"detail": "Erreur lors du changement de mot de passe"},
            status_code=500
        )

# API pour exporter les données utilisateur (RGPD)
async def api_export_user_data(request: Request):
    """API pour exporter toutes les données de l'utilisateur connecté"""
    try:
        current_user = await get_current_user(request)
        
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse(
                {"detail": "Non authentifié"},
                status_code=401
            )
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.services.auth_service import get_user_by_username
            user = get_user_by_username(db, current_user["username"])
            
            if not user:
                return JSONResponse(
                    {"detail": "Utilisateur non trouvé"},
                    status_code=404
                )
            
            # Collecter toutes les données utilisateur
            export_data = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                    "grade_level": user.grade_level,
                    "learning_style": user.learning_style,
                    "preferred_difficulty": user.preferred_difficulty,
                    "preferred_theme": user.preferred_theme,
                    "accessibility_settings": user.accessibility_settings,
                    "language_preference": getattr(user, 'language_preference', None),
                    "timezone": getattr(user, 'timezone', None),
                },
                "statistics": {
                    "total_points": user.total_points if hasattr(user, 'total_points') else 0,
                    "current_level": user.current_level if hasattr(user, 'current_level') else 1,
                    "experience_points": user.experience_points if hasattr(user, 'experience_points') else 0,
                    "jedi_rank": user.jedi_rank if hasattr(user, 'jedi_rank') else None,
                },
                "export_date": datetime.now(timezone.utc).isoformat(),
            }
            
            # Retourner en JSON avec headers pour téléchargement
            return Response(
                content=json.dumps(export_data, indent=2, ensure_ascii=False),
                media_type="application/json",
                headers={
                    "Content-Disposition": f'attachment; filename="mathakine-data-{user.username}-{datetime.now().strftime("%Y%m%d")}.json"'
                }
            )
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de l'export des données: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"detail": "Erreur lors de l'export des données"},
            status_code=500
        )

# API pour supprimer le compte utilisateur (RGPD)
async def api_delete_user_account(request: Request):
    """API pour supprimer le compte de l'utilisateur connecté"""
    try:
        current_user = await get_current_user(request)
        
        if not current_user or not current_user.get("is_authenticated"):
            return JSONResponse(
                {"detail": "Non authentifié"},
                status_code=401
            )
        
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.services.auth_service import get_user_by_username
            user = get_user_by_username(db, current_user["username"])
            
            if not user:
                return JSONResponse(
                    {"detail": "Utilisateur non trouvé"},
                    status_code=404
                )
            
            # Marquer le compte comme supprimé (soft delete pour MVP)
            # Pour une vraie suppression, on pourrait utiliser is_deleted si le champ existe
            user.is_active = False
            if hasattr(user, 'is_deleted'):
                user.is_deleted = True
            if hasattr(user, 'deletion_requested_at'):
                user.deletion_requested_at = datetime.now(timezone.utc)
            
            db.add(user)
            db.commit()
            
            return JSONResponse({
                "message": "Compte supprimé avec succès",
                "success": True
            })
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du compte: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"detail": "Erreur lors de la suppression du compte"},
            status_code=500
        )

# Page d'inscription
async def register_page(request: Request):
    """Rendu de la page d'inscription"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    if current_user["is_authenticated"]:
        return RedirectResponse(url="/", status_code=302)
    return render_template("register.html", request, {
        "current_user": current_user
    })

# Page mot de passe oublié
async def forgot_password_page(request: Request):
    """Rendu de la page mot de passe oublié"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    if current_user["is_authenticated"]:
        return RedirectResponse(url="/", status_code=302)
    return render_template("forgot_password.html", request, {
        "current_user": current_user
    })

# Page de profil
async def profile_page(request: Request):
    """Rendu de la page de profil utilisateur"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Obtenir l'utilisateur complet depuis la base de données
    try:
        db = EnhancedServerAdapter.get_db_session()
        try:
            from app.services.auth_service import get_user_by_username
            user = get_user_by_username(db, current_user["username"])
            if not user:
                return render_error(
                    request=request,
                    error="Utilisateur non trouvé",
                    message="Impossible de récupérer les informations de l'utilisateur",
                    status_code=404
                )
            
            # Convertir l'utilisateur en dictionnaire pour le template
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if hasattr(user.role, 'value') else user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "grade_level": user.grade_level,
                "learning_style": user.learning_style,
                "preferred_difficulty": user.preferred_difficulty,
                "preferred_theme": user.preferred_theme,
                "is_authenticated": True
            }
            
            return render_template("profile.html", request, {
                "current_user": user_dict
            })
        finally:
            EnhancedServerAdapter.close_db_session(db)
    except Exception as e:
        print(f"Erreur lors de la récupération du profil: {str(e)}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur lors du chargement du profil",
            message="Une erreur est survenue lors du chargement de votre profil",
            status_code=500
        )

# API pour rafraîchir le token d'accès
async def api_refresh_token(request: Request):
    """API pour rafraîchir le token d'accès en utilisant le refresh token depuis les cookies"""
    try:
        # Récupérer le refresh token depuis les cookies
        refresh_token = request.cookies.get("refresh_token")
        
        if not refresh_token:
            return JSONResponse(
                {"detail": "Refresh token manquant"},
                status_code=401
            )
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser le service d'authentification pour rafraîchir le token
            from app.services.auth_service import refresh_access_token
            
            new_token_data = refresh_access_token(db, refresh_token)
            
            # Importer settings pour la durée de vie du token
            from app.core.config import settings
            
            # Créer une réponse JSON
            response = JSONResponse({
                "access_token": new_token_data["access_token"],
                "token_type": new_token_data.get("token_type", "bearer"),
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }, status_code=200)
            
            # Déterminer si on est en production (pour secure cookie)
            is_production = os.getenv("MATH_TRAINER_PROFILE", "dev") == "prod"
            
            # Mettre à jour le cookie access_token avec le nouveau token
            access_token_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            
            response.set_cookie(
                key="access_token",
                value=new_token_data["access_token"],
                httponly=True,
                secure=True,  # Toujours True pour samesite=none
                samesite="none",  # Permet cross-domain
                max_age=access_token_max_age
            )
            
            return response
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except HTTPException as e:
        # Re-lancer les HTTPException (401, etc.)
        return JSONResponse(
            {"detail": e.detail},
            status_code=e.status_code
        )
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement du token: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            {"detail": "Erreur lors du rafraîchissement du token"},
            status_code=500
        )

# Déconnexion
async def logout(request: Request):
    """Déconnexion de l'utilisateur"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

# Page des exercices
async def exercises_page(request: Request):
    """Rendu de la page des exercices"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Vérifier si nous venons d'une génération d'exercices
    just_generated = request.query_params.get('generated', 'false') == 'true'
    logger.debug(f"Page d'exercices chargée, just_generated={just_generated}")
    
    # Récupérer les paramètres de filtrage
    exercise_type = request.query_params.get('exercise_type', None)
    difficulty = request.query_params.get('difficulty', None)
    
    logger.debug(f"Paramètres reçus - exercise_type: {exercise_type}, difficulty: {difficulty}")
    
    # Normaliser les paramètres si présents
    if exercise_type:
        exercise_type = normalize_exercise_type(exercise_type)
        logger.debug(f"Type d'exercice normalisé: {exercise_type}")
    if difficulty:
        difficulty = normalize_difficulty(difficulty)
        logger.debug(f"Difficulté normalisée: {difficulty}")

    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Utiliser l'adaptateur pour lister les exercices
            exercises = EnhancedServerAdapter.list_exercises(
                db,
                exercise_type=exercise_type,
                difficulty=difficulty
            )
            
            logger.debug(f"Nombre d'exercices récupérés: {len(exercises)}")
            if len(exercises) > 0:
                logger.debug(f"Premier exercice: ID={exercises[0].get('id')}, Titre={exercises[0].get('title')}")
                logger.debug(f"Dernier exercice: ID={exercises[-1].get('id')}, Titre={exercises[-1].get('title')}")
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des exercices: {e}")
        logger.debug(traceback.format_exc())
        exercises = []
    
    # Message pour indiquer si on vient de générer un exercice
    message = None
    message_type = None
    if just_generated:
        message = "Exercice généré avec succès. Vous pouvez maintenant le résoudre ou en générer un autre."
        message_type = "success"

    # Créer des dictionnaires pour l'affichage des types et niveaux
    exercise_types = {key: DISPLAY_NAMES[key] for key in ExerciseTypes.ALL_TYPES}
    difficulty_levels = {key: DISPLAY_NAMES[key] for key in DifficultyLevels.ALL_LEVELS}
    
    # Mappings pour l'affichage des exercices dans la liste
    exercise_type_display = DISPLAY_NAMES
    difficulty_display = DISPLAY_NAMES
    
    # Préfixe IA pour les templates
    ai_prefix = Messages.AI_EXERCISE_PREFIX

    logger.debug(f"Préparation du rendu template avec {len(exercises)} exercices")
    
    return render_template("exercises.html", request, {
        "exercises": exercises,
        "message": message,
        "message_type": message_type,
        "exercise_types": exercise_types,
        "difficulty_levels": difficulty_levels,
        "exercise_type_display": exercise_type_display,
        "difficulty_display": difficulty_display,
        "ai_prefix": ai_prefix,
        "current_user": current_user
    })

# Page du tableau de bord
async def dashboard(request: Request):
    """Rendu de la page de tableau de bord avec statistiques"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    print(f"Accès au tableau de bord pour l'utilisateur: {current_user.get('username')}")
        
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'utilisateur complet pour avoir son ID
            from app.services.auth_service import get_user_by_username
            user = get_user_by_username(db, current_user["username"])
            if not user:
                print(f"Utilisateur {current_user['username']} non trouvé dans la base de données")
                return render_error(
                    request=request,
                    error="Utilisateur non trouvé",
                    message="Impossible de récupérer les statistiques de l'utilisateur",
                    status_code=404
                )
            
            print(f"Utilisateur trouvé avec ID={user.id}, récupération des statistiques")
            
            # Préparer les données par défaut au cas où la récupération échoue
            stats = {
                "total_attempts": 0,
                "correct_attempts": 0,
                "success_rate": 0,
                "by_exercise_type": {}
            }
            
            # Utiliser l'adaptateur pour récupérer les statistiques utilisateur avec le bon ID
            try:
                user_stats = EnhancedServerAdapter.get_user_stats(db, user.id)
                if user_stats:
                    stats = user_stats
                    print(f"Statistiques récupérées avec succès")
                else:
                    print("Aucune statistique trouvée pour l'utilisateur")
            except Exception as stats_error:
                print(f"Erreur lors de la récupération des statistiques: {str(stats_error)}")
                traceback.print_exc()
                # Continuer avec les statistiques par défaut
                
            # Préparer les données pour le rendu
            total_completed = stats.get("total_attempts", 0)
            correct_answers = stats.get("correct_attempts", 0)
            success_rate = stats.get("success_rate", 0)
            
            # Performance par type d'exercice (avec gestion des cas où by_exercise_type n'existe pas)
            performance_by_type = {}
            by_exercise_type = stats.get("by_exercise_type", {})
            if not isinstance(by_exercise_type, dict):
                by_exercise_type = {}
            
            # Mapping des noms de types d'exercice (défini en dehors de la boucle)
            type_fr = {
                "addition": "Addition",
                "subtraction": "Soustraction", 
                "multiplication": "Multiplication",
                "division": "Division",
                "mixed": "Mixte"
            }
            
            for exercise_type, type_stats in by_exercise_type.items():
                exercise_type_name = type_fr.get(exercise_type, exercise_type)
                performance_by_type[exercise_type_name] = {
                    "total": type_stats.get("total", 0),
                    "correct": type_stats.get("correct", 0),
                    "success_rate": type_stats.get("success_rate", 0)
                }
            
            # Ajouter des types d'exercice vides si nécessaire
            for type_key, type_name in type_fr.items():
                if type_name not in performance_by_type:
                    performance_by_type[type_name] = {
                        "total": 0,
                        "correct": 0,
                        "success_rate": 0
                    }
            
            # Récupérer les exercices récents (simulation)
            recent_results = []
            
            # Préparer les données pour les graphiques
            chart_data = {
                "performance": {
                    "labels": list(performance_by_type.keys()) or ["Aucune donnée"],
                    "values": [stats.get("success_rate", 0) for stats in performance_by_type.values()] or [0]
                },
                "activity": {
                    "labels": ["Jour 1", "Jour 2", "Jour 3", "Jour 4", "Jour 5", "Jour 6", "Jour 7"],
                    "values": [5, 7, 3, 8, 10, 6, 4]  # Données fictives pour l'exemple
                }
            }
            
            # Récupérer les recommandations personnalisées
            recommendations_data = []
            try:
                from app.services.recommendation_service import RecommendationService
                print("Récupération des recommandations...")
                recommendations = RecommendationService.get_user_recommendations(db, user.id, limit=3)
                
                # Si aucune recommandation n'existe, générer de nouvelles recommandations
                if not recommendations:
                    print("Aucune recommandation trouvée, génération de nouvelles recommandations...")
                    try:
                        RecommendationService.generate_recommendations(db, user.id)
                        recommendations = RecommendationService.get_user_recommendations(db, user.id, limit=3)
                    except Exception as gen_error:
                        print(f"Erreur lors de la génération des recommandations: {str(gen_error)}")
                        traceback.print_exc()
                        recommendations = []
                
                # Préparer les données de recommandation pour le template
                for rec in recommendations:
                    # Marquer comme affichée (avec gestion d'erreur)
                    try:
                        RecommendationService.mark_recommendation_as_shown(db, rec.id)
                    except Exception as mark_error:
                        print(f"Erreur lors du marquage de la recommandation comme affichée: {str(mark_error)}")
                        # Continuer même en cas d'erreur
                    
                    rec_data = {
                        "id": rec.id,
                        "exercise_type": rec.exercise_type,
                        "difficulty": rec.difficulty,
                        "priority": rec.priority,
                        "reason": rec.reason,
                        "exercise_id": rec.exercise_id
                    }
                    
                    # Ajouter les informations de l'exercice si présent
                    if rec.exercise_id:
                        from app.models.exercise import Exercise
                        exercise = db.query(Exercise).filter(Exercise.id == rec.exercise_id).first()
                        if exercise:
                            rec_data["exercise_title"] = exercise.title
                            rec_data["exercise_question"] = exercise.question
                    
                    recommendations_data.append(rec_data)
            except Exception as rec_error:
                print(f"Erreur lors de la récupération des recommandations: {str(rec_error)}")
                traceback.print_exc()
                # Continuer sans recommandations
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
        context = {
            "user": current_user,
            "total_completed": total_completed,
            "correct_answers": correct_answers,
            "success_rate": success_rate,
            "performance": performance_by_type,
            "recent_results": recent_results,
            "chart_data": json.dumps(chart_data),
            "current_user": current_user,
            "recommendations": recommendations_data  # Ajouter les recommandations au contexte
        }
        
        print("Tentative de rendu du template dashboard.html")
        try:
            return render_template("dashboard.html", request, context)
        except Exception as template_error:
            print(f"Erreur de rendu du template dashboard.html: {str(template_error)}")
            traceback.print_exc()
            
            # En cas d'erreur, afficher une page d'erreur
            return render_error(
                request=request,
                error="Erreur d'affichage du tableau de bord",
                message="Une erreur est survenue lors de l'affichage du tableau de bord. L'équipe technique a été informée.",
                status_code=500
            )
        
    except Exception as e:
        print(f"Erreur lors de la génération du tableau de bord: {e}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur lors de la génération du tableau de bord",
            message=str(e),
            status_code=500
        )

# Page de détail d'un exercice
async def exercise_detail_page(request: Request):
    """Rendu de la page de détail d'un exercice"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    exercise_id = request.path_params["exercise_id"]
    print(f"Tentative d'accès à l'exercice ID={exercise_id}")
    
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'exercice
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            
            if not exercise:
                print(f"Exercice ID={exercise_id} non trouvé dans la base de données")
                return render_error(
                    request=request,
                    error="Exercice non trouvé",
                    message=f"L'exercice avec l'ID {exercise_id} n'existe pas ou a été supprimé.",
                    status_code=404
                )
            
            print(f"Exercice trouvé: {exercise.get('title')}")
            
            # S'assurer que l'exercice a des choix valides
            if not exercise.get('choices'):
                # Générer des choix aléatoires si non présents
                import random
                correct = exercise.get('correct_answer')
                # Générer quelques valeurs autour de la réponse correcte
                try:
                    correct_int = int(correct)
                    choices = [str(correct_int + random.randint(-10, 10)) for _ in range(3)]
                    choices.append(correct)
                    # Shuffle et s'assurer que la réponse correcte est dedans
                    random.shuffle(choices)
                    if correct not in choices:
                        choices[0] = correct
                except (ValueError, TypeError):
                    # Si la réponse n'est pas un nombre, créer des choix de base
                    choices = [correct, "Option A", "Option B", "Option C"]
                    random.shuffle(choices)
                
                exercise['choices'] = choices
                print(f"Choix générés pour l'exercice: {choices}")
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
        # Mappings pour l'affichage des types et niveaux
        exercise_type_display = DISPLAY_NAMES
        difficulty_display = DISPLAY_NAMES
        
        print(f"Tentative de rendu du template avec l'exercice ID={exercise_id}")
        try:
            return render_template("exercise_detail.html", request, {
                "exercise": exercise,
                "exercise_type_display": exercise_type_display,
                "difficulty_display": difficulty_display,
                "current_user": current_user
            })
        except Exception as template_error:
            print(f"Erreur de rendu du template exercise_detail.html: {str(template_error)}")
            traceback.print_exc()
            
            # Si le template exercise_detail.html pose problème, essayer avec exercise.html
            print("Tentative avec le template exercise.html...")
            try:
                return render_template("exercise.html", request, {
                    "exercise": exercise,
                    "exercise_type_display": exercise_type_display,
                    "difficulty_display": difficulty_display,
                    "current_user": current_user
                })
            except Exception as template_error2:
                print(f"Erreur également avec exercise.html: {str(template_error2)}")
                traceback.print_exc()
                
                # Si les deux templates échouent, essayer exercise_simple.html comme dernier recours
                try:
                    return render_template("exercise_simple.html", request, {
                        "exercise": exercise,
                        "exercise_type_display": exercise_type_display,
                        "difficulty_display": difficulty_display,
                        "current_user": current_user
                    })
                except Exception as template_error3:
                    print(f"Erreur avec tous les templates: {str(template_error3)}")
                    
                    # En dernier recours, afficher une page d'erreur
                    return render_error(
                        request=request,
                        error="Erreur d'affichage de l'exercice",
                        message="Une erreur est survenue lors de l'affichage de l'exercice. L'équipe technique a été informée.",
                        status_code=500
                    )
        
    except Exception as e:
        print(f"Exception lors de la récupération de l'exercice {exercise_id}: {str(e)}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur de base de données",
            message=f"Une erreur est survenue lors de la récupération de l'exercice: {str(e)}",
            status_code=500
        )

# Fonction pour normaliser le type d'exercice
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

# Fonction pour normaliser la difficulté
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

# Fonction de redirection pour les anciennes URLs d'exercices
async def redirect_old_exercise_url(request: Request):
    """Redirige de /exercises/{id} vers /exercise/{id}"""
    exercise_id = request.path_params["exercise_id"]
    print(f"Redirection de /exercises/{exercise_id} vers /exercise/{exercise_id}")
    return RedirectResponse(url=f"/exercise/{exercise_id}", status_code=301)

# Page des badges
async def badges_page(request: Request):
    """Rendu de la page des badges et achievements"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        return render_template("badges.html", request, {
            "current_user": current_user
        })
    except Exception as e:
        print(f"Erreur lors du chargement de la page badges: {str(e)}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur de chargement",
            message=f"Impossible de charger la page des badges: {str(e)}",
            status_code=500
        )

# Page des exercices en mode simple
async def exercises_simple_page(request: Request):
    """Rendu de la page des exercices en mode simplifié"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Mode simple = exercices de niveau initié uniquement
    difficulty = "initie"
    
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer seulement les exercices de niveau initié
            exercises = EnhancedServerAdapter.list_exercises(
                db,
                exercise_type=None,
                difficulty=difficulty
            )
            
            print(f"Mode simple : {len(exercises)} exercices de niveau initié récupérés")
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
    except Exception as e:
        print(f"Erreur lors de la récupération des exercices simples: {e}")
        traceback.print_exc()
        exercises = []
    
    # Créer des dictionnaires pour l'affichage des types et niveaux
    exercise_types = {key: DISPLAY_NAMES[key] for key in ExerciseTypes.ALL_TYPES}
    difficulty_levels = {key: DISPLAY_NAMES[key] for key in DifficultyLevels.ALL_LEVELS}
    
    # Mappings pour l'affichage des exercices dans la liste
    exercise_type_display = DISPLAY_NAMES
    difficulty_display = DISPLAY_NAMES
    
    # Préfixe IA pour les templates
    ai_prefix = Messages.AI_EXERCISE_PREFIX

    # Message pour indiquer qu'on est en mode simple
    message = "Mode Simple : Seuls les exercices de niveau Initié sont affichés"
    message_type = "info"
    
    return render_template("exercises.html", request, {
        "exercises": exercises,
        "message": message,
        "message_type": message_type,
        "exercise_types": exercise_types,
        "difficulty_levels": difficulty_levels,
        "exercise_type_display": exercise_type_display,
        "difficulty_display": difficulty_display,
        "ai_prefix": ai_prefix,
        "current_user": current_user,
        "simple_mode": True  # Indicateur pour le template
    })

async def new_exercise_page(request):
    # This function is mentioned in the code block but not implemented in the original file or the new file
    # It's assumed to exist as it's called in the exercises_page function
    pass

# Page des exercices simples
async def simple_exercises_page(request: Request):
    """Rendu de la page des exercices simples (addition, soustraction, division uniquement)"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer uniquement les exercices de base (addition, soustraction, division)
            basic_types = ['ADDITION', 'SOUSTRACTION', 'DIVISION']
            exercises = EnhancedServerAdapter.get_exercises_by_types(db, basic_types, limit=20)
            
            print(f"Nombre d'exercices simples récupérés: {len(exercises)}")
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
        
        # Types d'exercices pour la page simple
        exercise_types = ['ADDITION', 'SOUSTRACTION', 'DIVISION']
        difficulty_levels = ['INITIE', 'PADAWAN', 'CHEVALIER']
        
        # Mappings pour l'affichage
        exercise_type_display = DISPLAY_NAMES
        difficulty_display = DISPLAY_NAMES
        
        # Rendu avec un template spécialisé
        return render_template("simple_exercises.html", request, {
            "exercises": exercises,
            "exercise_types": exercise_types,
            "difficulty_levels": difficulty_levels,
            "exercise_type_display": exercise_type_display,
            "difficulty_display": difficulty_display,
            "current_user": current_user
        })
        
    except Exception as e:
        print(f"Erreur lors du chargement des exercices simples: {str(e)}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur de chargement",
            message=f"Impossible de charger les exercices simples: {str(e)}",
            status_code=500
        )

# Génération d'exercice simple
async def generate_simple_exercise(request: Request):
    """Génère un exercice simple aléatoire (addition, soustraction, division)"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    try:
        import random
        from server.handlers.exercise_handlers import ExerciseGenerator
        
        # Types d'exercices simples
        basic_types = ['ADDITION', 'SOUSTRACTION', 'DIVISION']
        exercise_type = random.choice(basic_types)
        
        # Difficulté adaptée pour exercices simples (plus facile)
        difficulties = ['INITIE', 'PADAWAN']
        difficulty = random.choice(difficulties)
        
        print(f"Génération d'exercice simple: {exercise_type} - {difficulty}")
        
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Générer l'exercice
            generator = ExerciseGenerator()
            exercise_data = generator.generate_exercise(exercise_type, difficulty)
            
            # Sauvegarder l'exercice
            new_exercise = EnhancedServerAdapter.create_exercise(
                db, 
                exercise_data, 
                current_user["id"]
            )
            
            print(f"Exercice simple créé avec ID: {new_exercise.get('id')}")
            
        finally:
            EnhancedServerAdapter.close_db_session(db)
        
        # Rediriger vers l'exercice avec le template simple
        return RedirectResponse(url=f"/exercise/simple/{new_exercise['id']}", status_code=302)
        
    except Exception as e:
        print(f"Erreur lors de la génération d'exercice simple: {str(e)}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur de génération",
            message=f"Impossible de générer un exercice simple: {str(e)}",
            status_code=500
        )

# Page d'exercice simple individuel
async def simple_exercise_page(request: Request):
    """Rendu d'un exercice simple avec le template exercise_simple.html"""
    current_user = await get_current_user(request) or {"is_authenticated": False}
    
    # Vérifier si l'utilisateur est connecté
    if not current_user["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    exercise_id = request.path_params["exercise_id"]
    print(f"Accès à l'exercice simple ID={exercise_id}")
    
    try:
        # Utiliser l'adaptateur pour obtenir une session SQLAlchemy
        db = EnhancedServerAdapter.get_db_session()
        
        try:
            # Récupérer l'exercice
            exercise = EnhancedServerAdapter.get_exercise_by_id(db, exercise_id)
            
            if not exercise:
                print(f"Exercice simple ID={exercise_id} non trouvé")
                return render_error(
                    request=request,
                    error="Exercice non trouvé",
                    message=f"L'exercice avec l'ID {exercise_id} n'existe pas.",
                    status_code=404
                )
            
            # Vérifier que c'est bien un exercice de base
            if exercise.get('exercise_type') not in ['ADDITION', 'SOUSTRACTION', 'DIVISION']:
                print(f"Exercice ID={exercise_id} n'est pas un exercice simple")
                return RedirectResponse(url=f"/exercise/{exercise_id}", status_code=302)
            
            print(f"Exercice simple trouvé: {exercise.get('title')}")
            
            # S'assurer que l'exercice a des choix valides
            if not exercise.get('choices'):
                import random
                correct = exercise.get('correct_answer')
                try:
                    correct_int = int(correct)
                    choices = [str(correct_int + random.randint(-5, 5)) for _ in range(3)]
                    choices.append(correct)
                    random.shuffle(choices)
                    if correct not in choices:
                        choices[0] = correct
                except (ValueError, TypeError):
                    choices = [correct, "Option A", "Option B", "Option C"]
                    random.shuffle(choices)
                
                exercise['choices'] = choices
                print(f"Choix générés pour l'exercice simple: {choices}")
                
        finally:
            EnhancedServerAdapter.close_db_session(db)
            
        # Mappings pour l'affichage
        exercise_type_display = DISPLAY_NAMES
        difficulty_display = DISPLAY_NAMES
        
        # Forcer l'utilisation du template simple
        return render_template("exercise_simple.html", request, {
            "exercise": exercise,
            "exercise_type_display": exercise_type_display,
            "difficulty_display": difficulty_display,
            "current_user": current_user
        })
        
    except Exception as e:
        print(f"Erreur lors de l'accès à l'exercice simple {exercise_id}: {str(e)}")
        traceback.print_exc()
        return render_error(
            request=request,
            error="Erreur de base de données",
            message=f"Une erreur est survenue: {str(e)}",
            status_code=500
        ) 