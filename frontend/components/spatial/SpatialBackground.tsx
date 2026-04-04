"use client";

import { Starfield } from "./Starfield";
import { Planet } from "./Planet";
import { Particles } from "./Particles";
import { DinoFloating } from "./DinoFloating";
import { UnicornFloating } from "./UnicornFloating";

/**
 * Composant SpatialBackground - Conteneur pour toutes les animations spatiales
 *
 * Combine Starfield, Planet et Particles
 * Thème Dino : silhouette dino + petit dino flottant
 * Thème Licorne : licorne principale (Planet) + petite licorne flottante (UnicornFloating)
 * S'adapte automatiquement au thème et aux préférences d'accessibilité
 */
export function SpatialBackground() {
  return (
    <>
      <Starfield />
      <Planet />
      <Particles />
      <DinoFloating />
      <UnicornFloating />
    </>
  );
}
