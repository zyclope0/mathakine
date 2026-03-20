import type { TimelinePoint } from "@/hooks/useProgressTimeline";

export interface PracticeConsistencyMetrics {
  totalDaysInPeriod: number;
  activeDays: number;
  regularityPercent: number;
  avgAttemptsPerActiveDay: number;
  /** Day with the highest attempt count in the period (not a performance / success metric). */
  mostActiveDay: { date: string; attempts: number } | null;
}

/** ISO date key YYYY-MM-DD from API date string. */
export function normalizeTimelineDateKey(date: string): string {
  return date.slice(0, 10);
}

/** Every calendar day from `from` to `to` (UTC, inclusive), as YYYY-MM-DD. */
export function listUtcDateKeysInclusive(fromIso: string, toIso: string): string[] {
  const from = new Date(fromIso);
  const to = new Date(toIso);
  if (Number.isNaN(from.getTime()) || Number.isNaN(to.getTime())) {
    return [];
  }
  const keys: string[] = [];
  let cur = Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), from.getUTCDate());
  const endTs = Date.UTC(to.getUTCFullYear(), to.getUTCMonth(), to.getUTCDate());
  while (cur <= endTs) {
    keys.push(new Date(cur).toISOString().slice(0, 10));
    cur += 86400000;
  }
  return keys;
}

/** One boolean per calendar day in range: true if at least one attempt that day. */
export function buildDailyPresenceFlags(
  fromIso: string,
  toIso: string,
  points: Pick<TimelinePoint, "date" | "attempts">[]
): boolean[] {
  const attemptByKey = new Map<string, number>();
  for (const p of points) {
    const k = normalizeTimelineDateKey(p.date);
    attemptByKey.set(k, (attemptByKey.get(k) ?? 0) + p.attempts);
  }
  return listUtcDateKeysInclusive(fromIso, toIso).map((k) => (attemptByKey.get(k) ?? 0) > 0);
}

export function computePracticeConsistency(
  fromIso: string,
  toIso: string,
  points: TimelinePoint[],
  totalAttempts: number
): PracticeConsistencyMetrics {
  const flags = buildDailyPresenceFlags(fromIso, toIso, points);
  const totalDaysInPeriod = flags.length;
  const activeDays = flags.filter(Boolean).length;

  const regularityPercent =
    totalDaysInPeriod > 0 ? Math.min(100, Math.round((activeDays / totalDaysInPeriod) * 100)) : 0;

  const avgAttemptsPerActiveDay =
    activeDays > 0 ? Math.round((totalAttempts / activeDays) * 10) / 10 : 0;

  const byDay = new Map<string, number>();
  for (const p of points) {
    const k = normalizeTimelineDateKey(p.date);
    byDay.set(k, (byDay.get(k) ?? 0) + p.attempts);
  }

  let mostActiveDay: { date: string; attempts: number } | null = null;
  for (const [date, attempts] of byDay) {
    if (attempts <= 0) continue;
    if (!mostActiveDay || attempts > mostActiveDay.attempts) {
      mostActiveDay = { date, attempts };
    }
  }

  return {
    totalDaysInPeriod,
    activeDays,
    regularityPercent,
    avgAttemptsPerActiveDay,
    mostActiveDay,
  };
}
