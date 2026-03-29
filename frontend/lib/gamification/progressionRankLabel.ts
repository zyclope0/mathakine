import { PROGRESSION_RANK_ICONS } from "@/lib/constants/leaderboard";

/** Champs API pour le bucket de rang public (F43-A3). */
export type PublicRankBucketSource = {
  /** Clé publique préférée (même valeur canonique que `jedi_rank`). */
  progression_rank?: string | null;
  /** @deprecated Legacy — compat clients ; préférer `progression_rank`. */
  jedi_rank?: string | null;
};

/** Lit le bucket brut : `progression_rank` en priorité, sinon `jedi_rank`. */
export function readPublicProgressionRankRaw(source: PublicRankBucketSource): string {
  return String(source.progression_rank ?? source.jedi_rank ?? "").trim();
}

/**
 * Anciens identifiants publics (pré C3C), encore possibles via API / données historiques.
 * Clés = slugs tels qu’exposés ou stockés — ne pas renommer sans migration.
 */
const LEGACY_TO_CANONICAL: Record<string, string> = {
  youngling: "cadet",
  padawan: "explorer",
  knight: "navigator",
  master: "commander",
  grand_master: "cosmic_legend",
};

export function canonicalProgressionRankBucket(raw: string): string {
  return LEGACY_TO_CANONICAL[raw] ?? raw;
}

/** True si le bucket (ou son legacy) a un libellé / style dédié. */
export function isKnownProgressionRankBucket(bucket: string): boolean {
  const c = canonicalProgressionRankBucket(bucket);
  return Object.prototype.hasOwnProperty.call(PROGRESSION_RANK_ICONS, c);
}
