"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import type { GamificationLevelIndicator } from "@/types/api";
import {
  buildProgressionArcNodes,
  canonicalRankFromGamificationLevelPayload,
  progressionArcAriaStepNumber,
} from "@/lib/gamification/progressionArc";
import { readPublicProgressionRankRaw } from "@/lib/gamification/progressionRankLabel";
import type { ProgressionConstellationNode } from "@/components/progression/ProgressionConstellation";

export interface UseProgressionArcResult {
  /** Nœuds + libellé d’accessibilité, ou null si pas de `gamification_level`. */
  constellation: {
    nodes: ProgressionConstellationNode[];
    ariaLabel: string;
  } | null;
}

/**
 * Arc de progression « permanent » (paliers publics), distinct du streak temporel.
 *
 * Source unique : `gamification_level` sur l’utilisateur (réponse `/api/users/me`, même objet que
 * `LevelIndicator`). On n’utilise pas `useProgressStats` ni les agrégats dashboard : ceux-ci
 * sont filtrés dans le temps ; le rang / palier persistant est porté uniquement par
 * `gamification_level`.
 */
export function useProgressionArc(
  gamificationLevel: GamificationLevelIndicator | null | undefined
): UseProgressionArcResult {
  const tRanks = useTranslations("progressionRanks");
  const tHome = useTranslations("homeLearner");

  return useMemo(() => {
    if (gamificationLevel == null) {
      return { constellation: null };
    }

    const raw = readPublicProgressionRankRaw(gamificationLevel);
    const canonicalUserRank = canonicalRankFromGamificationLevelPayload(raw);

    const nodes = buildProgressionArcNodes({
      canonicalUserRank,
      labelForBucket: (bucketId) => tRanks(bucketId),
    });

    const currentRankLabel = tRanks(canonicalUserRank);
    const step = progressionArcAriaStepNumber(nodes);

    const ariaLabel = tHome("progressionArc.ariaLabel", {
      rank: currentRankLabel,
      step: String(step),
      total: String(nodes.length),
    });

    return {
      constellation: { nodes, ariaLabel },
    };
  }, [gamificationLevel, tRanks, tHome]);
}
