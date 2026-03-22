"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
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

  const denom = level.next_level_xp > 0 ? level.next_level_xp : 1;
  const progressPercent = Math.min((level.current_xp / denom) * 100, 100);

  return (
    <Card className="dashboard-card-surface overflow-hidden">
      <CardContent className="p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row items-center gap-6 sm:gap-10">
          <div className="relative flex-shrink-0">
            <div className="h-24 w-24 rounded-full bg-primary/15 ring-2 ring-primary/30 flex items-center justify-center shadow-lg shadow-primary/20">
              <span
                className="text-5xl font-black tabular-nums bg-gradient-to-br from-primary to-primary/60 bg-clip-text text-transparent leading-none"
                aria-label={`${t("level")} ${level.current}`}
              >
                {level.current}
              </span>
            </div>
            <div className="absolute inset-0 rounded-full bg-primary/10 blur-xl -z-10" />
          </div>

          <div className="flex-1 w-full space-y-3 text-center sm:text-left">
            <div>
              <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-0.5">
                {t("title")}
              </p>
              <h3 className="text-2xl font-bold text-foreground">{level.title}</h3>
            </div>

            <div className="space-y-1.5">
              <Progress
                value={progressPercent}
                className="h-3"
                aria-label={`${Math.round(progressPercent)}% XP`}
              />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>
                  {level.current_xp.toLocaleString()} {t("xp")}
                </span>
                <span>
                  {t("xpForNextLevel", { level: level.current + 1 })} —{" "}
                  {level.next_level_xp.toLocaleString()} {t("xp")}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
