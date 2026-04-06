"use client";

import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { Trophy } from "lucide-react";
import { useBadges } from "@/hooks/useBadges";
import { useBadgesProgress } from "@/hooks/useBadgesProgress";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader } from "@/components/layout";
import { useBadgesPageController } from "@/hooks/useBadgesPageController";
import type { RarityInfo } from "@/components/badges/BadgeGrid";
import { getProgressionRankInfo, sortEarnedWithPinned } from "@/lib/badges/badgesPage";
import { BadgesHeaderStats } from "@/components/badges/BadgesHeaderStats";
import { BadgesMotivationBanner } from "@/components/badges/BadgesMotivationBanner";
import { BadgesLastExploitsSection } from "@/components/badges/BadgesLastExploitsSection";
import { BadgesClosestSection } from "@/components/badges/BadgesClosestSection";
import { BadgesFiltersBar } from "@/components/badges/BadgesFiltersBar";
import { BadgesCollectionSection } from "@/components/badges/BadgesCollectionSection";
import { BadgesProgressTabsSection } from "@/components/badges/BadgesProgressTabsSection";
import { BadgesDetailedStatsSection } from "@/components/badges/BadgesDetailedStatsSection";

export default function BadgesPage() {
  const t = useTranslations("badges");
  const tProgRank = useTranslations("progressionRanks");

  const {
    earnedBadges,
    availableBadges,
    userStats,
    gamificationStats,
    rarityMap,
    pinnedBadgeIds,
    pinBadges,
    isLoading,
    error,
    checkBadges,
    isChecking,
  } = useBadges();

  const { inProgress } = useBadgesProgress();

  const progressionRankBucket = userStats?.progression_rank ?? userStats?.jedi_rank ?? "cadet";
  const rankInfo = getProgressionRankInfo(progressionRankBucket, tProgRank);
  const earnedCount = earnedBadges.length;

  const ctrl = useBadgesPageController({
    earnedBadges,
    availableBadges,
    inProgress,
    earnedCount,
    isLoading,
    rankInfo,
  });

  const visibleTotal = availableBadges.filter(
    (b) => !(b.is_secret === true) || ctrl.earnedBadgeIds.has(b.id)
  ).length;

  const sortedEarnedFinal = sortEarnedWithPinned(ctrl.filtered.filteredEarned, pinnedBadgeIds);

  return (
    <ProtectedRoute requireFullAccess>
      <PageLayout maxWidth="2xl">
        {/* En-tête + stats condensées */}
        <div className="space-y-4">
          <PageHeader
            title={t("title")}
            description={t("description")}
            icon={Trophy}
            actions={
              <Button
                variant="outline"
                onClick={() => checkBadges()}
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
          {userStats && (
            <BadgesHeaderStats
              totalPoints={userStats.total_points ?? 0}
              currentLevel={userStats.current_level ?? 1}
              rankInfo={rankInfo}
              earnedCount={earnedCount}
              totalCount={visibleTotal}
              progressPercent={ctrl.progressPercent}
              statsCompactLabel={t("statsCompact")}
              levelTooltip={t("stats.levelTooltip")}
              rankTooltip={t("stats.rankTooltip")}
            />
          )}
        </div>

        {/* Bandeau motivationnel */}
        {ctrl.motivationInfo && !isLoading && (
          <BadgesMotivationBanner
            motivationInfo={ctrl.motivationInfo}
            earnedCount={earnedCount}
            labelPlural={t("badgesUnlockedPlural", {
              count: earnedCount,
              msg: t(`motivation.${ctrl.motivationInfo.key}`),
            })}
            labelSingular={t("badgesUnlocked", {
              count: earnedCount,
              msg: t(`motivation.${ctrl.motivationInfo.key}`),
            })}
            icon={t(`motivationIcon.${ctrl.motivationInfo.key}`)}
          />
        )}

        {/* Derniers Exploits */}
        {!isLoading && (
          <BadgesLastExploitsSection
            lastExploits={ctrl.lastExploits}
            earnedBadges={earnedBadges}
            title={t("lastExploits")}
            formatEarnedOn={(date) => t("earnedOn", { date })}
            formatPoints={(count) => t("exploitPoints", { count })}
          />
        )}

        {/* À portée de main */}
        {!isLoading && (
          <BadgesClosestSection
            closestBadges={ctrl.closestBadges}
            availableBadges={availableBadges}
            title={t("closestTitle")}
            formatRemainingPlural={(count) => t("remainingPlural", { count })}
            formatRemaining={(count) => t("remaining", { count })}
            almostThere={t("almostThere")}
          />
        )}

        {/* Filtres et tri */}
        <BadgesFiltersBar
          filterStatus={ctrl.filterStatus}
          onFilterStatusChange={ctrl.setFilterStatus}
          filterCategory={ctrl.filterCategory}
          onFilterCategoryChange={ctrl.setFilterCategory}
          filterDifficulty={ctrl.filterDifficulty}
          onFilterDifficultyChange={ctrl.setFilterDifficulty}
          sortBy={ctrl.sortBy}
          onSortByChange={ctrl.setSortBy}
          hasActiveFilters={ctrl.hasActiveFilters}
          onClearFilters={ctrl.clearFilters}
          isToUnlockTab={ctrl.isToUnlockTab}
          closeCount={ctrl.closeCount}
          categories={ctrl.filtered.categories}
          difficulties={ctrl.filtered.difficulties}
          filtersTitle={t("filters.title")}
          statusLabel={t("filters.status")}
          statusAll={t("filters.statusAll")}
          statusEarned={t("filters.statusEarned")}
          statusLocked={t("filters.statusLocked")}
          statusClose={t("filters.statusClose")}
          formatStatusClose={(count) => `${t("filters.statusClose")} (${count})`}
          filtersReset={t("filters.reset")}
          categoryLabel={t("filters.category")}
          categoryAll={t("filters.categoryAll")}
          formatCategory={(c) => t(`categories.${c}`)}
          difficultyLabel={t("filters.difficulty")}
          difficultyAll={t("filters.difficultyAll")}
          formatDifficulty={(d) => t(`difficulties.${d}`)}
          sortLabel={t("filters.sort")}
          sortProgress={t("filters.sortProgress")}
          sortDate={t("filters.sortDate")}
          sortPoints={t("filters.sortPoints")}
          sortCategory={t("filters.sortCategory")}
        />

        {/* Collection */}
        <BadgesCollectionSection
          filteredEarned={ctrl.filtered.filteredEarned}
          sortedEarned={sortedEarnedFinal}
          earnedBadges={earnedBadges}
          sortBy={ctrl.sortBy}
          rarityMap={rarityMap as Record<string, RarityInfo>}
          pinnedBadgeIds={pinnedBadgeIds}
          onTogglePin={async (badgeId) => {
            const isPinned = pinnedBadgeIds.includes(badgeId);
            const next = isPinned
              ? pinnedBadgeIds.filter((id: number) => id !== badgeId)
              : [...pinnedBadgeIds, badgeId].slice(0, 3);
            await pinBadges(next);
          }}
          collectionExpanded={ctrl.collectionExpanded}
          onToggleExpanded={() => ctrl.setCollectionExpanded(!ctrl.collectionExpanded)}
          isLoading={isLoading}
          error={error instanceof Error ? error : error ? new Error(String(error)) : null}
          hasActiveFilters={ctrl.hasActiveFilters}
          totalCount={visibleTotal}
          title={t("collection.title")}
          formatCount={(earned, total) =>
            t("collection.count", {
              earned,
              total: total || visibleTotal,
            })
          }
          errorTitle={t("error.title")}
          errorDescription={t("error.description")}
          errorRetry={t("error.retry")}
          loadingMessage={t("loading")}
          noResults={t("collection.noResults")}
          emptyLabel={t("collection.empty")}
          collapseCollection={t("collection.collapseCollection")}
          formatViewFull={(count) => t("collection.viewFullCollection", { count })}
          showLess={t("collection.showLess")}
          showMore={t("collection.showMore", { count: 0 })}
        />

        {/* Onglets progression / à débloquer */}
        <BadgesProgressTabsSection
          inProgressWithTarget={ctrl.inProgressWithTarget}
          filteredLocked={ctrl.filtered.filteredLocked}
          availableBadges={availableBadges}
          sortBy={ctrl.sortBy}
          rarityMap={rarityMap as Record<string, RarityInfo>}
          progressMap={ctrl.progressMap}
          activeTab={ctrl.activeTab}
          defaultTab={ctrl.defaultTab}
          onTabChange={(v) => {
            if (v === "inProgress" && ctrl.filterStatus === "close") ctrl.setFilterStatus("all");
            ctrl.setActiveTab(v);
          }}
          toUnlockExpanded={ctrl.toUnlockExpanded}
          onToUnlockToggle={() => ctrl.setToUnlockExpanded(!ctrl.toUnlockExpanded)}
          tabsAriaLabel={t("tabs.ariaLabel")}
          formatTabInProgress={(count) => t("tabs.inProgressWithCount", { count })}
          formatTabToUnlock={(count) => t("tabs.toUnlockWithCount", { count })}
          noInProgress={t("tabs.noInProgress")}
          noToUnlock={t("tabs.noToUnlock")}
          showLess={t("collection.showLess")}
          formatShowMore={(count) => t("collection.showMore", { count })}
          formatSuccessRate={({ correct, total, rate }) =>
            t("successRateDisplay", { correct, total, rate })
          }
          tuApproches={t("tuApproches")}
          formatPlusQueCorrect={(count) => t("plusQueCorrect", { count })}
          formatPlusQue={(count) => t("plusQue", { count })}
        />

        {/* Stats détaillées */}
        {gamificationStats?.performance && (
          <BadgesDetailedStatsSection
            performance={gamificationStats.performance}
            byCategory={gamificationStats.badges_summary?.by_category ?? undefined}
            statsExpanded={ctrl.statsExpanded}
            onToggleExpanded={() => ctrl.setStatsExpanded(!ctrl.statsExpanded)}
            showStats={t("statsDetails.show")}
            hideStats={t("statsDetails.hide")}
            performanceTitle={t("performance.title")}
            totalAttemptsLabel={t("performance.totalAttempts")}
            correctAttemptsLabel={t("performance.correctAttempts")}
            successRateLabel={t("performance.successRate")}
            avgTimeLabel={t("performance.avgTime")}
            byCategoryLabel={t("performance.byCategory")}
            formatCategory={(key) => t(`categories.${key}`)}
          />
        )}
      </PageLayout>
    </ProtectedRoute>
  );
}
