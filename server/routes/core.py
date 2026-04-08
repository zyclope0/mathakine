"""Routes système : health, robots, metrics."""

from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route


async def root_handler(request: Request):
    """
    GET|HEAD / — réponse minimale pour sondes plateforme (ex. Render envoie HEAD / au déploiement).

    L’API reste orientée /api/* et /health ; la racine évite un 404 bruyant dans les logs.
    """
    if request.method == "HEAD":
        return Response(status_code=200)
    return PlainTextResponse(
        "Mathakine API — see /health\n",
        status_code=200,
        media_type="text/plain",
    )


async def health_handler(request):
    """GET /health - Health check pour Render et load balancers."""
    return PlainTextResponse("ok", status_code=200)


async def robots_txt(request):
    """robots.txt - évite les 404 des crawlers sur le backend."""
    return PlainTextResponse("User-agent: *\nDisallow: /\n", media_type="text/plain")


async def metrics_handler(request):
    """GET /metrics - métriques Prometheus (p50/p95/p99, taux d'erreur)."""
    from app.core.monitoring import metrics_endpoint

    return await metrics_endpoint(request)


def get_core_routes():
    return [
        Route("/", endpoint=root_handler, methods=["GET", "HEAD"]),
        Route("/health", endpoint=health_handler, methods=["GET"]),
        Route("/robots.txt", endpoint=robots_txt, methods=["GET"]),
        Route("/metrics", endpoint=metrics_handler, methods=["GET"]),
    ]
