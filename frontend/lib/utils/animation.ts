/**
 * Utilitaires d'animation partagés.
 */

const STAGGER_CLASSES = [
  "animate-fade-in-up-delay-1",
  "animate-fade-in-up-delay-2",
  "animate-fade-in-up-delay-3",
] as const;

/**
 * Retourne la classe CSS d'animation décalée selon l'index.
 * Les index > max reçoivent la dernière classe (pas de délai visible infini).
 */
export function getStaggerDelay(index: number, max = STAGGER_CLASSES.length - 1): string {
  const clamped = Math.min(index, max);
  return STAGGER_CLASSES[clamped] ?? "animate-fade-in-up-delay-3";
}
