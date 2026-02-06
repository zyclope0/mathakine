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
    
    # Holocron Status
    print(f"📜 Holocron Status: {data.get('holocron_status')}")
    print()
    
    # Academy Statistics
    academy = data.get('academy_statistics', {})
    print("🏛️  STATISTIQUES DE L'ACADÉMIE JEDI")
    print("-" * 50)
    print(f"   Total des épreuves: {academy.get('total_challenges')}")
    print(f"   Épreuves archivées: {academy.get('archived_challenges')}")
    print(f"   Générées par la Force (IA): {academy.get('force_generated')} ({academy.get('force_generated_percentage')}%)")
    print()
    
    # By Force Art
    by_force = data.get('by_force_art', {})
    print("⚡ RÉPARTITION PAR ART DE LA FORCE")
    print("-" * 50)
    for art_code, art_data in by_force.items():
        print(f"   {art_data.get('force_name')}: {art_data.get('count')} ({art_data.get('percentage')}%)")
    print()
    
    # By Jedi Rank
    by_rank = data.get('by_jedi_rank', {})
    print("🎖️  RÉPARTITION PAR RANG JEDI")
    print("-" * 50)
    for rank_code, rank_data in by_rank.items():
        print(f"   {rank_data.get('rank_name')}: {rank_data.get('count')} - {rank_data.get('description')}")
    print()
    
    # By Padawan Group
    by_group = data.get('by_padawan_group', {})
    print("👥 RÉPARTITION PAR GROUPE DE PADAWANS")
    print("-" * 50)
    for group_code, group_data in by_group.items():
        print(f"   {group_data.get('group_name')} ({group_code} ans): {group_data.get('count')}")
    print()
    
    # Galactic Performance
    perf = data.get('galactic_performance', {})
    print("🌌 PERFORMANCE GALACTIQUE")
    print("-" * 50)
    print(f"   Total des tentatives: {perf.get('total_attempts')}")
    print(f"   Tentatives réussies: {perf.get('successful_attempts')}")
    print(f"   Taux de maîtrise de la Force: {perf.get('force_mastery_rate')}%")
    print(f"   📢 {perf.get('message')}")
    print()
    
    # Legendary Challenges
    legends = data.get('legendary_challenges', [])
    if legends:
        print("🏆 ÉPREUVES LÉGENDAIRES (les plus tentées)")
        print("-" * 50)
        for i, challenge in enumerate(legends, 1):
            print(f"   {i}. {challenge.get('title')}")
            print(f"      Art: {challenge.get('force_art')} | Rang: {challenge.get('jedi_rank')}")
            print(f"      Padawans entraînés: {challenge.get('padawans_trained')}")
        print()
    
    # Jedi Wisdom
    wisdom = data.get('jedi_wisdom')
    print("💫 SAGESSE JEDI")
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
