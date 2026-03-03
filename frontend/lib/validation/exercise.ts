/**
 * Validation des paramètres d'exercices
 * Les valeurs valides sont dérivées depuis lib/constants/exercises.ts (source unique).
 */

import { EXERCISE_TYPES, AGE_GROUPS } from "@/lib/constants/exercises";

export interface ExerciseParams {
  exercise_type?: string;
  age_group?: string;
}

const VALID_EXERCISE_TYPES: readonly string[] = Object.values(EXERCISE_TYPES);
const VALID_AGE_GROUPS: readonly string[] = Object.values(AGE_GROUPS);

/**
 * Valide les paramètres d'exercice
 */
export function validateExerciseParams(params: ExerciseParams): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // Validation du type d'exercice
  if (params.exercise_type && !VALID_EXERCISE_TYPES.includes(params.exercise_type)) {
    errors.push("Type d'exercice invalide");
  }

  // Validation du groupe d'âge
  if (params.age_group && !VALID_AGE_GROUPS.includes(params.age_group)) {
    errors.push("Groupe d'âge invalide");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
/**
 * Valide le prompt IA pour la génération d'exercices
 */
export function validateAIPrompt(prompt: string): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!prompt || prompt.trim().length === 0) {
    errors.push("Le prompt ne peut pas être vide");
  }

  if (prompt.length > 500) {
    errors.push("Le prompt ne peut pas dépasser 500 caractères");
  }

  // Vérifier les caractères interdits
  const forbiddenChars = /[<>{}]/;
  if (forbiddenChars.test(prompt)) {
    errors.push("Le prompt contient des caractères interdits");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
