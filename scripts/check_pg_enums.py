#!/usr/bin/env python3
"""Check exact PostgreSQL enum values"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import os

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, poolclass=NullPool, connect_args={"connect_timeout": 10})

try:
    with engine.connect() as conn:
        # Check all enum types
        result = conn.execute(text("""
            SELECT t.typname as enum_name, e.enumlabel as enum_value
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname IN ('exercisetype', 'difficultylevel', 'logicchallengetype', 'agegroup')
            ORDER BY t.typname, e.enumsortorder;
        """))
        
        current_enum = None
        for row in result:
            if row[0] != current_enum:
                current_enum = row[0]
                print(f"\n{current_enum}:")
            print(f"  - '{row[1]}'")
        
        conn.close()
finally:
    engine.dispose()

