"""
Module de tracking de l'utilisation des tokens OpenAI.
Permet de monitorer les coûts et l'utilisation de l'API.
"""
from datetime import datetime
from typing import Dict, Optional
from loguru import logger
from collections import defaultdict
import json


class TokenTracker:
    """Tracker simple en mémoire pour l'utilisation des tokens (peut être migré vers DB)."""
    
    def __init__(self):
        # Structure: {challenge_type: [{"timestamp": datetime, "tokens": int, "cost": float}]}
        self._usage_history: Dict[str, list] = defaultdict(list)
        self._daily_totals: Dict[str, Dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0})
    
    def track_usage(
        self,
        challenge_type: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "gpt-4o-mini"
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
        
        # Coûts par modèle (USD par 1K tokens) - Mise à jour janvier 2025
        # Source: https://openai.com/pricing
        cost_per_1k_tokens = {
            "gpt-4o-mini": {
                "input": 0.15 / 1000,   # $0.15 per 1M tokens = $0.00015 per 1K
                "output": 0.60 / 1000,  # $0.60 per 1M tokens = $0.0006 per 1K
            },
            "gpt-4o": {
                "input": 2.50 / 1000,   # $2.50 per 1M tokens = $0.0025 per 1K
                "output": 10.00 / 1000, # $10.00 per 1M tokens = $0.01 per 1K
            },
            "gpt-4-turbo": {
                "input": 10.00 / 1000,  # $10.00 per 1M tokens
                "output": 30.00 / 1000, # $30.00 per 1M tokens
            },
        }
        
        # Calculer le coût
        model_costs = cost_per_1k_tokens.get(model, cost_per_1k_tokens["gpt-4o-mini"])
        cost = (prompt_tokens / 1000 * model_costs["input"]) + (completion_tokens / 1000 * model_costs["output"])
        
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
                r for r in self._usage_history[challenge_type]
                if r["timestamp"] > cutoff_date
            ]
        else:
            # Tous les types
            records = []
            for type_records in self._usage_history.values():
                records.extend([
                    r for r in type_records
                    if r["timestamp"] > cutoff_date
                ])
        
        if not records:
            return {
                "total_tokens": 0,
                "total_cost": 0.0,
                "average_tokens": 0,
                "count": 0,
            }
        
        total_tokens = sum(r["total_tokens"] for r in records)
        total_cost = sum(r["cost"] for r in records)
        average_tokens = total_tokens / len(records)
        
        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "average_tokens": average_tokens,
            "count": len(records),
            "by_type": self._get_stats_by_type(cutoff_date) if not challenge_type else {},
        }
    
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
                    "average_tokens": sum(r["total_tokens"] for r in filtered) / len(filtered),
                }
        
        return stats_by_type
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict:
        """Retourne un résumé quotidien."""
        if date is None:
            date = datetime.now()
        
        date_key = date.date()
        summary = {}
        
        for key, totals in self._daily_totals.items():
            if str(date_key) in key:
                challenge_type = key.split("_")[0]
                summary[challenge_type] = totals
        
        return summary


# Instance globale du tracker
token_tracker = TokenTracker()

