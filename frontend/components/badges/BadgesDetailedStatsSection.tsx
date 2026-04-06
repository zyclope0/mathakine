"use client";

/**
 * BadgesDetailedStatsSection — stats détaillées repliables.
 * Composant purement visuel.
 * FFI-L12.
 */

import { ChevronDown, ChevronUp } from "lucide-react";
import { PageSection } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PerformanceStats {
  total_attempts: number;
  correct_attempts: number;
  success_rate: number;
  avg_time_spent: number;
}

interface BadgesDetailedStatsSectionProps {
  performance: PerformanceStats;
  byCategory?: Record<string, number> | undefined;
  statsExpanded: boolean;
  onToggleExpanded: () => void;

  // Labels i18n
  showStats: string;
  hideStats: string;
  performanceTitle: string;
  totalAttemptsLabel: string;
  correctAttemptsLabel: string;
  successRateLabel: string;
  avgTimeLabel: string;
  byCategoryLabel: string;
  formatCategory: (key: string) => string;
}

export function BadgesDetailedStatsSection({
  performance,
  byCategory,
  statsExpanded,
  onToggleExpanded,
  showStats,
  hideStats,
  performanceTitle,
  totalAttemptsLabel,
  correctAttemptsLabel,
  successRateLabel,
  avgTimeLabel,
  byCategoryLabel,
  formatCategory,
}: BadgesDetailedStatsSectionProps) {
  return (
    <PageSection className="animate-fade-in-up-delay-3">
      <Button
        variant="ghost"
        size="sm"
        className="text-muted-foreground hover:text-foreground -ml-2"
        onClick={onToggleExpanded}
        aria-expanded={statsExpanded}
      >
        {statsExpanded ? (
          <>
            <ChevronUp className="h-4 w-4 mr-1" aria-hidden="true" />
            {hideStats}
          </>
        ) : (
          <>
            <ChevronDown className="h-4 w-4 mr-1" aria-hidden="true" />
            {showStats}
          </>
        )}
      </Button>
      {statsExpanded && (
        <Card className="card-spatial-depth mt-3">
          <CardHeader>
            <CardTitle className="text-xl text-foreground">{performanceTitle}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">{totalAttemptsLabel}</div>
                <div className="text-2xl font-bold text-foreground">
                  {performance.total_attempts}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">{correctAttemptsLabel}</div>
                <div className="text-2xl font-bold text-green-500">
                  {performance.correct_attempts}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">{successRateLabel}</div>
                <div className="text-2xl font-bold text-foreground">
                  {performance.success_rate.toFixed(1)}%
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">{avgTimeLabel}</div>
                <div className="text-2xl font-bold text-foreground">
                  {performance.avg_time_spent.toFixed(1)}s
                </div>
              </div>
            </div>
            {byCategory && Object.keys(byCategory).length > 0 && (
              <div className="mt-6 pt-6 border-t border-border">
                <div className="text-sm font-medium text-muted-foreground mb-3">
                  {byCategoryLabel}
                </div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(byCategory).map(([category, count]) => (
                    <Badge
                      key={category}
                      variant="outline"
                      className="text-sm"
                      aria-label={`${formatCategory(category)}: ${count}`}
                    >
                      {category === "progression" && "📈"}
                      {category === "mastery" && "⭐"}
                      {category === "special" && "✨"} {formatCategory(category)}: {count}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </PageSection>
  );
}
