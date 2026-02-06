#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Performance Index Base de Données
======================================
Mesure l'impact réel des nouveaux index ajoutés le 06/02/2026

Index testés:
- exercises: 8 index (type, difficulty, creator_id, is_active, created_at + composites)
- users: 2 index (is_active, created_at)

Usage:
    python scripts/test_performance_indexes.py
    python scripts/test_performance_indexes.py --iterations 20
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Fix encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func, text
from app.db.base import SessionLocal
from app.models.exercise import Exercise
from app.models.user import User
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeAttempt


def benchmark_query(name: str, query_func, db, iterations: int = 10):
    """Mesure temps d'exécution moyen d'une requête"""
    times = []
    
    for i in range(iterations):
        start = time.perf_counter()
        result = query_func(db)
        # Force l'exécution (éviter lazy loading)
        if hasattr(result, '__iter__'):
            list(result)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # en ms
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    return {
        'name': name,
        'avg': avg_time,
        'min': min_time,
        'max': max_time,
        'iterations': iterations
    }


def run_tests(iterations: int = 10):
    """Exécute tous les tests de performance"""
    
    print("=" * 60)
    print("🚀 TEST PERFORMANCE INDEX BASE DE DONNÉES")
    print("=" * 60)
    print(f"Iterations par test: {iterations}")
    print()
    
    db = SessionLocal()
    results = []
    
    try:
        # ============================================================
        # TESTS TABLE EXERCISES (8 index ajoutés)
        # ============================================================
        print("📊 TABLE: exercises")
        print("-" * 40)
        
        # Test 1: Filtrage par type (index ix_exercises_exercise_type)
        def test_type(db):
            return db.execute(
                select(Exercise)
                .where(Exercise.exercise_type == 'ADDITION')
                .limit(100)
            ).scalars().all()
        
        results.append(benchmark_query(
            "1. Filtrage par type (ADDITION)",
            test_type, db, iterations
        ))
        
        # Test 2: Filtrage par difficulté (index ix_exercises_difficulty)
        def test_difficulty(db):
            return db.execute(
                select(Exercise)
                .where(Exercise.difficulty == 'PADAWAN')
                .limit(100)
            ).scalars().all()
        
        results.append(benchmark_query(
            "2. Filtrage par difficulté (PADAWAN)",
            test_difficulty, db, iterations
        ))
        
        # Test 3: Filtrage type + difficulté (index composite ix_exercises_type_difficulty)
        def test_type_difficulty(db):
            return db.execute(
                select(Exercise)
                .where(Exercise.exercise_type == 'MULTIPLICATION')
                .where(Exercise.difficulty == 'CHEVALIER')
                .limit(100)
            ).scalars().all()
        
        results.append(benchmark_query(
            "3. Type + Difficulté (composite)",
            test_type_difficulty, db, iterations
        ))
        
        # Test 4: Exercices actifs (index ix_exercises_is_active)
        def test_is_active(db):
            return db.execute(
                select(Exercise)
                .where(Exercise.is_active == True)
                .limit(100)
            ).scalars().all()
        
        results.append(benchmark_query(
            "4. Exercices actifs",
            test_is_active, db, iterations
        ))
        
        # Test 5: Tri chronologique (index ix_exercises_created_at)
        def test_created_at(db):
            return db.execute(
                select(Exercise)
                .order_by(Exercise.created_at.desc())
                .limit(50)
            ).scalars().all()
        
        results.append(benchmark_query(
            "5. Tri chronologique (récents)",
            test_created_at, db, iterations
        ))
        
        # Test 6: Actifs + type (index composite ix_exercises_active_type)
        def test_active_type(db):
            return db.execute(
                select(Exercise)
                .where(Exercise.is_active == True)
                .where(Exercise.exercise_type == 'SOUSTRACTION')
                .limit(100)
            ).scalars().all()
        
        results.append(benchmark_query(
            "6. Actifs + Type (composite)",
            test_active_type, db, iterations
        ))
        
        # Test 7: Créateur + actifs (index composite ix_exercises_creator_active)
        def test_creator_active(db):
            return db.execute(
                select(Exercise)
                .where(Exercise.creator_id == 1)
                .where(Exercise.is_active == True)
                .limit(50)
            ).scalars().all()
        
        results.append(benchmark_query(
            "7. Créateur + Actifs (composite)",
            test_creator_active, db, iterations
        ))
        
        print()
        
        # ============================================================
        # TESTS TABLE USERS (2 index ajoutés)
        # ============================================================
        print("👤 TABLE: users")
        print("-" * 40)
        
        # Test 8: Utilisateurs actifs (index ix_users_is_active)
        def test_users_active(db):
            return db.execute(
                select(User)
                .where(User.is_active == True)
                .limit(50)
            ).scalars().all()
        
        results.append(benchmark_query(
            "8. Utilisateurs actifs",
            test_users_active, db, iterations
        ))
        
        # Test 9: Tri chronologique utilisateurs (index ix_users_created_at)
        def test_users_recent(db):
            return db.execute(
                select(User)
                .order_by(User.created_at.desc())
                .limit(20)
            ).scalars().all()
        
        results.append(benchmark_query(
            "9. Utilisateurs récents",
            test_users_recent, db, iterations
        ))
        
        print()
        
        # ============================================================
        # TESTS TABLES DÉJÀ BIEN INDEXÉES (baseline)
        # ============================================================
        print("🎯 TABLES DÉJÀ INDEXÉES (baseline)")
        print("-" * 40)
        
        # Test 10: Logic challenges par type (index existant)
        def test_challenges_type(db):
            return db.execute(
                select(LogicChallenge)
                .where(LogicChallenge.challenge_type == 'sequence')
                .limit(50)
            ).scalars().all()
        
        results.append(benchmark_query(
            "10. Challenges par type",
            test_challenges_type, db, iterations
        ))
        
        # Test 11: Attempts user (index composite existant)
        def test_attempts_user(db):
            return db.execute(
                select(Attempt)
                .where(Attempt.user_id == 1)
                .where(Attempt.is_correct == True)
                .limit(100)
            ).scalars().all()
        
        results.append(benchmark_query(
            "11. Tentatives user (correct)",
            test_attempts_user, db, iterations
        ))
        
        print()
        
        # ============================================================
        # AFFICHAGE RÉSULTATS
        # ============================================================
        print("=" * 60)
        print("📈 RÉSULTATS")
        print("=" * 60)
        print()
        print(f"{'Test':<40} {'Avg (ms)':<12} {'Min':<10} {'Max':<10}")
        print("-" * 72)
        
        for r in results:
            print(f"{r['name']:<40} {r['avg']:>8.2f} ms {r['min']:>8.2f} {r['max']:>8.2f}")
        
        print()
        print("=" * 60)
        print("📊 ANALYSE")
        print("=" * 60)
        
        # Moyennes par catégorie
        exercises_results = results[:7]
        users_results = results[7:9]
        baseline_results = results[9:]
        
        avg_exercises = sum(r['avg'] for r in exercises_results) / len(exercises_results)
        avg_users = sum(r['avg'] for r in users_results) / len(users_results)
        avg_baseline = sum(r['avg'] for r in baseline_results) / len(baseline_results)
        
        print(f"\n🎯 Moyennes par catégorie:")
        print(f"  • Exercises (nouveaux index):  {avg_exercises:.2f} ms")
        print(f"  • Users (nouveaux index):      {avg_users:.2f} ms")
        print(f"  • Baseline (index existants):  {avg_baseline:.2f} ms")
        
        # Évaluation
        print(f"\n✅ Évaluation:")
        if avg_exercises < 50:
            print(f"  • Exercises: EXCELLENT (<50ms)")
        elif avg_exercises < 100:
            print(f"  • Exercises: BON (<100ms)")
        elif avg_exercises < 200:
            print(f"  • Exercises: ACCEPTABLE (<200ms)")
        else:
            print(f"  • Exercises: À OPTIMISER (>{avg_exercises:.0f}ms)")
        
        if avg_users < 30:
            print(f"  • Users: EXCELLENT (<30ms)")
        elif avg_users < 50:
            print(f"  • Users: BON (<50ms)")
        else:
            print(f"  • Users: À SURVEILLER (>{avg_users:.0f}ms)")
        
        print()
        print("=" * 60)
        print("💡 INTERPRÉTATION")
        print("=" * 60)
        print("""
Les nouveaux index (06/02/2026) optimisent:
- Table exercises: 8 index (simples + composites)
- Table users: 2 index (is_active, created_at)

Objectif attendu: -30-50% vs requêtes sans index
        
Si temps > 100ms sur exercices: vérifier avec EXPLAIN ANALYZE
Si temps comparable au baseline: index bien utilisés ✅
""")
        
        # Comptage enregistrements (contexte)
        print("📋 Contexte (nombre d'enregistrements):")
        count_exercises = db.execute(select(func.count(Exercise.id))).scalar()
        count_users = db.execute(select(func.count(User.id))).scalar()
        count_challenges = db.execute(select(func.count(LogicChallenge.id))).scalar()
        count_attempts = db.execute(select(func.count(Attempt.id))).scalar()
        
        print(f"  • Exercises: {count_exercises}")
        print(f"  • Users: {count_users}")
        print(f"  • Challenges: {count_challenges}")
        print(f"  • Attempts: {count_attempts}")
        print()
        
        return results
        
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='Test performance index DB')
    parser.add_argument('--iterations', '-i', type=int, default=10,
                        help='Nombre d\'itérations par test (défaut: 10)')
    args = parser.parse_args()
    
    run_tests(iterations=args.iterations)


if __name__ == "__main__":
    main()
