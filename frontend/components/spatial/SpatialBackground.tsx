"use client";

import { Starfield } from "./Starfield";
import { Planet } from "./Planet";
import { Particles } from "./Particles";

/**
 * Composant SpatialBackground - Conteneur pour toutes les animations spatiales
 *
 * Combine Starfield, Planet et Particles
 * S'adapte automatiquement au thème et aux préférences d'accessibilité
 */
export function SpatialBackground() {
  return (
    <>
      <Starfield />
      <Planet />
      <Particles />
    </>
  );
}
