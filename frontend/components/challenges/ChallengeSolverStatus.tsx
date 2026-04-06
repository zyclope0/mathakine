"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Loader2, XCircle, ArrowLeft, AlertCircle } from "lucide-react";
import { LearnerCard } from "@/components/learner";
import { useTranslations } from "next-intl";
import type { ApiClientError } from "@/lib/api/client";

interface ChallengeSolverStatusProps {
  challengeId: number;
  isLoading?: boolean;
  error?: ApiClientError | null;
  /** Cas not-found : challenge absent, pas d'erreur, pas de loading */
  notFound?: boolean;
}

/**
 * Renders the status screens for ChallengeSolver:
 *   - loading skeleton
 *   - error (generic or 404)
 *   - not-found (no error, no loading, no challenge)
 *
 * Returns null when none of these conditions apply (happy path).
 */
export function ChallengeSolverStatus({
  challengeId,
  isLoading,
  error,
  notFound,
}: ChallengeSolverStatusProps) {
  const t = useTranslations("challenges.solver");

  if (isLoading) {
    return (
      <LearnerCard variant="challenge">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
            <p className="text-muted-foreground">{t("loading")}</p>
          </div>
        </div>
      </LearnerCard>
    );
  }

  if (error) {
    return (
      <LearnerCard variant="challenge">
        <div className="text-center space-y-4" role="alert" aria-live="assertive">
          <XCircle className="h-12 w-12 text-destructive mx-auto" />
          <div>
            <h3 className="text-lg font-semibold text-destructive">{t("error.title")}</h3>
            <p className="text-muted-foreground mt-2">
              {error.status === 404 ? t("error.notFound") : error.message || t("error.generic")}
            </p>
          </div>
          <Button asChild variant="outline">
            <Link href="/challenges">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("back")}
            </Link>
          </Button>
        </div>
      </LearnerCard>
    );
  }

  if (notFound) {
    return (
      <LearnerCard variant="challenge">
        <div className="text-center space-y-4" role="alert" aria-live="assertive">
          <AlertCircle className="h-12 w-12 text-warning mx-auto" />
          <div>
            <h3 className="text-lg font-semibold text-warning">{t("notFound.title")}</h3>
            <p className="text-muted-foreground mt-2">
              {t("notFound.message", { id: challengeId })}
            </p>
          </div>
          <Button asChild variant="outline">
            <Link href="/challenges">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t("back")}
            </Link>
          </Button>
        </div>
      </LearnerCard>
    );
  }

  return null;
}
