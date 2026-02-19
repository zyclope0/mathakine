"use client";

import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, ArrowRight } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";

interface SequenceRendererProps {
  visualData: any;
  difficultyRating?: number | null | undefined;
  className?: string;
  onAnswerChange?: (answer: string) => void;
}

/** Seuil à partir duquel on masque le pattern suggéré (défis difficiles). */
const HIDE_PATTERN_ABOVE_DIFFICULTY = 4;

/**
 * Renderer pour les défis de type SEQUENCE.
 * Affiche une séquence de manière interactive avec animation.
 * Pour difficulté ≥ 4/5, le pattern suggéré est masqué pour garder le défi stimulant.
 */
export function SequenceRenderer({ visualData, difficultyRating, className, onAnswerChange }: SequenceRendererProps) {
  // Parser les données de séquence avec gestion robuste des différents formats
  const parseSequence = (data: any): any[] => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (typeof data === "string") {
      try {
        const parsed = JSON.parse(data);
        if (Array.isArray(parsed)) return parsed;
        if (parsed?.sequence) return parsed.sequence;
        if (parsed?.items) return parsed.items;
      } catch {
        // Si c'est une séquence sous forme de string séparée par des virgules
        return data
          .split(",")
          .map((s: string) => s.trim())
          .filter(Boolean);
      }
    }
    if (data?.sequence) return Array.isArray(data.sequence) ? data.sequence : [];
    if (data?.items) return Array.isArray(data.items) ? data.items : [];
    return [];
  };

  const sequence = parseSequence(visualData);
  const [highlightedIndex, setHighlightedIndex] = useState<number | null>(null);
  const [nextValue, setNextValue] = useState<string>("");

  if (!sequence || sequence.length === 0) {
    return (
      <Card className={`bg-card border-primary/20 ${className || ""}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          Aucune séquence disponible
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`bg-card border-primary/20 ${className || ""}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h4 className="text-sm font-semibold text-foreground">Séquence à analyser</h4>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 p-4 bg-muted/30 rounded-lg">
            {sequence.map((item: any, index: number) => {
              const isHighlighted = highlightedIndex === index;
              const itemValue =
                typeof item === "object"
                  ? item.value || item.label || JSON.stringify(item)
                  : String(item);

              return (
                <div key={index} className="flex items-center gap-2">
                  <motion.div
                    className={`
                      px-4 py-2 rounded-lg border-2 font-semibold text-lg
                      transition-all cursor-pointer
                      ${
                        isHighlighted
                          ? "bg-primary text-primary-foreground border-primary shadow-lg scale-110"
                          : "bg-card text-foreground border-primary/30 hover:border-primary/50"
                      }
                    `}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setHighlightedIndex(isHighlighted ? null : index)}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    {itemValue}
                  </motion.div>
                  {index < sequence.length - 1 && (
                    <ArrowRight className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
              );
            })}
          </div>

          {visualData?.pattern &&
            (difficultyRating == null || difficultyRating < HIDE_PATTERN_ABOVE_DIFFICULTY) && (
              <div className="text-xs text-muted-foreground italic text-center">
                Pattern suggéré: {visualData.pattern}
              </div>
            )}

          {/* Zone de réponse pour le prochain élément */}
          {onAnswerChange && (
            <div className="space-y-2 pt-2 border-t border-primary/20">
              <label className="text-sm font-medium text-foreground">
                Quel est le prochain élément ?
              </label>
              <input
                type="text"
                value={nextValue}
                onChange={(e) => {
                  const value = e.target.value;
                  setNextValue(value);
                  if (onAnswerChange) {
                    onAnswerChange(value);
                  }
                }}
                placeholder="Entrez le prochain nombre..."
                className="w-full px-3 py-2 rounded-lg border-2 border-primary/30 bg-card text-foreground focus:border-primary focus:outline-none"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
