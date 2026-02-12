"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

interface PageLayoutProps {
  children: ReactNode;
  className?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full";
}

const maxWidthClasses = {
  sm: "max-w-2xl",
  md: "max-w-4xl",
  lg: "max-w-6xl",
  xl: "max-w-7xl",
  "2xl": "max-w-[1536px]",
  full: "max-w-full",
};

/**
 * PageLayout - Layout standardisé pour toutes les pages
 *
 * Garantit :
 * - Padding responsive cohérent
 * - Container avec max-width
 * - Espacements verticaux standardisés
 *
 * NOTE: Ne pas ajouter min-h-screen ici, c'est géré par layout.tsx
 */
export function PageLayout({ children, className, maxWidth = "xl" }: PageLayoutProps) {
  return (
    <div className={cn("py-4 px-3 sm:px-4 md:px-6 lg:px-8", className)}>
      <div className={cn("mx-auto space-y-4 md:space-y-6", maxWidthClasses[maxWidth])}>
        {children}
      </div>
    </div>
  );
}
