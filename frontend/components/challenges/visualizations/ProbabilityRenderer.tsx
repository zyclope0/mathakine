"use client";

import { useEffect, useState, useMemo } from "react";
import { Dices, Percent, TrendingUp, Circle, Package } from "lucide-react";
import { useTranslations } from "next-intl";
import { motion } from "framer-motion";

interface ProbabilityRendererProps {
  visualData: any;
  className?: string;
}

// Couleurs prédéfinies pour les items colorés
const COLOR_MAP: Record<string, string> = {
  red: "#ef4444",
  rouge: "#ef4444",
  blue: "#3b82f6",
  bleu: "#3b82f6",
  green: "#22c55e",
  vert: "#22c55e",
  yellow: "#eab308",
  jaune: "#eab308",
  purple: "#a855f7",
  violet: "#a855f7",
  orange: "#f97316",
  pink: "#ec4899",
  rose: "#ec4899",
  white: "#f8fafc",
  blanc: "#f8fafc",
  black: "#1e293b",
  noir: "#1e293b",
  brown: "#92400e",
  marron: "#92400e",
  gray: "#6b7280",
  gris: "#6b7280",
};

/**
 * Renderer pour les défis de probabilités.
 * Affiche des événements, probabilités, et diagrammes de chances.
 */
export function ProbabilityRenderer({ visualData, className = "" }: ProbabilityRendererProps) {
  const t = useTranslations("challenges.visualizations.probability");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Détecter et extraire les items avec quantités (bonbons, billes, cartes, etc.)
  const itemsData = useMemo(() => {
    if (!visualData) return null;

    const items: Array<{ name: string; count: number; color?: string }> = [];
    let total = 0;
    let itemType = t("items");

    // Parcourir toutes les clés pour trouver des patterns d'items
    for (const [key, value] of Object.entries(visualData)) {
      const keyLower = key.toLowerCase();

      // Détecter le type d'item (bonbons, billes, cartes, etc.)
      if (keyLower.includes("bonbon")) itemType = t("candies");
      else if (keyLower.includes("bille")) itemType = t("marbles");
      else if (keyLower.includes("carte")) itemType = t("cards");
      else if (keyLower.includes("dé") || keyLower.includes("dice")) itemType = t("dice");
      else if (keyLower.includes("pièce") || keyLower.includes("coin")) itemType = t("coins");

      // Cas : "red_bonbons": 10, "blue_billes": 5, etc.
      if (typeof value === "number" && !keyLower.includes("total")) {
        // Extraire la couleur du nom de la clé
        const colorMatch = Object.keys(COLOR_MAP).find((c) => keyLower.includes(c));
        if (
          colorMatch ||
          keyLower.match(
            /^(red|blue|green|yellow|purple|orange|pink|white|black|brown|gray|rouge|bleu|vert|jaune|violet|rose|blanc|noir|marron|gris)_/
          )
        ) {
          const colorName = colorMatch ?? keyLower.split("_")[0] ?? keyLower;
          items.push({
            name: colorName.charAt(0).toUpperCase() + colorName.slice(1),
            count: value as number,
            color: COLOR_MAP[colorName.toLowerCase()] ?? colorName.toLowerCase(),
          });
        }
      }

      // Cas : "other_bonbons": {"blue": 5, "green": 5, ...}
      if (typeof value === "object" && value !== null && !Array.isArray(value)) {
        for (const [subKey, subValue] of Object.entries(value as Record<string, unknown>)) {
          if (typeof subValue === "number") {
            const colorName = subKey.toLowerCase();
            items.push({
              name: subKey.charAt(0).toUpperCase() + subKey.slice(1),
              count: subValue,
              color: COLOR_MAP[colorName] || "#6b7280",
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
  }, [visualData]);

  if (!mounted || !visualData) {
    return null;
  }

  // Extraire les données structurées standard
  const events = visualData.events || [];
  const probabilities = visualData.probabilities || visualData.probs || [];
  const outcomes = visualData.outcomes || [];
  const totalOutcomes = visualData.total_outcomes || visualData.total || 0;
  const favorableOutcomes = visualData.favorable_outcomes || visualData.favorable || 0;
  const question = visualData.question || "";
  const context = visualData.context || "";

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
      {question && (
        <div className="bg-primary/10 border border-primary/30 rounded-lg p-3">
          <p className="text-foreground font-medium">{question}</p>
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
            {events.map((event: any, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                {typeof event === "string" ? (
                  <p className="text-foreground font-medium">{event}</p>
                ) : (
                  <div>
                    {event.name && <p className="font-medium text-foreground">{event.name}</p>}
                    {event.probability !== undefined && (
                      <p className="text-xs text-muted-foreground mt-1">
                        <Percent className="h-3 w-3 inline mr-1" />
                        {event.probability}%
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
            {outcomes.map((outcome: any, index: number) => (
              <div
                key={index}
                className="bg-primary/10 border border-primary/30 rounded-md px-3 py-2 text-sm font-medium text-foreground"
              >
                {typeof outcome === "object" ? outcome.name || outcome.value : outcome}
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
            {probabilities.map((prob: any, index: number) => (
              <div key={index} className="bg-background/50 border border-border rounded-md p-3">
                {typeof prob === "string" || typeof prob === "number" ? (
                  <div className="flex items-center gap-2">
                    <Percent className="h-4 w-4 text-primary" />
                    <span className="text-foreground font-medium">{prob}%</span>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {prob.event && (
                      <p className="text-sm font-medium text-foreground">{prob.event}</p>
                    )}
                    <div className="flex items-center gap-3">
                      {prob.value !== undefined && (
                        <span className="text-lg font-semibold text-primary">{prob.value}%</span>
                      )}
                      {prob.fraction && (
                        <code className="text-xs bg-muted px-2 py-1 rounded text-muted-foreground">
                          {prob.fraction}
                        </code>
                      )}
                    </div>
                    {prob.description && (
                      <p className="text-xs text-muted-foreground">{prob.description}</p>
                    )}
                  </div>
                )}
              </div>
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
                  key={item.name}
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
        !question &&
        events.length === 0 &&
        probabilities.length === 0 &&
        outcomes.length === 0 &&
        totalOutcomes === 0 &&
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
