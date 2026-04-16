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
    <nav className="flex flex-wrap gap-2" aria-label={t("pageMap.label")}>
      {anchors.map(({ id, icon: Icon, labelKey }) => (
        <a
          key={id}
          href={`#${id}`}
          className={cn(
            "inline-flex min-h-11 items-center gap-1.5 rounded-full px-4 py-2",
            "border border-border/60 bg-[var(--bg-learner,var(--card))]",
            "text-xs font-medium text-muted-foreground",
            "hover:border-primary/40 hover:text-primary hover:bg-primary/5",
            "transition-colors duration-150 motion-reduce:transition-none",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          )}
        >
          <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
          {t(labelKey)}
        </a>
      ))}
    </nav>
  );
}
