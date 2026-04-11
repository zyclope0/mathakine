"use client";

import Link from "next/link";
import { ArrowLeft, XCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { DiagnosticFocusBoard } from "@/components/diagnostic/DiagnosticSolverPrimitives";

interface DiagnosticErrorStateProps {
  error: string | null;
  onRetry: () => void;
}

export function DiagnosticErrorState({ error, onRetry }: DiagnosticErrorStateProps) {
  const t = useTranslations("diagnostic");

  return (
    <DiagnosticFocusBoard className="text-center">
      <XCircle className="h-14 w-14 text-destructive mx-auto mb-4" />
      <h2 className="text-xl font-bold text-destructive mb-2">{t("error.title")}</h2>
      {error && <p className="text-muted-foreground mb-6 text-sm">{error}</p>}
      <div className="flex gap-3 justify-center">
        <Button variant="outline" onClick={onRetry}>
          {t("error.retry")}
        </Button>
        <Button variant="ghost" asChild>
          <Link href="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t("error.backHome")}
          </Link>
        </Button>
      </div>
    </DiagnosticFocusBoard>
  );
}
