"use client";

import { Sparkles } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { DiagnosticFocusBoard } from "@/components/diagnostic/DiagnosticSolverPrimitives";

interface DiagnosticIdleStateProps {
  onStart: () => void;
}

export function DiagnosticIdleState({ onStart }: DiagnosticIdleStateProps) {
  const t = useTranslations("diagnostic");

  return (
    <DiagnosticFocusBoard className="text-center">
      <div className="flex justify-center mb-6">
        <Sparkles className="h-16 w-16 text-primary" />
      </div>
      <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">{t("title")}</h1>
      <p className="text-muted-foreground text-lg mb-10 max-w-lg mx-auto">{t("subtitle")}</p>
      <Button
        size="lg"
        className="px-10 py-4 text-lg font-semibold rounded-2xl shadow-[0_0_20px_rgba(var(--primary-rgb),0.4)] hover:shadow-[0_0_30px_rgba(var(--primary-rgb),0.6)] transition-all"
        onClick={onStart}
      >
        {t("startButton")}
      </Button>
    </DiagnosticFocusBoard>
  );
}
