"use client";

/**
 * Composant d'interface du diagnostic adaptatif initial — F03.
 *
 * Responsabilité : affichage pur.
 * Toute la logique métier (IRT, appels API, état de session) est dans useDiagnostic.
 *
 * Phases gérées :
 *   idle       → écran de démarrage
 *   loading    → spinner
 *   question   → question + choix de réponse
 *   feedback   → résultat de la réponse + explication
 *   results    → bilan final avec scores par type
 *   error      → message d'erreur + retry
 *
 * Style : FocusBoard glassmorphism (identique ExerciseSolver/ChallengeSolver).
 * MathText : rendu Markdown+LaTeX pour les questions/explications.
 */

import { useTranslations } from "next-intl";
import Link from "next/link";
import { ArrowLeft, CheckCircle2, XCircle, Loader2, Sparkles, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MathText } from "@/components/ui/MathText";
import { GrowthMindsetHint } from "@/components/ui/GrowthMindsetHint";
import { useDiagnostic, type DiagnosticScores, type DiagnosticTypeScore } from "@/hooks/useDiagnostic";

// -------------------------------------------------------------------------- //
// FocusBoard — défini au niveau MODULE pour éviter le remontage React         //
// -------------------------------------------------------------------------- //

function FocusBoard({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "bg-card/90 backdrop-blur-xl border border-border shadow-[0_0_40px_rgba(0,0,0,0.15)] rounded-3xl p-8 md:p-12 w-full max-w-4xl mx-auto mt-8 md:mt-12",
        className
      )}
    >
      {children}
    </div>
  );
}

// -------------------------------------------------------------------------- //
// Barre de progression                                                        //
// -------------------------------------------------------------------------- //

function ProgressBar({ current, max, label }: { current: number; max: number; label: string }) {
  const pct = Math.min(100, Math.round((current / max) * 100));
  return (
    <div className="mb-8">
      <div className="flex justify-between text-sm text-muted-foreground mb-2">
        <span>{label}</span>
        <span>{pct}%</span>
      </div>
      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
          role="progressbar"
          title={label}
          aria-label={label}
          aria-valuenow={current}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
}

// -------------------------------------------------------------------------- //
// Carte score par type (résultats)                                            //
// -------------------------------------------------------------------------- //

const LEVEL_COLORS: Record<string, string> = {
  INITIE: "text-sky-400 border-sky-500/30 bg-sky-500/10",
  PADAWAN: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
  CHEVALIER: "text-amber-400 border-amber-500/30 bg-amber-500/10",
  MAITRE: "text-orange-400 border-orange-500/30 bg-orange-500/10",
  GRAND_MAITRE: "text-rose-400 border-rose-500/30 bg-rose-500/10",
};

function ScoreCard({
  typeKey,
  score,
  typeLabel,
  levelLabel,
  scoreDetail,
}: {
  typeKey: string;
  score: DiagnosticTypeScore;
  typeLabel: string;
  levelLabel: string;
  scoreDetail: string;
}) {
  const colorClass =
    LEVEL_COLORS[score.difficulty] ?? "text-muted-foreground border-border bg-muted/50";
  return (
    <div
      className={cn("flex items-center justify-between rounded-xl border p-4", colorClass)}
      aria-label={`${typeKey}: ${levelLabel}`}
    >
      <div>
        <p className="font-semibold text-foreground capitalize">{typeLabel}</p>
        <p className="text-sm mt-0.5 opacity-80">{scoreDetail}</p>
      </div>
      <Badge variant="outline" className={cn("text-sm font-medium border", colorClass)}>
        {levelLabel}
      </Badge>
    </div>
  );
}

// -------------------------------------------------------------------------- //
// Composant principal                                                          //
// -------------------------------------------------------------------------- //

interface DiagnosticSolverProps {
  triggeredFrom?: "onboarding" | "settings";
  /** Appelé après finalisation réussie pour permettre la redirection parente */
  onComplete?: () => void;
}

export function DiagnosticSolver({
  triggeredFrom = "onboarding",
  onComplete,
}: DiagnosticSolverProps) {
  const t = useTranslations("diagnostic");
  const {
    phase,
    currentQuestion,
    selectedAnswer,
    isCorrect,
    correctAnswerForFeedback,
    result,
    error,
    startDiagnostic,
    setSelectedAnswer,
    submitAnswer,
    nextQuestion,
  } = useDiagnostic(triggeredFrom);

  // ---- idle --------------------------------------------------------------- //

  if (phase === "idle") {
    return (
      <FocusBoard className="text-center">
        <div className="flex justify-center mb-6">
          <Sparkles className="h-16 w-16 text-primary" />
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">{t("title")}</h1>
        <p className="text-muted-foreground text-lg mb-10 max-w-lg mx-auto">{t("subtitle")}</p>
        <Button
          size="lg"
          className="px-10 py-4 text-lg font-semibold rounded-2xl shadow-[0_0_20px_rgba(var(--primary-rgb),0.4)] hover:shadow-[0_0_30px_rgba(var(--primary-rgb),0.6)] transition-all"
          onClick={startDiagnostic}
        >
          {t("startButton")}
        </Button>
      </FocusBoard>
    );
  }

  // ---- loading ------------------------------------------------------------ //

  if (phase === "loading") {
    return (
      <FocusBoard>
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="text-center space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
            <p className="text-muted-foreground">{t("title")}</p>
          </div>
        </div>
      </FocusBoard>
    );
  }

  // ---- error -------------------------------------------------------------- //

  if (phase === "error") {
    return (
      <FocusBoard className="text-center">
        <XCircle className="h-14 w-14 text-destructive mx-auto mb-4" />
        <h2 className="text-xl font-bold text-destructive mb-2">{t("error.title")}</h2>
        {error && <p className="text-muted-foreground mb-6 text-sm">{error}</p>}
        <div className="flex gap-3 justify-center">
          <Button variant="outline" onClick={startDiagnostic}>
            {t("error.retry")}
          </Button>
          <Button variant="ghost" asChild>
            <Link href="/">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("error.backHome")}
            </Link>
          </Button>
        </div>
      </FocusBoard>
    );
  }

  // ---- results ------------------------------------------------------------ //

  if (phase === "results" && result) {
    const scores: DiagnosticScores = result.scores ?? {};
    const scoreEntries = Object.entries(scores);

    return (
      <FocusBoard>
        {/* Titre */}
        <div className="text-center mb-10">
          <CheckCircle2 className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3">
            {t("results.title")}
          </h1>
          <p className="text-muted-foreground text-lg max-w-lg mx-auto">{t("results.subtitle")}</p>
          <div className="flex justify-center gap-4 mt-4 text-sm text-muted-foreground">
            <span>{t("results.questionsAnswered", { count: result.questions_asked })}</span>
            {result.duration_seconds && (
              <span>{t("results.duration", { seconds: result.duration_seconds })}</span>
            )}
          </div>
        </div>

        {/* Scores par type */}
        {scoreEntries.length > 0 ? (
          <div className="space-y-3 mb-10">
            {scoreEntries.map(([typeKey, score]) => {
              const typeLabel = t(`results.typeLabel.${typeKey}` as Parameters<typeof t>[0], {
                defaultValue: typeKey,
              });
              const levelLabel = t(
                `results.levelLabel.${score.difficulty}` as Parameters<typeof t>[0],
                { defaultValue: score.difficulty }
              );
              const scoreDetail = t("results.scoreDetail", {
                correct: score.correct,
                total: score.total,
              });
              return (
                <ScoreCard
                  key={typeKey}
                  typeKey={typeKey}
                  score={score}
                  typeLabel={typeLabel}
                  levelLabel={levelLabel}
                  scoreDetail={scoreDetail}
                />
              );
            })}
          </div>
        ) : (
          <p className="text-muted-foreground text-center mb-10">—</p>
        )}

        {/* CTA */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button
            size="lg"
            className="rounded-xl font-semibold"
            onClick={onComplete}
            asChild={!onComplete}
          >
            {onComplete ? (
              <span>
                {t("results.ctaDashboard")}
                <ChevronRight className="ml-2 h-4 w-4" />
              </span>
            ) : (
              <Link href="/dashboard">
                {t("results.ctaDashboard")}
                <ChevronRight className="ml-2 h-4 w-4" />
              </Link>
            )}
          </Button>
          <Button variant="outline" size="lg" className="rounded-xl" asChild>
            <Link href="/exercises">{t("results.ctaExercises")}</Link>
          </Button>
        </div>
      </FocusBoard>
    );
  }

  // ---- question / feedback ------------------------------------------------ //

  if (!currentQuestion) return null;

  const isFeedback = phase === "feedback";
  const progressLabel = t("progressLabel", {
    current: currentQuestion.question_number,
    max: currentQuestion.max_questions,
  });

  return (
    <FocusBoard>
      {/* Barre de progression */}
      <ProgressBar
        current={currentQuestion.question_number - 1}
        max={currentQuestion.max_questions}
        label={progressLabel}
      />

      {/* Tags */}
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

      {/* Question */}
      <div className="text-xl md:text-2xl font-medium text-foreground text-center mb-10 leading-relaxed">
        <MathText size="xl">{currentQuestion.question}</MathText>
      </div>

      {/* Choix de réponses */}
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
                // État neutre
                !isFeedback &&
                  !isSelected &&
                  "bg-secondary/50 border-border text-foreground hover:bg-secondary hover:border-primary/50 hover:-translate-y-0.5 cursor-pointer",
                // Sélectionné (avant soumission)
                !isFeedback &&
                  isSelected &&
                  "bg-primary/20 border-primary text-primary-foreground shadow-[0_0_20px_rgba(var(--primary-rgb),0.3)] cursor-pointer",
                // Correct (après soumission)
                isCorrectChoice &&
                  "bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.3)] cursor-default",
                // Incorrect (après soumission)
                isWrongChoice && "bg-red-500/20 border-red-500 text-red-400 cursor-default",
                // Autres choix désactivés (après soumission)
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

      {/* Feedback après soumission */}
      {isFeedback && (
        <div
          className={cn(
            "rounded-xl p-5 mb-6 border-l-4",
            isCorrect ? "bg-emerald-500/10 border-emerald-500" : "bg-red-500/10 border-red-500"
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
          {currentQuestion.explanation && (
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {t("explanation.title")}
              </p>
              <MathText size="base" className="text-foreground">
                {currentQuestion.explanation}
              </MathText>
            </div>
          )}
        </div>
      )}

      {/* Boutons d'action */}
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
    </FocusBoard>
  );
}
