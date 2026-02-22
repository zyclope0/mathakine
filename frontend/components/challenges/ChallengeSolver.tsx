"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
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
import { debugLog } from "@/lib/utils/debug";
import { ChallengeVisualRenderer } from "./visualizations/ChallengeVisualRenderer";
import { useTranslations } from "next-intl";
import {
  extractShapeChoicesFromVisualData,
  parsePositionsFromCorrectAnswer,
  parsePositionsFromQuestion,
  parsePositionsFromLayout,
} from "@/lib/utils/visualChallengeUtils";

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
          // JSON malformé, utiliser un tableau vide
          console.warn("Impossible de parser les indices JSON:", challenge.hints);
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

  // Réinitialiser l'état quand le défi change
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
  }, [challenge?.id]);

  // Syncer visualSelections multi-position vers userAnswer (doit être avant tout early return)
  const visualPositionsForSync =
    challenge &&
    (parsePositionsFromCorrectAnswer(challenge.correct_answer).length > 0
      ? parsePositionsFromCorrectAnswer(challenge.correct_answer)
      : parsePositionsFromQuestion(challenge.question).length > 0
        ? parsePositionsFromQuestion(challenge.question)
        : parsePositionsFromLayout(challenge.visual_data));
  const hasVisualButtonsForSync =
    challenge?.challenge_type?.toLowerCase() === "visual" &&
    !(Array.isArray(challenge.choices) && challenge.choices.length > 0) &&
    extractShapeChoicesFromVisualData(challenge.visual_data).length >= 2 &&
    !!challenge.visual_data;
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
    } catch (error) {
      // L'erreur est déjà gérée par le hook useChallenges
      // Ne pas logger en production pour éviter les fuites d'information
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">{t("loading")}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive">
        <CardContent className="pt-6">
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
        </CardContent>
      </Card>
    );
  }

  if (!challenge && !isLoading && !error) {
    // Cas où la requête a réussi mais n'a pas retourné de données
    return (
      <Card className="border-warning">
        <CardContent className="pt-6">
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
        </CardContent>
      </Card>
    );
  }

  if (!challenge) {
    // Pendant le chargement initial, afficher un loader
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">{t("loading")}</p>
        </div>
      </div>
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
  const hasChoices = choicesArray.length > 0;

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
    isVisual && !hasChoices && visualChoices.length >= 2 && !!challenge.visual_data;
  const isVisualMultiComplete =
    visualPositions.length <= 1 || visualPositions.every((p) => visualSelections[p]);

  return (
    <div className="space-y-6">
      {/* En-tête avec badges */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold text-foreground">
            {t("challengeNumber", { id: challenge.id })}
          </h2>
        </div>
        <div className="flex flex-wrap gap-2">
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
      </div>

      {/* Titre et description du défi */}
      <Card className="bg-card border-primary/20 shadow-lg">
        <CardHeader>
          <CardTitle className="text-3xl font-extrabold text-foreground">
            {challenge.title || t("noTitle")}
          </CardTitle>
          <CardDescription className="text-lg mt-2">
            {challenge.description || t("noDescription")}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {challenge.question && challenge.question !== challenge.description && (
            <div className="mb-4">
              <p className="text-foreground text-lg font-medium">{challenge.question}</p>
            </div>
          )}

          {challenge.image_url && (
            <div className="mb-4 flex justify-center">
              <div className="relative w-full max-w-2xl aspect-video rounded-lg overflow-hidden">
                <Image
                  src={challenge.image_url}
                  alt={t("challengeImage")}
                  fill
                  className="object-contain rounded-lg"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
                  loading="lazy"
                />
              </div>
            </div>
          )}

          {challenge.visual_data && (
            <div className="mb-4" key={`visual-${challenge.id}-${retryKey}`}>
              <ChallengeVisualRenderer
                challenge={challenge}
                onPuzzleOrderChange={handlePuzzleOrderChange}
                onAnswerChange={handleAnswerChange}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Zone de réponse */}
      {!hasSubmitted && (
        <Card className="bg-card border-primary/20">
          <CardHeader>
            <CardTitle>{t("yourAnswer")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {hasChoices ? (
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
                    tabIndex={userAnswer === choice ? 0 : -1}
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
            ) : challenge.challenge_type?.toLowerCase() === "puzzle" && puzzleOrder.length > 0 ? (
              <div className="space-y-3">
                <div className="p-4 bg-muted/30 rounded-lg border border-primary/20">
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
            ) : challenge.challenge_type?.toLowerCase() === "sequence" &&
              userAnswer &&
              challenge.visual_data ? (
              <div className="space-y-3">
                <div className="p-4 bg-muted/30 rounded-lg border border-primary/20">
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
            ) : challenge.challenge_type?.toLowerCase() === "pattern" &&
              userAnswer &&
              challenge.visual_data ? (
              <div className="space-y-3">
                <div className="p-4 bg-muted/30 rounded-lg border border-primary/20">
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
            ) : challenge.challenge_type?.toLowerCase() === "deduction" && challenge.visual_data ? (
              <div className="space-y-3">
                {userAnswer ? (
                  <div className="p-4 bg-success/10 rounded-lg border border-success/30">
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
                  <div className="p-4 bg-muted/30 rounded-lg border border-primary/20">
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

            <div className="flex gap-2">
              <Button
                onClick={handleSubmit}
                disabled={
                  isSubmitting ||
                  hasSubmitted ||
                  (hasVisualButtons
                    ? visualPositions.length > 1
                      ? !isVisualMultiComplete
                      : !userAnswer.trim()
                    : !userAnswer.trim())
                }
                className="flex-1"
                aria-label={isSubmitting ? t("validating") : t("validateAnswer")}
                aria-busy={isSubmitting}
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

              {/* Bouton d'indice - affiché si le challenge a des hints ou si on peut en demander */}
              {(availableHints.length > 0 || challenge?.hints) && (
                <Button
                  onClick={handleRequestHint}
                  variant="outline"
                  disabled={
                    hasSubmitted ||
                    (availableHints.length > 0 && hintsUsed.length >= availableHints.length)
                  }
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
          </CardContent>
        </Card>
      )}

      {/* Indices affichés */}
      {hintsUsed.length > 0 && (
        <Card className="bg-yellow-500/10 border-yellow-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-400">
              <Lightbulb className="h-5 w-5" />
              {t("hintsUsed")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {hintsUsed.map((hintIndex) => {
                const hintText =
                  hintIndex > 0 && hintIndex <= availableHints.length
                    ? availableHints[hintIndex - 1]
                    : null;
                if (!hintText) return null;
                return (
                  <li key={hintIndex} className="flex items-start gap-2">
                    <span className="text-yellow-400 font-bold">{hintIndex}.</span>
                    <span className="text-foreground">{hintText}</span>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Feedback après soumission */}
      {hasSubmitted && (
        <Card
          className={isCorrect ? "bg-success/10 border-success/30" : "bg-error/10 border-error/30"}
        >
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              {isCorrect ? (
                <CheckCircle className="h-8 w-8 text-success flex-shrink-0 mt-1" />
              ) : (
                <XCircle className="h-8 w-8 text-error flex-shrink-0 mt-1" />
              )}
              <div className="flex-1 space-y-2">
                <h3
                  className={`text-lg font-semibold ${isCorrect ? "text-success" : "text-error"}`}
                >
                  {isCorrect ? t("correctTitle") : t("incorrectTitle")}
                </h3>
                {isCorrect && challenge.solution_explanation && (
                  <div className="mt-4">
                    <p className="font-medium text-foreground mb-2">{t("explanationLabel")}</p>
                    <p className="text-muted-foreground">{challenge.solution_explanation}</p>
                  </div>
                )}
                {!isCorrect && (
                  <div className="mt-4">
                    <p className="text-muted-foreground mb-2">{t("tryAgain")}</p>
                    {availableHints.length > hintsUsed.length && (
                      <Button
                        onClick={handleRequestHint}
                        variant="outline"
                        size="sm"
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
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <Button asChild variant="outline" className="flex-1">
          <Link href="/challenges">
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t("back")}
          </Link>
        </Button>
        {hasSubmitted && !isCorrect && (
          <Button
            onClick={handleRetry}
            variant="default"
            className="flex-1"
            aria-label={t("retryLabel")}
          >
            <RotateCcw className="mr-2 h-4 w-4" aria-hidden="true" />
            {t("retry")}
          </Button>
        )}
        {hasSubmitted && isCorrect && (
          <Button asChild className="flex-1">
            <Link href="/challenges">{t("nextChallenge")}</Link>
          </Button>
        )}
      </div>
    </div>
  );
}
