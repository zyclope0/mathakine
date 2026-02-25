"""
Monitoring — Sentry (erreurs + métriques + corrélation request_id) et Prometheus (fallback).

RÉALITÉ (audit 2026-02):
- sentry_sdk.init() : appelé au startup si SENTRY_DSN défini
- Métriques : Prometheus + Sentry (éviter démultiplication outils)
- request_id : corrélation logs ↔ Sentry via RequestIdMiddleware
- Désactivé en mode TESTING
"""

import os
import time

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Prometheus (optionnel, évite import si désactivé)
_prometheus_available = False
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        REGISTRY,
        Counter,
        Histogram,
        generate_latest,
    )

    _prometheus_available = True
except ImportError:
    pass

# Métriques Prometheus (créées à l'init)
HTTP_REQUESTS_TOTAL: "Counter | None" = None
HTTP_REQUEST_DURATION: "Histogram | None" = None


def _sentry_before_send(event, hint):
    """Filtre optionnel : ignorer certaines URLs (health, metrics)."""
    if event.get("request", {}).get("url"):
        url = event["request"]["url"]
        if "/health" in url or "/metrics" in url:
            return None  # Ne pas envoyer les erreurs sur health/metrics
    return event


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
    global HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION
    initialized = False

    # 1. Sentry — erreurs et APM (SENTRY_DSN ou fallback NEXT_PUBLIC_SENTRY_DSN)
    sentry_dsn = (
        os.getenv("SENTRY_DSN") or os.getenv("NEXT_PUBLIC_SENTRY_DSN") or ""
    ).strip()
    testing = os.getenv("TESTING", "false").lower() == "true"

    if sentry_dsn and not testing:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration

            # Désactiver le logging integration par défaut (on a déjà loguru)
            logging_integration = LoggingIntegration(level=None, event_level=None)

            # Release : Render expose RENDER_GIT_COMMIT ; sinon SENTRY_RELEASE ou version
            release = (
                os.getenv("SENTRY_RELEASE")
                or os.getenv("RENDER_GIT_COMMIT")
                or os.getenv("VERCEL_GIT_COMMIT_SHA")
                or None
            )

            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=os.getenv("ENVIRONMENT", "development"),
                release=release,
                send_default_pii=False,
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
                profiles_sample_rate=float(
                    os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0")
                ),
                integrations=[logging_integration],
                before_send=_sentry_before_send,
            )
            logger.info(f"Sentry initialisé (DSN, release={release or 'auto'})")
            initialized = True
        except Exception as e:
            logger.warning(f"Sentry init échoué: {e}")
    elif testing:
        logger.debug("Sentry désactivé (mode TESTING)")
    else:
        logger.debug("Sentry non configuré (SENTRY_DSN manquant)")

    # 2. Prometheus — métriques (préfixe mathakine_ évite conflits avec uvicorn --reload)
    if _prometheus_available and HTTP_REQUESTS_TOTAL is None:
        try:
            HTTP_REQUESTS_TOTAL = Counter(
                "mathakine_http_requests_total",
                "Total des requêtes HTTP",
                ["method", "path", "status"],
            )
            HTTP_REQUEST_DURATION = Histogram(
                "mathakine_http_request_duration_seconds",
                "Durée des requêtes HTTP",
                ["method", "path"],
                buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
            )
            logger.info("Métriques Prometheus enregistrées")
            initialized = True
        except ValueError as e:
            if "Duplicated timeseries" in str(e):
                logger.debug("Métriques Prometheus déjà enregistrées (reload)")
            else:
                raise

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
            # Prometheus (fallback / scraping)
            if HTTP_REQUESTS_TOTAL and HTTP_REQUEST_DURATION:
                HTTP_REQUESTS_TOTAL.labels(
                    method=method, path=path, status=str(status)
                ).inc()
                HTTP_REQUEST_DURATION.labels(method=method, path=path).observe(duration)
            # Sentry métriques (SDK 2.44+) — un seul outil erreurs + métriques
            try:
                import sentry_sdk

                if hasattr(sentry_sdk, "metrics"):
                    attrs = {"method": method, "path": path, "status": str(status)}
                    sentry_sdk.metrics.count("http.requests", 1, attributes=attrs)
                    sentry_sdk.metrics.distribution(
                        "http.request.duration",
                        duration,
                        unit="second",
                        attributes={"method": method, "path": path},
                    )
            except Exception:
                pass
