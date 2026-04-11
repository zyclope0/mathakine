"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/hooks/useAuth";
import { useLeaderboard, type LeaderboardPeriod } from "@/hooks/useLeaderboard";
import { useMyLeaderboardRank } from "@/hooks/useMyLeaderboardRank";
import { Trophy, Medal } from "lucide-react";
import { useTranslations } from "next-intl";
import { PageLayout, PageHeader, PageSection, LoadingState, EmptyState } from "@/components/layout";
import {
  canonicalProgressionRankBucket,
  isKnownProgressionRankBucket,
  readPublicProgressionRankRaw,
} from "@/lib/gamification/progressionRankLabel";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { LeaderboardList } from "@/components/leaderboard/LeaderboardList";
import { LeaderboardCurrentUserFooter } from "@/components/leaderboard/LeaderboardCurrentUserFooter";
import { LeaderboardCardState } from "@/components/leaderboard/LeaderboardCardState";
import {
  buildLeaderboardListVariants,
  buildLeaderboardRowVariants,
} from "@/components/leaderboard/leaderboardPageMotion";

export function LeaderboardPageContent() {
  const t = useTranslations("leaderboard");
  const tProgRank = useTranslations("progressionRanks");
  const progressionRankLabel = (bucket: string) => {
    const c = canonicalProgressionRankBucket(bucket);
    return isKnownProgressionRankBucket(bucket) ? tProgRank(c) : bucket;
  };
  const { user } = useAuth();
  const [period, setPeriod] = useState<LeaderboardPeriod>("all");
  const { leaderboard, isLoading, error } = useLeaderboard(50, period);
  const { shouldReduceMotion } = useAccessibleAnimation();

  const inTop = useMemo(() => leaderboard.some((e) => e.is_current_user), [leaderboard]);
  const fetchMyRankEnabled = !isLoading && !error && leaderboard.length > 0 && !inTop;
  const {
    data: myRank,
    isLoading: myRankLoading,
    isError: myRankError,
  } = useMyLeaderboardRank(fetchMyRankEnabled, period);

  const showMyRankFooter =
    fetchMyRankEnabled && Boolean(user) && Boolean(myRank) && !myRankLoading && !myRankError;

  const myRankBucketRaw = user ? readPublicProgressionRankRaw(user) : "";

  const listVariants = buildLeaderboardListVariants(Boolean(shouldReduceMotion));
  const rowVariants = buildLeaderboardRowVariants(Boolean(shouldReduceMotion));

  const rankBadgeAriaPrefix = t("rank", { default: "Rang" });

  return (
    <PageLayout>
      <PageHeader title={t("title")} description={t("description")} icon={Trophy} />

      <PageSection>
        <Card className="overflow-hidden border-border/60">
          <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4 space-y-0">
            <CardTitle className="flex items-center gap-2">
              <Medal className="h-5 w-5 text-amber-400" aria-hidden />
              {t("ranking")}
            </CardTitle>
            <div className="flex w-full flex-col gap-1.5 sm:w-auto sm:min-w-[220px]">
              <span className="text-xs text-muted-foreground" id="leaderboard-period-label">
                {t("period.label")}
              </span>
              <Select
                value={period}
                onValueChange={(value) => setPeriod(value as LeaderboardPeriod)}
              >
                <SelectTrigger
                  aria-labelledby="leaderboard-period-label"
                  className="w-full"
                  size="sm"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("period.all")}</SelectItem>
                  <SelectItem value="week">{t("period.week")}</SelectItem>
                  <SelectItem value="month">{t("period.month")}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent className="p-0 min-h-[120px]">
            <LeaderboardCardState
              error={error}
              isLoading={isLoading}
              isEmpty={leaderboard.length === 0}
              errorContent={
                <div className="p-6">
                  <EmptyState
                    title={t("error") ?? "Erreur de chargement"}
                    description=""
                    icon={Trophy}
                  />
                </div>
              }
              loadingContent={
                <div className="p-6">
                  <LoadingState message={t("loading")} />
                </div>
              }
              emptyContent={
                <div className="p-6">
                  <EmptyState
                    title={t("emptyState.title")}
                    description={t("emptyState.description")}
                    icon={Medal}
                    action={
                      <Button asChild variant="default">
                        <Link href="/challenges">{t("emptyState.cta")}</Link>
                      </Button>
                    }
                  />
                </div>
              }
            >
              <>
                <LeaderboardList
                  leaderboard={leaderboard}
                  showMyRankFooter={showMyRankFooter}
                  listVariants={listVariants}
                  rowVariants={rowVariants}
                  shouldReduceMotion={Boolean(shouldReduceMotion)}
                  progressionRankLabel={progressionRankLabel}
                  tRankingAria={t("ranking")}
                  tLevel={t("level")}
                  tYou={t("you")}
                  tRank={t("rank")}
                  tStreak={t("streakStat")}
                  tBadges={t("badgesStat")}
                  podiumSeparator={t("podiumSeparator")}
                  topTenSeparator={t("topTenSeparator")}
                  restSeparator={t("restSeparator")}
                />

                {showMyRankFooter && user && myRank ? (
                  <LeaderboardCurrentUserFooter
                    user={user}
                    myRank={myRank}
                    myRankBucketRaw={myRankBucketRaw}
                    tSeparator={t("yourRank.separator")}
                    tYou={t("you")}
                    tLevel={t("level")}
                    rankBadgeAriaPrefix={rankBadgeAriaPrefix}
                    progressionRankLabel={progressionRankLabel}
                  />
                ) : null}
              </>
            </LeaderboardCardState>
          </CardContent>
        </Card>
      </PageSection>
    </PageLayout>
  );
}
