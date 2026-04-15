"use client";

import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ContentCardBase } from "@/components/shared/ContentCardBase";
import {
  getChallengeTypeDisplay,
  getAgeGroupDisplay,
  getAgeGroupColor,
} from "@/lib/constants/challenges";
import { useThemeStore } from "@/lib/stores/themeStore";
import { formatSuccessRate, hasAiTag } from "@/lib/utils/format";
import type { Challenge } from "@/types/api";
import { Clock, Eye, TrendingUp, ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { MathText } from "@/components/ui/MathText";

interface ChallengeCardProps {
  challenge: Challenge;
  /** État « résolu » fourni par la page (une seule query completed-ids). */
  completed: boolean;
}

export function ChallengeCard({ challenge, completed }: ChallengeCardProps) {
  const t = useTranslations("challenges");
  const { theme } = useThemeStore();
  const typeDisplay = getChallengeTypeDisplay(challenge.challenge_type);
  const ageGroupDisplay = getAgeGroupDisplay(challenge.age_group);
  const ageGroupColor = getAgeGroupColor(challenge.age_group, theme);

  return (
    <Link
      href={`/challenge/${challenge.id}`}
      aria-label={`${t("card.solve", { default: "Résoudre" })}: ${challenge.title}`}
      className="block h-full"
    >
      <ContentCardBase
        completed={completed}
        titleId={`challenge-title-${challenge.id}`}
        descriptionId={`challenge-description-${challenge.id}`}
        completedLabel={t("card.completed", { default: "Résolu" })}
        completedAriaLabel={t("card.completed", { default: "Défi résolu" })}
      >
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle
                id={`challenge-title-${challenge.id}`}
                className="text-lg font-semibold mb-2"
              >
                {hasAiTag(challenge.tags) && (
                  <Sparkles
                    className="inline-block h-4 w-4 text-primary mr-1.5 align-middle shrink-0"
                    aria-label="Généré par intelligence artificielle"
                    aria-hidden={false}
                  />
                )}
                {challenge.title}
              </CardTitle>
              <CardDescription
                id={`challenge-description-${challenge.id}`}
                className="line-clamp-2"
              >
                <MathText size="sm">{challenge.description}</MathText>
              </CardDescription>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            <Badge
              variant="outline"
              className={`badge-sweep ${ageGroupColor}`}
              aria-label={`${t("card.ageGroup", { default: "Groupe d'âge:" })} ${ageGroupDisplay}`}
            >
              {ageGroupDisplay}
            </Badge>
            <Badge variant="outline" className="badge-sweep" aria-label={`Type: ${typeDisplay}`}>
              {typeDisplay}
            </Badge>
            {challenge.difficulty_rating && (
              <Badge
                variant="outline"
                className="badge-sweep bg-sky-500/20 text-sky-700 border-sky-500/30 dark:text-sky-300"
                aria-label={`${t("card.difficulty", { default: "Difficulté:" })} ${challenge.difficulty_rating.toFixed(1)}/5`}
              >
                ⭐ {challenge.difficulty_rating.toFixed(1)}/5
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex flex-col">
          <div className="flex items-center justify-between text-sm text-muted-foreground mb-3">
            <div
              className="flex items-center gap-4"
              role="group"
              aria-label={t("card.challengeInfo", { default: "Informations sur le défi" })}
            >
              {challenge.estimated_time_minutes && (
                <div
                  className="flex items-center gap-1"
                  aria-label={`${t("card.estimatedTime", { default: "Temps estimé:" })} ${challenge.estimated_time_minutes} min`}
                >
                  <Clock className="h-4 w-4" aria-hidden="true" />
                  <span>{challenge.estimated_time_minutes} min</span>
                </div>
              )}
              <div
                className="flex items-center gap-1"
                aria-label={`${challenge.view_count || 0} vue${(challenge.view_count || 0) > 1 ? "s" : ""}`}
              >
                <Eye className="h-4 w-4" aria-hidden="true" />
                <span>{challenge.view_count || 0}</span>
              </div>
              {formatSuccessRate(challenge.success_rate) && (
                <div
                  className="flex items-center gap-1"
                  aria-label={`${t("card.successRate", { default: "Taux de réussite:" })} ${formatSuccessRate(challenge.success_rate)}`}
                >
                  <TrendingUp className="h-4 w-4" aria-hidden="true" />
                  <span>{formatSuccessRate(challenge.success_rate)}</span>
                </div>
              )}
            </div>
          </div>
          {/* CTA pill discret */}
          <div className="flex justify-end pt-2 mt-3 border-t border-border/30">
            <span
              className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary transition-colors group-hover:bg-primary/20"
              aria-hidden="true"
            >
              {t("card.solve", { default: "Résoudre" })}
              <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </span>
          </div>
        </CardContent>
      </ContentCardBase>
    </Link>
  );
}
