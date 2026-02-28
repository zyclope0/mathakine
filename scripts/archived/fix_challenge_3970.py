#!/usr/bin/env python3
"""Corrige les défis pattern avec réponses incorrectes."""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv(ROOT_DIR / ".env")


def main():
    from sqlalchemy import create_engine, text

    engine = create_engine(os.environ.get("DATABASE_URL"))
    with engine.connect() as conn:
        conn.execute(
            text(
                "UPDATE logic_challenges SET correct_answer = 'O, O, X, O' WHERE id = 3976"
            )
        )
        conn.commit()
    print(
        "Défi 3976 corrigé : correct_answer='O, O, X, O' (4 cases, ordre ligne par ligne)"
    )


if __name__ == "__main__":
    main()
