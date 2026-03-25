"use client";

import { Skeleton } from "@/components/ui/skeleton";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { RECHARTS_TOOLTIP_STYLE } from "@/lib/utils/chart";

export interface DashboardRadarCategoryRow {
  category: string;
  /** Pourcentage d’affichage 0–100. */
  accuracy: number;
  completed?: number;
  attempts?: number;
}

interface DashboardCategoryRadarPlotProps {
  rows: DashboardRadarCategoryRow[];
  /** Libellé série dans le tooltip Recharts. */
  tooltipSeriesLabel: string;
  ariaLabel: string;
  chartHeightClass?: string;
}

/**
 * Tracé radar seul (sans carte) — pour empiler plusieurs radars dans un même widget.
 */
export function DashboardCategoryRadarPlot({
  rows,
  tooltipSeriesLabel,
  ariaLabel,
  chartHeightClass = "h-[220px]",
}: DashboardCategoryRadarPlotProps) {
  const { shouldReduceMotion } = useAccessibleAnimation();

  return (
    <div className={`${chartHeightClass} w-full`} role="img" aria-label={ariaLabel}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={rows} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="var(--color-border)" strokeOpacity={0.5} />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
          />
          <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            dataKey="accuracy"
            stroke="var(--color-chart-1)"
            strokeOpacity={0.8}
            fill="var(--color-chart-1)"
            fillOpacity={0.3}
            strokeWidth={2}
            isAnimationActive={!shouldReduceMotion}
            animationDuration={800}
            animationEasing="ease-out"
          />
          <Tooltip
            contentStyle={RECHARTS_TOOLTIP_STYLE}
            formatter={(value, _name, item) => {
              const p = item?.payload as DashboardRadarCategoryRow | undefined;
              const pct = typeof value === "number" ? Math.round(value) : value;
              const base = `${pct}%`;
              if (p?.attempts != null && p?.completed != null) {
                return [`${base} (${p.completed}/${p.attempts})`, tooltipSeriesLabel];
              }
              if (p?.completed != null) {
                return [`${base} (${p.completed})`, tooltipSeriesLabel];
              }
              return [base, tooltipSeriesLabel];
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function DashboardRadarSubsectionSkeleton() {
  return (
    <div className="h-[220px] flex items-center justify-center">
      <Skeleton className="h-40 w-40 rounded-full" />
    </div>
  );
}
