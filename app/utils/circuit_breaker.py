"""
Circuit-breaker process-local pour les appels OpenAI (exercices / défis).

P5 — résilience : évite d'enchaîner les timeouts quand l'amont est dégradé.
Un seul breaker partagé pour tous les workloads OpenAI du process (Gunicorn worker).
"""

from __future__ import annotations

import threading
import time
from enum import Enum
from typing import Callable, List, Optional

# Seuils explicites (pas de magic numbers dans les services).
OPENAI_CIRCUIT_FAILURE_THRESHOLD = 5
OPENAI_CIRCUIT_FAILURE_WINDOW_SECONDS = 120.0
OPENAI_CIRCUIT_COOLDOWN_SECONDS = 60.0

OPENAI_CIRCUIT_OPEN_USER_MESSAGE = (
    "Le service de génération IA est temporairement indisponible. "
    "Veuillez réessayer dans quelques instants."
)


class _CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class OpenAiWorkloadCircuitBreaker:
    """
    États CLOSED / OPEN / HALF_OPEN, thread-safe.

    - CLOSED : appels autorisés ; les échecs comptables dans la fenêtre ouvrent le circuit.
    - OPEN : appels refusés jusqu'à fin du cooldown, puis passage HALF_OPEN pour une sonde.
    - HALF_OPEN : un seul appel autorisé ; succès → CLOSED, échec comptable → OPEN.
    """

    def __init__(
        self,
        *,
        failure_threshold: int = OPENAI_CIRCUIT_FAILURE_THRESHOLD,
        failure_window_s: float = OPENAI_CIRCUIT_FAILURE_WINDOW_SECONDS,
        cooldown_s: float = OPENAI_CIRCUIT_COOLDOWN_SECONDS,
        time_fn: Optional[Callable[[], float]] = None,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._failure_window_s = failure_window_s
        self._cooldown_s = cooldown_s
        self._time_fn = time_fn or time.monotonic
        self._lock = threading.Lock()
        self._state = _CircuitState.CLOSED
        self._failure_times: List[float] = []
        self._opened_at: Optional[float] = None
        self._half_open_probe_active = False

    def reset_for_testing(self) -> None:
        """Réinitialise l'état (tests uniquement)."""
        with self._lock:
            self._state = _CircuitState.CLOSED
            self._failure_times.clear()
            self._opened_at = None
            self._half_open_probe_active = False

    def _prune_failures(self, now: float) -> None:
        cutoff = now - self._failure_window_s
        self._failure_times = [t for t in self._failure_times if t >= cutoff]

    def check_allow(self) -> bool:
        """
        Retourne True si un appel OpenAI peut être tenté.
        En HALF_OPEN, réserve la sonde au premier appelant jusqu'à record_*.
        """
        with self._lock:
            now = self._time_fn()
            self._prune_failures(now)

            if self._state == _CircuitState.CLOSED:
                return True

            if self._state == _CircuitState.OPEN:
                if self._opened_at is None:
                    self._state = _CircuitState.CLOSED
                    return True
                if now < self._opened_at + self._cooldown_s:
                    return False
                self._state = _CircuitState.HALF_OPEN
                self._half_open_probe_active = False

            if self._state == _CircuitState.HALF_OPEN:
                if self._half_open_probe_active:
                    return False
                self._half_open_probe_active = True
                return True

            return True

    def record_success(self) -> None:
        """Appel après réponse OpenAI considérée comme réussie (stream terminé sans erreur)."""
        with self._lock:
            self._failure_times.clear()
            self._state = _CircuitState.CLOSED
            self._opened_at = None
            self._half_open_probe_active = False

    def record_countable_failure(self) -> None:
        """Enregistre un échec lié à la disponibilité OpenAI (timeout, 5xx, etc.)."""
        with self._lock:
            now = self._time_fn()
            self._half_open_probe_active = False

            if self._state == _CircuitState.HALF_OPEN:
                self._state = _CircuitState.OPEN
                self._opened_at = now
                return

            self._failure_times.append(now)
            self._prune_failures(now)
            if len(self._failure_times) >= self._failure_threshold:
                self._state = _CircuitState.OPEN
                self._opened_at = now

    def probe_finished_without_countable_outcome(self) -> None:
        """
        Libère la sonde HALF_OPEN sans ouvrir le circuit (erreur non liée à la santé OpenAI).
        """
        with self._lock:
            self._half_open_probe_active = False


openai_workload_circuit_breaker = OpenAiWorkloadCircuitBreaker()


def is_countable_openai_failure(exc: BaseException) -> bool:
    """
    Détermine si l'exception doit alimenter le breaker.

    Comptées : timeout, rate limit, erreur réseau, réponses serveur 5xx / 408.
    Non comptées : erreurs client 4xx (hors 429), erreurs sans code explicite hors familles ci-dessus.
    """
    try:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            InternalServerError,
            RateLimitError,
        )
    except ImportError:
        return False

    if isinstance(exc, (APITimeoutError, RateLimitError, APIConnectionError)):
        return True
    if isinstance(exc, InternalServerError):
        return True
    if isinstance(exc, APIStatusError):
        code = getattr(exc, "status_code", None)
        if code is None:
            return False
        if code >= 500 or code == 408:
            return True
        return False
    return False
