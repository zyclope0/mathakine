/**
 * F04-P5 — réponse GET /api/users/me/reviews/next (typage + parsing défensif).
 */

import {
  parseSpacedRepetitionUserSummary,
  type SpacedRepetitionUserSummary,
} from "@/lib/validation/dashboard";

export type SpacedRepetitionDueStatus = "overdue" | "due_today";

export interface ReviewSafeExercisePayload {
  id: number;
  title: string;
  question: string;
  exercise_type: string;
  difficulty: string;
  age_group: string;
  difficulty_tier: number | null;
  choices: string[] | null;
  image_url: string | null;
  audio_url: string | null;
}

export interface NextReviewPayload {
  review_item_id: number;
  exercise_id: number;
  due_status: SpacedRepetitionDueStatus;
  next_review_date: string;
  exercise: ReviewSafeExercisePayload;
}

export interface NextReviewApiResponse {
  has_due_review: boolean;
  summary: SpacedRepetitionUserSummary;
  next_review: NextReviewPayload | null;
}

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

function parseString(v: unknown): string | null {
  return typeof v === "string" ? v : null;
}

function parseFiniteInt(v: unknown): number | null {
  if (typeof v !== "number" || !Number.isFinite(v)) {
    return null;
  }
  const n = Math.trunc(v);
  return n;
}

function parseDifficultyTier(v: unknown): number | null {
  if (v === null || v === undefined) {
    return null;
  }
  if (typeof v !== "number" || !Number.isFinite(v)) {
    return null;
  }
  return Math.trunc(v);
}

function parseChoices(v: unknown): string[] | null {
  if (v === null || v === undefined) {
    return null;
  }
  if (!Array.isArray(v)) {
    return null;
  }
  const choices: string[] = [];
  for (const item of v) {
    if (typeof item !== "string") {
      return null;
    }
    choices.push(item);
  }
  return choices;
}

function parseReviewSafeExercise(data: unknown): ReviewSafeExercisePayload | null {
  if (data === null || data === undefined || typeof data !== "object" || Array.isArray(data)) {
    return null;
  }
  const o = data as Record<string, unknown>;
  if ("correct_answer" in o || "explanation" in o || "hint" in o) {
    return null;
  }
  const id = parseFiniteInt(o.id);
  const title = parseString(o.title);
  const question = parseString(o.question);
  const exercise_type = parseString(o.exercise_type);
  const difficulty = parseString(o.difficulty);
  const age_group = parseString(o.age_group);
  if (
    id === null ||
    title === null ||
    question === null ||
    exercise_type === null ||
    difficulty === null ||
    age_group === null
  ) {
    return null;
  }
  const rawImg = o.image_url;
  const rawAudio = o.audio_url;
  const image_url = rawImg == null ? null : parseString(rawImg);
  const audio_url = rawAudio == null ? null : parseString(rawAudio);
  if (rawImg != null && image_url === null) {
    return null;
  }
  if (rawAudio != null && audio_url === null) {
    return null;
  }
  return {
    id,
    title,
    question,
    exercise_type,
    difficulty,
    age_group,
    difficulty_tier: parseDifficultyTier(o.difficulty_tier),
    choices: parseChoices(o.choices),
    image_url,
    audio_url,
  };
}

function parseNextReviewItem(data: unknown): NextReviewPayload | null {
  if (data === null || data === undefined || typeof data !== "object" || Array.isArray(data)) {
    return null;
  }
  const o = data as Record<string, unknown>;
  const review_item_id = parseFiniteInt(o.review_item_id);
  const exercise_id = parseFiniteInt(o.exercise_id);
  const due = o.due_status;
  const next_review_date = parseString(o.next_review_date);
  if (
    review_item_id === null ||
    exercise_id === null ||
    next_review_date === null ||
    !ISO_DATE_RE.test(next_review_date)
  ) {
    return null;
  }
  if (due !== "overdue" && due !== "due_today") {
    return null;
  }
  const exercise = parseReviewSafeExercise(o.exercise);
  if (exercise === null) {
    return null;
  }
  return {
    review_item_id,
    exercise_id,
    due_status: due,
    next_review_date,
    exercise,
  };
}

/**
 * Retourne null si la charge utile est invalide ou incohérente.
 */
export function parseNextReviewApiResponse(data: unknown): NextReviewApiResponse | null {
  if (data === null || data === undefined || typeof data !== "object" || Array.isArray(data)) {
    return null;
  }
  const o = data as Record<string, unknown>;
  if (typeof o.has_due_review !== "boolean") {
    return null;
  }
  const summary = parseSpacedRepetitionUserSummary(o.summary);
  const rawNext = o.next_review;
  if (o.has_due_review) {
    const next = parseNextReviewItem(rawNext);
    if (next === null) {
      return null;
    }
    return { has_due_review: true, summary, next_review: next };
  }
  if (rawNext !== null && rawNext !== undefined) {
    return null;
  }
  return { has_due_review: false, summary, next_review: null };
}
