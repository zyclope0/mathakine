import { STORAGE_KEYS } from "@/lib/storage";

export const INTERLEAVED_STORAGE_KEY = STORAGE_KEYS.edtechInterleavedSession;

export type SessionMode = "interleaved" | "spaced-review" | null;

export function readSessionMode(searchParams: URLSearchParams | null): SessionMode {
  const v = searchParams?.get("session");
  if (v === "interleaved") {
    return "interleaved";
  }
  if (v === "spaced-review") {
    return "spaced-review";
  }
  return null;
}

export interface InterleavedSessionStored {
  plan: string[];
  completedCount: number;
  length: number;
  analytics?: { firstAttemptTracked?: boolean };
}

/** Best-effort parse of sessionStorage payload (same rules as legacy inline JSON.parse). */
export function parseInterleavedSessionFromStorage(raw: string): InterleavedSessionStored | null {
  try {
    const parsed = JSON.parse(raw) as {
      plan?: string[];
      completedCount?: number;
      length?: number;
      analytics?: { firstAttemptTracked?: boolean };
    };
    if (!parsed.plan || !Array.isArray(parsed.plan)) {
      return null;
    }
    return {
      plan: parsed.plan,
      completedCount: parsed.completedCount ?? 0,
      length: parsed.length ?? parsed.plan.length,
      ...(parsed.analytics && { analytics: parsed.analytics }),
    };
  } catch {
    return null;
  }
}
