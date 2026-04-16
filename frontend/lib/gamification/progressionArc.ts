import type {
  ProgressionConstellationNode,
  ProgressionConstellationNodeState,
} from "@/components/progression/ProgressionConstellation";
import { canonicalProgressionRankBucket } from "@/lib/gamification/progressionRankLabel";

/**
 * Échelle publique des rangs (F42-C3C), du plus accessible au plus avancé.
 * Alignée sur `PROGRESSION_RANK_ICONS` / contrat API — ne pas réordonner sans validation produit + backend.
 */
export const PROGRESSION_RANK_LADDER_ORDER = [
  "cadet",
  "scout",
  "explorer",
  "navigator",
  "cartographer",
  "commander",
  "stellar_archivist",
  "cosmic_legend",
] as const;

export type ProgressionRankBucketId = (typeof PROGRESSION_RANK_LADDER_ORDER)[number];

/**
 * Nœuds affichés sur la constellation = ladder public complet (8 rangs).
 * Le défilement horizontal est géré dans `ProgressionConstellation` (pas de réduction du GAP SVG).
 */
export const PROGRESSION_ARC_NODE_COUNT = PROGRESSION_RANK_LADDER_ORDER.length;

/**
 * Paliers représentés sur l’arc « permanent » : sous-suite du ladder (tous les rangs publics affichés).
 */
export const PROGRESSION_ARC_VISIBLE_BUCKETS = PROGRESSION_RANK_LADDER_ORDER.slice(
  0,
  PROGRESSION_ARC_NODE_COUNT
) as readonly ProgressionRankBucketId[];

function indexInLadder(canonicalRank: string): number {
  const idx = PROGRESSION_RANK_LADDER_ORDER.indexOf(canonicalRank as ProgressionRankBucketId);
  return idx === -1 ? 0 : idx;
}

function nodeStateForMilestone(
  userRankIndex: number,
  milestoneRankIndex: number
): ProgressionConstellationNodeState {
  if (userRankIndex > milestoneRankIndex) {
    return "completed";
  }
  if (userRankIndex === milestoneRankIndex) {
    return "current";
  }
  return "upcoming";
}

export interface BuildProgressionArcNodesParams {
  /** Rang canonique courant (après `canonicalProgressionRankBucket`). */
  canonicalUserRank: string;
  /** `progressionRanks.<bucket>` pour chaque nœud visible. */
  labelForBucket: (bucketId: string) => string;
}

/**
 * Mappe le rang utilisateur vers les nœuds de `ProgressionConstellation`.
 * Aucune donnée réseau ici — logique pure pour tests et hook.
 */
export function buildProgressionArcNodes(
  params: BuildProgressionArcNodesParams
): ProgressionConstellationNode[] {
  const { canonicalUserRank, labelForBucket } = params;
  const userRankIndex = indexInLadder(canonicalUserRank);

  return PROGRESSION_ARC_VISIBLE_BUCKETS.map((bucketId) => {
    const milestoneIndex = indexInLadder(bucketId);
    return {
      id: `progression-arc-${bucketId}`,
      state: nodeStateForMilestone(userRankIndex, milestoneIndex),
      label: labelForBucket(bucketId),
    };
  });
}

/**
 * Rang canonique à partir du champ `gamification_level` (même source que le widget niveau).
 */
export function canonicalRankFromGamificationLevelPayload(rawRank: string): string {
  const trimmed = rawRank.trim();
  if (trimmed === "") {
    return "cadet";
  }
  return canonicalProgressionRankBucket(trimmed);
}

/**
 * Indice 1-based de l’étape courante pour les textes accessibles (nœud `current`, ou fin d’arc si tout complété).
 */
export function progressionArcAriaStepNumber(
  nodes: readonly ProgressionConstellationNode[]
): number {
  const currentIdx = nodes.findIndex((n) => n.state === "current");
  if (currentIdx >= 0) {
    return currentIdx + 1;
  }
  if (nodes.length > 0 && nodes.every((n) => n.state === "completed")) {
    return nodes.length;
  }
  return 1;
}
