"""Routes système : health, robots, metrics."""

from starlette.responses import PlainTextResponse
from starlette.routing import Route


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
        Route("/health", endpoint=health_handler, methods=["GET"]),
        Route("/robots.txt", endpoint=robots_txt, methods=["GET"]),
        Route("/metrics", endpoint=metrics_handler, methods=["GET"]),
    ]
