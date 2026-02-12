/**
 * Validation des données du dashboard
 */

export interface UserStats {
  total_exercises: number;
  total_challenges?: number;
  correct_answers: number;
  incorrect_answers?: number;
  success_rate?: number;
  average_score?: number;
  experience_points?: number;
  level?: {
    current: number;
    title: string;
    current_xp: number;
    next_level_xp: number;
  };
  xp?: number;
  next_level_xp?: number;
  exercises_by_type?: Record<string, number>;
  exercises_by_difficulty?: Record<string, number>;
  performance_by_type?: Record<
    string,
    {
      completed: number;
      correct: number;
      success_rate: number;
    }
  >;
  progress_over_time?: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
    }>;
  };
  exercises_by_day?: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      borderColor?: string;
      backgroundColor?: string;
    }>;
  };
  recent_activity?: Array<{
    type: string;
    description: string;
    time: string;
    is_correct?: boolean;
  }>;
  lastUpdated?: string;
}

/**
 * Valide et nettoie les statistiques utilisateur
 */
export function safeValidateUserStats(data: unknown): UserStats | null {
  if (!data || typeof data !== "object") {
    return null;
  }

  const stats = data as any;

  // Valeurs par défaut pour les champs obligatoires
  const validated: UserStats = {
    total_exercises: typeof stats.total_exercises === "number" ? stats.total_exercises : 0,
    correct_answers: typeof stats.correct_answers === "number" ? stats.correct_answers : 0,
  };

  // Champs optionnels - Préserver TOUS les champs que le backend envoie
  if (typeof stats.total_challenges === "number") {
    validated.total_challenges = stats.total_challenges;
  }

  if (typeof stats.incorrect_answers === "number") {
    validated.incorrect_answers = stats.incorrect_answers;
  }

  if (typeof stats.success_rate === "number") {
    validated.success_rate = stats.success_rate;
  }

  if (typeof stats.average_score === "number") {
    validated.average_score = stats.average_score;
  }

  if (typeof stats.experience_points === "number") {
    validated.experience_points = stats.experience_points;
  }

  // Level peut être un objet ou un number
  if (stats.level) {
    if (typeof stats.level === "object" && typeof stats.level.current === "number") {
      validated.level = stats.level;
    } else if (typeof stats.level === "number") {
      validated.xp = stats.level;
    }
  }

  if (typeof stats.xp === "number") {
    validated.xp = stats.xp;
  }

  if (typeof stats.next_level_xp === "number") {
    validated.next_level_xp = stats.next_level_xp;
  }

  if (stats.exercises_by_type && typeof stats.exercises_by_type === "object") {
    validated.exercises_by_type = stats.exercises_by_type;
  }

  if (stats.exercises_by_difficulty && typeof stats.exercises_by_difficulty === "object") {
    validated.exercises_by_difficulty = stats.exercises_by_difficulty;
  }

  if (stats.performance_by_type && typeof stats.performance_by_type === "object") {
    validated.performance_by_type = stats.performance_by_type;
  }

  if (stats.progress_over_time && typeof stats.progress_over_time === "object") {
    validated.progress_over_time = stats.progress_over_time;
  }

  if (stats.exercises_by_day && typeof stats.exercises_by_day === "object") {
    validated.exercises_by_day = stats.exercises_by_day;
  }

  if (Array.isArray(stats.recent_activity)) {
    validated.recent_activity = stats.recent_activity;
  }

  if (typeof stats.lastUpdated === "string") {
    validated.lastUpdated = stats.lastUpdated;
  }

  return validated;
}
