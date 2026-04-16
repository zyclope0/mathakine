"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, XCircle, Zap, Activity, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { formatDistanceToNow, isToday, isYesterday, format } from "date-fns";
import { fr, enUS } from "date-fns/locale";

interface ActivityItem {
  type: string;
  description: string;
  time: string;
  is_correct?: boolean;
}

interface RecentActivityProps {
  activities: ActivityItem[];
}

const INITIAL_COUNT = 5;

function formatActivityTime(time: string, locale: string): string {
  try {
    const date = new Date(time);
    if (isNaN(date.getTime())) return time;

    const diffMs = Date.now() - date.getTime();
    const diffMins = diffMs / 60_000;

    if (diffMins < 1) return locale === "en" ? "Just now" : "À l'instant";
    if (diffMins < 60) {
      const mins = Math.round(diffMins);
      return locale === "en" ? `${mins} min ago` : `Il y a ${mins} min`;
    }
    if (isToday(date)) {
      const t = format(date, "HH:mm");
      return locale === "en" ? `Today at ${t}` : `Aujourd'hui à ${t}`;
    }
    if (isYesterday(date)) {
      const t = format(date, "HH:mm");
      return locale === "en" ? `Yesterday at ${t}` : `Hier à ${t}`;
    }
    return formatDistanceToNow(date, { addSuffix: true, locale: locale === "en" ? enUS : fr });
  } catch {
    /* swallowed: invalid date string, raw value returned */
    return time;
  }
}

interface ItemStyle {
  border: string;
  iconBg: string;
  iconColor: string;
  Icon: typeof Activity;
}

function getItemStyle(type: string, isCorrect?: boolean): ItemStyle {
  if (type === "exercise_completed") {
    return isCorrect
      ? {
          border: "border-l-[3px] border-success/60",
          iconBg: "bg-success/10",
          iconColor: "text-success",
          Icon: CheckCircle2,
        }
      : {
          border: "border-l-[3px] border-destructive/60",
          iconBg: "bg-destructive/10",
          iconColor: "text-destructive",
          Icon: XCircle,
        };
  }
  if (type === "level_up") {
    return {
      border: "border-l-[3px] border-primary/60",
      iconBg: "bg-primary/10",
      iconColor: "text-primary",
      Icon: Zap,
    };
  }
  return {
    border: "border-l-[3px] border-border/40",
    iconBg: "bg-muted/50",
    iconColor: "text-muted-foreground",
    Icon: Activity,
  };
}

export function RecentActivity({ activities }: RecentActivityProps) {
  const t = useTranslations("dashboard.recentActivity");
  const { locale } = useLocaleStore();
  const [showAll, setShowAll] = useState(false);

  const visible = showAll ? activities : activities.slice(0, INITIAL_COUNT);
  const remaining = activities.length - INITIAL_COUNT;
  const hasMore = remaining > 0;

  return (
    <Card className="dashboard-card-surface">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
          <Activity className="w-5 h-5 text-primary" />
          {t("title", { default: "Journal d'activité" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {activities && activities.length > 0 ? (
          <div className="space-y-1.5">
            {visible.map((activity, index) => {
              const { border, iconBg, iconColor, Icon } = getItemStyle(
                activity.type,
                activity.is_correct
              );
              const key = `${activity.type}-${activity.time}-${index}`;

              return (
                <div
                  key={key}
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-3 py-2.5",
                    "bg-muted/30 transition-colors duration-150 hover:bg-muted/45",
                    border
                  )}
                >
                  <div
                    className={cn(
                      "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center",
                      iconBg
                    )}
                  >
                    <Icon className={cn("h-4 w-4", iconColor)} />
                  </div>

                  <p className="flex-1 min-w-0 text-sm font-medium text-foreground truncate">
                    {activity.description}
                  </p>

                  <span className="flex-shrink-0 text-xs text-muted-foreground tabular-nums whitespace-nowrap">
                    {formatActivityTime(activity.time, locale)}
                  </span>
                </div>
              );
            })}

            {hasMore && !showAll && (
              <div className="relative pt-1">
                <div className="pointer-events-none absolute -top-8 left-0 right-0 h-8 bg-gradient-to-t from-card/90 to-transparent" />
                <button
                  onClick={() => setShowAll(true)}
                  className="mt-1 w-full inline-flex items-center justify-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary/10"
                >
                  <ChevronDown className="h-4 w-4" />
                  {t("showMore", {
                    count: remaining,
                    default: `Voir ${remaining} entrée(s) de plus`,
                  })}
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <p>{t("empty", { default: "Aucune activité récente." })}</p>
            <p className="text-sm mt-2">
              {t("emptyHint", {
                default: "Commencez à résoudre des exercices pour voir votre progression !",
              })}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
