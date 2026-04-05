"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  actions?: ReactNode;
  className?: string;
}

/**
 * PageHeader - En-tête standardisé pour toutes les pages
 *
 * Garantit :
 * - Hiérarchie typographique cohérente
 * - Espacements standardisés
 * - Actions alignées à droite
 */
export function PageHeader({
  title,
  description,
  icon: Icon,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <div
      className={cn("flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4", className)}
    >
      <div className="flex-1 min-w-0">
        <h1 className="text-3xl font-bold text-foreground flex items-center gap-2 leading-tight">
          {Icon && <Icon className="h-8 w-8 text-primary shrink-0" aria-hidden="true" />}
          <span className="truncate sm:overflow-visible sm:whitespace-normal">{title}</span>
        </h1>
        {description && <p className="text-muted-foreground mt-1.5 text-sm">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2 flex-shrink-0">{actions}</div>}
    </div>
  );
}
