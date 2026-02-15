#!/usr/bin/env python3
"""
Audit et correction de la cohérence des réponses dans les exercices.

Détecte les incohérences entre correct_answer et le calcul attendu selon :
- ADDITION, SOUSTRACTION, MULTIPLICATION, DIVISION : extraction des nombres de la question
- FRACTIONS : total, fractions (moitié/tiers/quart), reste = total - somme des parts
- TEXTE, MIXTE, GEOMETRIE, DIVERS : extraction du résultat final depuis l'explication

Usage:
    python scripts/audit_fix_exercises_db.py              # Dry-run (affiche sans modifier)
    python scripts/audit_fix_exercises_db.py --execute  # Applique les corrections
"""
import argparse
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
        return str(round(f, 2))
    except ValueError:
        return s.lower()


# ---------------------------------------------------------------------------
# Parsers par type d'exercice
# ---------------------------------------------------------------------------

def parse_addition(question):
    """Extrait les opérandes d'une addition. Retourne (expected, confidence)."""
    # Patterns: "12 + 7", "12+7", "Calcule 12 + 7", "combien font 12 + 7 ?", "12 + 7 = ?"
    if not question:
        return None, 0
    m = re.search(r'(\d+)\s*\+\s*(\d+)(?:\s*\+\s*(\d+))?', question)
    if not m:
        return None, 0
    a, b = int(m.group(1)), int(m.group(2))
    c = int(m.group(3)) if m.group(3) else 0
    return str(a + b + c), 1


def parse_subtraction(question):
    """Extrait les opérandes d'une soustraction."""
    if not question:
        return None, 0
    m = re.search(r'(\d+)\s*[-−]\s*(\d+)', question)
    if not m:
        return None, 0
    a, b = int(m.group(1)), int(m.group(2))
    if a < b:
        return None, 0
    return str(a - b), 1


def parse_multiplication(question):
    """Extrait les opérandes d'une multiplication."""
    if not question:
        return None, 0
    m = re.search(r'(\d+)\s*[×*xX]\s*(\d+)', question)
    if not m:
        return None, 0
    return str(int(m.group(1)) * int(m.group(2))), 1


def parse_division(question):
    """Extrait les opérandes d'une division (quotient entier)."""
    if not question:
        return None, 0
    m = re.search(r'(\d+)\s*[÷/:]\s*(\d+)', question)
    if not m:
        return None, 0
    a, b = int(m.group(1)), int(m.group(2))
    if b == 0:
        return None, 0
    return str(a // b), 1


def parse_fractions(question, explanation, correct_answer=None):
    """
    Uniquement pour "combien reste / ni l'un ni l'autre / ni rouges ni bleus".
    Formule: reste = total - (total*frac1) - (total*frac2)
    Exemple: 120 cristaux, 1/2 rouges, 1/3 bleus -> reste=20
    Ne pas appliquer si la question demande une fraction (1/2, 3/4) ou une part spécifique.
    """
    q = (question or "").lower()
    if not q:
        return None, 0

    # Uniquement si la question demande le RESTE / ni l'un ni l'autre
    reste_keywords = ["ni l'un ni l'autre", "ni rouges ni bleus", "ni rouge ni bleu",
                      "combien reste", "combien restent", "quel est le reste",
                      "aucune de ces couleurs", "reste-t-il", "restent-ils"]
    if not any(kw in q for kw in reste_keywords):
        return None, 0

    full = (question or "") + " " + (explanation or "")
    
    # Extraire le total
    total_m = re.search(r'(\d+)\s*(?:cristaux?|objets?|éléments?|pièces?|bonbons?|billes?|minéraux?|étoiles?)', full, re.I)
    if not total_m:
        total_m = re.search(r'(?:total\s+de\s+)?(\d+)\s', full, re.I)
    total = int(total_m.group(1)) if total_m else None
    if not total or total <= 0:
        return None, 0
    
    fracs = []
    for m in re.finditer(r'(\d+)/(\d+)', full):
        n, d = int(m.group(1)), int(m.group(2))
        if d > 0:
            fracs.append(n / d)
    if 'moitié' in full.lower() or 'moitie' in full.lower() or 'demi' in full.lower():
        if not any(abs(f - 0.5) < 0.01 for f in fracs):
            fracs.append(0.5)
    if 'tiers' in full.lower() or 'tier ' in full.lower():
        if not any(0.32 <= f <= 0.34 for f in fracs):
            fracs.append(1/3)
    if 'quart' in full.lower():
        if not any(abs(f - 0.25) < 0.01 for f in fracs):
            fracs.append(0.25)
    
    if not fracs:
        return None, 0
    
    parts_sum = sum(total * f for f in fracs)
    reste = total - int(round(parts_sum))
    if reste < 0:
        reste = 0
    # Cas spécial 120 cristaux : moitié + tiers = 100, reste = 20 (erreur fréquente : 30)
    if total == 120 and abs(parts_sum - 100) < 1 and correct_answer and str(correct_answer) == "30":
        return "20", 1.0
    return str(reste), 0.9


def extract_final_from_explanation(explanation):
    """
    Extrait le résultat final d'une explication (patterns explicites uniquement).
    Ne pas confondre avec paramètres (rayon, côté...) - privilégier fin de phrase.
    """
    if not explanation:
        return None
    # "La réponse est 42." / "donc 42." en fin de phrase
    m = re.search(r'(?:réponse|résultat|donc)\s*(?:est|:)?\s*(\d+(?:[.,]\d+)?)\s*\.?\s*$', explanation, re.I)
    if m:
        return m.group(1).replace(",", ".")
    # Dernier "= N" ou "= N." (éviter nombres trop petits type rayon 3)
    matches = re.findall(r'=\s*(\d+(?:[.,]\d+)?)(?:\s|\.|,|$)', explanation)
    if matches:
        last = matches[-1].replace(",", ".")
        # Ignorer si c'est un petit nombre isolé (risque paramètre)
        try:
            v = float(last)
            if v < 10 and "." not in last:
                return None  # 3, 2 etc. souvent des paramètres
        except ValueError:
            pass
        return last
    return None


# ---------------------------------------------------------------------------
# Audit principal
# ---------------------------------------------------------------------------

def audit_and_fix(dry_run=True):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(get_db_url())
    Session = sessionmaker(bind=engine, autocommit=False)
    session = Session()

    result = session.execute(
        text("""
            SELECT id, title, exercise_type, question, correct_answer, choices, explanation
            FROM exercises
            WHERE is_archived = false
            ORDER BY id
        """)
    )
    rows = result.fetchall()

    issues = []
    fixes = []

    type_map = {
        "addition": parse_addition,
        "soustraction": parse_subtraction,
        "subtraction": parse_subtraction,
        "multiplication": parse_multiplication,
        "division": parse_division,
        "fractions": lambda q, e, c=None: parse_fractions(q, e, c),
    }

    for row in rows:
        ex_id, title, ex_type, question, correct_answer, choices, explanation = row
        ex_type_lower = (ex_type or "").lower()
        correct_norm = normalize_answer(correct_answer)
        expected = None
        confidence = 0
        fix_reason = ""

        # 1. Parsing selon le type
        parser = type_map.get(ex_type_lower)
        if parser:
            if ex_type_lower == "fractions":
                expected, confidence = parser(question, explanation, correct_answer)
            else:
                expected, confidence = parser(question or "")
        else:
            # TEXTE, MIXTE, GEOMETRIE, DIVERS : tenter depuis l'explication (très prudent)
            expected = extract_final_from_explanation(explanation)
            confidence = 0.7 if expected else 0
            # Ne pas corriger si correct_answer est déjà un décimal (calcul précis type géométrie)
            if expected and "." in str(correct_answer):
                expected = None
                confidence = 0

        if not expected or confidence < 0.5:
            continue

        expected_norm = normalize_answer(expected)
        # Ne pas corriger si la réponse actuelle est une fraction (1/2, 3/4) et on a un entier
        if "/" in str(correct_answer) and expected_norm.isdigit():
            continue
        if not expected_norm or expected_norm == correct_norm:
            continue

        # Éviter fix si ordre de grandeur très différent (ex: 3 vs 201)
        try:
            curr_val = float(correct_norm.replace(",", "."))
            exp_val = float(expected_norm.replace(",", "."))
            if curr_val > 0 and (exp_val / curr_val < 0.1 or exp_val / curr_val > 10):
                continue  # Risque de faux positif
        except (ValueError, ZeroDivisionError):
            pass

        fix_reason = f"compute_{ex_type_lower}" if parser else "explanation_extract"

        issues.append({
            "id": ex_id,
            "type": fix_reason,
            "title": (title or "")[:50],
            "exercise_type": ex_type_lower,
            "correct_answer": correct_answer,
            "expected": expected_norm,
            "confidence": confidence,
        })
        fixes.append({
            "id": ex_id,
            "field": "correct_answer",
            "old": correct_answer,
            "new": expected_norm,
        })

    # Vérifier aussi que correct_answer est dans choices (si choices existent)
    for row in rows:
        ex_id, title, ex_type, question, correct_answer, choices, explanation = row
        if not choices or not isinstance(choices, list):
            continue
        choices_str = [str(c).strip() for c in choices]
        correct_norm = normalize_answer(correct_answer)
        if correct_norm and correct_norm not in choices_str:
            # Vérifier si une variante existe (ex: "20" vs "20 cristaux")
            found = any(correct_norm in c or c in correct_norm for c in choices_str)
            if not found and not any(f["id"] == ex_id for f in fixes):
                issues.append({
                    "id": ex_id,
                    "type": "correct_not_in_choices",
                    "title": (title or "")[:50],
                    "correct_answer": correct_answer,
                    "choices": choices_str[:4],
                })
                # Pas de fix auto pour ce cas - nécessite mise à jour des choices

    # Affichage
    print(f"\n=== Audit exercices ({len(rows)} exercices analysés) ===\n")
    if not issues:
        print("[OK] Aucune incohérence détectée.")
        session.close()
        return 0

    print(f"[!] {len(issues)} incohérence(s) détectée(s):\n")
    for i, iss in enumerate(issues, 1):
        print(f"{i}. Exercice #{iss['id']} - {iss['title']}...")
        print(f"   Type: {iss.get('exercise_type', '?')} / {iss['type']}")
        print(f"   correct_answer actuel: {iss['correct_answer']}")
        if "expected" in iss:
            print(f"   Valeur attendue: {iss['expected']} (confiance: {iss.get('confidence', 1)})")
        if "choices" in iss:
            print(f"   Choices: {iss['choices']}")
        print()

    # Appliquer les corrections (uniquement compute_* et explanation_extract)
    fixable_types = {"compute_addition", "compute_soustraction", "compute_subtraction",
                     "compute_multiplication", "compute_division", "compute_fractions",
                     "explanation_extract"}
    fixes_to_apply = [f for f in fixes if any(
        iss["type"] in fixable_types and iss["id"] == f["id"] for iss in issues
    )]

    if fixes_to_apply and not dry_run:
        for fix in fixes_to_apply:
            session.execute(
                text("UPDATE exercises SET correct_answer = :new WHERE id = :id"),
                {"new": fix["new"], "id": fix["id"]}
            )
            print(f"   Exercice #{fix['id']}: correct_answer {fix['old']} -> {fix['new']}")
        session.commit()
        print(f"\n[OK] {len(fixes_to_apply)} correction(s) appliquée(s).")
    elif dry_run:
        print("[MODE DRY-RUN] Lancez avec --execute pour appliquer les corrections.")

    session.close()
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Audit et correction des incohérences dans les exercices"
    )
    parser.add_argument("--execute", action="store_true", help="Appliquer les corrections")
    args = parser.parse_args()
    return audit_and_fix(dry_run=not args.execute)


if __name__ == "__main__":
    sys.exit(main())
