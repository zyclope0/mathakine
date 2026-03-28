/**
 * Validation des données du dashboard (stats période /api/users/stats).
 * Pas de pseudo-XP période ni de niveau temporel — gamification compte via /me.
 */

/** Agrégat F04 (révisions espacées) — GET /api/users/stats → spaced_repetition */
export interface SpacedRepetitionUserSummary {
  f04_initialized: boolean;
  active_cards_count: number;
  due_today_count: number;
  overdue_count: number;
  /** ISO date YYYY-MM-DD ou null */
  next_review_date: string | null;
}

const DEFAULT_SPACED_REPETITION: SpacedRepetitionUserSummary = {
  f04_initialized: false,
  active_cards_count: 0,
  due_today_count: 0,
  overdue_count: 0,
  next_review_date: null,
};

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

/**
 * Parse le bloc API ``spaced_repetition`` sans lever — fallback sur valeurs sûres.
 */
export function parseSpacedRepetitionUserSummary(data: unknown): SpacedRepetitionUserSummary {
  if (data === null || data === undefined || typeof data !== "object" || Array.isArray(data)) {
    return { ...DEFAULT_SPACED_REPETITION };
  }
  const o = data as Record<string, unknown>;
  const bool = (k: string, d: boolean): boolean => (typeof o[k] === "boolean" ? o[k] : d);
  const int0 = (k: string, d: number): number => {
    const v = o[k];
    if (typeof v === "number" && Number.isFinite(v) && v >= 0) {
      return Math.floor(v);
    }
    return d;
  };
  let next: string | null = DEFAULT_SPACED_REPETITION.next_review_date;
  const nr = o.next_review_date;
  if (nr === null) {
    next = null;
  } else if (typeof nr === "string" && ISO_DATE_RE.test(nr)) {
    next = nr;
  }
  return {
    f04_initialized: bool("f04_initialized", DEFAULT_SPACED_REPETITION.f04_initialized),
    active_cards_count: int0("active_cards_count", DEFAULT_SPACED_REPETITION.active_cards_count),
    due_today_count: int0("due_today_count", DEFAULT_SPACED_REPETITION.due_today_count),
    overdue_count: int0("overdue_count", DEFAULT_SPACED_REPETITION.overdue_count),
    next_review_date: next,
  };
}

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
  spaced_repetition: SpacedRepetitionUserSummary;
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
    spaced_repetition: parseSpacedRepetitionUserSummary(stats.spaced_repetition),
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
