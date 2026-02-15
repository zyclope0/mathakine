import {
  ListOrdered,
  Grid3X3,
  Eye,
  Puzzle,
  HelpCircle,
  Search,
  Percent,
  GitBranch,
  Code,
  Crown,
} from "lucide-react";
import { AGE_GROUP_DISPLAY } from "./exercises";

/**
 * Constantes pour les types de défis logiques
 * Note: SPATIAL a été fusionné dans VISUAL (même renderer, mêmes paramètres)
 */
export const CHALLENGE_TYPES = {
  SEQUENCE: "sequence",
  PATTERN: "pattern",
  VISUAL: "visual", // Inclut les défis spatiaux (rotation, symétrie)
  PUZZLE: "puzzle",
  RIDDLE: "riddle",
  DEDUCTION: "deduction",
  PROBABILITY: "probability",
  GRAPH: "graph",
  CODING: "coding",
  CHESS: "chess",
} as const;

export type ChallengeType = (typeof CHALLENGE_TYPES)[keyof typeof CHALLENGE_TYPES];

export const CHALLENGE_TYPE_DISPLAY: Record<ChallengeType, string> = {
  [CHALLENGE_TYPES.SEQUENCE]: "Séquence",
  [CHALLENGE_TYPES.PATTERN]: "Motif",
  [CHALLENGE_TYPES.VISUAL]: "Visuel & Spatial",
  [CHALLENGE_TYPES.PUZZLE]: "Puzzle",
  [CHALLENGE_TYPES.RIDDLE]: "Énigme",
  [CHALLENGE_TYPES.DEDUCTION]: "Déduction",
  [CHALLENGE_TYPES.PROBABILITY]: "Probabilité",
  [CHALLENGE_TYPES.GRAPH]: "Graphe",
  [CHALLENGE_TYPES.CODING]: "Codage",
  [CHALLENGE_TYPES.CHESS]: "Échecs",
};

// Associe chaque type de défi à une icône et un style
export const CHALLENGE_TYPE_STYLES = {
  [CHALLENGE_TYPES.SEQUENCE]: {
    icon: ListOrdered,
    className: "border-blue-400 dark:border-blue-600",
  },
  [CHALLENGE_TYPES.PATTERN]: {
    icon: Grid3X3,
    className: "border-purple-400 dark:border-purple-600",
  },
  [CHALLENGE_TYPES.VISUAL]: { icon: Eye, className: "border-green-400 dark:border-green-600" },
  [CHALLENGE_TYPES.PUZZLE]: { icon: Puzzle, className: "border-orange-400 dark:border-orange-600" },
  [CHALLENGE_TYPES.RIDDLE]: {
    icon: HelpCircle,
    className: "border-yellow-400 dark:border-yellow-600",
  },
  [CHALLENGE_TYPES.DEDUCTION]: { icon: Search, className: "border-red-400 dark:border-red-600" },
  [CHALLENGE_TYPES.PROBABILITY]: {
    icon: Percent,
    className: "border-pink-400 dark:border-pink-600",
  },
  [CHALLENGE_TYPES.GRAPH]: {
    icon: GitBranch,
    className: "border-indigo-400 dark:border-indigo-600",
  },
  [CHALLENGE_TYPES.CODING]: { icon: Code, className: "border-emerald-400 dark:border-emerald-600" },
  [CHALLENGE_TYPES.CHESS]: { icon: Crown, className: "border-amber-400 dark:border-amber-600" },
};

/**
 * Obtient le libellé d'affichage pour un type de challenge
 * Gère automatiquement la normalisation (majuscules/minuscules)
 */
export function getChallengeTypeDisplay(value: string | null | undefined): string {
  if (!value) return "Non identifié";

  // Normaliser en minuscule pour le lookup
  const normalized = value.toLowerCase() as ChallengeType;

  return CHALLENGE_TYPE_DISPLAY[normalized] || value;
}

/** Mapping pour affichage admin (ex. GROUP_10_12 → "9-11 ans", ADULT → "Adulte") */
export const ADMIN_AGE_GROUP_LABELS: Record<string, string> = {
  ...AGE_GROUP_DISPLAY,
  GROUP_6_8: "6-8 ans",
  GROUP_10_12: "9-11 ans",
  GROUP_13_15: "12-14 ans",
  GROUP_15_17: "15-17 ans",
  ADULT: "Adulte",
  ALL_AGES: "Tous âges",
};

export function getAdminAgeDisplay(val: string | null | undefined): string {
  if (!val) return "—";
  return ADMIN_AGE_GROUP_LABELS[val] ?? val;
}

// Importer et ré-exporter les constantes de groupe d'âge unifiées (DRY)
export {
  AGE_GROUPS,
  AGE_GROUP_DISPLAY,
  AGE_GROUP_COLORS,
  getAgeGroupColor,
  getAgeGroupDisplay,
  type AgeGroup,
} from "./exercises";
