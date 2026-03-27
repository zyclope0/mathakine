"""
Titres d'affichage des niveaux gamification (compte).

Les numéros de niveau suivent la formule persistée (total_points // POINTS_PER_LEVEL + 1).
Libellés publics neutres (F42-C3B) — sans folklore Jedi.
Au-delà des entrées connues, l'API retombe sur un libellé générique « Niveau N ».
"""

from typing import Dict

LEVEL_TITLES: Dict[int, str] = {
    1: "Cadet",
    2: "Éclaireur",
    3: "Explorateur",
    4: "Navigateur",
    5: "Cartographe",
    6: "Commandant",
    7: "Archiviste stellaire",
    8: "Légende cosmique",
    9: "Expert de mission",
    10: "Pilier",
    11: "Grand archiviste",
}
