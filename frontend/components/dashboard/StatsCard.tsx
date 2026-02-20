"use client";

import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils/cn";
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

  const showTrend = trend !== undefined && trend !== null && trendDirection !== "neutral" && (trendDirection === "up" || trendDirection === "down");

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={transition}
      whileHover={!shouldReduceMotion ? { scale: 1.02 } : {}}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
      tabIndex={0}
    >
      <Card className={cn("card-spatial-depth", className)}>
        <CardContent className="pt-6">
          <div className="text-center space-y-2">
            <motion.div
              className="flex justify-center"
              animate={!shouldReduceMotion ? { rotate: [0, -10, 10, -10, 0] } : {}}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Icon className="h-8 w-8 text-primary-on-dark" />
            </motion.div>
            <div className="flex items-center justify-center gap-2">
              <div className="text-3xl font-bold text-foreground">{value}</div>
              {showTrend && (
                <Badge
                  variant="outline"
                  className={cn("text-xs flex items-center gap-1", getTrendColor())}
                >
                  {trendDirection === "up" ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {trend !== undefined && trend !== null ? (trend > 0 ? "+" : "") + trend + "%" : ""}
                </Badge>
              )}
            </div>
            <div className="text-sm text-muted-foreground">{label}</div>
            {lastUpdate && (
              <div className="text-xs text-muted-foreground/70">
                {new Date(lastUpdate).toLocaleTimeString("fr-FR", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
