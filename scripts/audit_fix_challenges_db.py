#!/usr/bin/env python3
"""
Audit et correction des défis logiques en base de données.

Détecte les incohérences entre correct_answer et :
- La séquence logique (type SEQUENCE) : calcule le prochain élément
- L'explication (solution_explanation) : extrait les calculs finaux

Usage:
    python scripts/audit_fix_challenges_db.py              # Dry-run (affiche sans modifier)
    python scripts/audit_fix_challenges_db.py --execute   # Applique les corrections
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv(ROOT_DIR / ".env")


def get_db_url():
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        print("Erreur: DATABASE_URL non défini.")
        sys.exit(1)
    return url


def compute_next_sequence(seq):
    """
    Calcule le prochain élément d'une séquence numérique.
    Retourne (next_value, pattern_name) ou (None, None) si indéterminé.
    """
    if not seq or len(seq) < 2:
        return None, None

    try:
        nums = [float(x) for x in seq if x is not None]
    except (ValueError, TypeError):
        return None, None

    if len(nums) < 2:
        return None, None

    # Pattern 1: Différence constante (arithmétique)
    diffs = [nums[i + 1] - nums[i] for i in range(len(nums) - 1)]
    if len(set(diffs)) == 1:
        d = diffs[0]
        next_val = nums[-1] + d
        if next_val == int(next_val):
            return str(int(next_val)), "const_diff"
        return str(next_val), "const_diff"

    # Pattern 2: Différences en progression arithmétique (+2, +3, +4, +5...)
    if len(diffs) >= 2:
        diff_diffs = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]
        if len(set(diff_diffs)) == 1:
            dd = diff_diffs[0]
            next_diff = diffs[-1] + dd
            next_val = nums[-1] + next_diff
            if next_val == int(next_val):
                return str(int(next_val)), "arith_diffs"
            return str(next_val), "arith_diffs"

    # Pattern 3: Géométrique (×r)
    if 0 not in nums:
        ratios = [nums[i + 1] / nums[i] for i in range(len(nums) - 1)]
        if len(set(ratios)) == 1:
            r = ratios[0]
            next_val = nums[-1] * r
            if next_val == int(next_val):
                return str(int(next_val)), "geometric"
            return str(round(next_val, 2)), "geometric"

    return None, None


def extract_final_result_from_explanation(text):
    """
    Extrait le résultat final d'un calcul dans l'explication.
    Cherche des patterns comme "16+6=22", "16 + 6 = 22", "obtenir 22", etc.
    """
    if not text:
        return None

    # Pattern: "X + Y = Z" ou "X+Y=Z"
    m = re.search(r"(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)", text)
    if m:
        return m.group(3)

    # Pattern: "pour obtenir N" ou "obtenir N"
    m = re.search(r"obtenir\s+(\d+)", text, re.I)
    if m:
        return m.group(1)

    # Pattern: "= N." en fin de phrase (dernier calcul)
    matches = re.findall(r"=\s*(\d+)(?:\s|\.|$)", text)
    if matches:
        return matches[-1]

    # Pattern: "prochain élément est 'N'" ou "est N"
    m = re.search(r"(?:prochain|prochaine).*(?:est|:)\s*['\"]?(\d+)['\"]?", text, re.I)
    if m:
        return m.group(1)

    return None


def normalize_answer(val):
    """Normalise une réponse pour comparaison."""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return s
    except ValueError:
        return s.lower()


def audit_and_fix(dry_run=True):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(get_db_url())
    Session = sessionmaker(bind=engine, autocommit=False)
    session = Session()

    result = session.execute(text("""
            SELECT id, title, challenge_type, correct_answer, solution_explanation, visual_data
            FROM logic_challenges
            WHERE is_archived = false
            ORDER BY id
        """))
    rows = result.fetchall()

    issues = []
    fixes = []

    for row in rows:
        cid, title, ctype, correct_answer, solution_explanation, visual_data = row
        ctype_str = str(ctype).lower() if ctype else ""
        correct_norm = normalize_answer(correct_answer)

        # --- SEQUENCE: Vérifier cohérence avec la séquence ---
        if "sequence" in ctype_str and visual_data:
            vd = visual_data
            if isinstance(vd, str):
                try:
                    vd = json.loads(vd)
                except json.JSONDecodeError:
                    vd = {}
            vd = vd if isinstance(vd, dict) else {}
            seq = vd.get("sequence") or vd.get("numbers")
            if seq and isinstance(seq, list):
                next_val, pattern = compute_next_sequence(seq)
                if next_val and correct_norm and next_val != correct_norm:
                    issues.append(
                        {
                            "id": cid,
                            "type": "sequence_mismatch",
                            "title": (title or "")[:50],
                            "correct_answer": correct_answer,
                            "expected": next_val,
                            "pattern": pattern,
                            "sequence": seq,
                        }
                    )
                    fixes.append(
                        {
                            "id": cid,
                            "field": "correct_answer",
                            "old": correct_answer,
                            "new": next_val,
                        }
                    )

        # --- SEQUENCE seulement: si expl contient un calcul et contredit ---
        # (Pour les autres types, extraction trop risquée - faux positifs)
        if "sequence" in ctype_str and solution_explanation:
            expl_result = extract_final_result_from_explanation(solution_explanation)
            if expl_result and correct_norm and expl_result != correct_norm:
                # Déjà une fix sequence ? Si expl et computed diffèrent, priorité au computed
                if not any(f["id"] == cid for f in fixes):
                    issues.append(
                        {
                            "id": cid,
                            "type": "explanation_contradicts",
                            "title": (title or "")[:50],
                            "correct_answer": correct_answer,
                            "explanation_says": expl_result,
                        }
                    )
                    # Pour SEQUENCE : l'explication qui calcule est fiable (ex: 16+6=22)
                    fixes.append(
                        {
                            "id": cid,
                            "field": "correct_answer",
                            "old": correct_answer,
                            "new": expl_result,
                        }
                    )

    # Affichage
    print(f"\n=== Audit défis logiques ({len(rows)} défis analysés) ===\n")
    if not issues:
        print("[OK] Aucune incoherence detectee.")
        session.close()
        return 0

    print(f"[!] {len(issues)} incoherence(s) detectee(s):\n")
    for i, iss in enumerate(issues, 1):
        print(f"{i}. Défi #{iss['id']} - {iss['title']}...")
        print(f"   Type: {iss['type']}")
        print(f"   correct_answer actuel: {iss['correct_answer']}")
        if "expected" in iss:
            print(
                f"   Valeur attendue (séquence): {iss['expected']} (pattern: {iss.get('pattern', '?')})"
            )
            print(f"   Séquence: {iss.get('sequence', [])}")
        if "explanation_says" in iss:
            print(f"   L'explication conclut: {iss['explanation_says']}")
        print()

    # Appliquer les corrections (UNIQUEMENT sequence_mismatch - deterministic)
    fix_ids = {iss["id"] for iss in issues if iss["type"] == "sequence_mismatch"}
    fixes_to_apply = [f for f in fixes if f["id"] in fix_ids]

    if fixes_to_apply and not dry_run:
        for fix in fixes_to_apply:
            session.execute(
                text(
                    "UPDATE logic_challenges SET correct_answer = :new WHERE id = :id"
                ),
                {"new": fix["new"], "id": fix["id"]},
            )
            print(f"   Defi #{fix['id']}: correct_answer {fix['old']} -> {fix['new']}")
        session.commit()
        print(
            f"\n[OK] {len(fixes_to_apply)} correction(s) appliquee(s) (sequence_mismatch uniquement)."
        )
    elif dry_run:
        print("[MODE DRY-RUN] Lancez avec --execute pour appliquer les corrections.")

    session.close()
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Audit et correction des incohérences dans les défis logiques"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Appliquer les corrections"
    )
    args = parser.parse_args()
    return audit_and_fix(dry_run=not args.execute)


if __name__ == "__main__":
    sys.exit(main())
