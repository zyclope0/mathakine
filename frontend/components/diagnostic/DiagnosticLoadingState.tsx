"use client";

import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { DiagnosticFocusBoard } from "@/components/diagnostic/DiagnosticSolverPrimitives";

export function DiagnosticLoadingState() {
  const t = useTranslations("diagnostic");

  return (
    <DiagnosticFocusBoard>
      <div className="flex items-center justify-center min-h-[300px]">
        <div className="text-center space-y-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground">{t("title")}</p>
        </div>
      </div>
    </DiagnosticFocusBoard>
  );
}
