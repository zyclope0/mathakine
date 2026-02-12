"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, XCircle, ArrowUp, Clock } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useTranslations } from "next-intl";

interface ActivityItem {
  type: string;
  description: string;
  time: string;
  is_correct?: boolean;
}

interface RecentActivityProps {
  activities: ActivityItem[];
}

const getActivityIcon = (type: string, isCorrect?: boolean) => {
  if (type === "exercise_completed") {
    return isCorrect ? CheckCircle : XCircle;
  } else if (type === "level_up") {
    return ArrowUp;
  }
  return Clock;
};

const getActivityIconColor = (type: string, isCorrect?: boolean) => {
  if (type === "exercise_completed") {
    return isCorrect ? "text-success" : "text-destructive";
  } else if (type === "level_up") {
    return "text-primary-on-dark";
  }
  return "text-muted-foreground";
};

export function RecentActivity({ activities }: RecentActivityProps) {
  const t = useTranslations("dashboard.recentActivity");

  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <CardTitle className="text-xl text-foreground">
          {t("title", { default: "Activité récente" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {activities && activities.length > 0 ? (
          <div className="space-y-3">
            {activities.map((activity, index) => {
              const Icon = getActivityIcon(activity.type, activity.is_correct);
              const iconColor = getActivityIconColor(activity.type, activity.is_correct);

              // Générer une clé unique basée sur le contenu pour éviter les problèmes de ré-render
              const activityKey = `${activity.type}-${activity.time}-${activity.description}-${index}`;

              return (
                <div
                  key={activityKey}
                  className="flex items-start gap-3 p-3 rounded-lg bg-muted border border-primary/10 hover:border-primary/20 transition-colors"
                >
                  <div className={cn("flex-shrink-0 p-2 rounded-full bg-card", iconColor)}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-foreground">{activity.description}</div>
                    <div className="text-xs text-muted-foreground mt-1">{activity.time}</div>
                  </div>
                </div>
              );
            })}
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
