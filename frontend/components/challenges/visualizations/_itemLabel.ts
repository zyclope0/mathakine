/**
 * itemLabel — contrat d'affichage unifié pour les éléments de `visual_data`.
 *
 * Les pièces / items / indices / entités produits par le LLM peuvent arriver
 * sous plusieurs formes (string plate, objet riche avec `label` / `value` /
 * `name` / `id`, ou même chaîne ressemblant à une repr Python `{'name': ...}`
 * quand une ancienne persistence a été faite).
 *
 * Règle UI : aucun libellé visible ne doit jamais leaker :
 *   - la repr Python `{'id': 'A', 'pattern': [...]}`
 *   - la repr JSON brute `{"id":"A","pattern":[...]}`
 *   - la chaîne `[object Object]`
 *
 * Cette helper est la **seule** fonction autorisée pour transformer un élément
 * inconnu en libellé lisible. `JSON.stringify` reste uniquement acceptable pour
 * un bloc `<pre>` de debug explicite (hors contrat affichable).
 */

export const DEFAULT_ITEM_LABEL_FIELDS = [
  "label",
  "value",
  "name",
  "text",
  "description",
  "id",
  "piece_id",
  "tag",
] as const;

const PY_DICT_LABEL_FIELD_RE =
  /['"](?<field>name|label|value|text|description|id|piece_id|tag)['"]\s*:\s*['"](?<val>[^'"]*)['"]/gi;

/**
 * Extrait un libellé depuis une chaîne type `"{'name': 'cercle rouge'}"` ou
 * `'{"id":"A"}'` — fail-open sur les vraies chaînes de forme (`"cercle rouge"`).
 */
export function parseDictLikeLabel(
  text: string,
  fields: readonly string[] = DEFAULT_ITEM_LABEL_FIELDS
): string | null {
  const s = text.trim();
  if (!s.startsWith("{") || !s.endsWith("}")) return null;
  const collected: Record<string, string> = {};
  for (const match of s.matchAll(PY_DICT_LABEL_FIELD_RE)) {
    const key = match.groups?.field?.toLowerCase();
    const val = match.groups?.val?.trim();
    if (key && val && !(key in collected)) {
      collected[key] = val;
    }
  }
  if (Object.keys(collected).length === 0) return null;
  for (const k of fields) {
    const v = collected[k.toLowerCase()];
    if (v) return v;
  }
  return null;
}

/**
 * Libellé affichable pour un élément arbitraire de `visual_data`.
 *
 * @param raw       L'élément (string | number | boolean | object | null/undefined).
 * @param opts.fields  Liste ordonnée des clés à tenter (override du défaut).
 * @param opts.fallback Valeur si aucune clé reconnue — jamais `JSON.stringify`.
 */
export function itemLabel(
  raw: unknown,
  opts: { fields?: readonly string[]; fallback?: string } = {}
): string {
  const fields = opts.fields ?? DEFAULT_ITEM_LABEL_FIELDS;
  const fallback = opts.fallback ?? "";

  if (raw == null) return fallback;
  if (typeof raw === "boolean") return fallback;
  if (typeof raw === "number") {
    return Number.isFinite(raw) ? String(raw) : fallback;
  }
  if (typeof raw === "string") {
    const parsed = parseDictLikeLabel(raw, fields);
    if (parsed !== null) return parsed;
    return raw.trim();
  }
  if (typeof raw === "object" && !Array.isArray(raw)) {
    const o = raw as Record<string, unknown>;
    for (const k of fields) {
      const v = o[k];
      if (typeof v === "string" && v.trim()) return v.trim();
      if (typeof v === "number" && Number.isFinite(v)) return String(v);
    }
    return fallback;
  }
  // Tableaux / autres : pas de libellé stable → fallback.
  return fallback;
}

/**
 * Variante utile quand on veut aussi récupérer les métadonnées connues (size,
 * orientation, color) en plus du libellé principal — ex. symétrie visuelle.
 */
export function itemLabelWithExtras(
  raw: unknown,
  opts: {
    fields?: readonly string[];
    extraFields?: readonly string[];
    fallback?: string;
  } = {}
): { label: string; extras: Record<string, string> } {
  const label = itemLabel(raw, opts);
  const extras: Record<string, string> = {};
  const extraKeys = opts.extraFields ?? ["size", "orientation", "color"];
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const o = raw as Record<string, unknown>;
    for (const k of extraKeys) {
      const v = o[k];
      if (typeof v === "string" && v.trim()) extras[k] = v.trim();
    }
  }
  return { label, extras };
}
