#!/usr/bin/env python
"""Affiche ``visual_data`` brut + normalisé pour un défi donné.

Utile quand le renderer montre des chaînes dict Python-like
(``"{'name': 'cercle rouge', 'size': 'petit'}"``) : permet de
savoir si le défaut vient du stockage DB (objets / chaînes / repr
Python) et si ``apply_visual_contract_normalization`` corrige bien
au GET détail.

Usage :
    python scripts/debug_challenge_visual_data.py 4070
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import SessionLocal
from app.models.logic_challenge import LogicChallenge
from app.services.challenges.challenge_api_mapper import challenge_to_detail_dict


def _preview(obj, max_items: int = 4) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)[:3000]
    except Exception as e:  # pragma: no cover - diag
        return f"<unserializable: {e}>"


def main(challenge_id: int) -> int:
    db = SessionLocal()
    try:
        challenge = db.query(LogicChallenge).filter_by(id=challenge_id).first()
        if challenge is None:
            print(f"[ERR] LogicChallenge id={challenge_id} introuvable.")
            return 2

        raw = getattr(challenge, "visual_data", None)
        print(f"=== visual_data STOCKÉ (type={type(raw).__name__}) ===")
        if isinstance(raw, str):
            print(raw[:3000])
            print("--- parse JSON ---")
            try:
                parsed = json.loads(raw)
                print(_preview(parsed))
            except Exception as e:
                print(f"[JSONDecodeError] {e}")
                parsed = None
        else:
            print(_preview(raw))

        print()
        print("=== challenge_to_detail_dict(visual_data) (post-normalisation API) ===")
        detail = challenge_to_detail_dict(challenge)
        vd = detail.get("visual_data")
        print(_preview(vd))

        print()
        layout = (vd or {}).get("layout") if isinstance(vd, dict) else None
        if isinstance(layout, list):
            print(f"=== layout flat items = {len(layout)} ===")
            for i, item in enumerate(layout):
                shape = item.get("shape") if isinstance(item, dict) else item
                if isinstance(shape, str) and (
                    shape.startswith("{'") or shape.startswith('{"')
                ):
                    print(f"  [{i}] [KO] SHAPE ENCORE EN REPR PYTHON : {shape!r}")
                else:
                    print(f"  [{i}] shape={shape!r}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/debug_challenge_visual_data.py <challenge_id>")
        sys.exit(2)
    sys.exit(main(int(sys.argv[1])))
