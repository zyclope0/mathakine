"use client";

import { useTranslations } from "next-intl";
import { Puzzle } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { ListRouteLoadingLayout } from "@/components/shared/ContentListSkeleton";

/** Coquille chargement / Suspense pour la page exercices (header réel + skeleton liste). */
export function ExercisesListLoadingShell() {
  const t = useTranslations("exercises");
  return (
    <>
      <PageHeader title={t("title")} description={t("pageDescription")} />
      <ListRouteLoadingLayout loadingLabel={t("list.loading")} />
    </>
  );
}

/** Idem pour la page défis (icône Puzzle + skeleton filtre ordre). */
export function ChallengesListLoadingShell() {
  const t = useTranslations("challenges");
  return (
    <>
      <PageHeader title={t("title")} description={t("pageDescription")} icon={Puzzle} />
      <ListRouteLoadingLayout loadingLabel={t("list.loading")} showOrderSelectSkeleton />
    </>
  );
}
