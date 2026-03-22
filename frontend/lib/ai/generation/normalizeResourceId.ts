/**
 * Identifiant de ressource créée (exercice / défi) après persistance.
 * Le backend envoie en général un nombre ; certains chemins peuvent sérialiser autrement.
 */
export function normalizeCreatedResourceId(raw: unknown): number | undefined {
  if (typeof raw === "number" && Number.isFinite(raw) && raw > 0) {
    return Math.trunc(raw);
  }
  if (typeof raw === "string") {
    const t = raw.trim();
    if (/^\d+$/.test(t)) {
      const n = parseInt(t, 10);
      return n > 0 ? n : undefined;
    }
  }
  return undefined;
}
