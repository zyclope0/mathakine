"use client";

import { cn } from "@/lib/utils/cn";
import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";

interface LoadingStateProps {
  message?: string;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = {
  sm: "h-4 w-4",
  md: "h-8 w-8",
  lg: "h-12 w-12",
};

/**
 * LoadingState - État de chargement standardisé
 *
 * Garantit :
 * - Spinner centré
 * - Message optionnel
 * - Espacements cohérents
 */
export function LoadingState({ message, className, size = "md" }: LoadingStateProps) {
  const t = useTranslations("common");
  return (
    <div
      className={cn("flex flex-col items-center justify-center py-12", "min-h-[12rem]", className)}
    >
      <Loader2
        className={cn("animate-spin text-primary mb-4", sizeClasses[size])}
        aria-hidden="true"
      />
      <p className="text-sm text-muted-foreground">
        {message || t("loading", { default: "Chargement..." })}
      </p>
      <span className="sr-only">{t("loading", { default: "Chargement..." })}</span>
    </div>
  );
}
