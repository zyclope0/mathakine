"use client";

import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { Badge } from "@/components/ui/badge";

interface StatsCardProps {
  icon: LucideIcon;
  value: string | number;
  label: string;
  className?: string;
  trend?: number; // Variation en pourcentage (ex: +5 pour +5%)
  trendDirection?: "up" | "down" | "neutral";
  lastUpdate?: string; // Date de dernière mise à jour (ISO string)
}

export function StatsCard({
  icon: Icon,
  value,
  label,
  className,
  trend,
  trendDirection,
  lastUpdate,
}: StatsCardProps) {
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  // Variantes d'animation avec garde-fous
  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
  });

  const transition = createTransition({ duration: 0.2 });

  const getTrendColor = () => {
    if (!trend || trendDirection === "neutral") return "text-muted-foreground";
    return trendDirection === "up" ? "text-success" : "text-destructive";
  };

  const showTrend =
    trend !== undefined &&
    trend !== null &&
    trendDirection !== "neutral" &&
    (trendDirection === "up" || trendDirection === "down");

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={transition}
      whileHover={!shouldReduceMotion ? { y: -4 } : {}}
      className={cn(
        "group rounded-xl border border-white/10 bg-white/5 backdrop-blur-md",
        "shadow-sm transition-all duration-300",
        "hover:shadow-xl hover:shadow-primary/10 hover:border-white/20",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
        className
      )}
      tabIndex={0}
    >
      <div className="flex items-center gap-4 px-5 py-4">
        {/* Icône dans un cercle coloré */}
        <motion.div
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary"
          animate={!shouldReduceMotion ? { rotate: [0, -10, 10, -10, 0] } : {}}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Icon className="h-6 w-6" aria-hidden="true" />
        </motion.div>

        {/* Data à droite */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-3xl font-bold text-foreground tabular-nums">{value}</span>
            {showTrend && (
              <Badge
                variant="outline"
                className={cn("text-xs flex items-center gap-1 shrink-0", getTrendColor())}
              >
                {trendDirection === "up" ? (
                  <TrendingUp className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                {trend !== undefined && trend !== null
                  ? (trend > 0 ? "+" : "") + trend + "%"
                  : ""}
              </Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-0.5 truncate">{label}</p>
          {lastUpdate && (
            <p className="text-xs text-muted-foreground/60 mt-1">
              {new Date(lastUpdate).toLocaleTimeString("fr-FR", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
