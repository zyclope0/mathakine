"""
Template handler module for Mathakine.

Fournit l'instance Jinja2Templates partagée pour l'application.
L'app étant une API pure JSON (frontend Next.js séparé), ce module
se limite à l'initialisation des templates (utilisé par server/app.py).
"""

import json
from pathlib import Path

from starlette.templating import Jinja2Templates

# Get templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = str(BASE_DIR / "templates")

# Initialize templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Add tojson filter
templates.env.filters["tojson"] = lambda obj: json.dumps(obj)


def get_templates() -> Jinja2Templates:
    """
    Retourne l'instance Jinja2Templates partagée.
    Utilisé dans server/app.py pour l'initialisation de l'application.
    """
    return templates
