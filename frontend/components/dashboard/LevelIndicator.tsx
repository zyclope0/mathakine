"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useTranslations } from "next-intl";

interface LevelIndicatorProps {
  level: {
    current: number;
    title: string;
    current_xp: number;
    next_level_xp: number;
  };
}

export function LevelIndicator({ level }: LevelIndicatorProps) {
  const t = useTranslations("dashboard.levelIndicator");

  const progressPercent =
    level.next_level_xp > 0 ? Math.min((level.current_xp / level.next_level_xp) * 100, 100) : 0;

  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <CardTitle className="text-xl text-foreground">
          {t("title", { default: "Niveau actuel" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="flex-shrink-0">
            <Badge
              className="h-16 w-16 rounded-full flex items-center justify-center text-2xl font-bold bg-primary text-primary-foreground"
              aria-label={`${t("level", { default: "Niveau" })} ${level.current}`}
            >
              {level.current}
            </Badge>
          </div>
          <div className="flex-1 space-y-2">
            <div className="font-semibold text-lg text-foreground">{level.title}</div>
            <div className="space-y-1">
              <Progress
                value={progressPercent}
                className="h-2"
                aria-label={`${progressPercent.toFixed(0)}% ${t("xp", { default: "XP" })}`}
              />
              <div className="text-sm text-muted-foreground">
                {level.current_xp}/{level.next_level_xp} {t("xp", { default: "XP" })}{" "}
                {t("xpForNextLevel", {
                  level: level.current + 1,
                  default: `pour le niveau ${level.current + 1}`,
                })}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
