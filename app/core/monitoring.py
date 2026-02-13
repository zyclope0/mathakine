"""
Monitoring — Sentry (erreurs/APM) et Prometheus (métriques).

RÉALITÉ (audit 2026-02):
- sentry_sdk.init() : appelé au startup si SENTRY_DSN défini
- Endpoint /metrics : exposé pour Prometheus (p50/p95/p99, taux d'erreur)
- Désactivé en mode TESTING
"""
import os
import time
from typing import Callable

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Prometheus (optionnel, évite import si désactivé)
_prometheus_available = False
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        REGISTRY,
        generate_latest,
    )
    _prometheus_available = True
except ImportError:
    pass

# Métriques Prometheus (créées à l'init)
HTTP_REQUESTS_TOTAL: "Counter | None" = None
HTTP_REQUEST_DURATION: "Histogram | None" = None


def _normalize_path(path: str) -> str:
    """Réduit les IDs dynamiques pour limiter la cardinalité des métriques."""
    if "/api/" in path:
        parts = path.split("/")
        for i, p in enumerate(parts):
            if p.isdigit() and i > 0:
                parts[i] = "{id}"
        return "/".join(parts)
    return path


def init_monitoring() -> bool:
    """
    Initialise Sentry et les métriques Prometheus.

    Returns:
        True si au moins une partie du monitoring est active.
    """
    initialized = False

    # 1. Sentry — erreurs et APM
    sentry_dsn = os.getenv("SENTRY_DSN", "").strip()
    testing = os.getenv("TESTING", "false").lower() == "true"

    if sentry_dsn and not testing:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration

            # Désactiver le logging integration par défaut (on a déjà loguru)
            logging_integration = LoggingIntegration(level=None, event_level=None)

            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=os.getenv("ENVIRONMENT", "development"),
                send_default_pii=False,
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
                profiles_sample_rate=0.0,
                integrations=[logging_integration],
            )
            logger.info("Sentry initialisé (DSN configuré)")
            initialized = True
        except Exception as e:
            logger.warning(f"Sentry init échoué: {e}")
    elif testing:
        logger.debug("Sentry désactivé (mode TESTING)")
    else:
        logger.debug("Sentry non configuré (SENTRY_DSN manquant)")

    # 2. Prometheus — métriques
    if _prometheus_available:
        global HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION
        HTTP_REQUESTS_TOTAL = Counter(
            "http_requests_total",
            "Total des requêtes HTTP",
            ["method", "path", "status"],
        )
        HTTP_REQUEST_DURATION = Histogram(
            "http_request_duration_seconds",
            "Durée des requêtes HTTP",
            ["method", "path"],
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )
        logger.info("Métriques Prometheus enregistrées")
        initialized = True

    return initialized


async def metrics_endpoint(request):
    """Endpoint GET /metrics pour Prometheus."""
    from starlette.responses import PlainTextResponse, Response

    if not _prometheus_available:
        return PlainTextResponse("Prometheus client non installé", status_code=501)

    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


class PrometheusMetricsMiddleware:
    """Middleware Starlette (ASGI) pour enregistrer les métriques HTTP."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = _normalize_path(scope.get("path", ""))

        start = time.perf_counter()
        status = 500

        async def send_wrapper(message):
            nonlocal status
            if message.get("type") == "http.response.start":
                status = message.get("status", 500)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            status = 500
            raise
        finally:
            duration = time.perf_counter() - start
            if HTTP_REQUESTS_TOTAL and HTTP_REQUEST_DURATION:
                HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=str(status)).inc()
                HTTP_REQUEST_DURATION.labels(method=method, path=path).observe(duration)
