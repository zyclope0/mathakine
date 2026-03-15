"""
Monitoring — Sentry (erreurs + métriques + corrélation request_id) et Prometheus (fallback).

RÉALITÉ (audit 2026-02):
- sentry_sdk.init() : appelé au startup si SENTRY_DSN défini
- Métriques : Prometheus + Sentry (éviter démultiplication outils)
- request_id : corrélation logs ↔ Sentry via RequestIdMiddleware
- Désactivé en mode TESTING

Note: Prometheus désactivé sur Windows — import peut bloquer/freeze (deadlock connu
thread+import, CPython #125037). Pas de thread de contournement : ça déplace le blocage.
"""

import os
import sys
import time
from typing import Any

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Prometheus : désactivé sur Windows (blocage/freeze connu)
_prometheus_available = False
_CONTENT_TYPE_LATEST = None
_REGISTRY = None
_Counter = None
_Histogram = None
_generate_latest = None

# Métriques Prometheus (créées à l'init)
HTTP_REQUESTS_TOTAL: Any = None
HTTP_REQUEST_DURATION: Any = None
_monitoring_init_attempted = False
_monitoring_initialized = False


def _load_prometheus_client():
    """
    Import prometheus_client. Désactivé sur Windows : l'import peut bloquer indéfiniment
    (deadlock thread+import). Pas de thread de contournement — ça déplace le blocage.
    """
    global _prometheus_available, _CONTENT_TYPE_LATEST, _REGISTRY, _Counter, _Histogram, _generate_latest

    if _prometheus_available:
        return True

    if sys.platform == "win32":
        logger.info(
            "Prometheus désactivé sur Windows (blocage connu à l'import), métriques via Sentry uniquement"
        )
        return False

    try:
        from prometheus_client import (
            CONTENT_TYPE_LATEST,
            REGISTRY,
            Counter,
            Histogram,
            generate_latest,
        )

        _CONTENT_TYPE_LATEST = CONTENT_TYPE_LATEST
        _REGISTRY = REGISTRY
        _Counter = Counter
        _Histogram = Histogram
        _generate_latest = generate_latest
        _prometheus_available = True
        return True
    except ImportError:
        return False


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
    global _monitoring_init_attempted, _monitoring_initialized

    if _monitoring_init_attempted:
        return _monitoring_initialized

    _monitoring_init_attempted = True
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
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration

            # Désactiver le logging integration par défaut (on a déjà loguru)
            logging_integration = LoggingIntegration(level=None, event_level=None)

            # StarletteIntegration : transactions HTTP automatiques dans Sentry Performance
            # SqlalchemyIntegration : spans DB automatiques + détection N+1
            starlette_integration = StarletteIntegration(transaction_style="url")
            sqlalchemy_integration = SqlalchemyIntegration()

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
                integrations=[
                    logging_integration,
                    starlette_integration,
                    sqlalchemy_integration,
                ],
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
    if (
        _load_prometheus_client()
        and HTTP_REQUESTS_TOTAL is None
        and _Counter is not None
        and _Histogram is not None
    ):
        try:
            HTTP_REQUESTS_TOTAL = _Counter(
                "mathakine_http_requests_total",
                "Total des requêtes HTTP",
                ["method", "path", "status"],
            )
            HTTP_REQUEST_DURATION = _Histogram(
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

    _monitoring_initialized = initialized
    return initialized


async def metrics_endpoint(request):
    """Endpoint GET /metrics pour Prometheus."""
    from starlette.responses import PlainTextResponse, Response

    if not _load_prometheus_client():
        return PlainTextResponse("Prometheus client non installé", status_code=501)

    data = _generate_latest(_REGISTRY)
    return Response(content=data, media_type=_CONTENT_TYPE_LATEST)


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
