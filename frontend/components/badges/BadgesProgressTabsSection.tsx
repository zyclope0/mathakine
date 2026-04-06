"use client";

/**
 * BadgesProgressTabsSection — onglets "En cours" / "À débloquer".
 * Composant purement visuel.
 * FFI-L12.
 */

import { TrendingUp, Target, ChevronDown, ChevronUp } from "lucide-react";
import { PageSection } from "@/components/layout";
import { BadgeGrid } from "@/components/badges/BadgeGrid";
import { BadgeIcon } from "@/components/badges/BadgeIcon";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import type { Badge } from "@/types/api";
import type { BadgeProgressItem } from "@/hooks/useBadgesProgress";
import type { RarityInfo } from "@/components/badges/BadgeGrid";
import type { SortBy, ProgressMapEntry } from "@/lib/badges/badgesPage";

const TO_UNLOCK_PREVIEW = 12;

interface BadgesProgressTabsSectionProps {
  inProgressWithTarget: BadgeProgressItem[];
  filteredLocked: Badge[];
  availableBadges: Badge[];
  sortBy: SortBy;
  rarityMap: Record<string, RarityInfo>;
  progressMap: Record<number, ProgressMapEntry>;
  activeTab: string;
  defaultTab: string;
  onTabChange: (v: string) => void;
  toUnlockExpanded: boolean;
  onToUnlockToggle: () => void;

  // Labels i18n
  tabsAriaLabel: string;
  formatTabInProgress: (count: number) => string;
  formatTabToUnlock: (count: number) => string;
  noInProgress: string;
  noToUnlock: string;
  showLess: string;
  formatShowMore: (count: number) => string;
  formatSuccessRate: (args: { correct: number; total: number; rate: number }) => string;
  tuApproches: string;
  formatPlusQueCorrect: (count: number) => string;
  formatPlusQue: (count: number) => string;
}

export function BadgesProgressTabsSection({
  inProgressWithTarget,
  filteredLocked,
  availableBadges,
  sortBy,
  rarityMap,
  progressMap,
  activeTab,
  defaultTab,
  onTabChange,
  toUnlockExpanded,
  onToUnlockToggle,
  tabsAriaLabel,
  formatTabInProgress,
  formatTabToUnlock,
  noInProgress,
  noToUnlock,
  showLess,
  formatShowMore,
  formatSuccessRate,
  tuApproches,
  formatPlusQueCorrect,
  formatPlusQue,
}: BadgesProgressTabsSectionProps) {
  if (inProgressWithTarget.length === 0 && filteredLocked.length === 0) return null;

  return (
    <PageSection className="space-y-4 animate-fade-in-up-delay-2">
      <Tabs value={activeTab} onValueChange={onTabChange} key={defaultTab} className="w-full">
        <TabsList
          className="w-full sm:w-auto flex flex-wrap gap-1 h-auto p-1"
          role="tablist"
          aria-label={tabsAriaLabel}
        >
          <TabsTrigger value="inProgress" className="flex items-center gap-2 py-2 px-4">
            <TrendingUp className="h-4 w-4 shrink-0" aria-hidden="true" />
            {formatTabInProgress(inProgressWithTarget.length)}
          </TabsTrigger>
          <TabsTrigger value="toUnlock" className="flex items-center gap-2 py-2 px-4">
            <Target className="h-4 w-4 shrink-0" aria-hidden="true" />
            {formatTabToUnlock(filteredLocked.length)}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="inProgress" className="mt-4" role="tabpanel">
          {inProgressWithTarget.length > 0 ? (
            <div className="grid gap-3 grid-cols-1 xl:grid-cols-2">
              {inProgressWithTarget.map((badge) => {
                const fullBadge = availableBadges.find((b) => b.id === badge.id);
                const criteriaText =
                  fullBadge?.criteria_text || (badge as { criteria_text?: string }).criteria_text;
                const detail = badge.progress_detail as
                  | {
                      type: "success_rate";
                      correct: number;
                      total: number;
                      rate_pct: number;
                      required_rate_pct: number;
                    }
                  | undefined;
                const displayText =
                  detail?.type === "success_rate"
                    ? formatSuccessRate({
                        correct: detail.correct,
                        total: detail.total,
                        rate: detail.rate_pct,
                      })
                    : `${badge.current ?? 0}/${badge.target}`;
                const tooltipContent = [
                  criteriaText && `${criteriaText} — ${displayText}`,
                  fullBadge?.description,
                ]
                  .filter(Boolean)
                  .join("\n");
                const difficultyMedalSrc =
                  fullBadge?.difficulty === "gold"
                    ? "/badges/svg/medal.svg"
                    : fullBadge?.difficulty === "silver"
                      ? "/badges/svg/medal-silver.svg"
                      : fullBadge?.difficulty === "legendary"
                        ? "/badges/svg/medal-diamond.svg"
                        : "/badges/svg/medal-bronze.svg";

                return (
                  <TooltipProvider key={badge.id}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Card className="card-spatial-depth cursor-help transition-shadow hover:shadow-md">
                          <CardContent className="pt-4">
                            <div className="flex items-center gap-2 mb-2">
                              <BadgeIcon
                                code={fullBadge?.code}
                                iconUrl={fullBadge?.icon_url}
                                category={fullBadge?.category}
                                size="sm"
                                isEarned={false}
                              />
                              <span className="shrink-0 flex items-center" aria-hidden="true">
                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                <img
                                  src={difficultyMedalSrc}
                                  alt=""
                                  className="h-5 w-5 object-contain"
                                />
                              </span>
                              <span className="font-medium flex-1 min-w-0">{badge.name}</span>
                              <span className="text-sm font-semibold text-foreground tabular-nums shrink-0">
                                {displayText}
                              </span>
                            </div>
                            {(badge.progress ?? 0) >= 0.5 && (badge.target ?? 0) > 0 && (
                              <p className="text-sm font-semibold text-amber-500/90 mb-1">
                                {detail?.type === "success_rate"
                                  ? detail.rate_pct >= detail.required_rate_pct
                                    ? tuApproches
                                    : formatPlusQueCorrect(
                                        Math.ceil((detail.total * detail.required_rate_pct) / 100) -
                                          detail.correct
                                      )
                                  : (badge.target ?? 0) - (badge.current ?? 0) > 0
                                    ? formatPlusQue((badge.target ?? 0) - (badge.current ?? 0))
                                    : tuApproches}
                              </p>
                            )}
                            {badge.progress != null && (
                              <div
                                className="w-full bg-muted rounded-full h-3 overflow-hidden ring-1 ring-inset ring-border/60"
                                role="progressbar"
                                aria-valuenow={Math.round((badge.progress ?? 0) * 100)}
                                aria-valuemin={0}
                                aria-valuemax={100}
                                aria-label={`${badge.name}: ${Math.round((badge.progress ?? 0) * 100)}%`}
                              >
                                <div
                                  className="bg-primary h-3 rounded-full transition-all duration-500 min-w-[2px]"
                                  style={{
                                    width: `${Math.max((badge.progress ?? 0) * 100, 2)}%`,
                                  }}
                                />
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </TooltipTrigger>
                      <TooltipContent
                        side="top"
                        className="max-w-[280px] whitespace-pre-line py-2.5 px-3 text-sm"
                      >
                        {tooltipContent || `${badge.name}: ${displayText}`}
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                );
              })}
            </div>
          ) : (
            <p className="text-muted-foreground py-6" role="status">
              {noInProgress}
            </p>
          )}
        </TabsContent>

        <TabsContent value="toUnlock" className="mt-4" role="tabpanel">
          {filteredLocked.length > 0 ? (
            <>
              <div className="flex items-center justify-end gap-4 flex-wrap mb-2">
                {filteredLocked.length > TO_UNLOCK_PREVIEW && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onToUnlockToggle}
                    className="shrink-0"
                  >
                    {toUnlockExpanded ? (
                      <>
                        <ChevronUp className="h-4 w-4 mr-1" />
                        {showLess}
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4 mr-1" />
                        {formatShowMore(filteredLocked.length - TO_UNLOCK_PREVIEW)}
                      </>
                    )}
                  </Button>
                )}
              </div>
              <BadgeGrid
                badges={
                  filteredLocked.length > TO_UNLOCK_PREVIEW && !toUnlockExpanded
                    ? filteredLocked.slice(0, TO_UNLOCK_PREVIEW)
                    : filteredLocked
                }
                earnedBadges={[]}
                progressMap={progressMap}
                isLoading={false}
                sortBy={sortBy}
                rarityMap={rarityMap}
              />
            </>
          ) : (
            <p className="text-muted-foreground py-6" role="status">
              {noToUnlock}
            </p>
          )}
        </TabsContent>
      </Tabs>
    </PageSection>
  );
}
