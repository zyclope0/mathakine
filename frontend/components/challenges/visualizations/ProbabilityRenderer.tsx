"use client";

import {
  VISUALIZATION_COLOR_MAP,
  resolveVisualizationColor,
} from "@/components/challenges/visualizations/_colorMap";
import { useHydrated } from "@/lib/hooks/useHydrated";
import { useMemo } from "react";
import { Dices, Percent, TrendingUp, Circle, Package } from "lucide-react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";

interface ProbabilityRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string;
}

interface ProbabilityItem {
  name: string;
  count: number;
  color?: string;
}

interface ProbabilityUrn {
  label: string;
  items: ProbabilityItem[];
  total: number;
  selectionProbability?: number;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function formatProbabilityLabel(value: string): string {
  const labels: Record<string, string> = {
    red: "Rouge",
    rouge: "Rouge",
    blue: "Bleu",
    bleu: "Bleu",
    green: "Vert",
    vert: "Vert",
    yellow: "Jaune",
    jaune: "Jaune",
    purple: "Violet",
    violet: "Violet",
    orange: "Orange",
    pink: "Rose",
    rose: "Rose",
    white: "Blanc",
    blanc: "Blanc",
    black: "Noir",
    noir: "Noir",
    brown: "Marron",
    marron: "Marron",
    gray: "Gris",
    gris: "Gris",
  };
  const normalized = value.toLowerCase().trim();
  return labels[normalized] ?? value.charAt(0).toUpperCase() + value.slice(1);
}

const ENGLISH_PROBABILITY_TEXT_RE =
  /\b(probability|marbles?|drawn|without replacement|different colors|same color|bag|balls?)\b/i;

function shouldDisplayAuxiliaryText(value: string): boolean {
  const text = value.trim();
  return text.length > 0 && !ENGLISH_PROBABILITY_TEXT_RE.test(text);
}

const PROBABILITY_CONTAINER_META_KEYS = new Set([
  "total",
  "selection_probability",
  "selectionprobability",
  "probability",
  "weight",
]);

function isPopulationCountKey(key: string): boolean {
  return !PROBABILITY_CONTAINER_META_KEYS.has(key.toLowerCase().replace(/_/g, ""));
}

function extractCompositionItems(composition: Record<string, unknown>): ProbabilityItem[] {
  return Object.entries(composition)
    .filter(([key, value]) => isPopulationCountKey(key) && typeof value === "number" && value > 0)
    .map(([key, value]) => ({
      name: formatProbabilityLabel(key),
      count: Number(value),
      color: resolveVisualizationColor(key) ?? "#6b7280",
    }));
}

function extractSelectionProbability(composition: Record<string, unknown>): number | undefined {
  const raw =
    composition.selection_probability ??
    composition.selectionProbability ??
    composition.probability ??
    composition.weight;
  const value = Number(raw);
  return Number.isFinite(value) && value > 0 ? value : undefined;
}

function formatContainerLabel(raw: string): string {
  return raw.replace(/^(box|urn|urne)[_-]?/i, "").toUpperCase();
}

function formatSelectionProbability(value: number): string {
  const percent = value <= 1 ? value * 100 : value;
  return Number.isInteger(percent) ? `${percent}%` : `${percent.toFixed(1)}%`;
}

function extractDrawsWithoutReplacement(visualData: Record<string, unknown>): string | null {
  const explicit = visualData.draws_without_replacement;
  if (explicit !== undefined && explicit !== null && String(explicit).trim()) {
    return String(explicit);
  }
  const rawDraws = visualData.draws;
  const match = rawDraws === undefined || rawDraws === null ? null : String(rawDraws).match(/\d+/);
  return match ? match[0] : null;
}

function extractUrnData(visualData: Record<string, unknown>): ProbabilityUrn[] {
  const urnsRaw = visualData.urns;
  const source = isRecord(urnsRaw)
    ? urnsRaw
    : Object.fromEntries(
        Object.entries(visualData).filter(
          ([key, value]) =>
            isRecord(value) &&
            /^(box|urn|urne)[_-]/i.test(key) &&
            extractCompositionItems(value).length > 0
        )
      );
  if (!isRecord(source)) return [];

  const declaredTotal = Number(visualData.total_per_urn ?? 0);
  return Object.entries(source)
    .map(([label, composition]) => {
      if (!isRecord(composition)) return null;
      const items = extractCompositionItems(composition);

      if (items.length === 0) return null;
      const computedTotal = items.reduce((sum, item) => sum + item.count, 0);
      const containerTotal = Number(composition.total ?? 0);
      return {
        label: formatContainerLabel(label),
        items,
        total:
          containerTotal > 0 ? containerTotal : declaredTotal > 0 ? declaredTotal : computedTotal,
        selectionProbability: extractSelectionProbability(composition),
      };
    })
    .filter((urn): urn is ProbabilityUrn => urn !== null);
}

/**
 * Renderer pour les défis de probabilités.
 * Affiche des événements, probabilités, et diagrammes de chances.
 */
export function ProbabilityRenderer({ visualData, className = "" }: ProbabilityRendererProps) {
  const t = useTranslations("challenges.visualizations.probability");
  const isHydrated = useHydrated();

  const urnData = useMemo(() => {
    if (!visualData) return [];
    return extractUrnData(visualData);
  }, [visualData]);

  // Détecter et extraire les items avec quantités (bonbons, billes, cartes, etc.)
  const itemsData = useMemo(() => {
    if (!visualData) return null;
    if (urnData.length > 0) return null;

    const items: Array<{ name: string; count: number; color?: string }> = [];
    let total = 0;
    let itemType = t("items");

    // Parcourir toutes les clés pour trouver des patterns d'items
    for (const [key, value] of Object.entries(visualData)) {
      const keyLower = key.toLowerCase();

      // Détecter le type d'item (bonbons, billes, cartes, etc.)
      if (keyLower.includes("bonbon") || keyLower.includes("candy")) itemType = t("candies");
      else if (keyLower.includes("bille") || keyLower.includes("marble")) itemType = t("marbles");
      else if (keyLower.includes("carte") || keyLower.includes("card")) itemType = t("cards");
      else if (keyLower.includes("dé") || keyLower.includes("dice")) itemType = t("dice");
      else if (keyLower.includes("pièce") || keyLower.includes("coin")) itemType = t("coins");

      // Cas : "red_bonbons": 10, "blue_billes": 5, etc.
      if (typeof value === "number" && !keyLower.includes("total")) {
        // Extraire la couleur du nom de la clé
        const colorMatch = Object.keys(VISUALIZATION_COLOR_MAP).find((c) => keyLower.includes(c));
        if (
          colorMatch ||
          keyLower.match(
            /^(red|blue|green|yellow|purple|orange|pink|white|black|brown|gray|rouge|bleu|vert|jaune|violet|rose|blanc|noir|marron|gris)_/
          )
        ) {
          const colorName = colorMatch ?? keyLower.split("_")[0] ?? keyLower;
          items.push({
            name: formatProbabilityLabel(colorName),
            count: value as number,
            color: resolveVisualizationColor(colorName) ?? colorName.toLowerCase(),
          });
        }
      }

      // Cas : "other_bonbons": {"blue": 5, "green": 5, ...}
      if (typeof value === "object" && value !== null && !Array.isArray(value)) {
        for (const [subKey, subValue] of Object.entries(value as Record<string, unknown>)) {
          if (typeof subValue === "number") {
            const colorName = subKey.toLowerCase();
            items.push({
              name: formatProbabilityLabel(colorName),
              count: subValue,
              color: resolveVisualizationColor(colorName) ?? "#6b7280",
            });
          }
        }
      }

      // Extraire le total
      if (keyLower.includes("total") && typeof value === "number") {
        total = value as number;
      }
    }

    // Calculer le total si non fourni
    if (total === 0 && items.length > 0) {
      total = items.reduce((sum, item) => sum + item.count, 0);
    }

    return items.length > 0 ? { items, total, itemType } : null;
  }, [visualData, t, urnData.length]);

  if (!isHydrated || !visualData) {
    return null;
  }

  // Extraire les données structurées standard
  const events = Array.isArray(visualData.events) ? visualData.events : [];
  const probabilities = Array.isArray(visualData.probabilities)
    ? visualData.probabilities
    : Array.isArray(visualData.probs)
      ? visualData.probs
      : [];
  const outcomes = Array.isArray(visualData.outcomes) ? visualData.outcomes : [];
  const totalOutcomes: number = Number(visualData.total_outcomes ?? visualData.total ?? 0) || 0;
  const favorableOutcomes: number =
    Number(visualData.favorable_outcomes ?? visualData.favorable ?? 0) || 0;
  const question: string = String(visualData.question ?? "");
  const questionToDisplay = shouldDisplayAuxiliaryText(question) ? question : "";
  const context: string = String(visualData.context ?? "");
  const drawsWithoutReplacement = extractDrawsWithoutReplacement(visualData);

  // Calculer la probabilité si on a les données
  const calculatedProbability =
    totalOutcomes > 0 ? ((favorableOutcomes / totalOutcomes) * 100).toFixed(2) : null;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Contexte */}
      {context && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <p className="text-sm text-muted-foreground leading-relaxed">{context}</p>
        </div>
      )}

      {/* Question */}
      {questionToDisplay && (
        <div className="bg-primary/10 border border-primary/30 rounded-lg p-3">
          <p className="text-foreground font-medium">{questionToDisplay}</p>
        </div>
      )}

      {/* Événements */}
      {events.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Dices className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">{t("possibleEvents")}</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {events.map((event: string | Record<string, unknown>, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                {typeof event === "string" ? (
                  <p className="text-foreground font-medium">{event}</p>
                ) : (
                  <div>
                    {(event as Record<string, unknown>).name != null && (
                      <p className="font-medium text-foreground">
                        {String((event as Record<string, unknown>).name)}
                      </p>
                    )}
                    {(event as Record<string, unknown>).probability !== undefined && (
                      <p className="text-xs text-muted-foreground mt-1">
                        <Percent className="h-3 w-3 inline mr-1" />
                        {String((event as Record<string, unknown>).probability)}%
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Résultats possibles */}
      {outcomes.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">{t("possibleOutcomes")}</h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {outcomes.map((outcome: string | Record<string, unknown> | null, index: number) => (
              <div
                key={index}
                className="bg-primary/10 border border-primary/30 rounded-md px-3 py-2 text-sm font-medium text-foreground"
              >
                {outcome == null
                  ? ""
                  : typeof outcome === "object"
                    ? String(
                        (outcome as Record<string, unknown>).name ??
                          (outcome as Record<string, unknown>).value ??
                          ""
                      )
                    : String(outcome)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Probabilités */}
      {probabilities.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Percent className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">{t("probabilities")}</h4>
          </div>
          <div className="space-y-2">
            {probabilities.map((prob: string | number | Record<string, unknown>, index: number) => {
              const p = prob as Record<string, unknown>;
              return (
                <div key={index} className="bg-background/50 border border-border rounded-md p-3">
                  {typeof prob === "string" || typeof prob === "number" ? (
                    <div className="flex items-center gap-2">
                      <Percent className="h-4 w-4 text-primary" />
                      <span className="text-foreground font-medium">{String(prob)}%</span>
                    </div>
                  ) : (
                    <div className="space-y-1">
                      {p.event != null && (
                        <p className="text-sm font-medium text-foreground">{String(p.event)}</p>
                      )}
                      <div className="flex items-center gap-3">
                        {p.value !== undefined && (
                          <span className="text-lg font-semibold text-primary">
                            {String(p.value)}%
                          </span>
                        )}
                        {p.fraction != null && (
                          <code className="text-xs bg-muted px-2 py-1 rounded text-muted-foreground">
                            {String(p.fraction)}
                          </code>
                        )}
                      </div>
                      {p.description != null && (
                        <p className="text-xs text-muted-foreground">{String(p.description)}</p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Urnes structurées */}
      {urnData.length > 0 && (
        <div className="rounded-xl border border-border bg-card/50 p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">{t("urns")}</h4>
            </div>
            {drawsWithoutReplacement && (
              <span className="rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                {t("drawsWithoutReplacement", {
                  count: drawsWithoutReplacement,
                })}
              </span>
            )}
          </div>
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {urnData.map((urn) => (
              <section
                key={urn.label}
                className="rounded-lg border border-border bg-background/70 p-3 shadow-sm"
                aria-label={`${t("urn")} ${urn.label}`}
              >
                <div className="mb-3 flex items-start justify-between gap-3">
                  <span className="font-semibold text-foreground">
                    {t("urn")} {urn.label}
                  </span>
                  <div className="flex shrink-0 flex-wrap justify-end gap-1">
                    {urn.selectionProbability !== undefined && (
                      <span className="rounded-full bg-primary/10 px-2 py-1 text-xs text-primary">
                        {t("selectionProbability", {
                          value: formatSelectionProbability(urn.selectionProbability),
                        })}
                      </span>
                    )}
                    <span className="rounded-full bg-muted px-2 py-1 text-xs text-muted-foreground">
                      {t("total")} {urn.total}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  {urn.items.map((item) => {
                    const percentage =
                      urn.total > 0 ? Math.round((item.count / urn.total) * 100) : 0;
                    return (
                      <div key={`${urn.label}-${item.name}`} className="space-y-1">
                        <div className="flex items-center justify-between gap-3 text-sm">
                          <span className="flex min-w-0 items-center gap-2 font-medium text-foreground">
                            <Circle
                              className="h-4 w-4 shrink-0"
                              style={{
                                fill: item.color ?? "#6b7280",
                                color: item.color ?? "#6b7280",
                              }}
                              aria-hidden="true"
                            />
                            <span className="truncate">{item.name}</span>
                          </span>
                          <span className="tabular-nums text-muted-foreground">{item.count}</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-muted">
                          <div
                            className="h-full rounded-full"
                            style={{
                              width: `${percentage}%`,
                              backgroundColor: item.color ?? "#6b7280",
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>
        </div>
      )}

      {/* Calcul de probabilité */}
      {(totalOutcomes > 0 || favorableOutcomes > 0) && (
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">{t("calculation")}</h4>
          </div>
          <div className="space-y-2 text-sm">
            {favorableOutcomes > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">{t("favorableCases")}</span>
                <code className="bg-background px-2 py-1 rounded font-semibold text-foreground">
                  {favorableOutcomes}
                </code>
              </div>
            )}
            {totalOutcomes > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">{t("possibleCases")}</span>
                <code className="bg-background px-2 py-1 rounded font-semibold text-foreground">
                  {totalOutcomes}
                </code>
              </div>
            )}
            {calculatedProbability && (
              <div className="flex items-center gap-2 pt-2 border-t border-border">
                <span className="text-muted-foreground">{t("probability")}</span>
                <code className="bg-primary/20 border border-primary/30 px-3 py-1 rounded font-bold text-primary text-lg">
                  {calculatedProbability}%
                </code>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Visualisation des items colorés (bonbons, billes, cartes, etc.) */}
      {itemsData && itemsData.items.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <Package className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground capitalize">
              {t("composition", { total: String(itemsData.total), itemType: itemsData.itemType })}
            </h4>
          </div>

          {/* Affichage visuel des items */}
          <div className="space-y-3">
            {itemsData.items.map((item, index) => {
              const percentage =
                itemsData.total > 0 ? ((item.count / itemsData.total) * 100).toFixed(1) : 0;

              return (
                <motion.div
                  key={`${item.name}-${item.count}-${index}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="space-y-1"
                >
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Circle
                        className="h-4 w-4"
                        style={{
                          fill: item.color || "#6b7280",
                          color: item.color || "#6b7280",
                        }}
                      />
                      <span className="font-medium text-foreground">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">{item.count}</span>
                      <span className="text-xs text-muted-foreground">({percentage}%)</span>
                    </div>
                  </div>

                  {/* Barre de progression */}
                  <div className="h-2 bg-muted/50 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: item.color || "#6b7280" }}
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                    />
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Total */}
          <div className="mt-4 pt-3 border-t border-border flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">{t("total")}</span>
            <span className="text-lg font-bold text-primary">{itemsData.total}</span>
          </div>
        </div>
      )}

      {/* Fallback : afficher toutes les données structurées */}
      {!context &&
        !questionToDisplay &&
        events.length === 0 &&
        probabilities.length === 0 &&
        outcomes.length === 0 &&
        totalOutcomes === 0 &&
        urnData.length === 0 &&
        !itemsData && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="space-y-2">
              {Object.entries(visualData).map(([key, value]) => (
                <div key={key} className="flex gap-2">
                  <span className="text-sm font-semibold text-primary capitalize">
                    {key.replace(/_/g, " ")} :
                  </span>
                  <span className="text-sm text-foreground">
                    {typeof value === "object" ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
    </div>
  );
}
