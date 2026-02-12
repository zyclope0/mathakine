"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { BadgeGrid } from "@/components/badges/BadgeGrid";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useBadges } from "@/hooks/useBadges";
import { Trophy, RefreshCw, Zap, Star, Target } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils/cn";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, LoadingState } from "@/components/layout";

function getJediRankInfo(rank: string, t: any): { title: string; icon: string; color: string } {
  const icons = {
    youngling: "🌟",
    padawan: "⚔️",
    knight: "🗡️",
    master: "👑",
    grand_master: "✨",
  };

  const colors = {
    youngling: "text-yellow-400",
    padawan: "text-blue-400",
    knight: "text-green-400",
    master: "text-purple-400",
    grand_master: "text-gold-400",
  };

  return {
    title: t(`jediRanks.${rank}`) || t("jediRanks.youngling"),
    icon: icons[rank as keyof typeof icons] ?? icons.youngling,
    color: colors[rank as keyof typeof colors] ?? colors.youngling,
  };
}

export default function BadgesPage() {
  const t = useTranslations("badges");
  const {
    earnedBadges,
    availableBadges,
    userStats,
    gamificationStats,
    isLoading,
    checkBadges,
    isChecking,
  } = useBadges();

  const handleCheckBadges = async () => {
    await checkBadges();
  };

  const jediRank = userStats?.jedi_rank || "youngling";
  const rankInfo = getJediRankInfo(jediRank, t);
  const earnedCount = earnedBadges.length;
  const totalCount = availableBadges.length;
  const progressPercent = totalCount > 0 ? (earnedCount / totalCount) * 100 : 0;

  return (
    <ProtectedRoute>
      <PageLayout>
        {/* En-tête */}
        <PageHeader
          title={t("title")}
          description={t("description")}
          icon={Trophy}
          actions={
            <Button
              variant="outline"
              onClick={handleCheckBadges}
              disabled={isChecking}
              className="btn-cta-primary flex items-center gap-2"
              aria-label={isChecking ? t("checking") : t("checkBadges")}
            >
              <RefreshCw
                className={cn("h-4 w-4", isChecking && "animate-spin")}
                aria-hidden="true"
              />
              {isChecking ? t("checking") : t("checkBadges")}
            </Button>
          }
        />

        {/* Statistiques de gamification */}
        {userStats && (
          <PageSection className="space-y-4 animate-fade-in-up-delay-1">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Card
                className="card-spatial-depth hover:shadow-lg transition-shadow"
                role="article"
                aria-label={t("stats.totalPoints")}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {t("stats.totalPoints")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3">
                    <Zap className="h-6 w-6 text-yellow-500" aria-hidden="true" />
                    <span className="text-3xl font-bold text-foreground">
                      {userStats.total_points || 0}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card
                className="card-spatial-depth hover:shadow-lg transition-shadow"
                role="article"
                aria-label={t("stats.currentLevel")}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {t("stats.currentLevel")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3">
                    <Star className="h-6 w-6 text-primary" aria-hidden="true" />
                    <span className="text-3xl font-bold text-foreground">
                      {userStats.current_level || 1}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card
                className="card-spatial-depth hover:shadow-lg transition-shadow"
                role="article"
                aria-label={`${t("stats.jediRank")}: ${rankInfo.title}`}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {t("stats.jediRank")}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-3">
                    <span className="text-3xl" aria-hidden="true">
                      {rankInfo.icon}
                    </span>
                    <span className={cn("text-xl font-semibold", rankInfo.color)}>
                      {rankInfo.title}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card
                className="card-spatial-depth hover:shadow-lg transition-shadow"
                role="article"
                aria-label={`${t("stats.badgesEarned")}: ${earnedCount} sur ${totalCount}`}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {t("stats.badgesEarned")}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Target className="h-6 w-6 text-green-500" aria-hidden="true" />
                    <span className="text-3xl font-bold text-foreground">
                      {earnedCount}/{totalCount}
                    </span>
                  </div>
                  <div
                    className="w-full bg-muted rounded-full h-3 overflow-hidden"
                    role="progressbar"
                    aria-valuenow={progressPercent}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`Progression: ${progressPercent.toFixed(0)}%`}
                  >
                    <div
                      className="bg-gradient-to-r from-primary to-accent h-3 rounded-full transition-all duration-700 ease-out"
                      style={{ width: `${progressPercent}%` }}
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </PageSection>
        )}

        {/* Statistiques de performance */}
        {gamificationStats && gamificationStats.performance && (
          <PageSection className="space-y-4 animate-fade-in-up-delay-2">
            <Card className="card-spatial-depth">
              <CardHeader>
                <CardTitle className="text-xl text-foreground">{t("performance.title")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">
                      {t("performance.totalAttempts")}
                    </div>
                    <div className="text-2xl font-bold text-foreground">
                      {gamificationStats.performance.total_attempts}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">
                      {t("performance.correctAttempts")}
                    </div>
                    <div className="text-2xl font-bold text-green-500">
                      {gamificationStats.performance.correct_attempts}
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">
                      {t("performance.successRate")}
                    </div>
                    <div className="text-2xl font-bold text-foreground">
                      {gamificationStats.performance.success_rate.toFixed(1)}%
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm text-muted-foreground">{t("performance.avgTime")}</div>
                    <div className="text-2xl font-bold text-foreground">
                      {gamificationStats.performance.avg_time_spent.toFixed(1)}s
                    </div>
                  </div>
                </div>

                {/* Répartition par catégorie */}
                {gamificationStats.badges_summary?.by_category &&
                  Object.keys(gamificationStats.badges_summary.by_category).length > 0 && (
                    <div className="mt-6 pt-6 border-t border-border">
                      <div className="text-sm font-medium text-muted-foreground mb-3">
                        {t("performance.byCategory")}
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(gamificationStats.badges_summary.by_category).map(
                          ([category, count]) => (
                            <Badge
                              key={category}
                              variant="outline"
                              className="text-sm"
                              aria-label={`${t(`categories.${category}`)}: ${count as number}`}
                            >
                              {category === "progression" && "📈"}
                              {category === "mastery" && "⭐"}
                              {category === "special" && "✨"} {t(`categories.${category}`)}:{" "}
                              {count as number}
                            </Badge>
                          )
                        )}
                      </div>
                    </div>
                  )}
              </CardContent>
            </Card>
          </PageSection>
        )}

        {/* Grille de badges */}
        <PageSection className="space-y-4 animate-fade-in-up-delay-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg md:text-xl font-semibold">
              {t("collection.title")}{" "}
              {t("collection.count", { earned: earnedCount, total: totalCount })}
            </h2>
          </div>
          {isLoading ? (
            <LoadingState message={t("loading")} />
          ) : (
            <BadgeGrid badges={availableBadges} earnedBadges={earnedBadges} isLoading={isLoading} />
          )}
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
