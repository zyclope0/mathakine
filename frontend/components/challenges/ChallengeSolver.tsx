"use client";

/**
 * ChallengeSolver — orchestrateur mince du solver de défi.
 *
 * Responsabilités :
 *   - consommer useChallenge + useChallenges
 *   - déléguer la logique runtime à useChallengeSolverController
 *   - gérer les early returns de statut via ChallengeSolverStatus
 *   - assembler les blocs visuels dans l'ordre de rendu
 *
 * FFI-L10 lot 3 — orchestrateur final.
 */

import { useEffect } from "react";
import { Loader2 } from "lucide-react";
import { debugLog } from "@/lib/utils/debug";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useChallenges } from "@/hooks/useChallenges";
import { useChallenge } from "@/hooks/useChallenge";
import { useChallengeSolverController } from "@/hooks/useChallengeSolverController";
import { LearnerCard } from "@/components/learner";
import { ChallengeSolverStatus } from "@/components/challenges/ChallengeSolverStatus";
import { ChallengeSolverHeader } from "@/components/challenges/ChallengeSolverHeader";
import { ChallengeSolverContent } from "@/components/challenges/ChallengeSolverContent";
import { ChallengeSolverHintsPanel } from "@/components/challenges/ChallengeSolverHintsPanel";
import { ChallengeSolverFeedback } from "@/components/challenges/ChallengeSolverFeedback";
import { ChallengeSolverHint } from "@/components/challenges/ChallengeSolverHint";
import { ChallengeSolverCommandBar } from "@/components/challenges/ChallengeSolverCommandBar";
import {
  getChallengeTypeDisplay,
  getAgeGroupDisplay,
  getAgeGroupColor,
} from "@/lib/constants/challenges";
import { useTranslations } from "next-intl";

interface ChallengeSolverProps {
  challengeId: number;
  onChallengeCompleted?: () => void;
}

export function ChallengeSolver({ challengeId, onChallengeCompleted }: ChallengeSolverProps) {
  const t = useTranslations("challenges.solver");
  const { theme } = useThemeStore();
  const { submitAnswer, isSubmitting, submitResult, getHint, setHints } = useChallenges();
  const { challenge, isLoading, error } = useChallenge(challengeId);

  // Debug (dev only)
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

  // Logique runtime locale centralisée dans le hook controller
  const ctrl = useChallengeSolverController({
    challengeId,
    challenge,
    submitAnswer,
    isSubmitting,
    submitResult,
    getHint,
    setHints,
    onChallengeCompleted,
  });

  // ─── Status screens (early returns) ────────────────────────────────────────

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

  // ─── Dérivés d'affichage (thème, labels) ───────────────────────────────────

  const ageGroupColor = getAgeGroupColor(challenge.age_group, theme);
  const typeDisplay = getChallengeTypeDisplay(challenge.challenge_type);
  const ageGroupDisplay = getAgeGroupDisplay(challenge.age_group);

  // visualModel est garanti non-null ici (challenge est défini + hook l'a calculé)
  const visualModel = ctrl.visualModel ?? {
    responseMode: "open_text" as const,
    showMcq: false,
    isVisual: false,
    visualChoices: [],
    visualPositions: [],
    hasVisualButtons: false,
    isVisualMultiComplete: true,
    derivedUserAnswerFromSelections: "",
  };

  const hintResponseMode = visualModel.showMcq
    ? ("single_choice" as const)
    : visualModel.responseMode === "interactive_visual"
      ? ("interactive_visual" as const)
      : ("text" as const);

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
          retryKey={ctrl.retryKey}
          onPuzzleOrderChange={ctrl.handlePuzzleOrderChange}
          onAnswerChange={ctrl.handleAnswerChange}
        />

        <ChallengeSolverHintsPanel
          hintsUsed={ctrl.hintsUsed}
          availableHints={ctrl.availableHints}
        />

        {ctrl.hasSubmitted && (
          <ChallengeSolverFeedback
            isCorrect={ctrl.isCorrect}
            pointsEarned={submitResult?.points_earned}
            solutionExplanation={challenge.solution_explanation}
            hintsUsedCount={ctrl.hintsUsed.length}
            availableHintsCount={ctrl.availableHints.length}
            onRetry={ctrl.handleRetry}
            onRequestHint={ctrl.handleRequestHint}
          />
        )}
      </LearnerCard>

      {/* U3 — Aide de première visite (entre LearnerCard et Command Bar) */}
      {!ctrl.hasSubmitted && (
        <ChallengeSolverHint
          responseMode={hintResponseMode}
          hasHints={ctrl.availableHints.length > 0}
        />
      )}

      {/* Command Bar */}
      {!ctrl.hasSubmitted && (
        <ChallengeSolverCommandBar
          userAnswer={ctrl.userAnswer}
          hasSubmitted={ctrl.hasSubmitted}
          isSubmitting={isSubmitting}
          isAnswerEmpty={ctrl.isAnswerEmpty}
          isDisabled={ctrl.isDisabled}
          hintsUsedCount={ctrl.hintsUsed.length}
          availableHintsCount={ctrl.availableHints.length}
          hasHints={ctrl.availableHints.length > 0 || !!challenge.hints}
          showMcq={visualModel.showMcq}
          choicesArray={ctrl.choicesArray}
          hasVisualButtons={visualModel.hasVisualButtons}
          visualChoices={visualModel.visualChoices}
          visualPositions={visualModel.visualPositions}
          visualSelections={ctrl.visualSelections}
          responseMode={visualModel.responseMode}
          challengeType={challenge.challenge_type}
          hasVisualData={!!challenge.visual_data}
          puzzleOrder={ctrl.puzzleOrder}
          textInputKind={ctrl.textInputKind}
          onSelectChoice={ctrl.setUserAnswer}
          onSelectVisualPosition={(pos, choice) =>
            ctrl.setVisualSelections((prev) => ({
              ...prev,
              [pos]: prev[pos] === choice ? "" : choice,
            }))
          }
          onSelectVisualSimple={(choice) =>
            ctrl.setUserAnswer(ctrl.userAnswer === choice ? "" : choice)
          }
          onUserAnswerChange={ctrl.setUserAnswer}
          onSubmit={ctrl.handleSubmit}
          onRequestHint={ctrl.handleRequestHint}
        />
      )}
    </>
  );
}
