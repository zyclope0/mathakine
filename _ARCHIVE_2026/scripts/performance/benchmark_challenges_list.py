#!/usr/bin/env python3
"""
Benchmark pour comparer les performances de get_challenges_list.
Utilisé pour valider l'optimisation PERF-3.2.
"""

import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.db.base import SessionLocal
from app.models.logic_challenge import LogicChallenge
from sqlalchemy import func
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def benchmark_old_method(db):
    """Ancienne méthode : 2 requêtes"""
    start = time.time()
    
    # Requête 1 : Liste
    challenges = db.query(LogicChallenge).filter(LogicChallenge.is_active == True).limit(20).all()
    
    # Requête 2 : Count
    total = db.query(LogicChallenge).filter(LogicChallenge.is_active == True).count()
    
    elapsed = time.time() - start
    return elapsed, len(challenges), total

def benchmark_new_method(db):
    """Nouvelle méthode : 1 requête avec COUNT OVER"""
    start = time.time()
    
    # Une seule requête avec COUNT(*) OVER()
    query = db.query(
        LogicChallenge,
        func.count().over().label('total')
    ).filter(LogicChallenge.is_active == True).limit(20)
    
    results = query.all()
    challenges = [challenge for challenge, _ in results]
    total = results[0][1] if results else 0
    
    elapsed = time.time() - start
    return elapsed, len(challenges), total

def main():
    """Point d'entrée principal"""
    print("=" * 80)
    print("⚡ BENCHMARK: get_challenges_list")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        # Warmup
        db.query(LogicChallenge).first()
        
        # Benchmark ancienne méthode
        print("🔄 Test ancienne méthode (2 requêtes)...")
        old_times = []
        for _ in range(10):
            elapsed, _, _ = benchmark_old_method(db)
            old_times.append(elapsed)
        old_avg = sum(old_times) / len(old_times)
        old_min = min(old_times)
        old_max = max(old_times)
        
        # Benchmark nouvelle méthode
        print("🔄 Test nouvelle méthode (1 requête avec COUNT OVER)...")
        new_times = []
        for _ in range(10):
            elapsed, _, _ = benchmark_new_method(db)
            new_times.append(elapsed)
        new_avg = sum(new_times) / len(new_times)
        new_min = min(new_times)
        new_max = max(new_times)
        
        # Résultats
        print()
        print("=" * 80)
        print("📊 RÉSULTATS")
        print("=" * 80)
        print(f"Ancienne méthode (2 requêtes):")
        print(f"  Moyenne: {old_avg*1000:.2f}ms")
        print(f"  Min: {old_min*1000:.2f}ms")
        print(f"  Max: {old_max*1000:.2f}ms")
        print()
        print(f"Nouvelle méthode (1 requête):")
        print(f"  Moyenne: {new_avg*1000:.2f}ms")
        print(f"  Min: {new_min*1000:.2f}ms")
        print(f"  Max: {new_max*1000:.2f}ms")
        print()
        
        improvement = ((old_avg - new_avg) / old_avg) * 100
        print(f"💡 Amélioration: {improvement:.1f}%")
        
        if improvement > 0:
            print("✅ La nouvelle méthode est plus rapide")
        else:
            print("⚠️  La nouvelle méthode n'est pas plus rapide (vérifier l'implémentation)")
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())

