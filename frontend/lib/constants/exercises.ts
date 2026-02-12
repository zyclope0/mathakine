import {
  Plus,
  Minus,
  X,
  Divide,
  Ratio,
  Shapes,
  FileText,
  Combine,
  Calculator,
  BookOpenText,
} from "lucide-react";

/**
 * Constantes pour les types d'exercices
 */
export const EXERCISE_TYPES = {
  ADDITION: "addition",
  SUBTRACTION: "soustraction",
  MULTIPLICATION: "multiplication",
  DIVISION: "division",
  MIXTE: "mixte",
  FRACTIONS: "fractions",
  GEOMETRIE: "geometrie",
  TEXTE: "texte",
  DIVERS: "divers",
} as const;

export type ExerciseType = (typeof EXERCISE_TYPES)[keyof typeof EXERCISE_TYPES];

export const EXERCISE_TYPE_DISPLAY: Record<ExerciseType, string> = {
  [EXERCISE_TYPES.ADDITION]: "Addition",
  [EXERCISE_TYPES.SUBTRACTION]: "Soustraction",
  [EXERCISE_TYPES.MULTIPLICATION]: "Multiplication",
  [EXERCISE_TYPES.DIVISION]: "Division",
  [EXERCISE_TYPES.MIXTE]: "Mixte",
  [EXERCISE_TYPES.FRACTIONS]: "Fractions",
  [EXERCISE_TYPES.GEOMETRIE]: "Géométrie",
  [EXERCISE_TYPES.TEXTE]: "Texte",
  [EXERCISE_TYPES.DIVERS]: "Divers",
};

// Associe chaque type d'exercice à une icône et un style de badge
export const EXERCISE_TYPE_STYLES = {
  [EXERCISE_TYPES.ADDITION]: { icon: Plus, className: "border-slate-400 dark:border-slate-600" },
  [EXERCISE_TYPES.SUBTRACTION]: {
    icon: Minus,
    className: "border-slate-400 dark:border-slate-600",
  },
  [EXERCISE_TYPES.MULTIPLICATION]: { icon: X, className: "border-slate-400 dark:border-slate-600" },
  [EXERCISE_TYPES.DIVISION]: { icon: Divide, className: "border-slate-400 dark:border-slate-600" },
  [EXERCISE_TYPES.FRACTIONS]: { icon: Ratio, className: "border-blue-400 dark:border-blue-600" },
  [EXERCISE_TYPES.GEOMETRIE]: { icon: Shapes, className: "border-blue-400 dark:border-blue-600" },
  [EXERCISE_TYPES.TEXTE]: { icon: BookOpenText, className: "border-blue-400 dark:border-blue-600" },
  [EXERCISE_TYPES.MIXTE]: { icon: Combine, className: "border-purple-400 dark:border-purple-600" },
  [EXERCISE_TYPES.DIVERS]: {
    icon: Calculator,
    className: "border-purple-400 dark:border-purple-600",
  },
};

/**
 * Constantes pour les groupes d'âge
 */
export const AGE_GROUPS = {
  GROUP_6_8: "6-8",
  GROUP_9_11: "9-11",
  GROUP_12_14: "12-14",
  GROUP_15_17: "15-17",
  ADULT: "adulte",
  ALL_AGES: "tous-ages",
} as const;

export type AgeGroup = (typeof AGE_GROUPS)[keyof typeof AGE_GROUPS];

export const AGE_GROUP_DISPLAY: Record<AgeGroup, string> = {
  [AGE_GROUPS.GROUP_6_8]: "6-8 ans",
  [AGE_GROUPS.GROUP_9_11]: "9-11 ans",
  [AGE_GROUPS.GROUP_12_14]: "12-14 ans",
  [AGE_GROUPS.GROUP_15_17]: "15-17 ans",
  [AGE_GROUPS.ADULT]: "Adulte",
  [AGE_GROUPS.ALL_AGES]: "Tous âges",
};

export const AGE_GROUP_COLORS: Record<string, string> = {
  "6-8": "bg-green-500/20 text-green-300 border-green-500/30",
  "9-11": "bg-blue-500/20 text-blue-300 border-blue-500/30",
  "12-14": "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  "15-17": "bg-orange-500/20 text-orange-300 border-orange-500/30",
  adulte: "bg-red-500/20 text-red-300 border-red-500/30",
  "tous-ages": "bg-purple-500/20 text-purple-300 border-purple-500/30",
  default: "bg-gray-500/20 text-gray-300 border-gray-500/30",
};

export function getAgeGroupColor(ageGroup: string | null | undefined): string {
  const defaultColor = "bg-gray-500/20 text-gray-300 border-gray-500/30";
  if (!ageGroup) {
    return AGE_GROUP_COLORS["default"] ?? defaultColor;
  }
  return AGE_GROUP_COLORS[ageGroup] ?? AGE_GROUP_COLORS["default"] ?? defaultColor;
}

/**
 * Constantes pour les types de défis logiques
 */
export const CHALLENGE_TYPES = {
  SEQUENCE: "sequence",
  PATTERN: "pattern",
  VISUAL: "visual",
  PUZZLE: "puzzle",
  DEDUCTION: "deduction",
  SPATIAL: "spatial",
  PROBABILITY: "probability",
  GRAPH: "graph",
  CODING: "coding",
  CHESS: "chess",
  CUSTOM: "custom",
} as const;

export type ChallengeType = (typeof CHALLENGE_TYPES)[keyof typeof CHALLENGE_TYPES];
