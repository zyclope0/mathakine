/**
 * Helpers purs de dérivation métier pour ChallengeSolver.
 *
 * Toutes les fonctions de ce module sont pures (zéro React, zéro hooks, zéro side-effects).
 * Elles s'appuient sur les utilitaires existants :
 *   - resolveChallengeResponseMode (contrat response_mode IA9)
 *   - extractShapeChoicesFromVisualData, parsePositions* (visualChallengeUtils)
 *
 * FFI-L10 — lot 1 : extraction helpers purs
 */

import type { Challenge } from "@/types/api";
import { resolveChallengeResponseMode } from "@/lib/challenges/resolveChallengeResponseMode";
import type { ChallengeResponseMode } from "@/lib/challenges/resolveChallengeResponseMode";
import {
  extractShapeChoicesFromVisualData,
  hasGroupedSymmetryLayout,
  parsePositionsFromCorrectAnswer,
  parsePositionsFromQuestion,
  parsePositionsFromLayout,
} from "@/lib/utils/visualChallengeUtils";

// ─── Types exportés ──────────────────────────────────────────────────────────

export interface ChallengeVisualAnswerModel {
  responseMode: ChallengeResponseMode;
  showMcq: boolean;
  isVisual: boolean;
  visualChoices: string[];
  visualPositions: number[];
  hasVisualButtons: boolean;
  isVisualMultiComplete: boolean;
  /** Réponse synthétisée depuis visualSelections pour le mode multi-position. */
  derivedUserAnswerFromSelections: string;
}

export interface IsChallengeAnswerEmptyArgs {
  hasVisualButtons: boolean;
  visualPositions: number[];
  isVisualMultiComplete: boolean;
  userAnswer: string;
}

export type ChallengeTextInputKind = "default" | "visual" | "chess";

// ─── Normalisation des choices ────────────────────────────────────────────────

/**
 * Normalise `challenge.choices` en tableau de strings.
 * Gère : tableau natif, JSON string, valeur absente ou invalide → [].
 */
export function normalizeChallengeChoices(challenge: Challenge): string[] {
  const raw = challenge.choices;
  if (Array.isArray(raw)) return raw as string[];
  if (typeof raw === "string") {
    try {
      const parsed: unknown = JSON.parse(raw);
      return Array.isArray(parsed) ? (parsed as string[]) : [];
    } catch {
      return [];
    }
  }
  return [];
}

// ─── Normalisation des hints ─────────────────────────────────────────────────

/**
 * Normalise un champ hints brut en tableau de strings.
 * Gère : tableau natif, JSON string, valeur absente ou invalide → [].
 */
export function getChallengeHintsArray(rawHints: unknown): string[] {
  if (Array.isArray(rawHints)) return rawHints as string[];
  if (typeof rawHints === "string") {
    try {
      const parsed: unknown = JSON.parse(rawHints);
      return Array.isArray(parsed) ? (parsed as string[]) : [];
    } catch {
      return [];
    }
  }
  return [];
}

// ─── Modèle visuel ───────────────────────────────────────────────────────────

/**
 * Centralise toute la dérivation visuelle depuis un challenge et les sélections courantes.
 *
 * La logique de résolution des positions suit la priorité :
 *   1. correct_answer contient "Position N:"
 *   2. question contient "positions N (et M)"
 *   3. fallback layout/shapes dans visual_data
 */
export function getChallengeVisualAnswerModel(
  challenge: Challenge,
  visualSelections: Record<number, string>
): ChallengeVisualAnswerModel {
  const responseMode = resolveChallengeResponseMode(challenge);
  const choicesArray = normalizeChallengeChoices(challenge);

  const showMcq = responseMode === "single_choice" && choicesArray.length > 0;
  const isVisual = challenge.challenge_type?.toLowerCase() === "visual";
  const groupedSymmetryLayout = isVisual && hasGroupedSymmetryLayout(challenge.visual_data);

  const visualChoices =
    isVisual && challenge.visual_data && !groupedSymmetryLayout
      ? extractShapeChoicesFromVisualData(challenge.visual_data)
      : [];

  const visualPositions: number[] =
    parsePositionsFromCorrectAnswer(challenge.correct_answer).length > 0
      ? parsePositionsFromCorrectAnswer(challenge.correct_answer)
      : parsePositionsFromQuestion(challenge.question).length > 0
        ? parsePositionsFromQuestion(challenge.question)
        : parsePositionsFromLayout(challenge.visual_data);
  const correctAnswerText = String(challenge.correct_answer ?? "");
  const usesOrderedCsvVisualAnswer =
    isVisual &&
    visualPositions.length >= 2 &&
    correctAnswerText.includes(",") &&
    !correctAnswerText.toLowerCase().includes("position");

  const hasVisualButtons =
    responseMode === "interactive_visual" &&
    !showMcq &&
    !groupedSymmetryLayout &&
    !usesOrderedCsvVisualAnswer &&
    visualChoices.length >= 2 &&
    !!challenge.visual_data;

  const isVisualMultiComplete =
    visualPositions.length <= 1 || visualPositions.every((p) => !!visualSelections[p]);

  // Synthèse userAnswer depuis visualSelections pour le mode multi-position
  const derivedUserAnswerFromSelections =
    hasVisualButtons && visualPositions.length >= 2
      ? visualPositions
          .filter((p) => visualSelections[p])
          .map((p) => `Position ${p}: ${visualSelections[p]}`)
          .join(", ")
      : "";

  return {
    responseMode,
    showMcq,
    isVisual,
    visualChoices,
    visualPositions,
    hasVisualButtons,
    isVisualMultiComplete,
    derivedUserAnswerFromSelections,
  };
}

// ─── Vide de réponse ─────────────────────────────────────────────────────────

/**
 * Détermine si la réponse courante est vide / incomplète selon le mode actif.
 *
 * Règles :
 * - mode visual multi-position : incomplet si toutes les positions ne sont pas remplies
 * - mode visual simple         : vide si userAnswer est vide
 * - tous les autres modes      : vide si userAnswer.trim() est vide
 */
export function isChallengeAnswerEmpty({
  hasVisualButtons,
  visualPositions,
  isVisualMultiComplete,
  userAnswer,
}: IsChallengeAnswerEmptyArgs): boolean {
  if (hasVisualButtons) {
    if (visualPositions.length > 1) return !isVisualMultiComplete;
    return !userAnswer.trim();
  }
  return !userAnswer.trim();
}

// ─── Catégorie de saisie texte ────────────────────────────────────────────────

/**
 * Retourne la catégorie de placeholder/help-text à utiliser dans le champ texte.
 * Ne retourne pas de labels i18n — juste une clé discriminante.
 *
 * Usage dans ChallengeSolver : t(`${getChallengeTextInputKind(type)}AnswerPlaceholder`)
 */
export function getChallengeTextInputKind(
  challengeType: string | null | undefined
): ChallengeTextInputKind {
  const lower = challengeType?.toLowerCase() ?? "";
  if (lower === "chess") return "chess";
  if (lower === "visual") return "visual";
  return "default";
}
