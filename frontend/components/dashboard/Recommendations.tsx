"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sparkles, RefreshCw, Swords, Check } from "lucide-react";
import Link from "next/link";
import { useRecommendations, type Recommendation } from "@/hooks/useRecommendations";
import { cn } from "@/lib/utils/cn";
import { useExerciseTranslations } from "@/hooks/useChallengeTranslations";
import { useTranslations } from "next-intl";

export function Recommendations() {
  const { recommendations, isLoading, generate, isGenerating, complete, isCompleting } =
    useRecommendations();
  const t = useTranslations("dashboard.recommendations");
  const tCommon = useTranslations("common");
  const { getTypeDisplay, getAgeDisplay } = useExerciseTranslations();

  const handleRefresh = async () => {
    await generate();
  };

  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl text-foreground flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary-on-dark" />
            {t("title", { default: "Conseils du Maître Jedi" })}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isGenerating || isLoading}
          >
            <RefreshCw
              className={cn("h-4 w-4 mr-2", (isGenerating || isLoading) && "animate-spin")}
            />
            {t("refresh", { default: "Actualiser" })}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 2 }).map((_, index) => (
              <div key={index} className="p-4 rounded-lg bg-muted border animate-pulse">
                <div className="flex gap-2 mb-3">
                  <div className="h-5 w-20 bg-muted-foreground/20 rounded"></div>
                  <div className="h-5 w-16 bg-muted-foreground/20 rounded"></div>
                </div>
                <div className="h-4 w-3/4 bg-muted-foreground/20 rounded mb-2"></div>
                <div className="h-3 w-full bg-muted-foreground/20 rounded mb-2"></div>
                <div className="h-8 w-full bg-muted-foreground/20 rounded"></div>
              </div>
            ))}
          </div>
        ) : recommendations && recommendations.length > 0 ? (
          <div className="space-y-3">
            {recommendations.map((recommendation: Recommendation, index) => {
              const isChallenge =
                recommendation.recommendation_type === "challenge" || !!recommendation.challenge_id;
              const exerciseTypeDisplay = isChallenge
                ? t("challenge", { default: "Défi logique" })
                : getTypeDisplay(recommendation.exercise_type);
              const ageGroupDisplay = getAgeDisplay(recommendation.age_group);
              const priority = recommendation.priority ?? 5;
              const isHighPriority = priority >= 8;
              const title = recommendation.challenge_title || recommendation.exercise_title;

              return (
                <div
                  key={recommendation.id || index}
                  className={cn(
                    "p-4 rounded-lg bg-muted border transition-all hover:shadow-lg",
                    isHighPriority
                      ? "border-primary/30 hover:border-primary/50 shadow-md shadow-primary/10"
                      : "border-primary/10 hover:border-primary/30"
                  )}
                  role="article"
                  aria-label={`Recommandation: ${exerciseTypeDisplay} - ${ageGroupDisplay}`}
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex gap-2 flex-wrap flex-1">
                      <Badge
                        variant="outline"
                        className={cn(
                          "bg-primary/10 text-primary-on-dark border-primary/30",
                          isHighPriority && "bg-primary/20 border-primary/50",
                          isChallenge && "flex items-center gap-1"
                        )}
                      >
                        {isChallenge && <Swords className="h-3 w-3" />}
                        {exerciseTypeDisplay}
                      </Badge>
                      <Badge
                        variant="outline"
                        className="bg-secondary/10 text-secondary border-secondary/30"
                      >
                        {ageGroupDisplay}
                      </Badge>
                      {isHighPriority && (
                        <Badge className="bg-primary/20 text-primary-on-dark text-xs">
                          {t("priority", { default: "Prioritaire" })}
                        </Badge>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="shrink-0"
                      onClick={() => recommendation.id && complete(recommendation.id)}
                      disabled={isCompleting || !recommendation.id}
                      aria-label={tCommon("markAsDone")}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                  </div>
                  {title && <h4 className="font-semibold text-foreground mb-2">{title}</h4>}
                  <p className="text-sm text-muted-foreground italic mb-2">
                    {recommendation.reason}
                  </p>
                  {!isChallenge && recommendation.exercise_question && (
                    <p className="text-xs text-muted-foreground bg-card p-2 rounded mb-3 line-clamp-2">
                      {recommendation.exercise_question.length > 100
                        ? `${recommendation.exercise_question.substring(0, 100)}...`
                        : recommendation.exercise_question}
                    </p>
                  )}
                  {recommendation.challenge_id && (
                    <Button
                      asChild
                      size="sm"
                      variant={isChallenge ? "default" : "default"}
                      className="w-full"
                      aria-label={t("startChallenge", { default: "Relever le défi" })}
                    >
                      <Link href={`/challenge/${recommendation.challenge_id}`}>
                        {t("startChallenge", { default: "Relever le défi" })}
                      </Link>
                    </Button>
                  )}
                  {!recommendation.challenge_id && recommendation.exercise_id && (
                    <Button
                      asChild
                      size="sm"
                      className="w-full"
                      aria-label={`Commencer l'exercice ${title || exerciseTypeDisplay}`}
                    >
                      <Link href={`/exercises/${recommendation.exercise_id}`}>
                        {t("trainNow", { default: "S'entraîner maintenant" })}
                      </Link>
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <p>{t("empty", { default: "Aucune recommandation pour le moment." })}</p>
            <p className="text-sm mt-2">
              {t("emptyHint", { default: "Continuez votre entraînement !" })}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
