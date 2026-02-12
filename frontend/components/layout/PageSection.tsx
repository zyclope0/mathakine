"use client";

import { ReactNode } from "react";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils/cn";

interface PageSectionProps {
  title?: string;
  description?: string;
  icon?: LucideIcon;
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
  icon: Icon,
  children,
  className,
  headerClassName,
}: PageSectionProps) {
  return (
    <section className={cn("space-y-4", className)}>
      {(title || description) && (
        <div className={cn("space-y-2", headerClassName)}>
          {title && (
            <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
              {Icon && <Icon className="h-5 w-5 text-primary" />}
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
