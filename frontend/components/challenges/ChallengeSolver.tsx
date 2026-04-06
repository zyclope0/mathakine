"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Loader2, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";
import { debugLog } from "@/lib/utils/debug";
import { useTranslations } from "next-intl";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useChallenges } from "@/hooks/useChallenges";
import { useChallenge } from "@/hooks/useChallenge";
import { LearnerCard } from "@/components/learner";
import { ChallengeSolverHint } from "@/components/challenges/ChallengeSolverHint";
import { ChallengeSolverStatus } from "@/components/challenges/ChallengeSolverStatus";
import { ChallengeSolverHeader } from "@/components/challenges/ChallengeSolverHeader";
import { ChallengeSolverContent } from "@/components/challenges/ChallengeSolverContent";
import { ChallengeSolverHintsPanel } from "@/components/challenges/ChallengeSolverHintsPanel";
import { ChallengeSolverFeedback } from "@/components/challenges/ChallengeSolverFeedback";
import {
  getChallengeTypeDisplay,
  getAgeGroupDisplay,
  getAgeGroupColor,
} from "@/lib/constants/challenges";
import {
  getChallengeHintsArray,
  getChallengeVisualAnswerModel,
  isChallengeAnswerEmpty,
  getChallengeTextInputKind,
  normalizeChallengeChoices,
} from "@/lib/challenges/challengeSolver";

interface ChallengeSolverProps {
  challengeId: number;
  onChallengeCompleted?: () => void;
}

export function ChallengeSolver({ challengeId, onChallengeCompleted }: ChallengeSolverProps) {
  const t = useTranslations("challenges.solver");
  const { theme } = useThemeStore();
  const { submitAnswer, isSubmitting, submitResult, getHint, setHints } = useChallenges();
  const { challenge, isLoading, error } = useChallenge(challengeId);

  // ─── Debug (dev only) ──────────────────────────────────────────────────────
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

  // ─── State ─────────────────────────────────────────────────────────────────
  const [userAnswer, setUserAnswer] = useState<string>("");
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [, setShowExplanation] = useState(false);
  const [hintsUsed, setHintsUsed] = useState<number[]>([]);
  const [availableHints, setAvailableHints] = useState<string[]>([]);
  const [puzzleOrder, setPuzzleOrder] = useState<string[]>([]);
  const [visualSelections, setVisualSelections] = useState<Record<number, string>>({});
  const [retryKey, setRetryKey] = useState<number>(0);
  const startTimeRef = useRef<number>(0);

  useEffect(() => {
    startTimeRef.current = Date.now();
  }, []);

  // ─── Effects ───────────────────────────────────────────────────────────────

  // Initialise les indices disponibles à chaque changement de défi
  useEffect(() => {
    if (challenge?.hints) {
      setAvailableHints(getChallengeHintsArray(challenge.hints));
      setHints([]);
    } else {
      setAvailableHints([]);
    }
  }, [challenge, setHints]);

  // Marque comme soumis + callback quand le résultat arrive
  useEffect(() => {
    if (submitResult) {
      setHasSubmitted(true);
      if (submitResult.is_correct) {
        setShowExplanation(true);
        onChallengeCompleted?.();
      }
    }
  }, [submitResult, onChallengeCompleted]);

  // Réinitialise l'état à chaque changement de défi (id uniquement)
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [challenge?.id]);

  // ─── Dérivés visuels (avant tout early return) ─────────────────────────────
  const visualModel = challenge ? getChallengeVisualAnswerModel(challenge, visualSelections) : null;

  // Syncer les sélections multi-position vers userAnswer
  useEffect(() => {
    if (!visualModel?.hasVisualButtons || !visualModel.visualPositions.length) return;
    if (visualModel.visualPositions.length < 2) return;
    setUserAnswer(visualModel.derivedUserAnswerFromSelections);
  }, [
    visualModel?.hasVisualButtons,
    visualModel?.visualPositions,
    visualModel?.derivedUserAnswerFromSelections,
  ]);

  // ─── Handlers ──────────────────────────────────────────────────────────────

  const handleRetry = () => {
    setUserAnswer("");
    setHasSubmitted(false);
    setShowExplanation(false);
    setPuzzleOrder([]);
    setRetryKey((prev) => prev + 1);
    startTimeRef.current = Date.now();
  };

  const handlePuzzleOrderChange = useCallback(
    (order: string[]) => {
      setPuzzleOrder(order);
      if (challenge?.challenge_type?.toLowerCase() === "puzzle") {
        setUserAnswer(order.join(","));
      }
    },
    [challenge?.challenge_type]
  );

  const handleAnswerChange = useCallback(
    (answer: string) => {
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
      await getHint(challengeId);
    } catch {
      // L'indice local est révélé même si le tracking API échoue
    }
    setHintsUsed((prev) => [...prev, nextHintNumber]);
  };

  const handleSubmit = async () => {
    if (!userAnswer.trim() || !challenge || hasSubmitted) return;
    const timeSpent = (Date.now() - startTimeRef.current) / 1000;
    try {
      await submitAnswer({
        challenge_id: challenge.id,
        answer: userAnswer.trim(),
        time_spent: timeSpent,
        hints_used: hintsUsed,
      });
    } catch {
      // Erreur gérée par le hook useChallenges
    }
  };

  // ─── Early returns — status screens ────────────────────────────────────────

  if (isLoading || error || (!challenge && !isLoading && !error)) {
    return (
      <ChallengeSolverStatus
        challengeId={challengeId}
        isLoading={isLoading}
        error={error}
        notFound={!challenge && !isLoading && !error}
      />
    );
  }

  // Fallback spinner si challenge toujours absent après les conditions ci-dessus
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

  // ─── Dérivés post-guard ────────────────────────────────────────────────────

  const ageGroupColor = getAgeGroupColor(challenge.age_group, theme);
  const typeDisplay = getChallengeTypeDisplay(challenge.challenge_type);
  const ageGroupDisplay = getAgeGroupDisplay(challenge.age_group);
  const isCorrect = submitResult?.is_correct ?? false;
  const choicesArray = normalizeChallengeChoices(challenge);

  const {
    responseMode,
    showMcq,
    visualChoices,
    visualPositions,
    hasVisualButtons,
    isVisualMultiComplete,
  } = visualModel!;

  const isAnswerEmpty = isChallengeAnswerEmpty({
    hasVisualButtons,
    visualPositions,
    isVisualMultiComplete,
    userAnswer,
  });

  const isDisabled = isSubmitting || hasSubmitted || isAnswerEmpty;
  const textInputKind = getChallengeTextInputKind(challenge.challenge_type);

  // ─── Rendu principal ───────────────────────────────────────────────────────

  return (
    <>
      <LearnerCard variant="challenge">
        <ChallengeSolverHeader
          challengeId={challenge.id}
          title={challenge.title}
          ageGroupDisplay={ageGroupDisplay}
          ageGroupColor={ageGroupColor}
          typeDisplay={typeDisplay}
          difficultyRating={challenge.difficulty_rating}
        />

        <ChallengeSolverContent
          challenge={challenge}
          retryKey={retryKey}
          onPuzzleOrderChange={handlePuzzleOrderChange}
          onAnswerChange={handleAnswerChange}
        />

        <ChallengeSolverHintsPanel hintsUsed={hintsUsed} availableHints={availableHints} />

        {hasSubmitted && (
          <ChallengeSolverFeedback
            isCorrect={isCorrect}
            pointsEarned={submitResult?.points_earned}
            solutionExplanation={challenge.solution_explanation}
            hintsUsedCount={hintsUsed.length}
            availableHintsCount={availableHints.length}
            onRetry={handleRetry}
            onRequestHint={handleRequestHint}
          />
        )}
      </LearnerCard>

      {/* U3 — Aide de première visite (entre LearnerCard et Command Bar) */}
      {!hasSubmitted && (
        <ChallengeSolverHint
          responseMode={
            showMcq
              ? "single_choice"
              : responseMode === "interactive_visual"
                ? "interactive_visual"
                : "text"
          }
          hasHints={availableHints.length > 0}
        />
      )}

      {/* Command Bar — Zone de réponse (extraction prévue en lot 3) */}
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
                    textInputKind === "chess"
                      ? t("chessAnswerPlaceholder")
                      : textInputKind === "visual"
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
                {textInputKind === "chess" && (
                  <p className="text-xs text-muted-foreground">{t("chessAnswerFormat")}</p>
                )}
                {textInputKind === "visual" && (
                  <p className="text-xs text-muted-foreground">{t("visualAnswerFormat")}</p>
                )}
              </div>
            )}

            <div className="space-y-2 flex-1">
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
            </div>
          </div>
        </div>
      )}
    </>
  );
}
