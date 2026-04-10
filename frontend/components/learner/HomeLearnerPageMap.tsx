"use client";

import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import type { HomeLearnerNamespaceT } from "@/components/learner/homeLearnerI18n";

export interface HomeLearnerPageAnchor {
  id: string;
  icon: LucideIcon;
  labelKey: string;
}

interface HomeLearnerPageMapProps {
  anchors: HomeLearnerPageAnchor[];
  t: HomeLearnerNamespaceT;
}

export function HomeLearnerPageMap({ anchors, t }: HomeLearnerPageMapProps) {
  return (
    <nav className="mt-4 flex flex-wrap gap-2" aria-label={t("pageMap.label")}>
      {anchors.map(({ id, icon: Icon, labelKey }) => (
        <a
          key={id}
          href={`#${id}`}
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5",
            "border border-border/60 bg-[var(--bg-learner,var(--card))]",
            "text-xs font-medium text-muted-foreground",
            "hover:border-primary/40 hover:text-primary hover:bg-primary/5",
            "transition-colors duration-150",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
          )}
        >
          <Icon className="h-3.5 w-3.5" aria-hidden="true" />
          {t(labelKey)}
        </a>
      ))}
    </nav>
  );
}
