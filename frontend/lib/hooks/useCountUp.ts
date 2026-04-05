"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Anime un nombre de 0 vers `target` sur `duration` ms.
 * - Easing : ease-out-expo
 * - prefers-reduced-motion : reactif via matchMedia
 * - Rejoue l'animation a chaque changement de `target`
 */
export function useCountUp(target: number, duration = 700): number {
  const [current, setCurrent] = useState(0);
  const [prefersReduced, setPrefersReduced] = useState(() =>
    typeof window !== "undefined"
      ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
      : false
  );

  const rafRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handler = (event: MediaQueryListEvent) => setPrefersReduced(event.matches);
    mq.addEventListener("change", handler);

    return () => mq.removeEventListener("change", handler);
  }, []);

  useEffect(() => {
    if (prefersReduced) {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      return;
    }

    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    startTimeRef.current = null;

    const easeOutExpo = (progress: number): number =>
      progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

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

  return prefersReduced ? target : current;
}
