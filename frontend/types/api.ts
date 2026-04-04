/**
 * Types pour les réponses API standardisées.
 *
 * Compat legacy (encore servie par le backend) : `jedi_rank`, `star_wars_title`.
 * Le frontend préfère `progression_rank` et `thematic_title` — voir `progressionRankLabel`, `badgeThematicTitle`.
 */

import type { UserRole } from "@/lib/auth/userRoles";

/**
 * Niveau gamification persisté (aligné classement), fourni par le backend — pas dérivé du timeRange stats.
 */
export interface GamificationLevelIndicator {
  current: number;
  /** @deprecated F42-P5 — retiré du backend ; ne plus utiliser pour l’affichage. */
  title?: string;
  current_xp: number;
  next_level_xp: number;
  /** Bucket de rang public (F43-A3) — préféré côté contrat. */
  progression_rank?: string;
  /** @deprecated F43-A3 — alias legacy, même valeur que `progression_rank`. */
  jedi_rank?: string;
}

/**
 * Type User avec tous les champs possibles.
 */
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string | null;
  role: UserRole;
  is_active: boolean;
  is_email_verified?: boolean;
  /** "full" = accès complet ; "exercises_only" = uniquement exercices (non vérifié hors période de grâce) */
  access_scope?: "full" | "exercises_only";
  created_at?: string | null;
  updated_at?: string | null;
  grade_level?: number | null;
  grade_system?: "suisse" | "unifie" | null;
  /** Tranche d'âge pédagogique (système unifié) ; absent / null si Harmos */
  age_group?: "6-8" | "9-11" | "12-14" | "15+" | null;
  learning_style?: string | null;
  preferred_difficulty?: string | null;
  onboarding_completed_at?: string | null;
  learning_goal?: string | null;
  practice_rhythm?: string | null;
  preferred_theme?: string | null;
  accessibility_settings?: Record<string, boolean> | null;
  total_points?: number;
  current_level?: number;
  experience_points?: number;
  /** Bucket de rang public (F43-A3) — préféré. */
  progression_rank?: string;
  /** @deprecated F43-A3 — alias legacy. */
  jedi_rank?: string;
  /** Structure stable pour le widget « Niveau actuel » (hors filtre temporel dashboard) */
  gamification_level?: GamificationLevelIndicator;
  language_preference?: string | null;
  timezone?: string | null;
  is_public_profile?: boolean;
  allow_friend_requests?: boolean;
  show_in_leaderboards?: boolean;
  data_retention_consent?: boolean;
  marketing_consent?: boolean;
}

/**
 * Type Exercise avec tous les champs possibles.
 */
export interface Exercise {
  id: number;
  title: string;
  question: string;
  correct_answer: string;
  choices?: string[] | null;
  explanation?: string | null;
  hint?: string | null;
  exercise_type: string;
  age_group?: string | null;
  difficulty?: string; // Interne uniquement, dérivé de age_group
  /** Tier pédagogique 1–12 (F42), si persisté. */
  difficulty_tier?: number | null;
  tags?: string | null;
  image_url?: string | null;
  audio_url?: string | null;
  is_active?: boolean;
  is_archived?: boolean;
  ai_generated?: boolean;
  view_count?: number;
  created_at?: string;
  updated_at?: string;
  creator_id?: number | null;
  is_open_answer?: boolean;
}

/**
 * Réponse paginée standardisée pour les listes d'exercices.
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}

/**
 * Réponse d'exercices paginée.
 */
export type ExercisesPaginatedResponse = PaginatedResponse<Exercise>;

/**
 * Filtres pour les exercices avec recherche.
 */
export interface ExerciseFiltersWithSearch {
  exercise_type?: string;
  age_group?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

/**
 * Modalité d'interaction (lot IA9) — ne pas déduire un QCM depuis `choices` seul.
 * @see app/services/challenges/challenge_contract_policy.py
 */
export type ChallengeResponseMode =
  | "open_text"
  | "single_choice"
  | "interactive_visual"
  | "interactive_order"
  | "interactive_grid";

/**
 * Type Challenge avec tous les champs possibles.
 */
export interface Challenge {
  id: number;
  title: string;
  description: string;
  question?: string | null;
  solution_explanation?: string | null;
  challenge_type: string;
  age_group: string;
  difficulty?: string | null;
  correct_answer?: string | null;
  choices?: string[] | null;
  /** Fourni par GET détail ; défaut côté client si absent (legacy). */
  response_mode?: ChallengeResponseMode | string | null;
  hints?: string[] | null;
  visual_data?: Record<string, unknown> | null;
  difficulty_rating?: number | null;
  /** Tier pédagogique 1–12 (F42), si persisté. */
  difficulty_tier?: number | null;
  estimated_time_minutes?: number | null;
  success_rate?: number | null;
  image_url?: string | null;
  tags?: string | null;
  is_active?: boolean;
  is_archived?: boolean;
  ai_generated?: boolean;
  view_count?: number;
  created_at?: string;
  updated_at?: string;
  creator_id?: number | null;
}

/**
 * Réponse de défis paginée.
 */
export type ChallengesPaginatedResponse = PaginatedResponse<Challenge>;

/**
 * Défi quotidien (F02).
 */
export interface DailyChallenge {
  id: number;
  date: string;
  challenge_type: "volume_exercises" | "specific_type" | "logic_challenge";
  metadata: Record<string, string>;
  target_count: number;
  completed_count: number;
  status: "pending" | "completed" | "expired";
  bonus_points: number;
}

/**
 * Réponse GET /api/daily-challenges.
 */
export interface DailyChallengesResponse {
  challenges: DailyChallenge[];
}

/**
 * Filtres pour les défis avec recherche.
 */
export interface ChallengeFiltersWithSearch {
  challenge_type?: string;
  age_group?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

/**
 * Réponse d'une tentative de défi.
 */
export interface ChallengeAttemptResponse {
  is_correct: boolean;
  message?: string;
  correct_answer?: string;
  explanation?: string;
  new_badges?: Array<{
    id: number;
    name: string;
    /** Clé publique préférée (F43-A4) — même valeur que `star_wars_title`. */
    thematic_title?: string | null;
    /** @deprecated F43-A4 — alias legacy. */
    star_wars_title?: string | null;
  }>;
  points_earned?: number;
  progress_notification?: { name: string; remaining: number };
}

/** Segment de répartition (GET /api/challenges/stats). */
export interface ChallengeCatalogStatBucket {
  count: number;
  percentage: number;
}

/**
 * Réponse GET /api/challenges/stats — répartition du catalogue de défis actifs.
 */
export interface ChallengesStats {
  total: number;
  total_archived: number;
  by_type: Record<string, ChallengeCatalogStatBucket>;
  by_difficulty: Record<string, ChallengeCatalogStatBucket>;
  by_age_group: Record<string, ChallengeCatalogStatBucket>;
}

/**
 * Type Badge (achievement) avec tous les champs possibles.
 */
export interface Badge {
  id: number;
  code: string;
  name?: string | null;
  description?: string | null;
  criteria_text?: string | null;
  category?: string | null;
  difficulty?: string | null;
  points_reward?: number | null;
  /** Libellé narratif optionnel (F43-A4) — préféré pour l’affichage. */
  thematic_title?: string | null;
  /** @deprecated F43-A4 — même valeur que `thematic_title`. */
  star_wars_title?: string | null;
  icon_url?: string | null;
  is_secret?: boolean;
  is_active?: boolean;
  created_at?: string | null;
}

/**
 * Type UserBadge (badge obtenu par un utilisateur).
 */
export interface UserBadge extends Badge {
  earned_at?: string | null;
  points?: number;
}

/**
 * Réponse API pour les badges utilisateur.
 */
export interface UserBadgesResponse {
  success: boolean;
  data: {
    earned_badges: UserBadge[];
    user_stats?: {
      total_points: number;
      current_level?: number;
      experience_points?: number;
      progression_rank?: string;
      /** @deprecated F43-A3 — alias legacy. */
      jedi_rank?: string;
      pinned_badge_ids?: number[];
    };
  };
}

/**
 * Statistiques de gamification.
 */
export interface GamificationStats {
  total_badges: number;
  total_points: number;
  progression_rank?: string;
  /** @deprecated F43-A3 — alias legacy. */
  jedi_rank?: string;
  badges_by_category?: Record<string, number>;
  badges_by_difficulty?: Record<string, number>;
  performance?: {
    total_attempts: number;
    correct_attempts: number;
    success_rate: number;
    avg_time_spent: number;
  };
  badges_summary?: {
    by_category: Record<string, number>;
    by_difficulty?: Record<string, number>;
  };
}
