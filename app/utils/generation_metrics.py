"""
Module de métriques pour la génération IA.
Track la qualité, performance et fiabilité des générations.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class GenerationMetrics:
    """Tracker de métriques pour la génération IA."""
    
    def __init__(self):
        # Structure: {challenge_type: [{"timestamp": datetime, "success": bool, "validation_passed": bool, "auto_corrected": bool, "duration": float}]}
        self._generation_history: Dict[str, List] = defaultdict(list)
        self._validation_failures: Dict[str, int] = defaultdict(int)
        self._auto_corrections: Dict[str, int] = defaultdict(int)
        self._success_count: Dict[str, int] = defaultdict(int)
        self._failure_count: Dict[str, int] = defaultdict(int)
    
    def record_generation(
        self,
        challenge_type: str,
        success: bool,
        validation_passed: bool = True,
        auto_corrected: bool = False,
        duration_seconds: float = 0.0,
        error_type: Optional[str] = None
    ):
        """
        Enregistre une génération dans les métriques.
        
        Args:
            challenge_type: Type de challenge
            success: Si la génération a réussi
            validation_passed: Si la validation a passé
            auto_corrected: Si une auto-correction a été appliquée
            duration_seconds: Durée de la génération en secondes
            error_type: Type d'erreur si échec
        """
        record = {
            "timestamp": datetime.now(),
            "success": success,
            "validation_passed": validation_passed,
            "auto_corrected": auto_corrected,
            "duration": duration_seconds,
            "error_type": error_type,
        }
        
        self._generation_history[challenge_type].append(record)
        
        if success:
            self._success_count[challenge_type] += 1
        else:
            self._failure_count[challenge_type] += 1
        
        if not validation_passed:
            self._validation_failures[challenge_type] += 1
        
        if auto_corrected:
            self._auto_corrections[challenge_type] += 1
        
        logger.debug(
            f"Metrics recorded - Type: {challenge_type}, "
            f"Success: {success}, Validation: {validation_passed}, "
            f"Auto-corrected: {auto_corrected}, Duration: {duration_seconds:.2f}s"
        )
    
    def get_success_rate(self, challenge_type: Optional[str] = None, days: int = 1) -> float:
        """Calcule le taux de succès."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if challenge_type:
            records = [
                r for r in self._generation_history[challenge_type]
                if r["timestamp"] > cutoff_date
            ]
        else:
            records = []
            for type_records in self._generation_history.values():
                records.extend([
                    r for r in type_records
                    if r["timestamp"] > cutoff_date
                ])
        
        if not records:
            return 0.0
        
        success_count = sum(1 for r in records if r["success"])
        return success_count / len(records) * 100
    
    def get_validation_failure_rate(self, challenge_type: Optional[str] = None, days: int = 1) -> float:
        """Calcule le taux d'échec de validation."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if challenge_type:
            records = [
                r for r in self._generation_history[challenge_type]
                if r["timestamp"] > cutoff_date
            ]
        else:
            records = []
            for type_records in self._generation_history.values():
                records.extend([
                    r for r in type_records
                    if r["timestamp"] > cutoff_date
                ])
        
        if not records:
            return 0.0
        
        failure_count = sum(1 for r in records if not r["validation_passed"])
        return failure_count / len(records) * 100
    
    def get_auto_correction_rate(self, challenge_type: Optional[str] = None, days: int = 1) -> float:
        """Calcule le taux d'auto-correction."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if challenge_type:
            records = [
                r for r in self._generation_history[challenge_type]
                if r["timestamp"] > cutoff_date
            ]
        else:
            records = []
            for type_records in self._generation_history.values():
                records.extend([
                    r for r in type_records
                    if r["timestamp"] > cutoff_date
                ])
        
        if not records:
            return 0.0
        
        corrected_count = sum(1 for r in records if r["auto_corrected"])
        return corrected_count / len(records) * 100
    
    def get_average_duration(self, challenge_type: Optional[str] = None, days: int = 1) -> float:
        """Calcule la durée moyenne de génération."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if challenge_type:
            records = [
                r for r in self._generation_history[challenge_type]
                if r["timestamp"] > cutoff_date and r["success"]
            ]
        else:
            records = []
            for type_records in self._generation_history.values():
                records.extend([
                    r for r in type_records
                    if r["timestamp"] > cutoff_date and r["success"]
                ])
        
        if not records:
            return 0.0
        
        total_duration = sum(r["duration"] for r in records)
        return total_duration / len(records)
    
    def get_summary(self, days: int = 1) -> Dict:
        """Retourne un résumé complet des métriques."""
        return {
            "success_rate": self.get_success_rate(days=days),
            "validation_failure_rate": self.get_validation_failure_rate(days=days),
            "auto_correction_rate": self.get_auto_correction_rate(days=days),
            "average_duration": self.get_average_duration(days=days),
            "by_type": self._get_summary_by_type(days),
        }
    
    def _get_summary_by_type(self, days: int) -> Dict[str, Dict]:
        """Retourne les métriques groupées par type."""
        summary_by_type = {}
        
        for challenge_type in self._generation_history.keys():
            summary_by_type[challenge_type] = {
                "success_rate": self.get_success_rate(challenge_type, days),
                "validation_failure_rate": self.get_validation_failure_rate(challenge_type, days),
                "auto_correction_rate": self.get_auto_correction_rate(challenge_type, days),
                "average_duration": self.get_average_duration(challenge_type, days),
                "total_generations": len([
                    r for r in self._generation_history[challenge_type]
                    if r["timestamp"] > datetime.now() - timedelta(days=days)
                ]),
            }
        
        return summary_by_type


# Instance globale des métriques
generation_metrics = GenerationMetrics()

