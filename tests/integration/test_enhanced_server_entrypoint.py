from starlette.applications import Starlette

from enhanced_server import app, get_app


def test_enhanced_server_exports_concrete_starlette_app() -> None:
    """Gunicorn/Uvicorn must receive a concrete ASGI app, not a custom proxy."""
    assert isinstance(app, Starlette)
    assert app is get_app()

