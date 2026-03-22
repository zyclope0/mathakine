/**
 * Modalité de réponse défis (IA9) — alignée sur `challenge_contract_policy` backend.
 * Le détail GET /api/challenges/{id} expose `response_mode` ; ce helper valide et retombe en open_text si absent.
 */

import type { Challenge, ChallengeResponseMode } from "@/types/api";

const VALID_MODES = new Set<ChallengeResponseMode>([
  "open_text",
  "single_choice",
  "interactive_visual",
  "interactive_order",
  "interactive_grid",
]);

export function isChallengeResponseMode(v: string | null | undefined): v is ChallengeResponseMode {
  return v != null && VALID_MODES.has(v as ChallengeResponseMode);
}

/**
 * Source de vérité UI : préférer le champ API `response_mode` (fail-closed si inconnu).
 */
export function resolveChallengeResponseMode(challenge: Challenge): ChallengeResponseMode {
  const raw = challenge.response_mode;
  if (isChallengeResponseMode(raw)) {
    return raw;
  }
  return "open_text";
}

export type { ChallengeResponseMode };
