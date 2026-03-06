"use client";

/**
 * Hook — scores IRT de l'utilisateur connecté (F03 + F05).
 *
 * Consomme GET /api/diagnostic/status (endpoint existant) et expose :
 *   - irtScores : scores par type d'exercice (null si aucun diagnostic)
 *   - resolveIsOpenAnswer(exerciseType) : true si l'utilisateur doit répondre
 *     en saisie libre pour ce type (niveau IRT GRAND_MAITRE prouvé)
 *
 * Logique de résolution par type :
 *   Types directs  (add, sub, mul, div) → score IRT direct
 *   MIXTE                               → minimum des scores IRT des 4 types de base
 *   FRACTIONS                           → moyenne IRT de multiplication + division
 *   GEOMETRIE, TEXTE, DIVERS            → pas de proxy IRT → fallback profil utilisateur
 *
 * Le QCM est TOUJOURS généré côté backend. C'est uniquement le frontend qui
 * décide d'afficher les boutons ou le champ texte, selon le niveau IRT réel.
 * Cela permet de conserver l'aide QCM pour les niveaux inférieurs même sur des
 * exercices difficiles (scaffolding — Vygotsky 1978, ZPD).
 */

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { useAuth } from "@/hooks/useAuth";

// -------------------------------------------------------------------------- //
// Types                                                                       //
// -------------------------------------------------------------------------- //

export interface IrtTypeScore {
  level: number;
  difficulty: string; // "INITIE" | "PADAWAN" | "CHEVALIER" | "MAITRE" | "GRAND_MAITRE"
  correct: number;
  total: number;
}

export type IrtScores = Record<string, IrtTypeScore>;

interface DiagnosticStatusResponse {
  has_completed: boolean;
  latest: {
    id: number;
    completed_at: string;
    triggered_from: string;
    questions_asked: number;
    duration_seconds: number | null;
    scores: IrtScores;
  } | null;
}

// -------------------------------------------------------------------------- //
// Constantes de résolution (miroir de adaptive_difficulty_service.py)        //
// -------------------------------------------------------------------------- //

const DIFFICULTY_ORDER = ["INITIE", "PADAWAN", "CHEVALIER", "MAITRE", "GRAND_MAITRE"] as const;
type Difficulty = (typeof DIFFICULTY_ORDER)[number];

const DIFFICULTY_TO_ORDINAL: Record<string, number> = {
  INITIE: 0,
  PADAWAN: 1,
  CHEVALIER: 2,
  MAITRE: 3,
  GRAND_MAITRE: 4,
};

/** Types évalués directement par le diagnostic IRT */
const IRT_DIRECT_TYPES = new Set(["addition", "soustraction", "multiplication", "division"]);

/** Seuil à partir duquel on retire l'aide QCM */
const OPEN_ANSWER_THRESHOLD: Difficulty = "GRAND_MAITRE";

// -------------------------------------------------------------------------- //
// Helpers                                                                     //
// -------------------------------------------------------------------------- //

function toOrdinal(difficulty: string | undefined): number | null {
  if (!difficulty) return null;
  const o = DIFFICULTY_TO_ORDINAL[difficulty.toUpperCase()];
  return o !== undefined ? o : null;
}

function ordinalToDifficulty(ordinal: number): Difficulty {
  return DIFFICULTY_ORDER[Math.max(0, Math.min(4, ordinal))];
}

/**
 * Résout le niveau IRT effectif pour un type donné à partir des scores stockés.
 * Retourne null si le type n'est pas couvert par l'IRT et n'a pas de proxy.
 */
function resolveIrtOrdinal(scores: IrtScores, exerciseType: string): number | null {
  const key = exerciseType.toLowerCase();

  // 1. Score direct
  const direct = scores[key];
  if (direct) {
    const o = toOrdinal(direct.difficulty);
    if (o !== null) return o;
  }

  // 2. Proxy MIXTE → minimum des 4 types de base
  if (key === "mixte") {
    const baseKeys = ["addition", "soustraction", "multiplication", "division"];
    const ordinals = baseKeys
      .map((k) => toOrdinal(scores[k]?.difficulty))
      .filter((o): o is number => o !== null);
    return ordinals.length > 0 ? Math.min(...ordinals) : null;
  }

  // 3. Proxy FRACTIONS → moyenne arrondie vers le bas de mult + div
  if (key === "fractions") {
    const proxies = ["multiplication", "division"]
      .map((k) => toOrdinal(scores[k]?.difficulty))
      .filter((o): o is number => o !== null);
    if (proxies.length > 0) return Math.floor(proxies.reduce((a, b) => a + b, 0) / proxies.length);
  }

  // 4. Pas de proxy (geometrie, texte, divers) → null
  return null;
}

/**
 * Fallback profil : détermine si l'utilisateur devrait avoir la saisie libre
 * uniquement sur la base de son preferred_difficulty (age_group ou DifficultyLevel).
 */
function isOpenAnswerFromProfile(preferredDifficulty: string | null | undefined): boolean {
  if (!preferredDifficulty) return false;
  const normalized = preferredDifficulty.toUpperCase();
  // DifficultyLevel direct
  if (normalized === "GRAND_MAITRE") return true;
  // age_group "adulte"
  if (preferredDifficulty.toLowerCase() === "adulte") return true;
  return false;
}

// -------------------------------------------------------------------------- //
// Hook                                                                        //
// -------------------------------------------------------------------------- //

export function useIrtScores() {
  const { user, isAuthenticated } = useAuth();

  const { data, isLoading } = useQuery<DiagnosticStatusResponse>({
    queryKey: ["diagnostic", "status"],
    queryFn: () => api.get<DiagnosticStatusResponse>("/api/diagnostic/status"),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 min — les scores IRT ne changent pas souvent
    refetchOnWindowFocus: false,
  });

  const irtScores: IrtScores | null = data?.latest?.scores ?? null;

  /**
   * Retourne true si l'utilisateur doit répondre en saisie libre pour ce type.
   *
   * Règle :
   *   - Si score IRT disponible pour ce type (direct ou proxy) → saisie libre
   *     uniquement si niveau IRT = GRAND_MAITRE
   *   - Si pas de score IRT (type sans proxy : geo, texte, divers) → fallback
   *     sur preferred_difficulty du profil utilisateur
   */
  const resolveIsOpenAnswer = (exerciseType: string): boolean => {
    if (!irtScores) {
      // Aucun diagnostic → fallback profil
      return isOpenAnswerFromProfile(user?.preferred_difficulty);
    }

    const ordinal = resolveIrtOrdinal(irtScores, exerciseType);

    if (ordinal === null) {
      // Type sans couverture IRT (geo, texte, divers) → fallback profil
      return isOpenAnswerFromProfile(user?.preferred_difficulty);
    }

    const difficulty = ordinalToDifficulty(ordinal);
    return difficulty === OPEN_ANSWER_THRESHOLD;
  };

  /**
   * Retourne le niveau IRT résolu pour un type (ex: "CHEVALIER"), ou null.
   * Utile pour l'affichage d'info dans l'UI ("votre niveau en addition : Chevalier").
   */
  const getIrtLevel = (exerciseType: string): Difficulty | null => {
    if (!irtScores) return null;
    const ordinal = resolveIrtOrdinal(irtScores, exerciseType);
    return ordinal !== null ? ordinalToDifficulty(ordinal) : null;
  };

  /** True si le type est couvert par l'IRT (direct ou proxy) */
  const isIrtCovered = (exerciseType: string): boolean => {
    const key = exerciseType.toLowerCase();
    return IRT_DIRECT_TYPES.has(key) || key === "mixte" || key === "fractions";
  };

  return {
    irtScores,
    isLoading,
    hasCompletedDiagnostic: data?.has_completed ?? false,
    resolveIsOpenAnswer,
    getIrtLevel,
    isIrtCovered,
  };
}
