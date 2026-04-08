"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/hooks/useAuth";
import { useChallengesProgress } from "@/hooks/useChallengesProgress";
import { useDailyChallenges } from "@/hooks/useDailyChallenges";
import { useProgressStats } from "@/hooks/useProgressStats";
import { useUserStats, type TimeRange } from "@/hooks/useUserStats";
import type { TimelinePeriod } from "@/hooks/useProgressTimeline";
import { buildDashboardExportSnapshot } from "@/lib/dashboard/buildDashboardExportSnapshot";
import { useLocaleStore } from "@/lib/stores/localeStore";

const DASHBOARD_REFRESH_QUERY_KEYS = [
  ["auth", "me"],
  ["user", "stats"],
  ["user", "progress"],
  ["user", "progress", "timeline"],
  ["user", "challenges", "progress"],
  ["user", "challenges", "detailed-progress"],
  ["leaderboard"],
  ["daily-challenges"],
] as const;

type DashboardTranslationValues = Record<string, string | number | Date>;

type DashboardTranslationFn = (key: string, values?: DashboardTranslationValues) => string;

interface UseDashboardPageControllerOptions {
  tDashboard: DashboardTranslationFn;
  tDashboardToasts: DashboardTranslationFn;
}

export function useDashboardPageController({
  tDashboard,
  tDashboardToasts,
}: UseDashboardPageControllerOptions) {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { locale } = useLocaleStore();
  const [timeRange, setTimeRange] = useState<TimeRange>("30");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  const [timelinePeriod, setTimelinePeriod] = useState<TimelinePeriod>("7d");

  const { stats, isLoading, error, refetch } = useUserStats(timeRange);
  const { data: progressStats, isLoading: isLoadingProgress } = useProgressStats();
  const { data: challengesProgress, isLoading: isLoadingChallenges } = useChallengesProgress();
  const { challenges: dailyChallenges } = useDailyChallenges();

  const timeRangeLabel = useMemo(() => {
    const key =
      timeRange === "7"
        ? "7days"
        : timeRange === "30"
          ? "30days"
          : timeRange === "90"
            ? "90days"
            : "all";
    return tDashboard(`timeRange.${key}`);
  }, [timeRange, tDashboard]);

  const exportSnapshot = useMemo(() => {
    if (!stats || !user) {
      return null;
    }

    return buildDashboardExportSnapshot(
      {
        username: user.username,
        timeRange,
        timeRangeLabel,
        stats,
        gamificationLevel: user.gamification_level ?? null,
        accountTotalPoints: typeof user.total_points === "number" ? user.total_points : null,
        progressStats: progressStats ?? null,
        challengesProgress: challengesProgress ?? null,
        dailyChallenges,
      },
      new Date()
    );
  }, [challengesProgress, dailyChallenges, progressStats, stats, timeRange, timeRangeLabel, user]);

  const handleRefresh = useCallback(async () => {
    if (isRefreshing) {
      return;
    }

    setIsRefreshing(true);

    try {
      await refetch();
      await Promise.all(
        DASHBOARD_REFRESH_QUERY_KEYS.map((queryKey) =>
          queryClient.invalidateQueries({ queryKey: [...queryKey] })
        )
      );
      toast.success(tDashboardToasts("statsUpdated"));
    } catch {
      toast.error(tDashboard("error.title"));
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  }, [isRefreshing, queryClient, refetch, tDashboard, tDashboardToasts]);

  useEffect(() => {
    document.documentElement.setAttribute("data-mathakine-dashboard", "");
    return () => {
      document.documentElement.removeAttribute("data-mathakine-dashboard");
    };
  }, []);

  return {
    activeTab,
    challengesProgress: challengesProgress ?? null,
    dailyChallenges,
    error,
    exportSnapshot,
    handleRefresh,
    isLoading,
    isLoadingChallenges,
    isLoadingProgress,
    isRefreshing,
    locale,
    progressStats: progressStats ?? null,
    refetch,
    setActiveTab,
    setTimeRange,
    setTimelinePeriod,
    stats,
    timeRange,
    timeRangeLabel,
    timelinePeriod,
    user,
  };
}
