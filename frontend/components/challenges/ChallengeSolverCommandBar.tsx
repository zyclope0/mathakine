"use client";

/**
 * ChallengeSolverCommandBar — Zone de réponse et de validation du défi.
 *
 * Composant purement visuel + callbacks. Aucun fetch, aucun parsing JSON.
 * Toute la logique métier de dérivation est portée par useChallengeSolverController.
 *
 * Branches de rendu (mutuellement exclusives) :
 *   1. QCM              — showMcq=true
 *   2. Visual buttons   — hasVisualButtons=true  (simple ou multi-position)
 *   3. Order puzzle     — interactive_order + puzzleOrder non vide
 *   4. Grid sequence    — interactive_grid + type=sequence + réponse auto
 *   5. Grid pattern     — interactive_grid + type=pattern  + réponse auto
 *   6. Grid deduction   — interactive_grid + type=deduction
 *   7. Texte libre      — fallback
 *
 * FFI-L10 lot 3 — extraction Command Bar.
 */

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Loader2, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import type { ChallengeResponseMode } from "@/lib/challenges/resolveChallengeResponseMode";
import type { ChallengeTextInputKind } from "@/lib/challenges/challengeSolver";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ChallengeSolverCommandBarProps {
  // État courant
  userAnswer: string;
  hasSubmitted: boolean;
  isSubmitting: boolean;
  isAnswerEmpty: boolean;
  isDisabled: boolean;
  hintsUsedCount: number;
  availableHintsCount: number;
  hasHints: boolean;

  // Dérivés visuels
  showMcq: boolean;
  choicesArray: string[];
  hasVisualButtons: boolean;
  visualChoices: string[];
  visualPositions: number[];
  visualSelections: Record<number, string>;
  responseMode: ChallengeResponseMode;
  challengeType: string;
  hasVisualData: boolean;
  puzzleOrder: string[];
  textInputKind: ChallengeTextInputKind;

  // Handlers
  onSelectChoice: (choice: string) => void;
  onSelectVisualPosition: (pos: number, choice: string) => void;
  onSelectVisualSimple: (choice: string) => void;
  onUserAnswerChange: (value: string) => void;
  onSubmit: () => void;
  onRequestHint: () => void;
}

// ─── Helpers locaux (rendu uniquement, sans logique métier) ───────────────────

function McqGrid({
  choicesArray,
  userAnswer,
  hasSubmitted,
  onSelectChoice,
  t,
}: {
  choicesArray: string[];
  userAnswer: string;
  hasSubmitted: boolean;
  onSelectChoice: (c: string) => void;
  t: ReturnType<typeof useTranslations<"challenges.solver">>;
}) {
  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 gap-3"
      role="radiogroup"
      aria-label="Choix de réponses pour le défi logique"
    >
      {choicesArray.map((choice, index) => (
        <Button
          key={index}
          variant={userAnswer === choice ? "default" : "outline"}
          onClick={() => onSelectChoice(choice)}
          className="h-auto py-4 text-left justify-start"
          disabled={hasSubmitted}
          role="radio"
          aria-checked={userAnswer === choice}
          aria-label={`${t("option", { index: index + 1 })}: ${choice}`}
          tabIndex={hasSubmitted ? -1 : userAnswer === choice || index === 0 ? 0 : -1}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              onSelectChoice(choice);
            }
            if (e.key === "ArrowRight" && index < choicesArray.length - 1) {
              e.preventDefault();
              const next = e.currentTarget.parentElement?.children[index + 1] as HTMLElement;
              next?.focus();
            }
            if (e.key === "ArrowLeft" && index > 0) {
              e.preventDefault();
              const prev = e.currentTarget.parentElement?.children[index - 1] as HTMLElement;
              prev?.focus();
            }
          }}
        >
          {choice}
        </Button>
      ))}
    </div>
  );
}

function VisualButtons({
  visualPositions,
  visualChoices,
  visualSelections,
  userAnswer,
  hasSubmitted,
  onSelectPosition,
  onSelectSimple,
  t,
}: {
  visualPositions: number[];
  visualChoices: string[];
  visualSelections: Record<number, string>;
  userAnswer: string;
  hasSubmitted: boolean;
  onSelectPosition: (pos: number, choice: string) => void;
  onSelectSimple: (choice: string) => void;
  t: ReturnType<typeof useTranslations<"challenges.solver">>;
}) {
  return (
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
                    onClick={() => onSelectPosition(pos, choice)}
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
                onClick={() => onSelectSimple(choice)}
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
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────

export function ChallengeSolverCommandBar({
  userAnswer,
  hasSubmitted,
  isSubmitting,
  isAnswerEmpty,
  isDisabled,
  hintsUsedCount,
  availableHintsCount,
  hasHints,
  showMcq,
  choicesArray,
  hasVisualButtons,
  visualChoices,
  visualPositions,
  visualSelections,
  responseMode,
  challengeType,
  hasVisualData,
  puzzleOrder,
  textInputKind,
  onSelectChoice,
  onSelectVisualPosition,
  onSelectVisualSimple,
  onUserAnswerChange,
  onSubmit,
  onRequestHint,
}: ChallengeSolverCommandBarProps) {
  const t = useTranslations("challenges.solver");
  const type = challengeType.toLowerCase();

  const isOrderPuzzle =
    responseMode === "interactive_order" && type === "puzzle" && puzzleOrder.length > 0;
  const isGridSequence =
    responseMode === "interactive_grid" && type === "sequence" && !!userAnswer && hasVisualData;
  const isGridPattern =
    responseMode === "interactive_grid" && type === "pattern" && !!userAnswer && hasVisualData;
  const isGridDeduction =
    responseMode === "interactive_grid" && type === "deduction" && hasVisualData;

  return (
    <div
      data-learner-context
      className="bg-[var(--bg-learner,var(--card))] border border-border/40 rounded-2xl p-6 max-w-5xl mx-auto"
    >
      <h3 className="text-lg font-semibold text-foreground mb-4">{t("yourAnswer")}</h3>
      <div className="space-y-4">
        {/* ── Branche 1 : QCM ── */}
        {showMcq ? (
          <McqGrid
            choicesArray={choicesArray}
            userAnswer={userAnswer}
            hasSubmitted={hasSubmitted}
            onSelectChoice={onSelectChoice}
            t={t}
          />
        ) : /* ── Branche 2 : Visual buttons ── */
        hasVisualButtons ? (
          <VisualButtons
            visualPositions={visualPositions}
            visualChoices={visualChoices}
            visualSelections={visualSelections}
            userAnswer={userAnswer}
            hasSubmitted={hasSubmitted}
            onSelectPosition={onSelectVisualPosition}
            onSelectSimple={onSelectVisualSimple}
            t={t}
          />
        ) : /* ── Branche 3 : Order puzzle ── */
        isOrderPuzzle ? (
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
              onChange={(e) => onUserAnswerChange(e.target.value)}
              placeholder={t("orderAutoGenerated")}
              className="opacity-50"
              disabled
              aria-label={t("puzzleAnswerLabel")}
            />
          </div>
        ) : /* ── Branche 4 : Grid sequence ── */
        isGridSequence ? (
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
              onChange={(e) => onUserAnswerChange(e.target.value)}
              placeholder={t("answerFromVisualization")}
              className="opacity-50"
              disabled
              aria-label={t("sequenceAnswerLabel")}
            />
          </div>
        ) : /* ── Branche 5 : Grid pattern ── */
        isGridPattern ? (
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
              onChange={(e) => onUserAnswerChange(e.target.value)}
              placeholder={t("answerFromVisualization")}
              className="opacity-50"
              disabled
              aria-label={t("patternAnswerLabel")}
            />
          </div>
        ) : /* ── Branche 6 : Grid deduction ── */
        isGridDeduction ? (
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
          /* ── Branche 7 : Texte libre (fallback) ── */
          <div className="space-y-1.5">
            <Input
              type="text"
              value={userAnswer}
              onChange={(e) => onUserAnswerChange(e.target.value)}
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
                  onSubmit();
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

        {/* ── Boutons d'action ── */}
        <div className="space-y-2 flex-1">
          <div className="flex gap-3">
            <Button
              onClick={onSubmit}
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

            {hasHints && (
              <Button
                onClick={onRequestHint}
                variant="outline"
                disabled={
                  hasSubmitted || (availableHintsCount > 0 && hintsUsedCount >= availableHintsCount)
                }
                className="border border-amber-500/30 text-amber-400 hover:bg-amber-500/10 transition-colors px-6 py-3 rounded-2xl"
                aria-label={
                  availableHintsCount > 0
                    ? t("requestHint", {
                        current: hintsUsedCount + 1,
                        total: availableHintsCount,
                      })
                    : t("requestHintGeneric")
                }
              >
                <Lightbulb className="mr-2 h-4 w-4" aria-hidden="true" />
                {availableHintsCount > 0
                  ? t("hintButton", {
                      current: hintsUsedCount + 1,
                      total: availableHintsCount,
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
  );
}
