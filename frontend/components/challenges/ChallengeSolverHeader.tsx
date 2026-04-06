"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useTranslations } from "next-intl";

interface ChallengeSolverHeaderProps {
  challengeId: number;
  title: string | undefined;
  ageGroupDisplay: string;
  ageGroupColor: string;
  typeDisplay: string;
  difficultyRating?: number | null | undefined;
}

/**
 * En-tête du défi : lien retour, numéro, titre, badges.
 * Composant purement visuel — pas de fetch, pas de thème métier.
 */
export function ChallengeSolverHeader({
  challengeId,
  title,
  ageGroupDisplay,
  ageGroupColor,
  typeDisplay,
  difficultyRating,
}: ChallengeSolverHeaderProps) {
  const t = useTranslations("challenges.solver");

  return (
    <>
      {/* Bouton Retour */}
      <Link
        href="/challenges"
        className="text-muted-foreground hover:text-foreground transition-colors mb-6 inline-flex items-center gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        {t("back")}
      </Link>

      {/* Numéro de défi discret */}
      <p className="text-sm text-muted-foreground font-mono">
        {t("challengeNumber", { id: challengeId })}
      </p>

      {/* Titre */}
      <h1 className="text-3xl md:text-4xl font-bold text-foreground mt-2 mb-6">
        {title || t("noTitle")}
      </h1>

      {/* Badges */}
      <div className="flex flex-wrap gap-2 mb-6">
        <Badge variant="outline" className={ageGroupColor}>
          {ageGroupDisplay}
        </Badge>
        <Badge variant="outline">{typeDisplay}</Badge>
        {difficultyRating && (
          <Badge
            variant="outline"
            className="bg-purple-500/20 text-purple-400 border-purple-500/30"
          >
            ⭐ {difficultyRating.toFixed(1)}/5
          </Badge>
        )}
      </div>
    </>
  );
}
