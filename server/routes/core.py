"""Routes système : live, readiness, robots, metrics."""

from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route


async def root_handler(request: Request):
    """
    GET|HEAD / — réponse minimale pour sondes plateforme (ex. Render envoie HEAD / au déploiement).

    L’API reste orientée /api/* ; readiness : GET /ready (ou /health, alias).
    """
    if request.method == "HEAD":
        return Response(status_code=200)
    return PlainTextResponse(
        "Mathakine API — liveness: GET /live — readiness: GET /ready\n",
        status_code=200,
        media_type="text/plain",
    )


async def live_handler(request: Request) -> JSONResponse:
    """GET /live — liveness : process répond (aucune dépendance externe)."""
    return JSONResponse({"status": "live"}, status_code=200)


async def ready_handler(request: Request) -> JSONResponse:
    """GET /ready — readiness : DB (+ Redis en prod si configuré)."""
    from app.utils.readiness_probe import run_readiness_checks

    ok, checks = await run_readiness_checks()
    if ok:
        return JSONResponse({"status": "ready", "checks": checks}, status_code=200)
    return JSONResponse({"status": "not_ready", "checks": checks}, status_code=503)


async def health_handler(request: Request) -> JSONResponse:
    """GET /health — alias readiness (rétrocompat sondes / docs)."""
    return await ready_handler(request)


async def robots_txt(request: Request):
    """robots.txt - évite les 404 des crawlers sur le backend."""
    return PlainTextResponse("User-agent: *\nDisallow: /\n", media_type="text/plain")


async def metrics_handler(request: Request):
    """GET /metrics - métriques Prometheus (p50/p95/p99, taux d'erreur)."""
    from app.core.monitoring import metrics_endpoint

    return await metrics_endpoint(request)


def get_core_routes():
    return [
        Route("/", endpoint=root_handler, methods=["GET", "HEAD"]),
        Route("/live", endpoint=live_handler, methods=["GET"]),
        Route("/ready", endpoint=ready_handler, methods=["GET"]),
        Route("/health", endpoint=health_handler, methods=["GET"]),
        Route("/robots.txt", endpoint=robots_txt, methods=["GET"]),
        Route("/metrics", endpoint=metrics_handler, methods=["GET"]),
    ]
