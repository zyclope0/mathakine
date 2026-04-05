"use client";

import { X } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { useFirstVisitHint } from "@/hooks/useFirstVisitHint";
import { STORAGE_KEYS } from "@/lib/storage/keys";

interface ExerciseSolverHintProps {
  /** Whether the exercise uses open-answer mode (vs QCM). */
  isOpenAnswer: boolean;
  /** Whether a hint is available for this exercise. Controls helpNote visibility. */
  hasHint: boolean;
}

/**
 * First-visit inline contextual hint for ExerciseSolver and ExerciseModal.
 *
 * Shown once per browser (localStorage key), dismissed on explicit user action.
 * Placed inline between the question and the answer choices — no floating overlay,
 * no focus trap, no competition with the solver content.
 *
 * Uses lazy useState initializer (no useEffect) — SSR-safe via browser-storage guard.
 * Role: region (not dialog — not modal, no focus trap, no aria-modal).
 * NI plan U2 — lot neuro-inclusion.
 */
export function ExerciseSolverHint({ isOpenAnswer, hasHint }: ExerciseSolverHintProps) {
  const t = useTranslations("exercises.solver.hintOverlay");
  const { visible, dismiss } = useFirstVisitHint(STORAGE_KEYS.exerciseSolverHintSeen);

  if (!visible) return null;

  return (
    <div
      role="region"
      aria-label={t("title")}
      className="rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm mb-4"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1.5 min-w-0">
          <p className="font-semibold text-foreground text-sm">{t("title")}</p>
          <ol className="space-y-1 text-muted-foreground list-none">
            <li className="flex items-center gap-2">
              <span className="text-primary font-bold text-xs w-4 shrink-0">1.</span>
              {isOpenAnswer ? t("stepWrite") : t("stepChoose")}
            </li>
            <li className="flex items-center gap-2">
              <span className="text-primary font-bold text-xs w-4 shrink-0">2.</span>
              {t("stepValidate")}
            </li>
            {hasHint && (
              <li className="flex items-center gap-2 pt-0.5 text-xs text-muted-foreground/80">
                <span className="w-4 shrink-0">💡</span>
                {t("helpNote")}
              </li>
            )}
          </ol>
        </div>

        {/* X discret : sortie secondaire, cible 44×44px pour accessibilité touch */}
        <button
          type="button"
          onClick={dismiss}
          className="shrink-0 -mt-0.5 -mr-1 flex h-11 w-11 items-center justify-center rounded-sm text-muted-foreground hover:text-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={t("dismissAriaLabel")}
        >
          <X className="h-4 w-4" aria-hidden />
        </button>
      </div>

      {/* CTA principal : compact, ne prend pas toute la largeur */}
      <div className="mt-3">
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="h-10 min-h-[44px] text-sm font-medium border-primary/30 hover:bg-primary/10 hover:border-primary/50"
          onClick={dismiss}
        >
          {t("dismiss")}
        </Button>
      </div>
    </div>
  );
}
