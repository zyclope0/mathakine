"""
Module de rate limiting pour la génération IA.
Limite le nombre de générations par utilisateur et par période.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter simple en mémoire (peut être migré vers Redis pour production)."""
    
    def __init__(self):
        # Structure: {user_id: [timestamps]}
        self._user_generation_counts: Dict[int, List[datetime]] = defaultdict(list)
        self._cleanup_interval = timedelta(hours=1)
        self._last_cleanup = datetime.now()
    
    def check_rate_limit(
        self, 
        user_id: int, 
        max_per_hour: int = 10,
        max_per_day: int = 50
    ) -> tuple[bool, Optional[str]]:
        """
        Vérifie si l'utilisateur peut générer un challenge.
        
        Args:
            user_id: ID de l'utilisateur
            max_per_hour: Nombre maximum de générations par heure
            max_per_day: Nombre maximum de générations par jour
            
        Returns:
            Tuple (allowed, reason) où reason est None si autorisé
        """
        now = datetime.now()
        
        # Nettoyage périodique (toutes les heures)
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries()
            self._last_cleanup = now
        
        # Récupérer les timestamps de l'utilisateur
        user_timestamps = self._user_generation_counts[user_id]
        
        # Filtrer les timestamps récents (dernière heure)
        hour_ago = now - timedelta(hours=1)
        recent_timestamps = [ts for ts in user_timestamps if ts > hour_ago]
        
        # Vérifier limite horaire
        if len(recent_timestamps) >= max_per_hour:
            return False, f"Limite horaire atteinte ({max_per_hour} générations/heure)"
        
        # Filtrer les timestamps récents (dernières 24h)
        day_ago = now - timedelta(days=1)
        daily_timestamps = [ts for ts in user_timestamps if ts > day_ago]
        
        # Vérifier limite journalière
        if len(daily_timestamps) >= max_per_day:
            return False, f"Limite journalière atteinte ({max_per_day} générations/jour)"
        
        # Autoriser et enregistrer la génération
        # Stocker la liste filtrée à 24h (pas hourly) pour conserver la limite journalière
        daily_timestamps.append(now)
        self._user_generation_counts[user_id] = daily_timestamps
        
        return True, None
    
    def _cleanup_old_entries(self):
        """Nettoie les entrées de plus de 24h."""
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        
        for user_id in list(self._user_generation_counts.keys()):
            timestamps = self._user_generation_counts[user_id]
            filtered = [ts for ts in timestamps if ts > day_ago]
            
            if filtered:
                self._user_generation_counts[user_id] = filtered
            else:
                # Supprimer la clé si vide
                del self._user_generation_counts[user_id]
        
        logger.debug(f"Nettoyage rate limiter: {len(self._user_generation_counts)} utilisateurs actifs")
    
    def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """Retourne les statistiques de génération d'un utilisateur."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        timestamps = self._user_generation_counts.get(user_id, [])
        
        return {
            "last_hour": len([ts for ts in timestamps if ts > hour_ago]),
            "last_day": len([ts for ts in timestamps if ts > day_ago]),
            "total": len(timestamps),
        }


# Instance globale du rate limiter
rate_limiter = RateLimiter()

