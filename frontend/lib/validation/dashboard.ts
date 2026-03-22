/**
 * Validation des données du dashboard (stats période /api/users/stats).
 * Pas de pseudo-XP période ni de niveau temporel — gamification compte via /me.
 */

export interface UserStats {
  total_exercises: number;
  total_challenges?: number;
  correct_answers: number;
  incorrect_answers?: number;
  success_rate?: number;
  average_score?: number;
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

  const stats = data as Record<string, unknown>;

  const validated: UserStats = {
    total_exercises: typeof stats.total_exercises === "number" ? stats.total_exercises : 0,
    correct_answers: typeof stats.correct_answers === "number" ? stats.correct_answers : 0,
  };

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

  if (
    stats.exercises_by_type != null &&
    typeof stats.exercises_by_type === "object" &&
    !Array.isArray(stats.exercises_by_type)
  ) {
    validated.exercises_by_type = stats.exercises_by_type as Record<string, number>;
  }

  if (
    stats.exercises_by_difficulty != null &&
    typeof stats.exercises_by_difficulty === "object" &&
    !Array.isArray(stats.exercises_by_difficulty)
  ) {
    validated.exercises_by_difficulty = stats.exercises_by_difficulty as Record<string, number>;
  }

  if (
    stats.performance_by_type != null &&
    typeof stats.performance_by_type === "object" &&
    !Array.isArray(stats.performance_by_type)
  ) {
    validated.performance_by_type = stats.performance_by_type as Record<
      string,
      { completed: number; correct: number; success_rate: number }
    >;
  }

  const progressOverTime = stats.progress_over_time;
  if (
    progressOverTime != null &&
    typeof progressOverTime === "object" &&
    Array.isArray((progressOverTime as { labels?: unknown }).labels) &&
    Array.isArray((progressOverTime as { datasets?: unknown }).datasets)
  ) {
    validated.progress_over_time = progressOverTime as NonNullable<UserStats["progress_over_time"]>;
  }

  const exercisesByDay = stats.exercises_by_day;
  if (
    exercisesByDay != null &&
    typeof exercisesByDay === "object" &&
    Array.isArray((exercisesByDay as { labels?: unknown }).labels) &&
    Array.isArray((exercisesByDay as { datasets?: unknown }).datasets)
  ) {
    validated.exercises_by_day = exercisesByDay as NonNullable<UserStats["exercises_by_day"]>;
  }

  if (Array.isArray(stats.recent_activity)) {
    validated.recent_activity = stats.recent_activity;
  }

  if (typeof stats.lastUpdated === "string") {
    validated.lastUpdated = stats.lastUpdated;
  }

  return validated;
}
