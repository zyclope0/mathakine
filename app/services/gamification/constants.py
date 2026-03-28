"""Constantes du moteur de gamification persistant (compte utilisateur)."""

# Ancien palier linéaire fixe (pré F42-P4). Conservé pour références / docs historiques.
POINTS_PER_LEVEL_LEGACY = 100

# Compat : certains imports historiques utilisent encore ce nom.
POINTS_PER_LEVEL = POINTS_PER_LEVEL_LEGACY

# F42-P4 — coût en points pour passer du niveau L au niveau L+1.
# ``level_max`` : dernier niveau L pour lequel ce coût s’applique (inclus).
# Tranches successives : L=1..5 → 200, L=6..12 → 300, etc.
LEVEL_UP_COST_SEGMENTS: tuple[tuple[int, int], ...] = (
    (5, 200),
    (12, 300),
    (22, 420),
    (35, 580),
    (10**9, 750),
)
