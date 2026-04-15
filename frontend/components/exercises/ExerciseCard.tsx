"use client";

import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ContentCardBase } from "@/components/shared/ContentCardBase";
import {
  EXERCISE_TYPE_CARD_BORDER_LEFT,
  EXERCISE_TYPE_STYLES,
  getAgeGroupColor,
} from "@/lib/constants/exercises";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import type { Exercise } from "@/types/api";
import { Sparkles, Eye, Calendar, ArrowRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { MathText } from "@/components/ui/MathText";

interface ExerciseCardProps {
  exercise: Exercise;
  /** État « résolu » fourni par la page (une seule query completed-ids). */
  completed: boolean;
  /** Callback centralisé au niveau page — évite N instances ExerciseModal dans le DOM. */
  onOpen: (exerciseId: number) => void;
}

export function ExerciseCard({ exercise, completed, onOpen }: ExerciseCardProps) {
  const t = useTranslations("exercises");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();

  // Logique pour le type d'exercice
  const typeDisplay = getTypeDisplay(exercise.exercise_type);
  const exerciseTypeKey = (exercise.exercise_type?.toLowerCase() ??
    "divers") as keyof typeof EXERCISE_TYPE_STYLES;
  const { icon: IconComponent, className: typeClassName } =
    EXERCISE_TYPE_STYLES[exerciseTypeKey] || EXERCISE_TYPE_STYLES.divers;
  const cardBorderLeft =
    EXERCISE_TYPE_CARD_BORDER_LEFT[exerciseTypeKey] ?? EXERCISE_TYPE_CARD_BORDER_LEFT.divers;

  const { theme } = useThemeStore();
  const ageGroupDisplay = getAgeDisplay(exercise.age_group);
  const ageGroupBadgeClasses = getAgeGroupColor(exercise.age_group, theme);

  return (
    <ContentCardBase
      completed={completed}
      titleId={`exercise-title-${exercise.id}`}
      descriptionId={`exercise-description-${exercise.id}`}
      completedLabel={t("card.completed", { default: "Résolu" })}
      completedAriaLabel={t("card.completed", { default: "Exercice résolu" })}
      onClick={() => onOpen(exercise.id)}
      cardClassName={cardBorderLeft}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle
              id={`exercise-title-${exercise.id}`}
              className="text-lg font-semibold mb-2 leading-snug"
            >
              {exercise.ai_generated && (
                <Sparkles
                  className="inline-block h-4 w-4 text-primary mr-1.5 align-middle shrink-0"
                  aria-label={t("card.aiGenerated")}
                />
              )}
              {exercise.title}
            </CardTitle>
            <CardDescription id={`exercise-description-${exercise.id}`} className="line-clamp-3">
              <MathText size="sm">{exercise.question}</MathText>
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
          {/* Badge IA retiré — l'icône Sparkles dans le titre est suffisante (P2 distill) */}
        </div>
      </CardHeader>
      <CardContent className="flex flex-col">
        <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
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
        <div className="flex justify-end pt-2 mt-3 border-t border-border/30">
          <span
            className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary transition-colors group-hover:bg-primary/20"
            aria-hidden="true"
          >
            {t("solve")}
            <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
          </span>
        </div>
      </CardContent>
    </ContentCardBase>
  );
}
