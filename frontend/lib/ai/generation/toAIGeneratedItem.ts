import type { AIGeneratedItem } from "@/components/shared/AIGeneratorBase";
import { normalizeCreatedResourceId } from "./normalizeResourceId";

export function exerciseToAIGeneratedItem(
  exercise: { id?: number; title: string; question?: string | null } | null
): AIGeneratedItem | null {
  if (!exercise) return null;
  const persistedId = normalizeCreatedResourceId(exercise.id);
  const base: AIGeneratedItem = {
    ...(persistedId !== undefined ? { id: persistedId } : {}),
    title: exercise.title,
  };
  const q = exercise.question;
  if (q !== undefined && q !== null) {
    return { ...base, subtitle: q };
  }
  return base;
}

export function challengeToAIGeneratedItem(
  challenge: { id?: number; title: string } | null
): AIGeneratedItem | null {
  if (!challenge) return null;
  const persistedId = normalizeCreatedResourceId(challenge.id);
  return {
    ...(persistedId !== undefined ? { id: persistedId } : {}),
    title: challenge.title,
  };
}
