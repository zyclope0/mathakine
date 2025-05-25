"""
Utilitaires pour les tests unitaires

IMPORTANT: Meilleures pratiques pour les tests:

1. Tests asynchrones :
   - Toujours utiliser le décorateur @pytest.mark.asyncio pour les tests asynchrones
   - Nommer les fonctions de test asynchrones avec le suffixe '_async'
   - Utiliser create_mock_request() pour créer des requêtes mockées
   - Exemple: 
     @pytest.mark.asyncio
     async def test_some_handler_async():
         # Code du test...

2. Tests synchrones :
   - Éviter de mélanger les tests synchrones et asynchrones dans le même fichier
   - Pour les handlers asynchrones, utiliser sync_to_async_handler()
   - Exemple:
     def test_some_handler():
         # Code du test...

3. Mocks et patching :
   - Préférer le pattern with patch() à patch comme décorateur
   - Utiliser des noms explicites pour les mocks

4. Fixtures :
   - Utiliser les fixtures centralisées de conftest.py plutôt que redéfinir les mêmes dans chaque fichier
"""
import json
from unittest.mock import MagicMock
from starlette.requests import Request
from app.utils.db_helpers import get_enum_value

def create_mock_request(json_data=None, query_params=None, path_params=None):
    """
    Crée un objet Request mock pour les tests
    
    Args:
        json_data: Données JSON pour la requête
        query_params: Paramètres de requête
        path_params: Paramètres de chemin
        
    Returns:
        Un objet Request mocké
    """
    mock_request = MagicMock(spec=Request)
    
    # Configurer les données JSON de la requête
    if json_data:
        async def mock_json():
            return json_data
        mock_request.json = mock_json
    
    # Configurer les paramètres de requête
    if query_params:
        mock_request.query_params = query_params
    else:
        mock_request.query_params = {}
    
    # Configurer les paramètres de chemin
    if path_params:
        mock_request.path_params = path_params
    else:
        mock_request.path_params = {}
    
    # Ajouter app.state pour les templates
    mock_state = MagicMock()
    mock_templates = MagicMock()
    mock_state.templates = mock_templates
    mock_request.app.state = mock_state
    
    return mock_request

async def sync_to_async_handler(handler, json_data, auth_user=None):
    """
    Convertit un appel de handler asynchrone en appel synchrone pour les tests
    
    Args:
        handler: La fonction handler asynchrone
        json_data: Les données JSON à passer au handler
        auth_user: Utilisateur authentifié (mock)
        
    Returns:
        La réponse du handler convertie en dictionnaire
    """
    # Créer la requête mockée
    request = create_mock_request(json_data=json_data)
    
    # Définir le contexte d'authentification si nécessaire
    if auth_user:
        # Dans un cas réel, cela serait fait via le middleware d'authentification
        request.user = auth_user
    
    # Appeler le handler asynchrone
    response = await handler(request)
    
    # Si la réponse est une JSONResponse, convertir son contenu
    if hasattr(response, 'body'):
        try:
            response_content = json.loads(response.body.decode('utf-8'))
            return response_content
        except Exception:
            return {"error": "Erreur de décodage de la réponse JSON"}
    
    # Si c'est une redirection, retourner l'URL
    if hasattr(response, 'headers') and response.status_code in (301, 302, 303, 307, 308):
        return {"redirect": response.headers.get('location')}
    
    # Pour les réponses template
    if hasattr(response, 'template') and hasattr(response, 'context'):
        return {
            "template": response.template.name,
            "context": response.context
        }
    
    # Fallback
    return {"status_code": getattr(response, 'status_code', 200)} 