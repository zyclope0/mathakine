"""
Template handler module for Mathakine.

This module centralizes template rendering logic, providing consistent
error handling and template context preparation across the application.
"""
import json
import traceback
from pathlib import Path

from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

# Get templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = str(BASE_DIR / 'templates')

# Initialize templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Add tojson filter
templates.env.filters["tojson"] = lambda obj: json.dumps(obj)

def render_template(
    template_name: str,
    request: Request,
    context: dict = None,
    status_code: int = 200
) -> HTMLResponse:
    """
    Render a template with consistent error handling.
    
    Args:
        template_name: Name of the template to render
        request: The Starlette request object
        context: Template context dictionary
        status_code: HTTP status code
        
    Returns:
        HTMLResponse with the rendered template
    """
    try:
        # Initialize context if None
        context = context or {}
        
        # Ensure 'request' is in context
        context['request'] = request
        
        # Ensure current_user is set (default to unauthenticated)
        if 'current_user' not in context:
            context['current_user'] = {"is_authenticated": False}
            
        # Render template
        return templates.TemplateResponse(
            template_name,
            context=context,
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Error rendering template {template_name}: {e}")
        traceback.print_exc()
        
        # Render error template
        return render_error(
            request=request,
            error="Template Error",
            message=f"Error rendering template: {str(e)}",
            status_code=500
        )

def render_error(
    request: Request,
    error: str,
    message: str = None,
    status_code: int = 500
) -> HTMLResponse:
    """
    Render an error template.
    
    Args:
        request: The Starlette request object
        error: Error title
        message: Error message
        status_code: HTTP status code
        
    Returns:
        HTMLResponse with the rendered error template
    """
    try:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error": error,
                "message": message or "An error occurred.",
                "current_user": {"is_authenticated": False}
            },
            status_code=status_code
        )
    except Exception as template_error:
        # If rendering error template fails, fallback to basic HTML
        logger.critical(f"Error rendering error template: {template_error}")
        logger.critical(traceback.format_exc())
        
        return HTMLResponse(
            f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>{error}</h1>
                    <p>{message or "An error occurred."}</p>
                    <p>Additionally, an error occurred while rendering the error page.</p>
                    <a href="/">Return to home</a>
                </body>
            </html>
            """,
            status_code=status_code
        )

def get_templates() -> Jinja2Templates:
    """
    Get the templates object for use in application initialization.
    
    Returns:
        Jinja2Templates object
    """
    return templates 