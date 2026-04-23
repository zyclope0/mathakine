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
 * Champs considérés comme **identifiants** d'un élément, donc exclus du
 * descriptif (déjà couverts par `itemLabel`). Synchronisé avec la liste
 * officielle + alias courants.
 */
const IDENTIFIER_FIELDS: readonly string[] = [...DEFAULT_ITEM_LABEL_FIELDS];

/** Préférences de séparateur pour certaines paires domain-level. */
const SPECIAL_JOINERS: Record<string, { left: string; right: string; sep: string }> = {
  left_right: { left: "left", right: "right", sep: " ↔ " },
  from_to: { left: "from", right: "to", sep: " → " },
  start_end: { left: "start", right: "end", sep: " → " },
};

function formatDescriptiveValue(value: unknown): string | null {
  if (value == null) return null;
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed ? trimmed : null;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }
  if (typeof value === "boolean") {
    return null;
  }
  if (Array.isArray(value)) {
    const plain = value
      .map((x) =>
        typeof x === "string"
          ? x.trim()
          : typeof x === "number" && Number.isFinite(x)
            ? String(x)
            : null
      )
      .filter((x): x is string => Boolean(x));
    return plain.length > 0 ? plain.join(", ") : null;
  }
  // Objets imbriqués : on refuse plutôt que de risquer un leak.
  return null;
}

/**
 * Construit un descriptif court depuis les champs **non-identifiants** d'un
 * élément. Utilisé pour enrichir un libellé d'affichage quand le champ-clé
 * (ex. ``id``) ne contient pas l'information pédagogique (``left``, ``right``,
 * ``pattern``, ``content`` …).
 *
 * Règles :
 * - Saute les champs identifiants (``label``, ``value``, ``name``, …).
 * - Accepte string / number / array plate de strings/numbers.
 * - Refuse les objets imbriqués (pas de JSON.stringify silencieux).
 * - Détecte les paires domain-level connues (``left``/``right``,
 *   ``from``/``to``, ``start``/``end``) pour les joindre joliment.
 * - Limite à ``maxFields`` paires pour éviter les libellés trop longs.
 */
export function itemDescriptiveText(
  raw: unknown,
  opts: {
    skipFields?: readonly string[];
    maxFields?: number;
    pairSeparator?: string;
  } = {}
): string {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return "";

  const o = raw as Record<string, unknown>;
  const skip = new Set<string>(
    [...IDENTIFIER_FIELDS, ...(opts.skipFields ?? [])].map((k) => k.toLowerCase())
  );
  const maxFields = opts.maxFields ?? 3;
  const pairSeparator = opts.pairSeparator ?? " · ";

  // 1) Paires domain-level prioritaires.
  for (const spec of Object.values(SPECIAL_JOINERS)) {
    const leftVal = formatDescriptiveValue(o[spec.left]);
    const rightVal = formatDescriptiveValue(o[spec.right]);
    if (leftVal && rightVal) {
      return `${leftVal}${spec.sep}${rightVal}`;
    }
  }

  // 2) Agrégat générique ``k: v``.
  const parts: string[] = [];
  for (const [k, v] of Object.entries(o)) {
    if (parts.length >= maxFields) break;
    if (skip.has(k.toLowerCase())) continue;
    const formatted = formatDescriptiveValue(v);
    if (formatted == null) continue;
    parts.push(`${k}: ${formatted}`);
  }
  return parts.join(pairSeparator);
}

/**
 * Libellé d'affichage complet : ``orderKey`` (ou ``label``) suivi du
 * descriptif si utile. Retourne seulement l'``orderKey`` si aucun descriptif
 * pertinent n'est extractible.
 *
 * Exemple : ``{ id: "P1", left: "11", right: "13" }`` → ``"P1 · 11 ↔ 13"``.
 */
export function itemDisplayLabel(
  raw: unknown,
  opts: {
    fields?: readonly string[];
    fallback?: string;
    descriptiveSeparator?: string;
  } = {}
): string {
  const label = itemLabel(raw, {
    fields: opts.fields ?? DEFAULT_ITEM_LABEL_FIELDS,
    fallback: opts.fallback ?? "",
  });
  const descriptive = itemDescriptiveText(raw);
  if (label && descriptive) {
    return `${label}${opts.descriptiveSeparator ?? " · "}${descriptive}`;
  }
  return label || descriptive || opts.fallback || "";
}

/**
 * Clé d'ordre pour la validation (ex. ``correct_answer``). Différent
 * d'``itemLabel`` : ``itemOrderKey`` garantit l'utilisation d'un champ
 * **identifiant stable** (``id`` par défaut) si présent, sans tomber sur
 * ``label`` / ``name`` / ``value`` qui peuvent contenir du texte éditorial
 * variable.
 *
 * Raison d'être : éviter que ``{ id: "P1", name: "paire première" }`` produise
 * ``orderKey = "paire première"`` qui casserait silencieusement la
 * comparaison backend avec ``correct_answer = "P1, P2, …"``.
 *
 * @param preferField Champ prioritaire pour l'orderKey (défaut : ``"id"``,
 *   avec alias ``piece_id``). Si absent sur la pièce, retombe sur
 *   ``itemLabel`` classique pour garder le fallback lisible.
 */
export function itemOrderKey(
  raw: unknown,
  opts: { preferField?: string; fallback?: string } = {}
): string {
  const preferField = opts.preferField ?? "id";
  const fallback = opts.fallback ?? "";
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const o = raw as Record<string, unknown>;
    // Priorité stricte : ``preferField`` puis alias courants (``piece_id``).
    const candidates = preferField === "id" ? [preferField, "piece_id"] : [preferField];
    for (const key of candidates) {
      const v = o[key];
      if (typeof v === "string" && v.trim()) return v.trim();
      if (typeof v === "number" && Number.isFinite(v)) return String(v);
    }
  }
  // Pas de champ préféré trouvé → fallback sur itemLabel (lecture ordonnée).
  return itemLabel(raw, { fallback });
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
