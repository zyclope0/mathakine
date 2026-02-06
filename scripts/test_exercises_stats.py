#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'endpoint /api/exercises/stats
"""
import sys
import os
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from unittest.mock import MagicMock, AsyncMock

async def test_exercises_stats():
    """Test du handler get_exercises_stats"""
    from server.handlers.exercise_handlers import get_exercises_stats
    
    # Créer une requête mock
    mock_request = MagicMock()
    mock_request.query_params = {}
    
    # Appeler le handler
    response = await get_exercises_stats(mock_request)
    
    # Afficher le résultat
    print("=" * 70)
    print("TEST ENDPOINT /api/exercises/stats")
    print("=" * 70)
    print()
    
    data = json.loads(response.body.decode('utf-8'))
    
    # Archive Status
    print(f"📜 Statut des Archives: {data.get('archive_status')}")
    print()
    
    # Academy Statistics
    academy = data.get('academy_statistics', {})
    print("🏛️  STATISTIQUES DE L'ACADÉMIE")
    print("-" * 50)
    print(f"   Total des épreuves: {academy.get('total_challenges')}")
    print(f"   Épreuves archivées: {academy.get('archived_challenges')}")
    print(f"   Générées par IA: {academy.get('ai_generated')} ({academy.get('ai_generated_percentage')}%)")
    print()
    
    # By Discipline
    by_discipline = data.get('by_discipline', {})
    print("📐 RÉPARTITION PAR DISCIPLINE")
    print("-" * 50)
    for disc_code, disc_data in by_discipline.items():
        print(f"   {disc_data.get('discipline_name')}: {disc_data.get('count')} ({disc_data.get('percentage')}%)")
    print()
    
    # By Rank
    by_rank = data.get('by_rank', {})
    print("🎖️  RÉPARTITION PAR RANG")
    print("-" * 50)
    for rank_code, rank_data in by_rank.items():
        print(f"   {rank_data.get('rank_name')}: {rank_data.get('count')} - {rank_data.get('description')}")
    print()
    
    # By Apprentice Group
    by_group = data.get('by_apprentice_group', {})
    print("👥 RÉPARTITION PAR GROUPE D'APPRENTIS")
    print("-" * 50)
    for group_code, group_data in by_group.items():
        print(f"   {group_data.get('group_name')} ({group_code} ans): {group_data.get('count')}")
    print()
    
    # Global Performance
    perf = data.get('global_performance', {})
    print("📊 PERFORMANCE GLOBALE")
    print("-" * 50)
    print(f"   Total des tentatives: {perf.get('total_attempts')}")
    print(f"   Tentatives réussies: {perf.get('successful_attempts')}")
    print(f"   Taux de maîtrise: {perf.get('mastery_rate')}%")
    print(f"   📢 {perf.get('message')}")
    print()
    
    # Legendary Challenges
    legends = data.get('legendary_challenges', [])
    if legends:
        print("🏆 ÉPREUVES LÉGENDAIRES (les plus tentées)")
        print("-" * 50)
        for i, challenge in enumerate(legends, 1):
            print(f"   {i}. {challenge.get('title')}")
            print(f"      Discipline: {challenge.get('discipline')} | Rang: {challenge.get('rank')}")
            print(f"      Apprentis formés: {challenge.get('apprentices_trained')}")
        print()
    
    # Sage Wisdom
    wisdom = data.get('sage_wisdom')
    print("💫 SAGESSE DES MAÎTRES")
    print("-" * 50)
    print(f"   \"{wisdom}\"")
    print()
    
    print("=" * 70)
    print("✅ TEST RÉUSSI - Endpoint opérationnel")
    print("=" * 70)
    
    return data


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_exercises_stats())
