"use client";

import Link from "next/link";
import { CheckCircle2, ChevronRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  DiagnosticFocusBoard,
  DiagnosticScoreCard,
} from "@/components/diagnostic/DiagnosticSolverPrimitives";
import type { DiagnosticResult, DiagnosticScores } from "@/hooks/useDiagnostic";

interface DiagnosticResultsStateProps {
  result: DiagnosticResult;
  onComplete?: () => void;
}

export function DiagnosticResultsState({ result, onComplete }: DiagnosticResultsStateProps) {
  const t = useTranslations("diagnostic");
  const scores: DiagnosticScores = result.scores ?? {};
  const scoreEntries = Object.entries(scores);

  return (
    <DiagnosticFocusBoard>
      <div className="text-center mb-10">
        <CheckCircle2 className="h-16 w-16 text-emerald-400 mx-auto mb-4" />
        <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3">
          {t("results.title")}
        </h1>
        <p className="text-muted-foreground text-lg max-w-lg mx-auto">{t("results.subtitle")}</p>
        <div className="flex justify-center gap-4 mt-4 text-sm text-muted-foreground">
          <span>{t("results.questionsAnswered", { count: result.questions_asked })}</span>
          {result.duration_seconds ? (
            <span>{t("results.duration", { seconds: result.duration_seconds })}</span>
          ) : null}
        </div>
      </div>

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
              <DiagnosticScoreCard
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
    </DiagnosticFocusBoard>
  );
}
