"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Loader2,
  XCircle,
  ArrowLeft,
  CheckCircle,
  Lightbulb,
  AlertCircle,
  RotateCcw,
} from "lucide-react";
import {
  getChallengeTypeDisplay,
  getAgeGroupDisplay,
  getAgeGroupColor,
} from "@/lib/constants/challenges";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useChallenges } from "@/hooks/useChallenges";
import { useChallenge } from "@/hooks/useChallenge";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { debugLog } from "@/lib/utils/debug";
import { ChallengeVisualRenderer } from "./visualizations/ChallengeVisualRenderer";
import { useTranslations } from "next-intl";
import { MathText } from "@/components/ui/MathText";
import { GrowthMindsetHint } from "@/components/ui/GrowthMindsetHint";
import {
  extractShapeChoicesFromVisualData,
  parsePositionsFromCorrectAnswer,
  parsePositionsFromQuestion,
  parsePositionsFromLayout,
} from "@/lib/utils/visualChallengeUtils";
import { resolveChallengeResponseMode } from "@/lib/challenges/resolveChallengeResponseMode";
import { LearnerCard } from "@/components/learner";

interface ChallengeSolverProps {
  challengeId: number;
  onChallengeCompleted?: () => void;
}

export function ChallengeSolver({ challengeId, onChallengeCompleted }: ChallengeSolverProps) {
  const t = useTranslations("challenges.solver");
  const { theme } = useThemeStore();
  const { submitAnswer, isSubmitting, submitResult, getHint, setHints } = useChallenges();
  const { challenge, isLoading, error } = useChallenge(challengeId);

  // Debug logs (uniquement en développement)
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      debugLog("[ChallengeSolver] State:", {
        challengeId,
        isLoading,
        hasChallenge: !!challenge,
        error: error?.message,
      });
    }
  }, [challengeId, isLoading, challenge, error]);

  const [userAnswer, setUserAnswer] = useState<string>("");
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [, setShowExplanation] = useState(false);
  const [hintsUsed, setHintsUsed] = useState<number[]>([]);
  const [availableHints, setAvailableHints] = useState<string[]>([]);
  const [puzzleOrder, setPuzzleOrder] = useState<string[]>([]);
  const [visualSelections, setVisualSelections] = useState<Record<number, string>>({});
  const [retryKey, setRetryKey] = useState<number>(0); // Clé pour forcer la réinitialisation des visualisations
  const startTimeRef = useRef<number>(0);
  useEffect(() => {
    startTimeRef.current = Date.now();
  }, []);

  // Initialiser les indices disponibles
  useEffect(() => {
    if (challenge?.hints) {
      // S'assurer que hints est un tableau avec gestion d'erreur JSON
      let hintsArray: string[] = [];
      if (Array.isArray(challenge.hints)) {
        hintsArray = challenge.hints;
      } else if (typeof challenge.hints === "string") {
        try {
          const parsed = JSON.parse(challenge.hints);
          hintsArray = Array.isArray(parsed) ? parsed : [];
        } catch {
          hintsArray = [];
        }
      }
      setAvailableHints(hintsArray);
      // Réinitialiser les indices du hook quand on change de défi
      setHints([]);
    } else {
      setAvailableHints([]);
    }
  }, [challenge, setHints]);

  // Mettre à jour l'état quand le résultat arrive
  useEffect(() => {
    if (submitResult) {
      setHasSubmitted(true);
      if (submitResult.is_correct) {
        setShowExplanation(true);

        // L'invalidation est déjà gérée dans useChallenges.ts dans onSuccess de la mutation
        // On peut juste appeler le callback si fourni
        if (onChallengeCompleted) {
          onChallengeCompleted();
        }
      }
    }
  }, [submitResult, onChallengeCompleted]);

  // Réinitialiser l'état quand le défi change (dépendance sur l'id pour éviter
  // un reset si l'objet challenge est recréé sans changement de contenu)
  useEffect(() => {
    if (challenge) {
      setUserAnswer("");
      setHasSubmitted(false);
      setShowExplanation(false);
      setHintsUsed([]);
      setPuzzleOrder([]);
      setVisualSelections({});
      startTimeRef.current = Date.now();
    }
    // exhaustive-deps: id seul (voir commentaire ci-dessus) — éviter reset si l’objet challenge est recréé à contenu identique.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [challenge?.id]);

  // Syncer visualSelections multi-position vers userAnswer (doit être avant tout early return)
  const visualPositionsForSync =
    challenge &&
    (parsePositionsFromCorrectAnswer(challenge.correct_answer).length > 0
      ? parsePositionsFromCorrectAnswer(challenge.correct_answer)
      : parsePositionsFromQuestion(challenge.question).length > 0
        ? parsePositionsFromQuestion(challenge.question)
        : parsePositionsFromLayout(challenge.visual_data));
  const challengeForSync = challenge;
  const responseModeForSync = challengeForSync
    ? resolveChallengeResponseMode(challengeForSync)
    : "open_text";
  const choicesLen =
    challengeForSync && Array.isArray(challengeForSync.choices)
      ? challengeForSync.choices.length
      : 0;
  const showMcqForSync = responseModeForSync === "single_choice" && choicesLen > 0;
  const hasVisualButtonsForSync =
    challengeForSync?.challenge_type?.toLowerCase() === "visual" &&
    responseModeForSync === "interactive_visual" &&
    !showMcqForSync &&
    extractShapeChoicesFromVisualData(challengeForSync?.visual_data).length >= 2 &&
    !!challengeForSync?.visual_data;
  useEffect(() => {
    if (!hasVisualButtonsForSync || !visualPositionsForSync || visualPositionsForSync.length < 2)
      return;
    const parts = visualPositionsForSync
      .filter((p) => visualSelections[p])
      .map((p) => `Position ${p}: ${visualSelections[p]}`);
    setUserAnswer(parts.join(", "));
  }, [visualSelections, visualPositionsForSync, hasVisualButtonsForSync]);

  // Fonction pour réessayer le défi
  const handleRetry = () => {
    setUserAnswer("");
    setHasSubmitted(false);
    setShowExplanation(false);
    // Réinitialiser l'ordre du puzzle pour permettre une nouvelle tentative
    setPuzzleOrder([]);
    // Incrémenter la clé pour forcer la réinitialisation des visualisations
    setRetryKey((prev) => prev + 1);
    // Réinitialiser le timer
    startTimeRef.current = Date.now();
    // Note: On garde les indices utilisés pour que l'utilisateur puisse les voir
    // mais il peut toujours demander de nouveaux indices
  };

  // Callbacks mémorisés pour les visualisations
  const handlePuzzleOrderChange = useCallback(
    (order: string[]) => {
      setPuzzleOrder(order);
      // Pour les puzzles, utiliser l'ordre comme réponse
      if (challenge?.challenge_type?.toLowerCase() === "puzzle") {
        setUserAnswer(order.join(","));
      }
    },
    [challenge?.challenge_type]
  );

  const handleAnswerChange = useCallback(
    (answer: string) => {
      // Pour les séquences, patterns et déduction, utiliser la réponse directement
      const challengeType = challenge?.challenge_type?.toLowerCase();
      if (
        challengeType === "sequence" ||
        challengeType === "pattern" ||
        challengeType === "deduction"
      ) {
        setUserAnswer(answer);
      }
    },
    [challenge?.challenge_type]
  );

  const handleRequestHint = async () => {
    if (!challenge || hintsUsed.length >= availableHints.length) return;

    const nextHintNumber = hintsUsed.length + 1;

    try {
      // Appel API pour signaler l'utilisation de l'indice (tracking)
      await getHint(challengeId);
    } catch {
      // Même si l'API échoue, on révèle l'indice local
    }

    // Révéler l'indice suivant depuis les indices déjà chargés
    setHintsUsed((prev) => [...prev, nextHintNumber]);
  };

  const handleSubmit = async () => {
    if (!userAnswer.trim() || !challenge || hasSubmitted) return;

    const timeSpent = (Date.now() - startTimeRef.current) / 1000; // en secondes

    try {
      await submitAnswer({
        challenge_id: challenge.id,
        answer: userAnswer.trim(),
        time_spent: timeSpent,
        hints_used: hintsUsed,
      });
    } catch {
      // L'erreur est déjà gérée par le hook useChallenges
    }
  };

  if (isLoading) {
    return (
      <LearnerCard variant="challenge">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
            <p className="text-muted-foreground">{t("loading")}</p>
          </div>
        </div>
      </LearnerCard>
    );
  }

  if (error) {
    return (
      <LearnerCard variant="challenge">
        <div className="text-center space-y-4" role="alert" aria-live="assertive">
          <XCircle className="h-12 w-12 text-destructive mx-auto" />
          <div>
            <h3 className="text-lg font-semibold text-destructive">{t("error.title")}</h3>
            <p className="text-muted-foreground mt-2">
              {error.status === 404 ? t("error.notFound") : error.message || t("error.generic")}
            </p>
          </div>
          <Button asChild variant="outline">
            <Link href="/challenges">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("back")}
            </Link>
          </Button>
        </div>
      </LearnerCard>
    );
  }

  if (!challenge && !isLoading && !error) {
    return (
      <LearnerCard variant="challenge">
        <div className="text-center space-y-4" role="alert" aria-live="assertive">
          <AlertCircle className="h-12 w-12 text-warning mx-auto" />
          <div>
            <h3 className="text-lg font-semibold text-warning">{t("notFound.title")}</h3>
            <p className="text-muted-foreground mt-2">
              {t("notFound.message", { id: challengeId })}
            </p>
          </div>
          <Button asChild variant="outline">
            <Link href="/challenges">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("back")}
            </Link>
          </Button>
        </div>
      </LearnerCard>
    );
  }

  if (!challenge) {
    return (
      <LearnerCard variant="challenge">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
            <p className="text-muted-foreground">{t("loading")}</p>
          </div>
        </div>
      </LearnerCard>
    );
  }

  const ageGroupColor = getAgeGroupColor(challenge.age_group, theme);
  const typeDisplay = getChallengeTypeDisplay(challenge.challenge_type);
  const ageGroupDisplay = getAgeGroupDisplay(challenge.age_group);
  const isCorrect = submitResult?.is_correct ?? false;

  // Normaliser choices pour s'assurer que c'est toujours un tableau
  const choicesArray = Array.isArray(challenge.choices)
    ? challenge.choices
    : typeof challenge.choices === "string"
      ? (() => {
          try {
            const parsed = JSON.parse(challenge.choices);
            return Array.isArray(parsed) ? parsed : [];
          } catch {
            return [];
          }
        })()
      : [];

  const responseMode = resolveChallengeResponseMode(challenge);
  const showMcq = responseMode === "single_choice" && choicesArray.length > 0;

  // Choix dérivés pour VISUAL (toutes les formes du défi, pas d'orientation)
  const isVisual = challenge.challenge_type?.toLowerCase() === "visual";
  const visualChoices =
    isVisual && challenge.visual_data
      ? extractShapeChoicesFromVisualData(challenge.visual_data)
      : [];
  const visualPositions =
    parsePositionsFromCorrectAnswer(challenge.correct_answer).length > 0
      ? parsePositionsFromCorrectAnswer(challenge.correct_answer)
      : parsePositionsFromQuestion(challenge.question).length > 0
        ? parsePositionsFromQuestion(challenge.question)
        : parsePositionsFromLayout(challenge.visual_data);
  const hasVisualButtons =
    responseMode === "interactive_visual" &&
    !showMcq &&
    visualChoices.length >= 2 &&
    !!challenge.visual_data;
  const isVisualMultiComplete =
    visualPositions.length <= 1 || visualPositions.every((p) => visualSelections[p]);

  return (
    <>
      <LearnerCard variant="challenge">
        {/* Bouton Retour */}
        <Link
          href="/challenges"
          className="text-muted-foreground hover:text-foreground transition-colors mb-6 inline-flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          {t("back")}
        </Link>

        {/* En-tête : Défi #XXXX discret, titre star, tags */}
        <p className="text-sm text-muted-foreground font-mono">
          {t("challengeNumber", { id: challenge.id })}
        </p>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground mt-2 mb-6">
          {challenge.title || t("noTitle")}
        </h1>
        <div className="flex flex-wrap gap-2 mb-6">
          <Badge variant="outline" className={ageGroupColor}>
            {ageGroupDisplay}
          </Badge>
          <Badge variant="outline">{typeDisplay}</Badge>
          {challenge.difficulty_rating && (
            <Badge
              variant="outline"
              className="bg-purple-500/20 text-purple-400 border-purple-500/30"
            >
              ⭐ {challenge.difficulty_rating.toFixed(1)}/5
            </Badge>
          )}
        </div>

        {/* Description et contenu */}
        <div className="space-y-4">
          {challenge.description && (
            <div className="bg-muted/50 border border-border rounded-xl p-4">
              <MathText size="lg" className="text-foreground">
                {challenge.description}
              </MathText>
            </div>
          )}
          {challenge.question && challenge.question !== challenge.description && (
            <div className="bg-muted/50 border border-border rounded-xl p-4">
              <MathText size="lg" className="text-foreground font-medium">
                {challenge.question}
              </MathText>
            </div>
          )}

          {challenge.image_url && (
            <div className="flex justify-center">
              <div className="relative w-full max-w-2xl aspect-video rounded-xl overflow-hidden border border-border">
                <Image
                  src={challenge.image_url}
                  alt={t("challengeImage")}
                  fill
                  className="object-contain rounded-xl"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
                  loading="lazy"
                />
              </div>
            </div>
          )}

          {challenge.visual_data && (
            <div key={`visual-${challenge.id}-${retryKey}`}>
              <ChallengeVisualRenderer
                challenge={challenge}
                onPuzzleOrderChange={handlePuzzleOrderChange}
                onAnswerChange={handleAnswerChange}
              />
            </div>
          )}
        </div>

        {/* Indices affichés */}
        {hintsUsed.length > 0 && (
          <div className="mt-6 bg-muted/50 border border-border rounded-xl p-4">
            <h3 className="flex items-center gap-2 text-amber-400 font-semibold mb-3">
              <Lightbulb className="h-5 w-5" />
              {t("hintsUsed")}
            </h3>
            <ul className="space-y-2">
              {hintsUsed.map((hintIndex) => {
                const hintText =
                  hintIndex > 0 && hintIndex <= availableHints.length
                    ? availableHints[hintIndex - 1]
                    : null;
                if (!hintText) return null;
                return (
                  <li key={hintIndex} className="flex items-start gap-2">
                    <span className="text-amber-400 font-bold">{hintIndex}.</span>
                    <span className="text-foreground">{hintText}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {/* Feedback après soumission */}
        {hasSubmitted && (
          <div
            className={cn(
              "mt-6 rounded-xl p-4 border",
              isCorrect
                ? "bg-emerald-500/10 border-emerald-500/30"
                : "bg-red-500/10 border-red-500/30"
            )}
          >
            <div className="flex items-start gap-4">
              {isCorrect ? (
                <CheckCircle className="h-8 w-8 text-emerald-400 flex-shrink-0 mt-1" />
              ) : (
                <XCircle className="h-8 w-8 text-red-400 flex-shrink-0 mt-1" />
              )}
              <div className="flex-1 space-y-2">
                <h3
                  className={cn(
                    "text-lg font-semibold",
                    isCorrect ? "text-emerald-400" : "text-red-400"
                  )}
                >
                  {isCorrect ? t("correctTitle") : t("incorrectTitle")}
                </h3>
                {isCorrect &&
                  submitResult &&
                  typeof submitResult.points_earned === "number" &&
                  submitResult.points_earned > 0 && (
                    <p
                      className="text-sm font-medium text-emerald-500/95"
                      data-testid="challenge-points-earned"
                    >
                      {t("pointsEarned", { count: submitResult.points_earned })}
                    </p>
                  )}
                {isCorrect && challenge.solution_explanation && (
                  <div className="mt-4">
                    <p className="font-medium text-foreground mb-2">{t("explanationLabel")}</p>
                    <MathText size="base" className="text-muted-foreground">
                      {challenge.solution_explanation}
                    </MathText>
                  </div>
                )}
                {!isCorrect && (
                  <div className="mt-4">
                    <GrowthMindsetHint
                      className="text-muted-foreground mb-3"
                      supportText={t("tryAgain")}
                      strategyText={t("tryAgainStrategy")}
                    />
                    {availableHints.length > hintsUsed.length && (
                      <Button
                        onClick={handleRequestHint}
                        variant="outline"
                        size="sm"
                        className="border-amber-500/30 text-amber-400 hover:bg-amber-500/10"
                        aria-label={t("requestHint", {
                          current: hintsUsed.length + 1,
                          total: availableHints.length,
                        })}
                      >
                        <Lightbulb className="mr-2 h-4 w-4" aria-hidden="true" />
                        {t("seeNextHint")}
                      </Button>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-8 mt-8 border-t border-border">
          <Button
            asChild
            variant="outline"
            className="flex-1 bg-transparent border border-border text-muted-foreground hover:bg-accent hover:text-foreground px-6 py-3 rounded-xl transition-colors"
          >
            <Link href="/challenges">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("back")}
            </Link>
          </Button>
          {hasSubmitted && !isCorrect && (
            <Button
              onClick={handleRetry}
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
              aria-label={t("retryLabel")}
            >
              <RotateCcw className="mr-2 h-4 w-4" aria-hidden="true" />
              {t("retry")}
            </Button>
          )}
          {hasSubmitted && isCorrect && (
            <Button
              asChild
              className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/25 border-none px-6 py-3 rounded-xl font-medium transition-all hover:-translate-y-0.5"
            >
              <Link href="/challenges">{t("nextChallenge")}</Link>
            </Button>
          )}
        </div>
      </LearnerCard>

      {/* Command Bar — Zone de réponse et d'action */}
      {!hasSubmitted && (
        <div
          data-learner-context
          className="bg-[var(--bg-learner,var(--card))] border border-border/40 rounded-2xl p-6 max-w-5xl mx-auto"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">{t("yourAnswer")}</h3>
          <div className="space-y-4">
            {showMcq ? (
              <div
                className="grid grid-cols-1 sm:grid-cols-2 gap-3"
                role="radiogroup"
                aria-label="Choix de réponses pour le défi logique"
              >
                {choicesArray.map((choice, index) => (
                  <Button
                    key={index}
                    variant={userAnswer === choice ? "default" : "outline"}
                    onClick={() => setUserAnswer(choice)}
                    className="h-auto py-4 text-left justify-start"
                    disabled={hasSubmitted}
                    role="radio"
                    aria-checked={userAnswer === choice}
                    aria-label={`${t("option", { index: index + 1 })}: ${choice}`}
                    tabIndex={hasSubmitted ? -1 : userAnswer === choice || index === 0 ? 0 : -1}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setUserAnswer(choice);
                      }
                      // Navigation par flèches
                      if (e.key === "ArrowRight" && index < choicesArray.length - 1) {
                        e.preventDefault();
                        const nextButton = e.currentTarget.parentElement?.children[
                          index + 1
                        ] as HTMLElement;
                        nextButton?.focus();
                      }
                      if (e.key === "ArrowLeft" && index > 0) {
                        e.preventDefault();
                        const prevButton = e.currentTarget.parentElement?.children[
                          index - 1
                        ] as HTMLElement;
                        prevButton?.focus();
                      }
                    }}
                  >
                    {choice}
                  </Button>
                ))}
              </div>
            ) : hasVisualButtons ? (
              <div className="space-y-4">
                {visualPositions.length > 1 ? (
                  visualPositions.map((pos) => (
                    <div key={pos}>
                      <p className="text-sm font-medium text-foreground mb-2">
                        {t("positionLabel", { position: pos })}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {visualChoices.map((choice) => {
                          const isSelected = visualSelections[pos] === choice;
                          return (
                            <Button
                              key={`${pos}-${choice}`}
                              variant={isSelected ? "default" : "outline"}
                              size="sm"
                              onClick={() =>
                                setVisualSelections((prev) => ({
                                  ...prev,
                                  [pos]: prev[pos] === choice ? "" : choice,
                                }))
                              }
                              disabled={hasSubmitted}
                              aria-pressed={isSelected}
                            >
                              {choice}
                            </Button>
                          );
                        })}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {visualChoices.map((choice) => {
                      const isSelected = userAnswer === choice;
                      return (
                        <Button
                          key={choice}
                          variant={isSelected ? "default" : "outline"}
                          size="sm"
                          onClick={() => setUserAnswer(isSelected ? "" : choice)}
                          disabled={hasSubmitted}
                          aria-pressed={isSelected}
                        >
                          {choice}
                        </Button>
                      );
                    })}
                  </div>
                )}
                <p className="text-xs text-muted-foreground">{t("visualSelectHint")}</p>
              </div>
            ) : responseMode === "interactive_order" &&
              challenge.challenge_type?.toLowerCase() === "puzzle" &&
              puzzleOrder.length > 0 ? (
              <div className="space-y-3">
                <div className="p-4 bg-muted/50 rounded-xl border border-border">
                  <p className="text-sm font-medium text-foreground mb-2">{t("currentOrder")}</p>
                  <div className="flex flex-wrap gap-2">
                    {puzzleOrder.map((item, index) => (
                      <Badge key={index} variant="outline" className="text-sm">
                        {index + 1}. {item}
                      </Badge>
                    ))}
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">{t("reorderHint")}</p>
                <Input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder={t("orderAutoGenerated")}
                  className="opacity-50"
                  disabled
                  aria-label={t("puzzleAnswerLabel")}
                />
              </div>
            ) : responseMode === "interactive_grid" &&
              challenge.challenge_type?.toLowerCase() === "sequence" &&
              userAnswer &&
              challenge.visual_data ? (
              <div className="space-y-3">
                <div className="p-4 bg-muted/50 rounded-xl border border-border">
                  <p className="text-sm font-medium text-foreground mb-2">{t("yourAnswerLabel")}</p>
                  <Badge variant="outline" className="text-lg px-4 py-2">
                    {userAnswer}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{t("modifyInVisualization")}</p>
                <Input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder={t("answerFromVisualization")}
                  className="opacity-50"
                  disabled
                  aria-label={t("sequenceAnswerLabel")}
                />
              </div>
            ) : responseMode === "interactive_grid" &&
              challenge.challenge_type?.toLowerCase() === "pattern" &&
              userAnswer &&
              challenge.visual_data ? (
              <div className="space-y-3">
                <div className="p-4 bg-muted/50 rounded-xl border border-border">
                  <p className="text-sm font-medium text-foreground mb-2">{t("yourAnswerLabel")}</p>
                  <Badge variant="outline" className="text-lg px-4 py-2">
                    {userAnswer}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{t("modifyInVisualization")}</p>
                <Input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder={t("answerFromVisualization")}
                  className="opacity-50"
                  disabled
                  aria-label={t("patternAnswerLabel")}
                />
              </div>
            ) : responseMode === "interactive_grid" &&
              challenge.challenge_type?.toLowerCase() === "deduction" &&
              challenge.visual_data ? (
              <div className="space-y-3">
                {userAnswer ? (
                  <div className="p-4 bg-muted/50 rounded-xl border border-border">
                    <p className="text-sm font-medium text-foreground mb-2">
                      {t("yourAssociations") || "Vos associations"}
                    </p>
                    <div className="space-y-1">
                      {userAnswer.split(",").map((association, index) => {
                        const parts = association.split(":");
                        return (
                          <div key={index} className="flex items-center gap-2 text-sm">
                            <Badge variant="outline" className="bg-primary/10">
                              {parts[0]}
                            </Badge>
                            <span className="text-muted-foreground">→</span>
                            {parts.slice(1).map((part, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {part}
                              </Badge>
                            ))}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-muted/50 rounded-xl border border-border">
                    <p className="text-sm text-muted-foreground">
                      {t("completeAssociationsAbove") ||
                        "Complétez vos associations dans la grille ci-dessus"}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-1.5">
                <Input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder={
                    challenge.challenge_type?.toLowerCase() === "chess"
                      ? t("chessAnswerPlaceholder")
                      : challenge.challenge_type?.toLowerCase() === "visual"
                        ? t("visualAnswerPlaceholder")
                        : t("enterAnswer")
                  }
                  className="text-lg"
                  disabled={hasSubmitted}
                  aria-label={t("answerFieldLabel")}
                  aria-required="true"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && userAnswer.trim() && !isSubmitting) {
                      handleSubmit();
                    }
                  }}
                />
                {challenge.challenge_type?.toLowerCase() === "chess" && (
                  <p className="text-xs text-muted-foreground">{t("chessAnswerFormat")}</p>
                )}
                {challenge.challenge_type?.toLowerCase() === "visual" && (
                  <p className="text-xs text-muted-foreground">{t("visualAnswerFormat")}</p>
                )}
              </div>
            )}

            <div className="space-y-2 flex-1">
              {(() => {
                const isAnswerEmpty = hasVisualButtons
                  ? visualPositions.length > 1
                    ? !isVisualMultiComplete
                    : !userAnswer.trim()
                  : !userAnswer.trim();
                const isDisabled = isSubmitting || hasSubmitted || isAnswerEmpty;
                return (
                  <>
                    <div className="flex gap-3">
                      <Button
                        onClick={handleSubmit}
                        disabled={isDisabled}
                        className={cn(
                          "flex-1 px-6 py-3 rounded-2xl font-medium transition-all",
                          isAnswerEmpty && !isSubmitting
                            ? "opacity-60 cursor-not-allowed bg-muted text-muted-foreground border border-border"
                            : "bg-primary text-primary-foreground"
                        )}
                        aria-label={isSubmitting ? t("validating") : t("validateAnswer")}
                        aria-busy={isSubmitting}
                        aria-describedby={
                          isAnswerEmpty && !isSubmitting ? "challenge-validate-hint" : undefined
                        }
                      >
                        {isSubmitting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            {t("checking")}
                          </>
                        ) : (
                          t("validate")
                        )}
                      </Button>

                      {(availableHints.length > 0 || challenge?.hints) && (
                        <Button
                          onClick={handleRequestHint}
                          variant="outline"
                          disabled={
                            hasSubmitted ||
                            (availableHints.length > 0 && hintsUsed.length >= availableHints.length)
                          }
                          className="border border-amber-500/30 text-amber-400 hover:bg-amber-500/10 transition-colors px-6 py-3 rounded-2xl"
                          aria-label={
                            availableHints.length > 0
                              ? t("requestHint", {
                                  current: hintsUsed.length + 1,
                                  total: availableHints.length,
                                })
                              : t("requestHintGeneric")
                          }
                        >
                          <Lightbulb className="mr-2 h-4 w-4" aria-hidden="true" />
                          {availableHints.length > 0
                            ? t("hintButton", {
                                current: hintsUsed.length + 1,
                                total: availableHints.length,
                              })
                            : t("hintButtonGeneric")}
                        </Button>
                      )}
                    </div>
                    {isAnswerEmpty && !isSubmitting && (
                      <p
                        id="challenge-validate-hint"
                        className="text-center text-xs text-muted-foreground"
                        aria-live="polite"
                      >
                        {t("validateHint")}
                      </p>
                    )}
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
