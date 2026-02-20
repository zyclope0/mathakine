"use client";

import { useAcademyStats } from "@/hooks/useAcademyStats";
import { Card, CardContent } from "@/components/ui/card";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { BookOpen, Sparkles, Target, Users, Puzzle } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils/cn";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { useTranslations } from "next-intl";

/**
 * Widget affichant les statistiques globales de l'Académie
 *
 * Affiche sur la page d'accueil :
 * - Nombre total d'exercices et défis disponibles
 * - Taux de maîtrise global
 * - Nombre de contenus générés par IA
 * - Citation de sagesse
 *
 * Chaque stat a un tooltip explicatif au hover.
 */
export function AcademyStatsWidget() {
  const { stats, isLoading, error } = useAcademyStats();
  const { shouldReduceMotion } = useAccessibleAnimation();
  const t = useTranslations("home.academy");

  // Ne rien afficher en cas d'erreur (widget optionnel)
  if (error || (!isLoading && !stats)) {
    return null;
  }

  // Skeleton loader
  if (isLoading) {
    return (
      <Card className="bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5 border-primary/10">
        <CardContent className="py-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="text-center space-y-2">
                <Skeleton className="h-8 w-8 mx-auto rounded-full" />
                <Skeleton className="h-6 w-12 mx-auto" />
                <Skeleton className="h-4 w-20 mx-auto" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const { academy_statistics, global_performance, sage_wisdom } = stats!;

  const statItems = [
    {
      icon: BookOpen,
      value: academy_statistics.total_exercises,
      label: t("exercises.label"),
      tooltip: t("exercises.tooltip"),
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
    },
    {
      icon: Puzzle,
      value: academy_statistics.total_challenges,
      label: t("challenges.label"),
      tooltip: t("challenges.tooltip"),
      color: "text-indigo-500",
      bgColor: "bg-indigo-500/10",
    },
    {
      icon: Target,
      value: `${Math.round(global_performance.mastery_rate)}%`,
      label: t("mastery.label"),
      tooltip: t("mastery.tooltip"),
      color: "text-green-500",
      bgColor: "bg-green-500/10",
    },
    {
      icon: Sparkles,
      value: academy_statistics.ai_generated,
      label: t("aiGenerated.label"),
      tooltip: t("aiGenerated.tooltip"),
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
    },
    {
      icon: Users,
      value: global_performance.total_attempts,
      label: t("attempts.label"),
      tooltip: t("attempts.tooltip"),
      color: "text-orange-500",
      bgColor: "bg-orange-500/10",
    },
  ];

  return (
    <Card
      className={cn(
        "bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5 border-primary/10",
        !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4"
      )}
    >
      <CardContent className="py-6 space-y-4">
        {/* Titre */}
        <div className="text-center">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            {t("title")}
          </h3>
        </div>

        {/* Stats en grille */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {statItems.map((item) => {
            const Icon = item.icon;
            return (
              <Tooltip key={item.label}>
                <TooltipTrigger asChild>
                  <div
                    className="text-center space-y-1 cursor-help transition-transform hover:scale-105"
                    tabIndex={0}
                    role="group"
                    aria-label={`${item.label}: ${item.value}. ${item.tooltip}`}
                  >
                    <div
                      className={cn(
                        "mx-auto flex h-10 w-10 items-center justify-center rounded-full",
                        item.bgColor
                      )}
                    >
                      <Icon className={cn("h-5 w-5", item.color)} aria-hidden="true" />
                    </div>
                    <div className="text-xl md:text-2xl font-bold">{item.value}</div>
                    <div className="text-xs text-muted-foreground">{item.label}</div>
                  </div>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs text-center">{item.tooltip}</TooltipContent>
              </Tooltip>
            );
          })}
        </div>

        {/* Citation de sagesse */}
        {sage_wisdom && (
          <div className="text-center pt-2 border-t border-primary/10">
            <p className="text-sm italic text-muted-foreground">&quot;{sage_wisdom}&quot;</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
