/**
 * Validation des données du dashboard
 */

export interface UserStats {
  total_exercises: number;
  total_challenges: number;
  correct_answers: number;
  incorrect_answers: number;
  average_score: number;
  level?: number;
  xp?: number;
  next_level_xp?: number;
  exercises_by_type?: Record<string, number>;
  exercises_by_difficulty?: Record<string, number>;
  recent_activity?: Array<{
    id: number;
    type: string;
    completed_at: string;
    score?: number;
  }>;
}

/**
 * Valide et nettoie les statistiques utilisateur
 */
export function safeValidateUserStats(data: unknown): UserStats | null {
  if (!data || typeof data !== 'object') {
    return null;
  }
  
  const stats = data as Partial<UserStats>;
  
  // Valeurs par défaut
  const validated: UserStats = {
    total_exercises: typeof stats.total_exercises === 'number' ? stats.total_exercises : 0,
    total_challenges: typeof stats.total_challenges === 'number' ? stats.total_challenges : 0,
    correct_answers: typeof stats.correct_answers === 'number' ? stats.correct_answers : 0,
    incorrect_answers: typeof stats.incorrect_answers === 'number' ? stats.incorrect_answers : 0,
    average_score: typeof stats.average_score === 'number' ? stats.average_score : 0,
  };
  
  // Champs optionnels
  if (typeof stats.level === 'number') {
    validated.level = stats.level;
  }
  
  if (typeof stats.xp === 'number') {
    validated.xp = stats.xp;
  }
  
  if (typeof stats.next_level_xp === 'number') {
    validated.next_level_xp = stats.next_level_xp;
  }
  
  if (stats.exercises_by_type && typeof stats.exercises_by_type === 'object') {
    validated.exercises_by_type = stats.exercises_by_type;
  }
  
  if (stats.exercises_by_difficulty && typeof stats.exercises_by_difficulty === 'object') {
    validated.exercises_by_difficulty = stats.exercises_by_difficulty;
  }
  
  if (Array.isArray(stats.recent_activity)) {
    validated.recent_activity = stats.recent_activity;
  }
  
  return validated;
}
