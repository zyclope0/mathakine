"use client";

import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ElementType } from "react";

interface CompactListItemProps {
  title: string;
  subtitle: string;
  TypeIcon: ElementType;
  aiGenerated?: boolean;
  completed: boolean;
  typeDisplay: string;
  ageDisplay?: string;
  onClick: () => void;
}

/**
 * Ligne de liste compacte partagée entre exercises/page et challenges/page.
 * Affiche icône de type, titre, badges et indicateurs IA/complété.
 */
export function CompactListItem({
  title,
  subtitle,
  TypeIcon,
  aiGenerated,
  completed,
  typeDisplay,
  ageDisplay,
  onClick,
}: CompactListItemProps) {
  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all",
        "bg-card border-border/60",
        "hover:bg-accent hover:border-primary/50 hover:shadow-md",
        completed && "bg-emerald-500/5 border-emerald-500/30"
      )}
    >
      {/* Icône du type */}
      <div
        className={cn(
          "flex-shrink-0 h-10 w-10 rounded-lg flex items-center justify-center",
          "bg-primary/10 border border-primary/20"
        )}
      >
        <TypeIcon className="h-5 w-5 text-primary" aria-hidden="true" />
      </div>

      {/* Infos principales */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h3 className="font-medium truncate text-sm">{title}</h3>
          {aiGenerated && (
            <Sparkles className="h-3.5 w-3.5 text-amber-500 flex-shrink-0" aria-hidden="true" />
          )}
          {completed && (
            <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0" aria-hidden="true" />
          )}
        </div>
        <p className="text-xs text-muted-foreground truncate mt-0.5">{subtitle}</p>
      </div>

      {/* Badges type + âge (masqués sur mobile) */}
      <div className="hidden sm:flex items-center gap-2 flex-shrink-0">
        <Badge variant="outline" className="text-xs">
          {typeDisplay}
        </Badge>
        {ageDisplay && (
          <Badge variant="outline" className="text-xs">
            {ageDisplay}
          </Badge>
        )}
      </div>
    </div>
  );
}
