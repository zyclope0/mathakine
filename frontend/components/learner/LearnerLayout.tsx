import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * LearnerLayout — layout tubulaire pour les pages de résolution d'exercice et de défi.
 *
 * Différences intentionnelles vs PageLayout global :
 * - maxWidth paramétrable : "4xl" pour exercices (aligné LearnerCard exercise), "5xl" pour défis
 * - gap-12 entre sections : espace généreux pour réduire la charge cognitive
 * - Fond `--background` sur la page, `--bg-learner` porté par LearnerCard (contraste carte/page)
 * - Zéro sidebar, zéro décoration périphérique
 * - Padding horizontal responsive cohérent avec PageLayout
 *
 * NE PAS utiliser pour le dashboard, les pages liste, les pages admin.
 * Réservé aux routes /exercises/[id] et /challenge/[id].
 *
 * NOTE: Ne pas ajouter min-h-screen ici — géré par layout.tsx parent.
 */

const MAX_WIDTH_CLASSES = {
  "4xl": "max-w-4xl",
  "5xl": "max-w-5xl",
} as const;

interface LearnerLayoutProps {
  children: ReactNode;
  className?: string;
  /** Largeur max du conteneur interne. "4xl" pour exercices, "5xl" pour défis. */
  maxWidth?: keyof typeof MAX_WIDTH_CLASSES;
}

export function LearnerLayout({ children, className, maxWidth = "4xl" }: LearnerLayoutProps) {
  return (
    <div
      data-learner-context
      className={cn(
        // Fond de page neutre — la carte LearnerCard porte --bg-learner pour le contraste
        "bg-[var(--background)]",
        // Padding responsive identique à PageLayout pour cohérence
        "py-4 px-3 sm:px-4 md:px-6 lg:px-8",
        // Transition douce si le thème change
        "transition-colors duration-200",
        className
      )}
    >
      <div
        className={cn(
          "mx-auto",
          MAX_WIDTH_CLASSES[maxWidth],
          // Espacement vertical généreux entre sections
          "space-y-12"
        )}
      >
        {children}
      </div>
    </div>
  );
}
