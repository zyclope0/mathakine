#!/usr/bin/env python3
import sys
import json
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from app.db.base import SessionLocal
from app.models.logic_challenge import LogicChallenge

db = SessionLocal()
challenges = db.query(LogicChallenge).filter(LogicChallenge.id.in_([3004, 3005, 3011])).all()

for ch in challenges:
    print(f"\n{'='*60}")
    print(f"Challenge ID: {ch.id}")
    print(f"Title: {ch.title}")
    print(f"Type: {ch.challenge_type}")
    print(f"Visual data:")
    if ch.visual_data:
        print(json.dumps(ch.visual_data, indent=2, ensure_ascii=False))
    else:
        print("None")
    print('='*60)

db.close()

