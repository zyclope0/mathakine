"use client";

import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { MathText } from "@/components/ui/MathText";
import type { SessionMode } from "@/lib/exercises/exerciseSolverSession";

interface ExerciseSolverHeaderProps {
  sessionMode: SessionMode;
  typeDisplay: string;
  ageGroupDisplay: string;
  title: string;
  question: string;
  /** i18n strings pre-resolved by ExerciseSolver */
  labels: {
    reviewNavLabel: string;
    reviewBackDashboard: string;
    reviewAllExercises: string;
    reviewContextBadge: string;
    back: string;
  };
}

export function ExerciseSolverHeader({
  sessionMode,
  typeDisplay,
  ageGroupDisplay,
  title,
  question,
  labels,
}: ExerciseSolverHeaderProps) {
  return (
    <>
      {/* Navigation — contexte révision : sortie vers tableau de bord + exercices */}
      {sessionMode === "spaced-review" ? (
        <nav
          className="flex flex-wrap gap-x-6 gap-y-2 mb-6 text-sm"
          aria-label={labels.reviewNavLabel}
        >
          <Link
            href="/dashboard"
            className="text-muted-foreground hover:text-foreground inline-flex items-center gap-2 min-h-11 py-2"
          >
            <ArrowLeft className="h-4 w-4 shrink-0" aria-hidden />
            {labels.reviewBackDashboard}
          </Link>
          <Link
            href="/exercises"
            className="text-muted-foreground hover:text-foreground inline-flex items-center gap-2 min-h-11 py-2"
          >
            {labels.reviewAllExercises}
          </Link>
        </nav>
      ) : (
        <Link
          href="/exercises"
          className="text-muted-foreground hover:text-foreground transition-colors mb-6 inline-flex items-center gap-2 min-h-11 py-2"
        >
          <ArrowLeft className="h-4 w-4" />
          {labels.back}
        </Link>
      )}

      {/* Tags centrés au-dessus du titre */}
      <div className="flex justify-center flex-wrap gap-2 mb-4">
        {sessionMode === "spaced-review" ? (
          <Badge variant="secondary" className="border-border text-foreground/90">
            {labels.reviewContextBadge}
          </Badge>
        ) : null}
        {ageGroupDisplay && <Badge variant="outline">{ageGroupDisplay}</Badge>}
        <Badge variant="outline">{typeDisplay}</Badge>
      </div>

      {/* Titre centré */}
      <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-8 text-center">{title}</h1>

      {/* Énoncé — la star de la page */}
      <div className="text-xl md:text-2xl font-medium text-foreground text-center mb-12 leading-relaxed">
        <MathText size="xl">{question}</MathText>
      </div>
    </>
  );
}
