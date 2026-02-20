"use client";

import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useReducedMotion, type Variants, type Transition } from "framer-motion";

/**
 * Hook pour créer des animations accessibles qui respectent les préférences utilisateur
 * - reducedMotion : Réduit ou désactive les animations
 * - focusMode : Simplifie les animations pour TSA/TDAH
 * - prefers-reduced-motion : Respecte la préférence système
 */
export function useAccessibleAnimation() {
  const { reducedMotion, focusMode } = useAccessibilityStore();
  const prefersReducedMotion = useReducedMotion();

  // Déterminer si les animations doivent être réduites
  const shouldReduceMotion = reducedMotion || focusMode || prefersReducedMotion;

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
  const createTransition = (
    baseTransition: Partial<Transition> = {}
  ): Transition => {
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
