"use client";

/**
 * Bouton "Enregistrer" réutilisable pour les sections de la page Settings.
 * Élimine la duplication du pattern Loader2 + Save icon présent 3× dans settings/page.tsx.
 */

import { Loader2, Save } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";

interface SaveButtonProps {
  onClick: () => void;
  isLoading: boolean;
  className?: string;
}

export function SaveButton({ onClick, isLoading, className }: SaveButtonProps) {
  const t = useTranslations("settings.actions");
  return (
    <Button
      type="button"
      onClick={onClick}
      disabled={isLoading}
      aria-busy={isLoading}
      size="sm"
      className={className}
    >
      {isLoading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          {t("saving")}
        </>
      ) : (
        <>
          <Save className="mr-2 h-4 w-4" aria-hidden="true" />
          {t("save")}
        </>
      )}
    </Button>
  );
}
