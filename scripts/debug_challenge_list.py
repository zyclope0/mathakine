#!/usr/bin/env python
"""Script de debug pour list_challenges + random_offset.
Usage: TESTING=true python scripts/debug_challenge_list.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ["TESTING"] = "true"

from app.db.base import SessionLocal
from app.services.challenges import challenge_service

def main():
    db = SessionLocal()
    try:
        total = challenge_service.count_challenges(db)
        print(f"count_challenges: {total}")

        challenges = challenge_service.list_challenges(db, limit=20, offset=0, order="random")
        print(f"list_challenges (random): {len(challenges)} items")

        if total > 0 and len(challenges) == 0:
            print("BUG: count>0 mais list=0")
        elif total > 0 and len(challenges) > 0:
            print("OK: données cohérentes")
    finally:
        db.close()

if __name__ == "__main__":
    main()
