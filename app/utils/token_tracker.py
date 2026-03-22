"""
Module de tracking de l'utilisation des tokens OpenAI.
Permet de monitorer les coûts et l'utilisation de l'API.
"""

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, Optional

from app.core.logging_config import get_logger
from app.utils import ai_workload_keys as _ai_workload_keys
from app.utils.ai_workload_keys import (
    classify_ai_workload_key,
    runtime_ai_metrics_retention_meta,
)

logger = get_logger(__name__)


class TokenTracker:
    """Tracker simple en mémoire pour l'utilisation des tokens (peut être migré vers DB)."""

    def __init__(self):
        # Structure: {metric_key: [{"timestamp": datetime, "tokens": int, "cost": float}]}
        self._usage_history: Dict[str, list] = defaultdict(list)
        self._daily_totals: Dict[str, Dict] = defaultdict(
            lambda: {"tokens": 0, "cost": 0.0}
        )

    def track_usage(
        self,
        challenge_type: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini",
    ) -> Dict[str, float]:
        """
        Track l'utilisation de tokens pour une génération.

        Args:
            challenge_type: Type de challenge généré
            prompt_tokens: Nombre de tokens dans le prompt
            completion_tokens: Nombre de tokens dans la réponse
            model: Modèle OpenAI utilisé

        Returns:
            Dict avec 'tokens' (total) et 'cost' (coût estimé en USD)
        """
        total_tokens = prompt_tokens + completion_tokens

        # Coûts par modèle (USD par 1K tokens) - mise à jour mars 2026
        # Source: https://openai.com/api/pricing/
        # Les modèles o3/o3-mini sont facturés sur les tokens de raisonnement (output élargi)
        cost_per_1k_tokens = {
            "gpt-4o-mini": {
                "input": 0.15 / 1000,  # $0.15 per 1M tokens
                "output": 0.60 / 1000,  # $0.60 per 1M tokens
            },
            "gpt-4o": {
                "input": 2.50 / 1000,  # $2.50 per 1M tokens
                "output": 10.00 / 1000,  # $10.00 per 1M tokens
            },
            "gpt-4-turbo": {
                "input": 10.00 / 1000,  # $10.00 per 1M tokens
                "output": 30.00 / 1000,  # $30.00 per 1M tokens
            },
            "o3": {
                "input": 2.00 / 1000,  # $2.00 per 1M tokens
                "output": 8.00 / 1000,  # $8.00 per 1M tokens (inclut reasoning tokens)
            },
            "o3-mini": {
                "input": 1.10 / 1000,  # $1.10 per 1M tokens
                "output": 4.40 / 1000,  # $4.40 per 1M tokens
            },
            "o4-mini": {
                "input": 1.10 / 1000,  # $1.10 per 1M tokens (estimation)
                "output": 4.40 / 1000,  # $4.40 per 1M tokens (estimation)
            },
            # Exercices IA (allowlist) — grilles indicatives ; ajuster selon openai.com/pricing
            "o1": {
                "input": 15.00 / 1000,
                "output": 60.00 / 1000,
            },
            "o1-mini": {
                "input": 1.10 / 1000,
                "output": 4.40 / 1000,
            },
            "gpt-5": {
                "input": 1.25 / 1000,  # $1.25 per 1M tokens
                "output": 10.00 / 1000,  # $10.00 per 1M tokens
            },
            "gpt-5.1": {
                "input": 1.25 / 1000,  # $1.25 per 1M tokens
                "output": 10.00 / 1000,  # $10.00 per 1M tokens
            },
            "gpt-5.2": {
                "input": 1.75 / 1000,  # $1.75 per 1M tokens
                "output": 14.00 / 1000,  # $14.00 per 1M tokens
            },
            "gpt-5.4": {
                "input": 2.50 / 1000,  # $2.50 per 1M tokens
                "output": 15.00 / 1000,  # $15.00 per 1M tokens
            },
            "gpt-5-mini": {
                "input": 0.25 / 1000,  # $0.25 per 1M tokens
                "output": 2.00 / 1000,  # $2.00 per 1M tokens
            },
            "gpt-5-nano": {
                "input": 0.05 / 1000,  # $0.05 per 1M tokens
                "output": 0.40 / 1000,  # $0.40 per 1M tokens
            },
            "gpt5-nano": {
                "input": 0.05 / 1000,  # $0.05 per 1M tokens
                "output": 0.40 / 1000,  # $0.40 per 1M tokens
            },
            "gpt-3.5-turbo": {
                "input": 0.50 / 1000,
                "output": 1.50 / 1000,
            },
        }

        # Calculer le coût — warning explicite si modèle inconnu (pas de fallback silencieux)
        if model not in cost_per_1k_tokens:
            logger.warning(
                f"Modèle '{model}' absent de la table de coûts — estimation avec gpt-4o-mini. "
                f"Mettre à jour token_tracker.py § cost_per_1k_tokens."
            )
        model_costs = cost_per_1k_tokens.get(model, cost_per_1k_tokens["gpt-4o-mini"])
        cost = (prompt_tokens / 1000 * model_costs["input"]) + (
            completion_tokens / 1000 * model_costs["output"]
        )

        # Enregistrer l'utilisation
        usage_record = {
            "timestamp": datetime.now(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": cost,
            "model": model,
        }

        self._usage_history[challenge_type].append(usage_record)

        # Mettre à jour les totaux quotidiens
        today = datetime.now().date()
        day_key = f"{challenge_type}_{today}"
        self._daily_totals[day_key]["tokens"] += total_tokens
        self._daily_totals[day_key]["cost"] += cost

        self._prune_metric_key_records(challenge_type)
        self._prune_stale_daily_totals()

        logger.info(
            f"Token usage tracked - Type: {challenge_type}, "
            f"Tokens: {total_tokens} (prompt: {prompt_tokens}, completion: {completion_tokens}), "
            f"Cost: ${cost:.6f}, Model: {model}"
        )

        return {
            "tokens": total_tokens,
            "cost": cost,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }

    def get_stats(self, challenge_type: Optional[str] = None, days: int = 1) -> Dict:
        """
        Retourne les statistiques d'utilisation.

        Args:
            challenge_type: Type de challenge (None pour tous)
            days: Nombre de jours à considérer

        Returns:
            Dict avec statistiques agrégées
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        if challenge_type:
            records = [
                r
                for r in self._usage_history[challenge_type]
                if r["timestamp"] > cutoff_date
            ]
        else:
            # Tous les types
            records = []
            for type_records in self._usage_history.values():
                records.extend(
                    [r for r in type_records if r["timestamp"] > cutoff_date]
                )

        if not records:
            return {
                "total_tokens": 0,
                "total_cost": 0.0,
                "average_tokens": 0,
                "count": 0,
                "by_type": {},
                "by_model": {},
                "by_workload": {},
                "retention": runtime_ai_metrics_retention_meta(),
                "cost_disclaimer_fr": (
                    "Coûts USD = estimation à partir de grilles token_tracker (OpenAI indicatif)."
                ),
            }

        total_tokens = sum(r["total_tokens"] for r in records)
        total_cost = sum(r["cost"] for r in records)
        average_tokens = total_tokens / len(records)

        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_tokens": average_tokens,
            "count": len(records),
            "by_type": (
                self._get_stats_by_type(cutoff_date) if not challenge_type else {}
            ),
            "by_model": self._get_stats_by_model(records),
            "by_workload": self._get_stats_by_workload(cutoff_date),
            "retention": runtime_ai_metrics_retention_meta(),
            "cost_disclaimer_fr": (
                "Coûts USD = estimation à partir de grilles token_tracker (OpenAI indicatif) ; "
                "modèles absents de la table retombent sur gpt-4o-mini avec log warning."
            ),
        }

    def _get_stats_by_model(self, records: list) -> Dict[str, Dict]:
        """Retourne les stats groupées par modèle IA utilisé."""
        stats_by_model: Dict[str, Dict] = {}
        for r in records:
            model = r.get("model", "unknown")
            if model not in stats_by_model:
                stats_by_model[model] = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "count": 0,
                }
            stats_by_model[model]["total_tokens"] += r["total_tokens"]
            stats_by_model[model]["total_cost"] += r["cost"]
            stats_by_model[model]["count"] += 1
        return stats_by_model

    def _get_stats_by_type(self, cutoff_date: datetime) -> Dict[str, Dict]:
        """Retourne les stats groupées par type."""
        stats_by_type = {}

        for challenge_type, records in self._usage_history.items():
            filtered = [r for r in records if r["timestamp"] > cutoff_date]
            if filtered:
                stats_by_type[challenge_type] = {
                    "total_tokens": sum(r["total_tokens"] for r in filtered),
                    "total_cost": sum(r["cost"] for r in filtered),
                    "count": len(filtered),
                    "average_tokens": sum(r["total_tokens"] for r in filtered)
                    / len(filtered),
                }

        return stats_by_type

    def _get_stats_by_workload(self, cutoff_date: datetime) -> Dict[str, Dict]:
        """Retourne les stats groupées par workload stable."""
        stats_by_workload: Dict[str, Dict] = {}

        for metric_key, records in self._usage_history.items():
            filtered = [r for r in records if r["timestamp"] > cutoff_date]
            if not filtered:
                continue

            workload = classify_ai_workload_key(metric_key)

            bucket = stats_by_workload.setdefault(
                workload,
                {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "count": 0,
                    "average_tokens": 0.0,
                },
            )
            bucket["total_tokens"] += sum(r["total_tokens"] for r in filtered)
            bucket["total_cost"] += sum(r["cost"] for r in filtered)
            bucket["count"] += len(filtered)

        for bucket in stats_by_workload.values():
            count = bucket["count"]
            bucket["average_tokens"] = (
                bucket["total_tokens"] / count if count > 0 else 0.0
            )

        return stats_by_workload

    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict:
        """Retourne un résumé quotidien."""
        if date is None:
            date = datetime.now()

        date_key = date.date()
        date_suffix = f"_{date_key}"
        summary = {}

        for key, totals in self._daily_totals.items():
            if key.endswith(date_suffix):
                challenge_type = key[: -len(date_suffix)]
                summary[challenge_type] = totals

        return summary

    def _prune_metric_key_records(self, metric_key: str) -> None:
        """Purge TTL + cap par clé pour borner la mémoire process (IA12)."""
        lst = self._usage_history.get(metric_key)
        if not lst:
            return
        cutoff = datetime.now() - timedelta(
            days=_ai_workload_keys.RUNTIME_AI_METRICS_RETENTION_DAYS
        )
        kept = [r for r in lst if r["timestamp"] > cutoff]
        max_n = _ai_workload_keys.RUNTIME_AI_METRICS_MAX_EVENTS_PER_KEY
        if len(kept) > max_n:
            kept = kept[-max_n:]
        self._usage_history[metric_key] = kept
        if not kept:
            del self._usage_history[metric_key]

    def _prune_stale_daily_totals(self) -> None:
        """Supprime les agrégats journaliers plus vieux que la rétention."""
        cutoff = date.today() - timedelta(
            days=_ai_workload_keys.RUNTIME_AI_METRICS_RETENTION_DAYS
        )
        to_del = []
        for key in list(self._daily_totals.keys()):
            if len(key) < 11:
                continue
            suffix = key[-10:]
            if suffix[4] != "-" or suffix[7] != "-":
                continue
            try:
                d = date.fromisoformat(suffix)
            except ValueError:
                continue
            if d < cutoff:
                to_del.append(key)
        for k in to_del:
            del self._daily_totals[k]


# Instance globale du tracker
token_tracker = TokenTracker()
