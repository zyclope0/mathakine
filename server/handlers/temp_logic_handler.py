"""
Handler temporaire pour debugging du problème render_template
"""

from starlette.responses import JSONResponse, RedirectResponse, PlainTextResponse
from server.views import get_current_user


async def temp_logic_challenge_page(request):
    """Handler temporaire pour debugging"""
    try:
        from server.template_handler import render_template, render_error
        
        current_user = await get_current_user(request) or {"is_authenticated": False}
        
        if not current_user["is_authenticated"]:
            return RedirectResponse(url="/login", status_code=302)
        
        challenge_id = int(request.path_params["challenge_id"])
        
        # Retour simple pour tester
        return PlainTextResponse(f"Challenge ID: {challenge_id} - Test OK")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return PlainTextResponse(f"Erreur: {str(e)}", status_code=500) 