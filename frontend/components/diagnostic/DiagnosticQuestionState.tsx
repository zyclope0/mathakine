"use client";

import { CheckCircle2, ChevronRight, XCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MathText } from "@/components/ui/MathText";
import { GrowthMindsetHint } from "@/components/ui/GrowthMindsetHint";
import {
  DiagnosticFocusBoard,
  DiagnosticProgressBar,
} from "@/components/diagnostic/DiagnosticSolverPrimitives";
import type { DiagnosticPhase, DiagnosticQuestion } from "@/hooks/useDiagnostic";

export interface DiagnosticQuestionStateProps {
  phase: DiagnosticPhase;
  currentQuestion: DiagnosticQuestion;
  selectedAnswer: string | null;
  isCorrect: boolean | null;
  correctAnswerForFeedback: string | null;
  setSelectedAnswer: (choice: string) => void;
  submitAnswer: () => void;
  nextQuestion: () => void;
}

export function DiagnosticQuestionState({
  phase,
  currentQuestion,
  selectedAnswer,
  isCorrect,
  correctAnswerForFeedback,
  setSelectedAnswer,
  submitAnswer,
  nextQuestion,
}: DiagnosticQuestionStateProps) {
  const t = useTranslations("diagnostic");
  const isFeedback = phase === "feedback";
  const progressLabel = t("progressLabel", {
    current: currentQuestion.question_number,
    max: currentQuestion.max_questions,
  });

  return (
    <DiagnosticFocusBoard>
      <DiagnosticProgressBar
        current={currentQuestion.question_number - 1}
        max={currentQuestion.max_questions}
        label={progressLabel}
      />

      <div className="flex justify-center gap-2 mb-6">
        <Badge variant="outline" className="capitalize">
          {t(
            `results.typeLabel.${currentQuestion.exercise_type.toLowerCase()}` as Parameters<
              typeof t
            >[0],
            {
              defaultValue: currentQuestion.exercise_type,
            }
          )}
        </Badge>
        <Badge variant="outline">
          {t(`results.levelLabel.${currentQuestion.difficulty}` as Parameters<typeof t>[0], {
            defaultValue: currentQuestion.difficulty,
          })}
        </Badge>
      </div>

      <div className="text-xl md:text-2xl font-medium text-foreground text-center mb-10 leading-relaxed">
        <MathText size="xl">{currentQuestion.question}</MathText>
      </div>

      <div
        className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
        role="radiogroup"
        aria-label={t("question.chooseAnswer")}
      >
        {currentQuestion.choices.map((choice, choiceIdx) => {
          const isSelected = selectedAnswer === choice;
          const isCorrectChoice =
            isFeedback && correctAnswerForFeedback != null && choice === correctAnswerForFeedback;
          const isWrongChoice = isFeedback && isSelected && !isCorrect;

          return (
            <button
              key={`choice-${choiceIdx}`}
              onClick={() => !isFeedback && setSelectedAnswer(choice)}
              disabled={isFeedback}
              role="radio"
              aria-checked={isSelected}
              className={cn(
                "w-full text-left rounded-2xl py-5 px-6 border-2 text-lg font-medium transition-all duration-200",
                !isFeedback &&
                  !isSelected &&
                  "bg-secondary/50 border-border text-foreground hover:bg-secondary hover:border-primary/50 hover:-translate-y-0.5 cursor-pointer",
                !isFeedback &&
                  isSelected &&
                  "bg-primary/20 border-primary text-primary-foreground shadow-[0_0_20px_rgba(var(--primary-rgb),0.3)] cursor-pointer",
                isCorrectChoice &&
                  "bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)] cursor-default",
                isWrongChoice && "bg-red-500/20 border-red-500 text-red-400 cursor-default",
                isFeedback &&
                  !isCorrectChoice &&
                  !isWrongChoice &&
                  "bg-muted/50 border-border text-muted-foreground cursor-default"
              )}
            >
              {choice}
            </button>
          );
        })}
      </div>

      {isFeedback && (
        <div
          className={cn(
            "rounded-xl p-5 mb-6 border-2",
            isCorrect
              ? "bg-emerald-500/10 border-emerald-500/50"
              : "bg-red-500/10 border-red-500/50"
          )}
        >
          <div className="flex items-center gap-3 mb-3">
            {isCorrect ? (
              <CheckCircle2 className="h-6 w-6 text-emerald-400 shrink-0" />
            ) : (
              <XCircle className="h-6 w-6 text-red-400 shrink-0" />
            )}
            <p
              className={cn(
                "font-semibold text-lg",
                isCorrect ? "text-emerald-400" : "text-red-400"
              )}
            >
              {isCorrect ? t("answer.correct") : t("answer.incorrect")}
            </p>
          </div>
          {!isCorrect && (
            <GrowthMindsetHint
              className="text-muted-foreground mb-3"
              supportText={t("answer.incorrectSupport")}
              correctAnswerLabel={t("answer.correctAnswerWas")}
              {...(typeof correctAnswerForFeedback === "string"
                ? { correctAnswer: correctAnswerForFeedback }
                : {})}
            />
          )}
          {currentQuestion.explanation ? (
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t("explanation.title")}
              </p>
              <MathText size="base" className="text-foreground">
                {currentQuestion.explanation}
              </MathText>
            </div>
          ) : null}
        </div>
      )}

      <div className="flex justify-end">
        {!isFeedback ? (
          <Button
            size="lg"
            disabled={!selectedAnswer}
            onClick={submitAnswer}
            className={cn(
              "px-8 py-3 rounded-xl font-semibold transition-all",
              selectedAnswer
                ? "shadow-[0_0_20px_rgba(var(--primary-rgb),0.4)] hover:shadow-[0_0_30px_rgba(var(--primary-rgb),0.6)]"
                : "bg-muted text-muted-foreground opacity-60 cursor-not-allowed border border-border"
            )}
          >
            {selectedAnswer ? t("answer.validate") : t("answer.validateDisabled")}
          </Button>
        ) : (
          <Button size="lg" onClick={nextQuestion} className="px-8 py-3 rounded-xl font-semibold">
            {t("answer.next")}
            <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>
    </DiagnosticFocusBoard>
  );
}
