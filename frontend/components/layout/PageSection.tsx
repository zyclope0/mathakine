"use client";

import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface PageSectionProps {
  title?: string;
  description?: string;
  /**
   * Pass a rendered icon element (e.g. `<Sparkles className="h-5 w-5 text-primary" aria-hidden />`),
   * not a Lucide component reference, when the parent is a Server Component (non-serializable across the boundary).
   */
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
  headerClassName?: string;
}

/**
 * PageSection - Section de page standardisée
 *
 * Garantit :
 * - Espacements cohérents
 * - Hiérarchie visuelle claire
 */
export function PageSection({
  title,
  description,
  icon,
  children,
  className,
  headerClassName,
}: PageSectionProps) {
  return (
    <section className={cn("space-y-5", className)}>
      {(title || description) && (
        <div className={cn("space-y-2", headerClassName)}>
          {title && (
            <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
              {icon ? <span className="inline-flex shrink-0 items-center">{icon}</span> : null}
              {title}
            </h2>
          )}
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      )}
      <div>{children}</div>
    </section>
  );
}
