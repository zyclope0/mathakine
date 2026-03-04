"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sparkles, RefreshCw, Swords, CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useRecommendations, type Recommendation } from "@/hooks/useRecommendations";
import { cn } from "@/lib/utils";
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
    <Card className="border-primary/20 bg-card/40 backdrop-blur-md">
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
            className="text-muted-foreground hover:text-foreground"
          >
            <RefreshCw
              className={cn("h-4 w-4 mr-2", (isGenerating || isLoading) && "animate-spin")}
            />
            {t("refresh", { default: "Actualiser" })}
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {/* Skeleton */}
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 2 }).map((_, index) => (
              <div key={index} className="p-5 rounded-xl border border-border/50 animate-pulse">
                <div className="flex gap-2 mb-4">
                  <div className="h-5 w-20 bg-muted-foreground/20 rounded-full" />
                  <div className="h-5 w-16 bg-muted-foreground/20 rounded-full" />
                </div>
                <div className="h-4 w-3/4 bg-muted-foreground/20 rounded mb-3" />
                <div className="h-3 w-full bg-muted-foreground/20 rounded mb-2" />
                <div className="h-12 w-full bg-muted-foreground/10 rounded-lg" />
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
              const href = recommendation.challenge_id
                ? `/challenge/${recommendation.challenge_id}`
                : recommendation.exercise_id
                  ? `/exercises/${recommendation.exercise_id}`
                  : null;
              const ctaLabel = isChallenge
                ? t("startChallenge", { default: "Relever le défi" })
                : t("trainNow", { default: "S'entraîner" });

              return (
                <div
                  key={recommendation.id || index}
                  className={cn(
                    "group rounded-xl border p-5 backdrop-blur-md",
                    "transition-all duration-300 hover:-translate-y-1 hover:shadow-lg",
                    isHighPriority
                      ? "border-primary/30 bg-primary/5 hover:border-primary/50 hover:shadow-primary/10"
                      : "border-border/50 bg-card/40 hover:border-primary/30"
                  )}
                  role="article"
                  aria-label={`Recommandation: ${exerciseTypeDisplay} - ${ageGroupDisplay}`}
                >
                  {/* Ligne 1 — Tags + bouton marquer comme fait */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex gap-2 flex-wrap flex-1">
                      <Badge
                        variant="outline"
                        className={cn(
                          "border-primary/30 bg-primary/10 text-primary-on-dark",
                          isChallenge && "flex items-center gap-1"
                        )}
                      >
                        {isChallenge && <Swords className="h-3 w-3" aria-hidden="true" />}
                        {exerciseTypeDisplay}
                      </Badge>
                      <Badge
                        variant="outline"
                        className="border-border/50 bg-muted/40 text-muted-foreground"
                      >
                        {ageGroupDisplay}
                      </Badge>
                      {isHighPriority && (
                        <Badge className="bg-amber-500/10 text-amber-500 border border-amber-500/30 text-xs">
                          {t("priority", { default: "Prioritaire" })}
                        </Badge>
                      )}
                    </div>

                    {/* Marquer comme fait — discret, coin haut-droit */}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 shrink-0 rounded-full text-muted-foreground/50 hover:text-success hover:bg-success/10 transition-colors"
                      onClick={() => recommendation.id && complete(recommendation.id)}
                      disabled={isCompleting || !recommendation.id}
                      aria-label={tCommon("markAsDone")}
                    >
                      <CheckCircle2 className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Titre */}
                  {title && (
                    <h4 className="font-semibold text-foreground mb-1.5 leading-snug">{title}</h4>
                  )}

                  {/* Raison — en italique discret */}
                  <p className="text-sm text-muted-foreground italic mb-3">
                    {recommendation.reason}
                  </p>

                  {/* Aperçu de l'exercice — style citation */}
                  {!isChallenge && recommendation.exercise_question && (
                    <blockquote className="border-l-4 border-primary/60 bg-primary/5 rounded-r-md px-4 py-3 mb-4">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {recommendation.exercise_question.length > 120
                          ? `${recommendation.exercise_question.substring(0, 120)}…`
                          : recommendation.exercise_question}
                      </p>
                    </blockquote>
                  )}

                  {/* CTA — pill discret aligné à droite */}
                  {href && (
                    <div className="flex justify-end">
                      <Link
                        href={href}
                        className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary transition-colors hover:bg-primary/20 group-hover:gap-3"
                        aria-label={`${ctaLabel}${title ? ` : ${title}` : ""}`}
                      >
                        {ctaLabel}
                        <ArrowRight className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                      </Link>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-10 text-muted-foreground">
            <Sparkles className="h-8 w-8 mx-auto mb-3 opacity-30" aria-hidden="true" />
            <p>{t("empty", { default: "Aucune recommandation pour le moment." })}</p>
            <p className="text-sm mt-1">
              {t("emptyHint", { default: "Continuez votre entraînement !" })}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
