"use client";

import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ContentCardBase } from "@/components/shared/ContentCardBase";
import {
  getChallengeTypeDisplay,
  getAgeGroupDisplay,
  getAgeGroupColor,
} from "@/lib/constants/challenges";
import { formatSuccessRate } from "@/lib/utils/format";
import type { Challenge } from "@/types/api";
import { Clock, Eye, TrendingUp, ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";
import { useCompletedChallenges } from "@/hooks/useCompletedItems";
import { useTranslations } from "next-intl";

interface ChallengeCardProps {
  challenge: Challenge;
}

export function ChallengeCard({ challenge }: ChallengeCardProps) {
  const t = useTranslations("challenges");
  const { isCompleted } = useCompletedChallenges();
  const typeDisplay = getChallengeTypeDisplay(challenge.challenge_type);
  const ageGroupDisplay = getAgeGroupDisplay(challenge.age_group);
  const ageGroupColor = getAgeGroupColor(challenge.age_group);
  const completed = isCompleted(challenge.id);

  return (
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
                className="text-lg mb-2 flex items-center gap-2"
              >
                {challenge.tags &&
                  (Array.isArray(challenge.tags)
                    ? challenge.tags.includes("ai")
                    : challenge.tags === "ai" ||
                      challenge.tags
                        .split(",")
                        .map((t) => t.trim())
                        .includes("ai")) && (
                    <Sparkles className="h-4 w-4 text-primary-on-dark" aria-hidden="true" />
                  )}
                {challenge.title}
              </CardTitle>
              <CardDescription
                id={`challenge-description-${challenge.id}`}
                className="line-clamp-2"
              >
                {challenge.description}
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
                className="badge-sweep bg-purple-500/20 text-purple-400 border-purple-500/30"
                aria-label={`${t("card.difficulty", { default: "Difficulté:" })} ${challenge.difficulty_rating.toFixed(1)}/5`}
              >
                ⭐ {challenge.difficulty_rating.toFixed(1)}/5
              </Badge>
            )}
            {challenge.tags &&
              (Array.isArray(challenge.tags)
                ? challenge.tags.includes("ai")
                : challenge.tags === "ai" ||
                  challenge.tags
                    .split(",")
                    .map((t) => t.trim())
                    .includes("ai")) && (
                <Badge
                  variant="outline"
                  className="badge-ai-pulse bg-primary/10 text-primary-on-dark border-primary/30"
                  aria-label={t("card.aiGenerated", {
                    default: "Généré par intelligence artificielle",
                  })}
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
          <div className="flex gap-2">
            <Button asChild className="btn-cta-primary flex-1">
              <Link
                href={`/challenge/${challenge.id}`}
                aria-label={`${t("card.solve", { default: "Résoudre" })}: ${challenge.title}`}
              >
                {t("card.solve", { default: "Résoudre" })}
                <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
              </Link>
            </Button>
          </div>
        </CardContent>
    </ContentCardBase>
  );
}
