"use client";

import Link from "next/link";
import { useIrtScores } from "@/hooks/useIrtScores";
import { useTranslations } from "next-intl";
import { Target, ChevronRight, Plus, Minus, X, Divide } from "lucide-react";

/** Ordre d'affichage et icônes par type d'opération (héritage couleur, contraste thèmes) */
const TYPE_ORDER = ["addition", "soustraction", "multiplication", "division"] as const;
const TYPE_ICON = {
  addition: Plus,
  soustraction: Minus,
  multiplication: X,
  division: Divide,
} as const;

/**
 * Widget F05 — Affiche le statut du niveau IRT établi (diagnostic F03).
 *
 * Design Premium : badges de compétences, conteneur distinct, bouton secondaire.
 * Semantic Design : variables CSS (bg-card, border, text-foreground, etc.).
 */
export function LevelEstablishedWidget() {
  const { hasCompletedDiagnostic, irtScores, isLoading } = useIrtScores();
  const t = useTranslations("dashboard.levelWidget");
  const tType = useTranslations("diagnostic.results.typeLabel");
  const tLevel = useTranslations("diagnostic.results.levelLabel");

  if (isLoading) return null;

  const skillBadges =
    hasCompletedDiagnostic && irtScores && Object.keys(irtScores).length > 0
      ? TYPE_ORDER.filter((type) => type in irtScores).map((type) => {
          const score = irtScores[type];
          const Icon = TYPE_ICON[type];
          const typeLabel = tType(
            type as "addition" | "soustraction" | "multiplication" | "division"
          );
          const levelLabel = tLevel(
            score.difficulty as "INITIE" | "PADAWAN" | "CHEVALIER" | "MAITRE" | "GRAND_MAITRE"
          );
          return { type, Icon, typeLabel, levelLabel };
        })
      : [];

  return (
    <div
      className="mt-8 bg-card border border-primary/20 shadow-sm rounded-xl p-4 md:p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
      role="region"
      aria-label={hasCompletedDiagnostic ? t("title") : t("notDone")}
    >
      <div className="flex flex-col min-w-0 flex-1">
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
            <Target className="h-5 w-5" aria-hidden="true" />
          </div>
          <h3 className="text-base font-semibold text-foreground">
            {hasCompletedDiagnostic ? t("title") : t("notDone")}
          </h3>
        </div>
        {skillBadges.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3 md:mt-2">
            {skillBadges.map(({ type, Icon, typeLabel, levelLabel }) => (
              <span
                key={type}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary border border-border hover:bg-primary/15 transition-colors"
              >
                <Icon className="w-3.5 h-3.5 mr-1.5 shrink-0 text-current opacity-80" aria-hidden />
                <span>
                  {typeLabel} ·{" "}
                  <span className="font-semibold bg-primary/5 px-1.5 py-0.5 rounded">
                    {levelLabel}
                  </span>
                </span>
              </span>
            ))}
          </div>
        )}
      </div>
      <Link
        href="/diagnostic"
        className="whitespace-nowrap inline-flex items-center justify-center gap-1 rounded-lg text-sm font-medium transition-colors border border-border bg-transparent hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 shrink-0"
      >
        {hasCompletedDiagnostic ? t("ctaRedo") : t("cta")}
        <ChevronRight className="h-4 w-4" aria-hidden="true" />
      </Link>
    </div>
  );
}
