"use client";

import { useState, useMemo } from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { BadgeGrid } from "@/components/badges/BadgeGrid";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useBadges } from "@/hooks/useBadges";
import { useBadgesProgress } from "@/hooks/useBadgesProgress";
import {
  Trophy,
  RefreshCw,
  Zap,
  Star,
  Target,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Filter,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, LoadingState } from "@/components/layout";

function getJediRankInfo(rank: string, t: (k: string) => string): { title: string; icon: string; color: string } {
  const icons: Record<string, string> = {
    youngling: "🌟",
    padawan: "⚔️",
    knight: "🗡️",
    master: "👑",
    grand_master: "✨",
  };
  const colors: Record<string, string> = {
    youngling: "text-yellow-400",
    padawan: "text-blue-400",
    knight: "text-green-400",
    master: "text-purple-400",
    grand_master: "text-gold-400",
  };
  return {
    title: t(`jediRanks.${rank}`) || t("jediRanks.youngling"),
    icon: icons[rank] || "🌟",
    color: colors[rank] || "text-yellow-400",
  };
}

export default function BadgesPage() {
  const t = useTranslations("badges");
  const tCommon = useTranslations("common");
  const {
    earnedBadges,
    availableBadges,
    userStats,
    gamificationStats,
    rarityMap,
    pinnedBadgeIds,
    pinBadges,
    isLoading,
    checkBadges,
    isChecking,
  } = useBadges();
  const { inProgress, isLoading: isLoadingProgress } = useBadgesProgress();
  const [statsExpanded, setStatsExpanded] = useState(false);

  // A-3 : filtres et tri
  const [filterStatus, setFilterStatus] = useState<"all" | "earned" | "locked" | "close">("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [filterDifficulty, setFilterDifficulty] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"progress" | "date" | "points" | "category">("category");

  const handleCheckBadges = async () => {
    await checkBadges();
  };

  const jediRank = userStats?.jedi_rank || "youngling";
  const rankInfo = getJediRankInfo(jediRank, t);
  const earnedCount = earnedBadges.length;
  const totalCount = availableBadges.length;
  const progressPercent = totalCount > 0 ? (earnedCount / totalCount) * 100 : 0;

  // Séparation : obtenus vs à débloquer (plan A-1 : Ma collection / À débloquer)
  const earnedBadgeIds = new Set(earnedBadges.map((ub) => ub.id));
  const earnedBadgesList = availableBadges.filter((b) => earnedBadgeIds.has(b.id));
  const lockedBadgesList = availableBadges.filter((b) => !earnedBadgeIds.has(b.id));

  // Map progression pour BadgeCard (A-2)
  const progressMap = inProgress.reduce(
    (acc, b) => {
      if (b.target != null && b.target > 0) {
        acc[b.id] = { current: b.current ?? 0, target: b.target, progress: b.progress ?? 0 };
      }
      return acc;
    },
    {} as Record<number, { current: number; target: number; progress: number }>
  );

  // A-3 : listes filtrées
  const { filteredEarned, filteredLocked, categories, difficulties } = useMemo(() => {
    const catSet = new Set<string>();
    const diffSet = new Set<string>();
    availableBadges.forEach((b) => {
      if (b.category) catSet.add(b.category);
      if (b.difficulty) diffSet.add(b.difficulty);
    });
    const categories = Array.from(catSet).sort();
    const difficulties = Array.from(diffSet).sort();

    const matchesCategory = (b: (typeof availableBadges)[0]) =>
      filterCategory === "all" || (b.category ?? "") === filterCategory;
    const matchesDifficulty = (b: (typeof availableBadges)[0]) =>
      filterDifficulty === "all" || (b.difficulty ?? "") === filterDifficulty;

    let earned = earnedBadgesList.filter((b) => matchesCategory(b) && matchesDifficulty(b));
    let locked = lockedBadgesList.filter((b) => matchesCategory(b) && matchesDifficulty(b));

    if (filterStatus === "earned") locked = [];
    else if (filterStatus === "locked") earned = [];
    else if (filterStatus === "close") {
      earned = [];
      locked = locked.filter((b) => {
        const p = progressMap[b.id];
        return p && p.progress >= 0.5;
      });
    }

    return { filteredEarned: earned, filteredLocked: locked, categories, difficulties };
  }, [
    earnedBadgesList,
    lockedBadgesList,
    filterStatus,
    filterCategory,
    filterDifficulty,
    progressMap,
  ]);

  const closeCount = lockedBadgesList.filter((b) => {
    const p = progressMap[b.id];
    return p && p.progress >= 0.5;
  }).length;

  const hasActiveFilters =
    filterStatus !== "all" ||
    filterCategory !== "all" ||
    filterDifficulty !== "all" ||
    sortBy !== "category";
  const clearFilters = () => {
    setFilterStatus("all");
    setFilterCategory("all");
    setFilterDifficulty("all");
    setSortBy("category");
  };

  return (
    <ProtectedRoute>
      <PageLayout maxWidth="2xl">
        {/* En-tête allégé : titre + stats condensées (A-1) */}
        <div className="space-y-4">
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
                title={t("checkBadgesTooltip")}
              >
                <RefreshCw
                  className={cn("h-4 w-4", isChecking && "animate-spin")}
                  aria-hidden="true"
                />
                {isChecking ? t("checking") : t("checkBadges")}
              </Button>
            }
          />
          {/* Barre stats condensée */}
          {userStats && (
            <div
              className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground"
              role="region"
              aria-label={t("statsCompact")}
            >
              <span className="flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-yellow-500" aria-hidden="true" />
                <strong className="text-foreground">{userStats.total_points ?? 0}</strong> pts
              </span>
              <span className="flex items-center gap-1.5" title={t("stats.levelTooltip")}>
                <Star className="h-4 w-4 text-primary" aria-hidden="true" />
                <strong className="text-foreground">Niv. {userStats.current_level ?? 1}</strong>
              </span>
              <span className={cn("flex items-center gap-1.5", rankInfo.color)} title={t("stats.rankTooltip")}>
                <span aria-hidden="true">{rankInfo.icon}</span>
                <strong>{rankInfo.title}</strong>
              </span>
              <span className="flex items-center gap-1.5">
                <Target className="h-4 w-4 text-green-500" aria-hidden="true" />
                <strong className="text-foreground">{earnedCount}/{totalCount}</strong> badges
              </span>
              <div
                className="w-24 bg-muted rounded-full h-2 overflow-hidden"
                role="progressbar"
                aria-valuenow={progressPercent}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Progression: ${progressPercent.toFixed(0)}%`}
              >
                <div
                  className="bg-gradient-to-r from-primary to-accent h-2 rounded-full transition-all duration-700"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* A-3 : barre filtres et tri */}
        <PageSection className="space-y-4 animate-fade-in-up">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-primary" aria-hidden="true" />
              <h2 className="text-lg font-semibold">{t("filters.title")}</h2>
            </div>
            {closeCount > 0 && (
              <Button
                variant={filterStatus === "close" ? "default" : "outline"}
                size="sm"
                onClick={() => setFilterStatus("close")}
                className={cn(
                  filterStatus === "close" && "ring-2 ring-primary ring-offset-2 ring-offset-background"
                )}
              >
                <Target className="h-4 w-4 mr-1" aria-hidden="true" />
                {t("filters.statusClose")} ({closeCount})
              </Button>
            )}
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters} className="gap-1">
                <X className="h-4 w-4" aria-hidden="true" />
                {t("filters.reset")}
              </Button>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <label htmlFor="filter-status" className="text-sm text-muted-foreground">
                {t("filters.status")}
              </label>
              <Select value={filterStatus} onValueChange={(v) => setFilterStatus(v as typeof filterStatus)}>
                <SelectTrigger id="filter-status" className="h-10 w-[160px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("filters.statusAll")}</SelectItem>
                  <SelectItem value="earned">{t("filters.statusEarned")}</SelectItem>
                  <SelectItem value="locked">{t("filters.statusLocked")}</SelectItem>
                  <SelectItem value="close">{t("filters.statusClose")}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <label htmlFor="filter-category" className="text-sm text-muted-foreground">
                {t("filters.category")}
              </label>
              <Select value={filterCategory} onValueChange={setFilterCategory}>
                <SelectTrigger id="filter-category" className="h-10 w-[140px]">
                  <SelectValue placeholder={t("filters.categoryAll")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("filters.categoryAll")}</SelectItem>
                  {categories.map((c) => (
                    <SelectItem key={c} value={c}>
                      {t(`categories.${c}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <label htmlFor="filter-difficulty" className="text-sm text-muted-foreground">
                {t("filters.difficulty")}
              </label>
              <Select value={filterDifficulty} onValueChange={setFilterDifficulty}>
                <SelectTrigger id="filter-difficulty" className="h-10 w-[140px]">
                  <SelectValue placeholder={t("filters.difficultyAll")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("filters.difficultyAll")}</SelectItem>
                  {difficulties.map((d) => (
                    <SelectItem key={d} value={d}>
                      {t(`difficulties.${d}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <label htmlFor="sort-by" className="text-sm text-muted-foreground">
                {t("filters.sort")}
              </label>
              <Select value={sortBy} onValueChange={(v) => setSortBy(v as typeof sortBy)}>
                <SelectTrigger id="sort-by" className="h-10 w-[200px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="progress">{t("filters.sortProgress")}</SelectItem>
                  <SelectItem value="date">{t("filters.sortDate")}</SelectItem>
                  <SelectItem value="points">{t("filters.sortPoints")}</SelectItem>
                  <SelectItem value="category">{t("filters.sortCategory")}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </PageSection>

        {/* 1) Ma collection — badges obtenus (endowment, A-1) */}
        <PageSection className="space-y-4 animate-fade-in-up-delay-1">
          <h2 className="text-lg md:text-xl font-semibold">
            {t("collection.title")}{" "}
            {t("collection.count", {
              earned: filteredEarned.length,
              total: filteredEarned.length + filteredLocked.length || totalCount,
            })}
          </h2>
          {isLoading ? (
            <LoadingState message={t("loading")} />
          ) : filteredEarned.length > 0 ? (
            <BadgeGrid
              badges={(() => {
                type BadgeItem = (typeof filteredEarned)[number];
                const pinned = pinnedBadgeIds
                  .map((id: number) => filteredEarned.find((b: BadgeItem) => b.id === id))
                  .filter((b: BadgeItem | undefined): b is BadgeItem => !!b);
                const rest = filteredEarned.filter((b: BadgeItem) => !pinnedBadgeIds.includes(b.id));
                return [...pinned, ...rest];
              })()}
              earnedBadges={earnedBadges.filter((ub) => filteredEarned.some((b: (typeof filteredEarned)[number]) => b.id === ub.id))}
              isLoading={false}
              sortBy={sortBy}
              rarityMap={rarityMap}
              pinnedBadgeIds={pinnedBadgeIds}
              onTogglePin={async (badgeId) => {
                const isPinned = pinnedBadgeIds.includes(badgeId);
                const next = isPinned
                  ? pinnedBadgeIds.filter((id: number) => id !== badgeId)
                  : [...pinnedBadgeIds, badgeId].slice(0, 3);
                await pinBadges(next);
              }}
            />
          ) : (
            <p className="text-muted-foreground py-6" role="status">
              {hasActiveFilters && earnedBadgesList.length > 0
                ? t("collection.noResults")
                : t("collection.empty")}
            </p>
          )}
        </PageSection>

        {/* 2) Badges en cours — progression vers les prochains (A-1), exclut 0/0 (non mesurables) */}
        {(() => {
          const inProgressWithTarget = inProgress.filter((b) => b.target != null && b.target > 0);
          return inProgressWithTarget.length > 0 ? (
            <PageSection className="space-y-4 animate-fade-in-up-delay-2">
              <h2 className="text-lg md:text-xl font-semibold flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" aria-hidden="true" />
                {tCommon("badgesProgressTitle")}
              </h2>
              <div className="grid gap-3 grid-cols-1 xl:grid-cols-2">
                {inProgressWithTarget.map((badge) => {
                  const fullBadge = availableBadges.find((b) => b.id === badge.id);
                  const catIcon =
                    fullBadge?.category === "progression"
                      ? "📈"
                      : fullBadge?.category === "mastery"
                        ? "⭐"
                        : fullBadge?.category === "special"
                          ? "✨"
                          : "🏆";
                  const diffIcon =
                    fullBadge?.difficulty === "gold"
                      ? "🥇"
                      : fullBadge?.difficulty === "silver"
                        ? "🥈"
                        : fullBadge?.difficulty === "legendary"
                          ? "💎"
                          : "🥉";
                  return (
                    <Card key={badge.id} className="card-spatial-depth">
                      <CardContent className="pt-4">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-2xl shrink-0" aria-hidden="true">
                            {catIcon}
                          </span>
                          <span className="text-lg shrink-0 opacity-75" aria-hidden="true">
                            {diffIcon}
                          </span>
                          <span className="font-medium flex-1 min-w-0">{badge.name}</span>
                          <span className="text-sm font-semibold text-foreground tabular-nums shrink-0">
                            {badge.current ?? 0} / {badge.target}
                          </span>
                        </div>
                        {badge.progress != null && (
                          <div
                            className="w-full bg-muted rounded-full h-2.5 overflow-hidden ring-1 ring-inset ring-border/50"
                            role="progressbar"
                            aria-valuenow={Math.round((badge.progress ?? 0) * 100)}
                            aria-valuemin={0}
                            aria-valuemax={100}
                            aria-label={`${badge.name}: ${Math.round((badge.progress ?? 0) * 100)}%`}
                          >
                            <div
                              className="bg-primary h-2.5 rounded-full transition-all duration-500 min-w-[2px]"
                              style={{ width: `${Math.max((badge.progress ?? 0) * 100, 2)}%` }}
                            />
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </PageSection>
          ) : null;
        })()}

        {/* 3) À débloquer — badges verrouillés avec conditions (A-1, A-2) */}
        {filteredLocked.length > 0 && (
          <PageSection className="space-y-4 animate-fade-in-up-delay-3">
            <h2 className="text-lg md:text-xl font-semibold">{t("collection.toUnlock")}</h2>
            <BadgeGrid
              badges={filteredLocked}
              earnedBadges={[]}
              progressMap={progressMap}
              isLoading={false}
              sortBy={sortBy}
              rarityMap={rarityMap}
            />
          </PageSection>
        )}

        {/* 4) Stats détaillées — repliable (A-1) */}
        {gamificationStats?.performance && (
          <PageSection className="animate-fade-in-up-delay-3">
            <Button
              variant="ghost"
              size="sm"
              className="text-muted-foreground hover:text-foreground -ml-2"
              onClick={() => setStatsExpanded(!statsExpanded)}
              aria-expanded={statsExpanded}
            >
              {statsExpanded ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" aria-hidden="true" />
                  {t("statsDetails.hide")}
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" aria-hidden="true" />
                  {t("statsDetails.show")}
                </>
              )}
            </Button>
            {statsExpanded && (
              <Card className="card-spatial-depth mt-3">
                <CardHeader>
                  <CardTitle className="text-xl text-foreground">{t("performance.title")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground">{t("performance.totalAttempts")}</div>
                      <div className="text-2xl font-bold text-foreground">
                        {gamificationStats.performance.total_attempts}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground">{t("performance.correctAttempts")}</div>
                      <div className="text-2xl font-bold text-green-500">
                        {gamificationStats.performance.correct_attempts}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-muted-foreground">{t("performance.successRate")}</div>
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
            )}
          </PageSection>
        )}
      </PageLayout>
    </ProtectedRoute>
  );
}
