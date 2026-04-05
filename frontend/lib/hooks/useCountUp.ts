"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Anime un nombre de 0 vers `target` sur `duration` ms.
 * - Easing : ease-out-expo (décélération rapide → chiffres "tombe en place")
 * - prefers-reduced-motion : valeur finale affichée immédiatement, 0 animation
 * - Rejoue l'animation à chaque changement de `target` (ex: changement de période)
 */
export function useCountUp(target: number, duration = 700): number {
  const [current, setCurrent] = useState(0);
  const rafRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const prefersReduced =
    typeof window !== "undefined"
      ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
      : false;

  useEffect(() => {
    if (prefersReduced) {
      setCurrent(target); // Intentional direct setState in effect — prefers-reduced-motion fast-path
      return;
    }

    // Annule l'animation précédente si target change pendant le compte
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
    }
    startTimeRef.current = null;
    setCurrent(0);

    const easeOutExpo = (t: number): number =>
      t === 1 ? 1 : 1 - Math.pow(2, -10 * t);

    const tick = (timestamp: number) => {
      if (startTimeRef.current === null) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutExpo(progress);
      setCurrent(Math.round(eased * target));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        setCurrent(target);
      }
    };

    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [target, duration, prefersReduced]);

  return current;
}
