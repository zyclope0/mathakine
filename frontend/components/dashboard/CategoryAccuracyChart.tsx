"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { BarChart3 } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils/cn";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

interface CategoryData {
  completed: number;
  accuracy: number;
}

interface CategoryAccuracyChartProps {
  categoryData: Record<string, CategoryData>;
  isLoading?: boolean;
}

export function CategoryAccuracyChart({ categoryData, isLoading }: CategoryAccuracyChartProps) {
  const t = useTranslations("dashboard.categoryAccuracy");
  const tExercises = useTranslations("exercises");
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();

  if (isLoading) {
    return (
      <Card className="bg-card border-primary/20 animate-pulse h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="h-6 w-48 bg-muted rounded"></div>
        </CardHeader>
        <CardContent className="flex-grow">
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-32 bg-muted rounded"></div>
                <div className="h-3 w-full bg-muted rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const categories = Object.entries(categoryData);

  if (categories.length === 0) {
    return (
      <Card className="bg-card border-primary/20 h-full flex flex-col">
        <CardHeader className="flex-shrink-0">
          <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <BarChart3 className="w-5 h-5 text-primary-on-dark" />
            {t("title")}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow flex items-center justify-center">
          <div className="text-sm text-muted-foreground text-center">{t("noData")}</div>
        </CardContent>
      </Card>
    );
  }

  // Trier par nombre d'exercices complétés (décroissant)
  const sortedCategories = categories.sort((a, b) => b[1].completed - a[1].completed);

  // Fonction pour obtenir la couleur selon l'accuracy
  const getAccuracyColor = (accuracy: number): { bg: string; text: string; border: string } => {
    if (accuracy >= 0.9)
      return {
        bg: "bg-green-500/20",
        text: "text-green-400",
        border: "border-green-500/30",
      };
    if (accuracy >= 0.7)
      return {
        bg: "bg-blue-500/20",
        text: "text-blue-400",
        border: "border-blue-500/30",
      };
    if (accuracy >= 0.5)
      return {
        bg: "bg-yellow-500/20",
        text: "text-yellow-400",
        border: "border-yellow-500/30",
      };
    return {
      bg: "bg-red-500/20",
      text: "text-red-400",
      border: "border-red-500/30",
    };
  };

  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
  });

  const transition = createTransition({ duration: 0.2 });

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={transition}
      whileHover={!shouldReduceMotion ? { scale: 1.02 } : {}}
      className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
    >
      <Card className="bg-card border-primary/20 h-full flex flex-col">
        <CardHeader className="pb-3 flex-shrink-0">
          <CardTitle className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <BarChart3 className="w-5 h-5 text-primary-on-dark" />
            {t("title")}
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-grow">
          <div className="space-y-4">
            {sortedCategories.map(([category, data]) => {
              const accuracyPercentage = Math.round(data.accuracy * 100);
              const colors = getAccuracyColor(data.accuracy);
              const isExcellent = data.accuracy >= 0.9;

              // Normaliser la catégorie en minuscules pour la traduction
              const categoryKey = category.toLowerCase().replace("exercises.types.", "");

              return (
                <div key={category}>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={cn(colors.text, colors.border)}>
                        {tExercises(`types.${categoryKey}`, { defaultValue: categoryKey })}
                      </Badge>
                      {isExcellent && (
                        <Badge className="bg-green-500/20 text-green-400 text-xs">
                          {t("excellent")}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className={cn("text-lg font-bold", colors.text)}>
                        {accuracyPercentage}%
                      </span>
                      <span className="text-xs text-muted-foreground">
                        ({data.completed} {t("exercises")})
                      </span>
                    </div>
                  </div>

                  <Progress value={accuracyPercentage} className="h-3" />
                </div>
              );
            })}
          </div>

          <div className="mt-6 pt-4 border-t border-border">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
                <span>{t("excellent")} (90%+)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-blue-400"></div>
                <span>{t("good")} (70-89%)</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                <span>{t("fair")} (50-69%)</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
