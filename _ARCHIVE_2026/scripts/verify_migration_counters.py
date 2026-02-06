#!/usr/bin/env python3
"""
Script pour vérifier minutieusement les résultats de la migration add_challenge_counters.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.base import SessionLocal
from app.models.logic_challenge import LogicChallenge
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def verify_migration():
    """Vérifie minutieusement les résultats de la migration."""
    db = SessionLocal()
    
    print("=" * 80)
    print("🔍 VÉRIFICATION MIGRATION - Compteurs Challenges")
    print("=" * 80)
    print()
    
    # 1. Vérifier que les colonnes existent
    print("1️⃣ Vérification des colonnes ajoutées...")
    result = db.execute(text("""
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'logic_challenges' 
        AND column_name IN ('success_count', 'attempt_count')
        ORDER BY column_name
    """))
    cols = result.fetchall()
    
    if len(cols) == 2:
        print("   ✅ Les 2 colonnes existent:")
        for col in cols:
            print(f"      - {col[0]}: {col[1]} (default: {col[2]})")
    else:
        print(f"   ❌ ERREUR: {len(cols)} colonnes trouvées au lieu de 2")
        return 1
    
    print()
    
    # 2. Vérifier les valeurs NULL
    print("2️⃣ Vérification des valeurs NULL...")
    result = db.execute(text("""
        SELECT COUNT(*) 
        FROM logic_challenges 
        WHERE attempt_count IS NULL OR success_count IS NULL
    """))
    nulls = result.fetchone()[0]
    
    if nulls == 0:
        print("   ✅ Aucune valeur NULL détectée")
    else:
        print(f"   ⚠️ {nulls} challenges avec compteurs NULL")
    
    print()
    
    # 3. Vérifier la cohérence globale
    print("3️⃣ Vérification cohérence globale...")
    result = db.execute(text("""
        SELECT 
            COUNT(*) as total_challenges,
            SUM(attempt_count) as total_attempts_counter,
            SUM(success_count) as total_success_counter
        FROM logic_challenges
    """))
    stats = result.fetchone()
    
    result2 = db.execute(text("SELECT COUNT(*) FROM logic_challenge_attempts"))
    real_total_attempts = result2.fetchone()[0]
    
    result3 = db.execute(text("""
        SELECT COUNT(*) 
        FROM logic_challenge_attempts 
        WHERE is_correct = true
    """))
    real_total_success = result3.fetchone()[0]
    
    print(f"   Total challenges: {stats[0]}")
    print(f"   Total attempts (compteurs): {stats[1] or 0}")
    print(f"   Total attempts (réel): {real_total_attempts}")
    print(f"   Total success (compteurs): {stats[2] or 0}")
    print(f"   Total success (réel): {real_total_success}")
    
    if (stats[1] or 0) == real_total_attempts and (stats[2] or 0) == real_total_success:
        print("   ✅ Cohérence globale parfaite")
    else:
        print("   ⚠️ Incohérence détectée entre compteurs et données réelles")
    
    print()
    
    # 4. Vérifier la cohérence par challenge
    print("4️⃣ Vérification cohérence par challenge...")
    result = db.execute(text("""
        SELECT 
            lc.id,
            lc.attempt_count as counter_attempts,
            COUNT(lca.id) as real_attempts,
            lc.success_count as counter_success,
            COUNT(CASE WHEN lca.is_correct THEN 1 END) as real_success
        FROM logic_challenges lc
        LEFT JOIN logic_challenge_attempts lca ON lc.id = lca.challenge_id
        GROUP BY lc.id, lc.attempt_count, lc.success_count
        HAVING lc.attempt_count != COUNT(lca.id) 
            OR lc.success_count != COUNT(CASE WHEN lca.is_correct THEN 1 END)
        LIMIT 10
    """))
    incoh = result.fetchall()
    
    if len(incoh) == 0:
        print("   ✅ Tous les compteurs sont cohérents avec les données réelles")
    else:
        print(f"   ⚠️ {len(incoh)} challenges avec incohérences:")
        for c in incoh:
            print(f"      Challenge {c[0]}: attempts compteur={c[1]}, réel={c[2]} | success compteur={c[3]}, réel={c[4]}")
    
    print()
    
    # 5. Vérifier le calcul de success_rate
    print("5️⃣ Vérification calcul success_rate...")
    result = db.execute(text("""
        SELECT 
            id,
            attempt_count,
            success_count,
            CASE 
                WHEN attempt_count > 0 
                THEN ROUND((success_count::float / attempt_count::float * 100)::numeric, 2)
                ELSE 0 
            END as calculated_rate,
            success_rate
        FROM logic_challenges
        WHERE attempt_count > 0
        LIMIT 10
    """))
    rates = result.fetchall()
    
    print("   ID | Attempts | Success | Calculé | Stocké | Diff")
    print("   " + "-" * 60)
    errors = 0
    for r in rates:
        calculated = float(r[3]) if r[3] is not None else 0.0
        stored = float(r[4]) if r[4] is not None else 0.0
        diff = abs(calculated - stored)
        status = "✅" if diff < 0.01 else "⚠️"
        if diff >= 0.01:
            errors += 1
        print(f"   {r[0]:3} | {r[1]:8} | {r[2]:7} | {calculated:7.2f}% | {stored:6.2f}% | {status}")
    
    if errors == 0:
        print("   ✅ Tous les success_rate sont cohérents")
    else:
        print(f"   ⚠️ {errors} success_rate avec des différences > 0.01%")
    
    print()
    
    # 6. Vérifier l'accès via le modèle SQLAlchemy
    print("6️⃣ Vérification accès via modèle SQLAlchemy...")
    challenge = db.query(LogicChallenge).first()
    if challenge:
        print(f"   Challenge ID {challenge.id}:")
        print(f"      attempt_count: {challenge.attempt_count} (type: {type(challenge.attempt_count).__name__})")
        print(f"      success_count: {challenge.success_count} (type: {type(challenge.success_count).__name__})")
        print(f"      Attributs accessibles: {'attempt_count' in dir(challenge) and 'success_count' in dir(challenge)}")
        print("   ✅ Le modèle SQLAlchemy peut accéder aux colonnes")
    else:
        print("   ⚠️ Aucun challenge trouvé")
    
    print()
    
    # 7. Afficher quelques exemples
    print("7️⃣ Exemples de challenges avec compteurs...")
    result = db.execute(text("""
        SELECT 
            id, 
            title, 
            attempt_count, 
            success_count, 
            success_rate
        FROM logic_challenges
        ORDER BY attempt_count DESC
        LIMIT 5
    """))
    examples = result.fetchall()
    
    print("   ID | Title (30 chars) | Attempts | Success | Rate")
    print("   " + "-" * 70)
    for ex in examples:
        title = ex[1][:30] if ex[1] else "N/A"
        print(f"   {ex[0]:3} | {title:30} | {ex[2]:8} | {ex[3]:7} | {ex[4]:.1f}%")
    
    print()
    print("=" * 80)
    print("✅ Vérification terminée")
    print("=" * 80)
    
    db.close()
    return 0

if __name__ == "__main__":
    sys.exit(verify_migration())

