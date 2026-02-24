"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "next-intl";
import { Mail, Sparkles } from "lucide-react";

/**
 * Bandeau affiché pour les utilisateurs connectés dont l'email n'est pas vérifié.
 * Incite à vérifier l'email pour débloquer toutes les fonctionnalités (ou les garder).
 */
export function UnverifiedBanner() {
  const { user, isAuthenticated } = useAuth();
  const t = useTranslations("auth.login");

  if (!isAuthenticated || !user || user.is_email_verified) {
    return null;
  }

  const isLimited = user.access_scope === "exercises_only";

  return (
    <div
      role="alert"
      aria-live="polite"
      className="bg-gradient-to-r from-amber-400 via-amber-500 to-amber-400 dark:from-amber-600 dark:via-amber-700 dark:to-amber-600 text-amber-950 dark:text-amber-50 px-4 py-2.5 relative z-40 border-b border-amber-600/30"
    >
      <div className="container mx-auto flex items-center justify-center gap-2 flex-wrap text-sm">
        <Sparkles className="h-4 w-4 flex-shrink-0 text-amber-800 dark:text-amber-200" aria-hidden="true" />
        <span className="font-medium">
          {isLimited
            ? t("unverifiedBanner")
            : t("unverifiedBannerEarly")}
        </span>
        <Link
          href="/verify-email"
          className="inline-flex items-center gap-1 underline hover:no-underline font-semibold text-amber-900 dark:text-amber-100 hover:text-amber-950 dark:hover:text-amber-50 transition-colors"
        >
          <Mail className="h-4 w-4" aria-hidden="true" />
          {t("verifyEmailCta")}
        </Link>
      </div>
    </div>
  );
}
