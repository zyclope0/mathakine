"use client";

import { useState } from "react";
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ContentCardBase } from "@/components/shared/ContentCardBase";
import { getAgeGroupColor, EXERCISE_TYPE_STYLES } from "@/lib/constants/exercises";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import type { Exercise } from "@/types/api";
import { Sparkles, Eye, Calendar } from "lucide-react";
import dynamic from "next/dynamic";
import { useTranslations } from "next-intl";
import { useCompletedExercises } from "@/hooks/useCompletedItems";

// Lazy load modal pour réduire le bundle initial
const ExerciseModal = dynamic(
  () => import("./ExerciseModal").then((mod) => ({ default: mod.ExerciseModal })),
  {
    loading: () => null, // Pas de loading pour les modals (s'ouvrent seulement au clic)
  }
);

interface ExerciseCardProps {
  exercise: Exercise;
}

export function ExerciseCard({ exercise }: ExerciseCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();
  const { isCompleted } = useCompletedExercises();

  // Logique pour le type d'exercice
  const typeDisplay = getTypeDisplay(exercise.exercise_type);
  const exerciseTypeKey = (exercise.exercise_type?.toLowerCase() ??
    "divers") as keyof typeof EXERCISE_TYPE_STYLES;
  const { icon: IconComponent, className: typeClassName } =
    EXERCISE_TYPE_STYLES[exerciseTypeKey] || EXERCISE_TYPE_STYLES.divers;

  const { theme } = useThemeStore();
  const ageGroupDisplay = getAgeDisplay(exercise.age_group);
  const ageGroupBadgeClasses = getAgeGroupColor(exercise.age_group, theme);

  const completed = isCompleted(exercise.id);

  return (
    <>
      <ContentCardBase
        completed={completed}
        titleId={`exercise-title-${exercise.id}`}
        descriptionId={`exercise-description-${exercise.id}`}
        completedLabel={t("card.completed", { default: "Résolu" })}
        completedAriaLabel={t("card.completed", { default: "Exercice résolu" })}
      >
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle
                id={`exercise-title-${exercise.id}`}
                className="text-lg mb-2 flex items-center gap-2"
              >
                {exercise.ai_generated && (
                  <Sparkles className="h-4 w-4 text-primary-on-dark" aria-hidden="true" />
                )}
                {exercise.title}
              </CardTitle>
              <CardDescription
                id={`exercise-description-${exercise.id}`}
                className="line-clamp-3 min-h-[3.6rem]"
              >
                {exercise.question}
              </CardDescription>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            <Badge
              variant="outline"
              className={`badge-sweep ${ageGroupBadgeClasses}`}
              aria-label={t("card.ageGroup", { ageGroup: ageGroupDisplay })}
            >
              {ageGroupDisplay}
            </Badge>
            <Badge
              variant="outline"
              className={`badge-sweep flex items-center ${typeClassName}`}
              aria-label={t("card.type", { type: typeDisplay })}
            >
              <IconComponent className="h-3 w-3 mr-1.5" />
              {typeDisplay}
            </Badge>
            {exercise.ai_generated && (
              <Badge
                variant="outline"
                className="badge-ai-pulse bg-primary/10 text-primary-on-dark border-primary/30"
                aria-label={t("card.aiGenerated")}
              >
                IA
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
            <div
              className="flex items-center gap-4"
              role="group"
              aria-label={t("card.exerciseInfo", { default: "Informations sur l'exercice" })}
            >
              <div
                className="flex items-center gap-1"
                aria-label={
                  (exercise.view_count || 0) === 1
                    ? t("card.views", { count: exercise.view_count || 0 })
                    : t("card.viewsPlural", { count: exercise.view_count || 0 })
                }
              >
                <Eye className="h-4 w-4" aria-hidden="true" />
                <span>{exercise.view_count || 0}</span>
              </div>
              {exercise.created_at && (
                <div
                  className="flex items-center gap-1"
                  aria-label={t("card.createdOn", {
                    date: new Date(exercise.created_at).toLocaleDateString("fr-FR"),
                  })}
                >
                  <Calendar className="h-4 w-4" aria-hidden="true" />
                  <time dateTime={exercise.created_at}>
                    {new Date(exercise.created_at).toLocaleDateString("fr-FR")}
                  </time>
                </div>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={() => setIsModalOpen(true)}
              className="btn-cta-primary flex-1"
              aria-label={t("card.solveExercise", { title: exercise.title })}
            >
              {t("solve")}
            </Button>
          </div>
        </CardContent>
        <ExerciseModal
          exerciseId={exercise.id}
          open={isModalOpen}
          onOpenChange={setIsModalOpen}
          onExerciseCompleted={() => {
            // Invalider les queries pour rafraîchir les badges de progression
            // Le hook useCompletedExercises se mettra à jour automatiquement
          }}
        />
      </ContentCardBase>
    </>
  );
}
