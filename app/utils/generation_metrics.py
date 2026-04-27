"""
Runtime metrics for AI-assisted generation workloads.

The historical parameter name `challenge_type` is retained for backward compatibility,
but now stores a generic AI metric key for challenges, exercises, and assistant chat.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.logging_config import get_logger
from app.utils import ai_workload_keys as _ai_workload_keys
from app.utils.ai_workload_keys import (
    classify_ai_workload_key,
    runtime_ai_metrics_retention_meta,
)

logger = get_logger(__name__)


class GenerationMetrics:
    """In-memory runtime metrics tracker for AI workloads."""

    def __init__(self):
        # Structure: {metric_key: [{timestamp, success, validation_passed, auto_corrected, duration, error_type}]}
        self._generation_history: Dict[str, List] = defaultdict(list)
        self._validation_failures: Dict[str, int] = defaultdict(int)
        self._auto_corrections: Dict[str, int] = defaultdict(int)
        self._success_count: Dict[str, int] = defaultdict(int)
        self._failure_count: Dict[str, int] = defaultdict(int)
        self._chess_repair_events: List[Dict] = (
            []
        )  # {timestamp: datetime, succeeded: bool}

    def record_chess_repair(self, succeeded: bool) -> None:
        """Enregistre une tentative de réparation IA chess (tentative et résultat)."""
        self._chess_repair_events.append(
            {"timestamp": datetime.now(), "succeeded": succeeded}
        )
        cutoff = datetime.now() - timedelta(
            days=_ai_workload_keys.RUNTIME_AI_METRICS_RETENTION_DAYS
        )
        self._chess_repair_events = [
            e for e in self._chess_repair_events if e["timestamp"] > cutoff
        ]

    def record_generation(
        self,
        challenge_type: str,
        success: bool,
        validation_passed: bool = True,
        auto_corrected: bool = False,
        duration_seconds: float = 0.0,
        error_type: Optional[str] = None,
        generation_status: Optional[str] = None,
        error_codes: Optional[List[str]] = None,
        fallback_trigger_reason: Optional[str] = None,
    ):
        """Record one generation attempt in runtime metrics.

        ``generation_status`` (défis) : statut d'orchestration une fois le pipeline
        validation / réparation résolu. Optionnel pour rétrocompatibilité (exercices, chat).
        ``error_codes`` : codes de validation stables (défis) ; optionnel ailleurs.
        ``fallback_trigger_reason`` : cause du déclenchement fallback o-series (défis).
        """
        record: Dict[str, Any] = {
            "timestamp": datetime.now(),
            "success": success,
            "validation_passed": validation_passed,
            "auto_corrected": auto_corrected,
            "duration": duration_seconds,
            "error_type": error_type,
            "generation_status": generation_status,
        }
        if error_codes is not None:
            record["error_codes"] = list(error_codes)
        if fallback_trigger_reason is not None:
            record["fallback_trigger_reason"] = fallback_trigger_reason

        self._generation_history[challenge_type].append(record)
        self._prune_metric_key_records(challenge_type)

        logger.debug(
            "Metrics recorded - "
            "Type: {}, Success: {}, Validation: {}, "
            "Auto-corrected: {}, Duration: {:.2f}s",
            challenge_type,
            success,
            validation_passed,
            auto_corrected,
            duration_seconds,
        )

    def _records_in_window(
        self,
        challenge_type: Optional[str],
        days: int,
        *,
        success_only: bool = False,
    ) -> List[Dict]:
        cutoff_date = datetime.now() - timedelta(days=days)

        if challenge_type:
            records = [
                r
                for r in self._generation_history[challenge_type]
                if r["timestamp"] > cutoff_date
            ]
        else:
            records = []
            for type_records in self._generation_history.values():
                records.extend(
                    [r for r in type_records if r["timestamp"] > cutoff_date]
                )

        if success_only:
            return [r for r in records if r["success"]]
        return records

    def get_success_rate(
        self, challenge_type: Optional[str] = None, days: int = 1
    ) -> float:
        records = self._records_in_window(challenge_type, days)
        if not records:
            return 0.0
        success_count = sum(1 for r in records if r["success"])
        return success_count / len(records) * 100

    def get_validation_failure_rate(
        self, challenge_type: Optional[str] = None, days: int = 1
    ) -> float:
        records = self._records_in_window(challenge_type, days)
        if not records:
            return 0.0
        failure_count = sum(1 for r in records if not r["validation_passed"])
        return failure_count / len(records) * 100

    def get_auto_correction_rate(
        self, challenge_type: Optional[str] = None, days: int = 1
    ) -> float:
        records = self._records_in_window(challenge_type, days)
        if not records:
            return 0.0
        corrected_count = sum(1 for r in records if r["auto_corrected"])
        return corrected_count / len(records) * 100

    def get_average_duration(
        self, challenge_type: Optional[str] = None, days: int = 1
    ) -> float:
        records = self._records_in_window(challenge_type, days, success_only=True)
        if not records:
            return 0.0
        total_duration = sum(r["duration"] for r in records)
        return total_duration / len(records)

    def _get_latency_percentiles(
        self, challenge_type: Optional[str] = None, days: int = 1
    ) -> Dict[str, float]:
        """P50 et P95 de latence en ms sur les générations réussies de la fenêtre."""
        records = self._records_in_window(challenge_type, days, success_only=True)
        durations_ms = sorted(r["duration"] * 1000 for r in records)
        if not durations_ms:
            return {"p50_ms": 0.0, "p95_ms": 0.0}

        def _percentile(data: list, p: float) -> float:
            k = (len(data) - 1) * p / 100
            lo, hi = int(k), min(int(k) + 1, len(data) - 1)
            return data[lo] + (data[hi] - data[lo]) * (k - lo)

        return {
            "p50_ms": round(_percentile(durations_ms, 50), 1),
            "p95_ms": round(_percentile(durations_ms, 95), 1),
        }

    def get_summary(self, days: int = 1) -> Dict:
        """Return full runtime summary for admin read-only."""
        return {
            "success_rate": self.get_success_rate(days=days),
            "validation_failure_rate": self.get_validation_failure_rate(days=days),
            "auto_correction_rate": self.get_auto_correction_rate(days=days),
            "average_duration": self.get_average_duration(days=days),
            "latency": self._get_latency_percentiles(days=days),
            "chess_repair": self._get_chess_repair_stats(days),
            "fallback_stats": self._get_fallback_stats(days),
            "repair_success_rate": self._get_repair_success_rate(days),
            "error_code_counts": self._get_error_code_counts(days, challenge_type=None),
            "generation_status_counts": self._get_generation_status_counts(
                days, challenge_type=None
            ),
            "by_type": self._get_summary_by_type(days),
            "by_workload": self._get_summary_by_workload(days),
            "error_types": self._get_error_type_counts(days),
            "retention": runtime_ai_metrics_retention_meta(),
            "metrics_disclaimer_fr": (
                "Métriques runtime opportunistes (mémoire process) : pas d'historique long terme ; "
                "pour comparer des runs figés, utiliser les exécutions harness persistées."
            ),
        }

    def _get_summary_by_type(self, days: int) -> Dict[str, Dict]:
        """Return runtime metrics grouped by fine-grained metric key."""
        summary_by_type = {}

        for metric_key in self._generation_history.keys():
            summary_by_type[metric_key] = {
                "success_rate": self.get_success_rate(metric_key, days),
                "validation_failure_rate": self.get_validation_failure_rate(
                    metric_key, days
                ),
                "auto_correction_rate": self.get_auto_correction_rate(metric_key, days),
                "average_duration": self.get_average_duration(metric_key, days),
                "latency": self._get_latency_percentiles(metric_key, days),
                "total_generations": len(self._records_in_window(metric_key, days)),
                "error_code_counts": self._get_error_code_counts(
                    days, challenge_type=metric_key
                ),
                "generation_status_counts": self._get_generation_status_counts(
                    days, challenge_type=metric_key
                ),
            }

        return summary_by_type

    def _get_summary_by_workload(self, days: int) -> Dict[str, Dict]:
        """Return runtime metrics grouped by stable workload."""
        cutoff = datetime.now() - timedelta(days=days)
        summary_by_workload: Dict[str, Dict] = {}

        for metric_key, records in self._generation_history.items():
            workload = classify_ai_workload_key(metric_key)

            filtered = [r for r in records if r["timestamp"] > cutoff]
            if not filtered:
                continue

            bucket = summary_by_workload.setdefault(
                workload,
                {
                    "success_count": 0,
                    "validation_failures": 0,
                    "auto_corrections": 0,
                    "total_duration": 0.0,
                    "duration_count": 0,
                    "total_generations": 0,
                },
            )
            bucket["total_generations"] += len(filtered)
            bucket["success_count"] += sum(1 for r in filtered if r["success"])
            bucket["validation_failures"] += sum(
                1 for r in filtered if not r["validation_passed"]
            )
            bucket["auto_corrections"] += sum(
                1 for r in filtered if r["auto_corrected"]
            )

            success_records = [r for r in filtered if r["success"]]
            bucket["total_duration"] += sum(r["duration"] for r in success_records)
            bucket["duration_count"] += len(success_records)

        final_summary: Dict[str, Dict] = {}
        for workload, bucket in summary_by_workload.items():
            total = bucket["total_generations"]
            duration_count = bucket["duration_count"]
            final_summary[workload] = {
                "success_rate": (
                    (bucket["success_count"] / total * 100) if total else 0.0
                ),
                "validation_failure_rate": (
                    (bucket["validation_failures"] / total * 100) if total else 0.0
                ),
                "auto_correction_rate": (
                    (bucket["auto_corrections"] / total * 100) if total else 0.0
                ),
                "average_duration": (
                    bucket["total_duration"] / duration_count if duration_count else 0.0
                ),
                "total_generations": total,
            }

        return final_summary

    def _get_generation_status_counts(
        self, days: int, challenge_type: Optional[str] = None
    ) -> Dict[str, int]:
        """Décompte des statuts d'orchestration défis (champ optionnel sur les enregistrements)."""
        records = self._records_in_window(challenge_type, days)
        counts: Dict[str, int] = {}
        for record in records:
            status = record.get("generation_status")
            if not status:
                continue
            counts[status] = counts.get(status, 0) + 1
        return counts

    def _get_error_type_counts(self, days: int) -> Dict[str, int]:
        """Return runtime errors grouped by error_type."""
        cutoff = datetime.now() - timedelta(days=days)
        counts: Dict[str, int] = {}

        for records in self._generation_history.values():
            for record in records:
                if record["timestamp"] <= cutoff:
                    continue
                error_type = record.get("error_type")
                if not error_type:
                    continue
                counts[error_type] = counts.get(error_type, 0) + 1

        return counts

    def _get_error_code_counts(
        self, days: int, challenge_type: Optional[str] = None
    ) -> Dict[str, int]:
        """Décompte des codes d'erreur de validation (champ optionnel)."""
        records = self._records_in_window(challenge_type, days)
        counts: Dict[str, int] = {}
        for record in records:
            codes = record.get("error_codes")
            if not codes:
                continue
            for code in codes:
                counts[code] = counts.get(code, 0) + 1
        return counts

    def _get_chess_repair_stats(self, days: int) -> Dict[str, int]:
        """Compteurs de tentatives/succès/échecs du repair IA chess."""
        cutoff = datetime.now() - timedelta(days=days)
        events = [e for e in self._chess_repair_events if e["timestamp"] > cutoff]
        attempted = len(events)
        succeeded = sum(1 for e in events if e["succeeded"])
        return {
            "chess_repair_attempted": attempted,
            "chess_repair_succeeded": succeeded,
            "chess_repair_failed": attempted - succeeded,
        }

    def _get_fallback_stats(
        self, days: int, challenge_type: Optional[str] = None
    ) -> Dict:
        """Taux et causes des déclenchements fallback o-series."""
        records = self._records_in_window(challenge_type, days)
        total = len(records)
        fallback_records = [r for r in records if r.get("fallback_trigger_reason")]
        fallback_count = len(fallback_records)
        causes: Dict[str, int] = {}
        for r in fallback_records:
            cause = r["fallback_trigger_reason"]
            causes[cause] = causes.get(cause, 0) + 1
        return {
            "fallback_rate": round((fallback_count / total * 100), 2) if total else 0.0,
            "fallback_count": fallback_count,
            "fallback_causes": causes,
        }

    def _get_repair_success_rate(
        self, days: int, challenge_type: Optional[str] = None
    ) -> float:
        """% de défis réparés qui ont nécessité le repair IA chess (repaired_by_ai / total repaired)."""
        records = self._records_in_window(challenge_type, days)
        total_repaired = sum(
            1
            for r in records
            if r.get("generation_status") in ("repaired", "repaired_by_ai")
        )
        repaired_by_ai = sum(
            1 for r in records if r.get("generation_status") == "repaired_by_ai"
        )
        if total_repaired == 0:
            return 0.0
        return round(repaired_by_ai / total_repaired * 100, 1)

    def _prune_metric_key_records(self, metric_key: str) -> None:
        """Purge TTL + cap par clé (aligné token_tracker, IA12)."""
        lst = self._generation_history.get(metric_key)
        if not lst:
            return
        cutoff = datetime.now() - timedelta(
            days=_ai_workload_keys.RUNTIME_AI_METRICS_RETENTION_DAYS
        )
        kept = [r for r in lst if r["timestamp"] > cutoff]
        max_n = _ai_workload_keys.RUNTIME_AI_METRICS_MAX_EVENTS_PER_KEY
        if len(kept) > max_n:
            kept = kept[-max_n:]
        self._generation_history[metric_key] = kept
        if not kept:
            del self._generation_history[metric_key]


# Instance globale des métriques

generation_metrics = GenerationMetrics()
