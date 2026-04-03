import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * LearnerCard — shell de contenu pour les flux apprenant (exercice, défi).
 *
 * Différences intentionnelles vs Card globale et SolverFocusBoard :
 * - Fond `--bg-learner` (token par thème, légèrement teinté, zéro blanc éblouissant)
 * - Zéro glassmorphism (pas de backdrop-blur, pas de bg-card/90)
 * - Zéro shadow décorative (shadow-none) — la hiérarchie vient de l'espace, pas de la profondeur
 * - Zéro border animée
 * - Radius 2xl (plus organique, moins "SaaS admin")
 * - Padding généreux pour réduire la charge cognitive (NI plan, neuro-inclusion)
 *
 * NE PAS utiliser sur le dashboard, les pages admin, ou les surfaces marketing.
 * Réservé aux pages où l'enfant résout un exercice ou un défi.
 */

interface LearnerCardProps {
  children: ReactNode;
  className?: string;
  /** Variante de taille pour exercice (max-w-4xl) vs défi (max-w-5xl) */
  variant?: "exercise" | "challenge";
  /** Rôle ARIA pour les lecteurs d'écran — "main" par défaut */
  role?: string;
}

const VARIANT_CLASSES: Record<"exercise" | "challenge", string> = {
  exercise: "w-full max-w-4xl mx-auto mt-8 md:mt-12 p-8 md:p-12",
  challenge: "w-full max-w-5xl mx-auto mt-6 p-6 md:p-10",
};

export function LearnerCard({ children, className, variant = "exercise", role }: LearnerCardProps) {
  return (
    <div
      role={role}
      data-learner-context
      className={cn(
        // Fond teinté par thème — token défini dans globals.css (NI-2)
        "rounded-2xl",
        "bg-[var(--bg-learner,var(--card))]",
        // Zéro shadow, zéro blur, zéro border colorée animée
        "shadow-none border border-border/40",
        VARIANT_CLASSES[variant],
        className
      )}
    >
      {children}
    </div>
  );
}
