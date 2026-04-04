"use client";

import { useSyncExternalStore } from "react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import type { Variants, Transition } from "framer-motion";
import { useSystemReducedMotion } from "@/lib/hooks/useSystemReducedMotion";

function subscribeToHydration() {
  return () => {};
}

interface UseAccessibleAnimationOptions {
  /** Dashboard adulte : peut ignorer focusMode tout en respectant reduced-motion. */
  respectFocusMode?: boolean;
}

/**
 * Hook pour créer des animations accessibles qui respectent les préférences utilisateur
 * - reducedMotion : Réduit ou désactive les animations
 * - focusMode : Simplifie les animations pour TSA/TDAH
 * - prefers-reduced-motion : Respecte la préférence système
 *
 * SSR-safe : shouldReduceMotion est initialisé à false côté serveur pour éviter
 * le hydration mismatch. La vraie valeur est appliquée après montage côté client.
 * Référence : https://react.dev/link/hydration-mismatch
 */
export function useAccessibleAnimation({
  respectFocusMode = true,
}: UseAccessibleAnimationOptions = {}) {
  const { reducedMotion, focusMode } = useAccessibilityStore();
  const prefersReducedMotion = useSystemReducedMotion();

  // `useSyncExternalStore` permet un guard SSR-safe sans `setState` dans un effet.
  // Snapshot serveur = false, snapshot client = true après hydratation.
  const isHydrated = useSyncExternalStore(
    subscribeToHydration,
    () => true,
    () => false
  );

  // Avant montage : toujours false → pas d'animation → pas de mismatch SSR/client.
  // Après montage : valeur réelle lue depuis window.matchMedia et les stores.
  const shouldReduceMotion =
    isHydrated &&
    (reducedMotion || Boolean(prefersReducedMotion) || (respectFocusMode && focusMode));

  /**
   * Crée une variante d'animation avec garde-fous
   */
  const createVariants = (variants: Variants): Variants => {
    if (shouldReduceMotion) {
      // En mode réduit : animations minimales ou désactivées
      return {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        exit: { opacity: 0 },
      };
    }
    return variants;
  };

  /**
   * Crée une transition avec durée réduite si nécessaire
   */
  const createTransition = (baseTransition: Partial<Transition> = {}): Transition => {
    if (shouldReduceMotion) {
      return {
        duration: 0.1,
        delay: 0,
        ease: "easeOut",
      } as Transition;
    }
    return {
      duration: baseTransition.duration ?? 0.3,
      delay: baseTransition.delay ?? 0,
      ease: baseTransition.ease ?? [0.4, 0, 0.2, 1],
    } as Transition;
  };

  /**
   * Props d'animation pour motion.div avec garde-fous
   */
  const getMotionProps = (customVariants?: Variants, customTransition?: Partial<Transition>) => {
    const variants =
      customVariants ||
      createVariants({
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        exit: { opacity: 0, y: -20 },
      });

    const transition = customTransition || createTransition();

    return {
      variants,
      transition,
      initial: "initial",
      animate: "animate",
      exit: "exit",
    };
  };

  return {
    shouldReduceMotion,
    createVariants,
    createTransition,
    getMotionProps,
  };
}
