/**
 * F43-A4 — titre narratif badge : clé publique `thematic_title` + alias legacy `star_wars_title`.
 * Même valeur côté API ; lecture défensive côté client.
 */
export type BadgeThematicTitleSource = {
  thematic_title?: string | null;
  /** @deprecated F43-A4 — compat ; préférer `thematic_title`. */
  star_wars_title?: string | null;
};

/** Titre d’affichage brut (non vide) ou chaîne vide si absent. */
export function readBadgeThematicTitleRaw(source: BadgeThematicTitleSource): string {
  const v = source.thematic_title ?? source.star_wars_title;
  if (v == null) {
    return "";
  }
  return String(v).trim();
}
