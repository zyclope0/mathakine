#!/usr/bin/env python3
"""
Backup BDD Mathakine — fonctionne sans pg_dump dans le PATH.
Usage: python scripts/backup_db.py
Charge DATABASE_URL depuis .env si non définie.
"""

import os
import subprocess
import sys
from pathlib import Path

# Charger .env
try:
    from dotenv import load_dotenv

    load_dotenv(override=False)
except ImportError:
    pass

url = os.environ.get("DATABASE_URL")
if not url:
    print(
        "ERREUR: DATABASE_URL non définie. Définir la var ou ajouter DATABASE_URL dans .env"
    )
    sys.exit(1)

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
dump_file = backup_dir / f"mathakine_backup_{timestamp}.dump"

print(f"Backup vers {dump_file} ...")

# Chercher pg_dump (Windows: Program Files, Linux: PATH)
pg_dump = "pg_dump"
for candidate in [
    r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe",
    r"C:\Program Files\PostgreSQL\15\bin\pg_dump.exe",
    r"C:\Program Files\PostgreSQL\14\bin\pg_dump.exe",
]:
    if Path(candidate).exists():
        pg_dump = candidate
        break

try:
    subprocess.run(
        [pg_dump, url, "-F", "c", "-f", str(dump_file)],
        check=True,
        capture_output=True,
        text=True,
    )
    print(f"Backup terminé: {dump_file}")
except subprocess.CalledProcessError as e:
    print(f"Erreur: {e.stderr or e}")
    sys.exit(1)
except FileNotFoundError:
    print("ERREUR: pg_dump introuvable. Installer PostgreSQL ou l'ajouter au PATH.")
    sys.exit(1)
