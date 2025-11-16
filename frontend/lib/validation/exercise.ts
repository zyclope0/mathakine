/**
 * Validation des paramètres d'exercices
 */

export interface ExerciseParams {
  exercise_type?: string;
  difficulty?: string;
  age_group?: string;
  topic?: string;
}

/**
 * Valide les paramètres d'exercice
 */
export function validateExerciseParams(params: ExerciseParams): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Validation du type d'exercice
  if (params.exercise_type && !['multiple_choice', 'open_ended', 'calculation'].includes(params.exercise_type)) {
    errors.push('Type d\'exercice invalide');
  }
  
  // Validation de la difficulté
  if (params.difficulty && !['easy', 'medium', 'hard'].includes(params.difficulty)) {
    errors.push('Niveau de difficulté invalide');
  }
  
  // Validation du groupe d'âge
  if (params.age_group && !['6-8', '9-11', '12-14', '15-17', '18+'].includes(params.age_group)) {
    errors.push('Groupe d\'âge invalide');
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
    errors.push('Le prompt ne peut pas être vide');
  }
  
  if (prompt.length > 500) {
    errors.push('Le prompt ne peut pas dépasser 500 caractères');
  }
  
  // Vérifier les caractères interdits
  const forbiddenChars = /[<>{}]/;
  if (forbiddenChars.test(prompt)) {
    errors.push('Le prompt contient des caractères interdits');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}
