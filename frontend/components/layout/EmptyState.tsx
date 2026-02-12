"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";
import { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: LucideIcon;
  action?: ReactNode;
  className?: string;
}

/**
 * EmptyState - État vide standardisé
 *
 * Garantit :
 * - Message clair et centré
 * - Icône optionnelle
 * - Action optionnelle
 * - Espacements cohérents
 */
export function EmptyState({ title, description, icon: Icon, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center py-12 text-center",
        "min-h-[12rem]",
        className
      )}
    >
      {Icon && <Icon className="h-16 w-16 text-muted-foreground mb-4" aria-hidden="true" />}
      <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
      {description && <p className="text-muted-foreground mb-4 max-w-md">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
