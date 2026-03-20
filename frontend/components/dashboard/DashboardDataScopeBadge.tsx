"use client";

import { Badge } from "@/components/ui/badge";
import { useTranslations } from "next-intl";

/** Compact scope label for cumulative / all-time dashboard widgets. */
export function DashboardDataScopeBadge() {
  const t = useTranslations("dashboard.scope");
  return (
    <Badge
      variant="outline"
      className="shrink-0 border-border/80 bg-muted/40 text-muted-foreground font-normal text-[0.7rem] leading-tight px-2 py-0.5 min-h-8 sm:min-h-0"
    >
      {t("cumulative")}
    </Badge>
  );
}
