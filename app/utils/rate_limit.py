"""
Rate limiting pour les endpoints sensibles (audit 3.4).
Protege contre bruteforce (login, forgot-password) et enumeration.
validate-token utilise un bucket et un plafond distincts (trafic Next serveur).

C2: Store distribue Redis en prod. Fallback memoire borne pour dev/test (REDIS_URL vide).

FFI-L19C — IP cliente pour cles rate-limit : voir ``_get_client_ip`` et
``settings.RATE_LIMIT_TRUST_X_FORWARDED_FOR``.
"""

from functools import wraps
from typing import Callable, Optional

from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import get_logger
from app.utils.rate_limit_store import _get_store

logger = get_logger(__name__)

RATE_LIMIT_WINDOW_SEC = 60

# Brute-force / enumeration: login, forgot-password (strict, unchanged).
RATE_LIMIT_AUTH_SENSITIVE_MAX = 5

# Server-side JWT checks from Next (routeSession, syncCookie): higher ceiling than login;
# same IP key as today — see RAPPORT_VALIDATE_TOKEN_RATE_LIMIT_2026-04-07.
RATE_LIMIT_VALIDATE_TOKEN_MAX = 90

# Truncation limits for operational logging (no secrets; never log body or Authorization).
_AUTH_LOG_UA_MAX = 160
_AUTH_LOG_REFERER_MAX = 220
_AUTH_LOG_XFF_MAX = 160
_AUTH_LOG_CALLER_MAX = 48

# Next.js server-side validate-token fetches may set this for log attribution (forged by clients is possible).
VALIDATE_TOKEN_CALLER_HEADER = "x-mathakine-validate-caller"
RATE_LIMIT_REGISTER_MAX = 3  # creation de compte
RATE_LIMIT_FEEDBACK_MAX = 10  # feedback – 10 req/min/IP
RATE_LIMIT_RESEND_VERIFICATION_MAX = 2  # resend-verification (abus email)
RATE_LIMIT_CHAT_MAX = 15  # chat/stream - cout OpenAI, eviter abus
RATE_LIMIT_AI_MAX_PER_HOUR = 10
RATE_LIMIT_AI_MAX_PER_DAY = 50

# Generation IA exercices (OpenAI) — cles Redis distinctes des defis ; quotas separes.
RATE_LIMIT_EXERCISE_AI_MAX_PER_HOUR = 10
RATE_LIMIT_EXERCISE_AI_MAX_PER_DAY = 50

# Messages d'erreur centralises (429 Too Many Requests)
MSG_RATE_LIMIT_RETRY = "Trop de tentatives. Veuillez reessayer dans une minute."
MSG_FEEDBACK_RATE_LIMIT = "Trop de signalements. Veuillez reessayer dans une minute."
MSG_CHAT_RATE_LIMIT = "Limite de messages atteinte. Veuillez reessayer dans une minute."
MSG_AI_HOURLY_RATE_LIMIT = "Limite horaire de generation atteinte."
MSG_AI_DAILY_RATE_LIMIT = "Limite journaliere de generation atteinte."
MSG_EXERCISE_AI_HOURLY_RATE_LIMIT = (
    "Limite horaire de generation d'exercices IA atteinte. Reessayez plus tard."
)
MSG_EXERCISE_AI_DAILY_RATE_LIMIT = (
    "Limite journaliere de generation d'exercices IA atteinte. Reessayez demain."
)


def _xff_first_non_empty_hop(forwarded: str) -> str | None:
    """Premier hop non vide dans une chaine X-Forwarded-For (virgule-separee)."""
    for segment in forwarded.split(","):
        hop = segment.strip()
        if hop:
            return hop
    return None


def _get_client_ip(request) -> str:
    """
    IP utilisee pour les cles de rate-limit (auth, register, chat, etc.) et logs alignes.

    Politique explicite (FFI-L19C) :
    - Si ``RATE_LIMIT_TRUST_X_FORWARDED_FOR`` est True et ``X-Forwarded-For`` contient
      au moins un hop non vide, utiliser le **premier** hop (client declare par la chaine).
      A n'utiliser que lorsque le bord reseau de confiance reecrit ou append XFF
      (ex. hebergeur), pas lorsque des clients peuvent imposer une fausse cle sans proxy.
    - Sinon : ``request.client.host`` (pair TCP ASGI), ou ``unknown``.
    """
    if settings.RATE_LIMIT_TRUST_X_FORWARDED_FOR:
        raw = request.headers.get("X-Forwarded-For")
        if raw:
            first = _xff_first_non_empty_hop(raw)
            if first:
                return first
    peer = getattr(request.client, "host", None) if request.client else None
    return peer or "unknown"


def get_client_ip_for_request(request) -> str:
    """IP alignee sur les cles de rate limit (meme logique que _get_client_ip)."""
    return _get_client_ip(request)


def auth_request_rate_limit_diagnostics(request) -> str:
    """
    Indices courts pour logs operationnels (429 / validate-token).
    Ne jamais inclure de token ni d'en-tete Authorization.
    """
    ua = (request.headers.get("user-agent") or "-")[:_AUTH_LOG_UA_MAX]
    ref = (request.headers.get("referer") or "-")[:_AUTH_LOG_REFERER_MAX]
    xff_raw = (request.headers.get("x-forwarded-for") or "-")[:_AUTH_LOG_XFF_MAX]
    caller = (request.headers.get(VALIDATE_TOKEN_CALLER_HEADER) or "-")[
        :_AUTH_LOG_CALLER_MAX
    ]
    return (
        f"ua={ua!r} referer={ref!r} xff_raw_head={xff_raw!r} validate_caller={caller!r}"
    )


def _rate_limit_response(message: str) -> JSONResponse:
    """Retourne une reponse 429 Too Many Requests."""
    from app.utils.error_handler import api_error_response

    return api_error_response(429, message)


def _check_rate_limit(
    key: str,
    max_requests: int,
    window_sec: int = RATE_LIMIT_WINDOW_SEC,
) -> bool:
    """
    Verifie si la requete depasse la limite.
    Returns True si autorise, False si limite.
    Store: Redis en prod (REDIS_URL), memoire en dev/test.
    """
    if settings.TESTING:
        return True
    return _get_store().check(key=key, max_requests=max_requests, window_sec=window_sec)


def check_ai_generation_rate_limit(user_id: int) -> tuple[bool, Optional[str]]:
    """
    Verifie les limites de generation IA par utilisateur sur 1h et 24h.
    Source de verite: store distribue Redis en prod, fallback memoire en dev/test.
    """
    if settings.TESTING:
        return True, None

    store = _get_store()
    hourly_key = f"rate_limit:ai_generation:hour:{user_id}"
    daily_key = f"rate_limit:ai_generation:day:{user_id}"

    if not store.check(hourly_key, RATE_LIMIT_AI_MAX_PER_HOUR, 3600):
        return False, MSG_AI_HOURLY_RATE_LIMIT
    if not store.check(daily_key, RATE_LIMIT_AI_MAX_PER_DAY, 86400):
        return False, MSG_AI_DAILY_RATE_LIMIT
    return True, None


def check_exercise_ai_generation_rate_limit(user_id: int) -> tuple[bool, Optional[str]]:
    """
    Limites dediees au flux exercices IA (OpenAI), independantes du compteur defis.

    Meme principe que check_ai_generation_rate_limit : refus explicite, pas de contournement.
    """
    if settings.TESTING:
        return True, None

    store = _get_store()
    hourly_key = f"rate_limit:exercise_ai_generation:hour:{user_id}"
    daily_key = f"rate_limit:exercise_ai_generation:day:{user_id}"

    if not store.check(hourly_key, RATE_LIMIT_EXERCISE_AI_MAX_PER_HOUR, 3600):
        return False, MSG_EXERCISE_AI_HOURLY_RATE_LIMIT
    if not store.check(daily_key, RATE_LIMIT_EXERCISE_AI_MAX_PER_DAY, 86400):
        return False, MSG_EXERCISE_AI_DAILY_RATE_LIMIT
    return True, None


def rate_limit_auth(endpoint_name: str):
    """Decorateur rate limit pour endpoints auth sensibles (login, forgot-password): 5 req/min / IP."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapped(request, *args, **kwargs):
            ip = _get_client_ip(request)
            key = f"rate_limit:{endpoint_name}:{ip}"
            if not _check_rate_limit(key, RATE_LIMIT_AUTH_SENSITIVE_MAX):
                diag = auth_request_rate_limit_diagnostics(request)
                logger.warning(
                    "Rate limit depasse | bucket=auth_sensitive | endpoint={} | ip={} | {}",
                    endpoint_name,
                    ip,
                    diag,
                )
                return _rate_limit_response(MSG_RATE_LIMIT_RETRY)
            return await func(request, *args, **kwargs)

        return wrapped

    return decorator


def rate_limit_validate_token(func: Callable):
    """
    Rate limit dedie a POST /api/auth/validate-token (trafic Next serveur legitime).

    Cle par IP comme les autres buckets auth ; quota distinct de login/forgot-password.
    """

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:validate-token:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_VALIDATE_TOKEN_MAX):
            diag = auth_request_rate_limit_diagnostics(request)
            logger.warning(
                "Rate limit depasse | bucket=validate_token | endpoint=validate-token | ip={} | {}",
                ip,
                diag,
            )
            return _rate_limit_response(MSG_RATE_LIMIT_RETRY)
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_register(func: Callable):
    """Decorateur rate limit pour creation de compte (3 req/min)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:register:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_REGISTER_MAX):
            logger.warning("Rate limit depasse pour register depuis {}", ip)
            return _rate_limit_response(MSG_RATE_LIMIT_RETRY)
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_feedback(func: Callable):
    """Decorateur rate limit pour POST /api/feedback : 10 req/min par IP."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:feedback:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_FEEDBACK_MAX):
            logger.warning("Rate limit depasse pour feedback depuis {}", ip)
            return _rate_limit_response(MSG_FEEDBACK_RATE_LIMIT)
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_resend_verification(func: Callable):
    """Decorateur rate limit pour resend-verification (2 req/min par IP)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:resend_verification:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_RESEND_VERIFICATION_MAX):
            logger.warning("Rate limit depasse pour resend-verification depuis {}", ip)
            return _rate_limit_response(MSG_RATE_LIMIT_RETRY)
        return await func(request, *args, **kwargs)

    return wrapped


def rate_limit_chat(func: Callable):
    """Decorateur rate limit pour chat/stream (15 req/min par IP - cout OpenAI)."""

    @wraps(func)
    async def wrapped(request, *args, **kwargs):
        ip = _get_client_ip(request)
        key = f"rate_limit:chat:{ip}"
        if not _check_rate_limit(key, RATE_LIMIT_CHAT_MAX):
            logger.warning("Rate limit depasse pour chat depuis {}", ip)
            return _rate_limit_response(MSG_CHAT_RATE_LIMIT)
        return await func(request, *args, **kwargs)

    return wrapped
