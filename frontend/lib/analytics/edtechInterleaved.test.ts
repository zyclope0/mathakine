/**
 * Tests Lot 1 — Analytics interleaved : 1 seul first_attempt par session.
 */
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { trackFirstAttempt } from "./edtech";

const KEY_INTERLEAVED = "interleaved_session";

describe("edtech trackFirstAttempt interleaved", () => {
  let events: Array<{ event: string; payload: unknown }>;
  let handler: (e: Event) => void;

  beforeEach(() => {
    events = [];
    handler = (e: Event) => {
      const ce = e as CustomEvent;
      const detail = ce.detail as { event?: string; payload?: unknown };
      if (detail?.event) events.push({ event: detail.event, payload: detail.payload });
    };
    window.addEventListener("mathakine-edtech", handler);
  });

  afterEach(() => {
    window.removeEventListener("mathakine-edtech", handler);
    sessionStorage.removeItem(KEY_INTERLEAVED);
    sessionStorage.removeItem("mathakine_quick_start_clicked_at");
  });

  it("émet first_attempt au premier submit interleaved, pas au second", () => {
    sessionStorage.setItem(
      KEY_INTERLEAVED,
      JSON.stringify({
        plan: ["addition", "multiplication"],
        completedCount: 0,
        length: 2,
        analytics: { firstAttemptTracked: false },
      })
    );

    trackFirstAttempt("interleaved", 101);
    expect(events).toHaveLength(1);
    expect(events[0]?.event).toBe("first_attempt");
    expect((events[0]?.payload as { type?: string })?.type).toBe("interleaved");

    const parsed = JSON.parse(sessionStorage.getItem(KEY_INTERLEAVED) ?? "{}");
    expect(parsed.analytics?.firstAttemptTracked).toBe(true);

    trackFirstAttempt("interleaved", 102);
    expect(events).toHaveLength(1);
  });

  it("exercise et challenge émettent à chaque submit (pas de régression)", () => {
    trackFirstAttempt("exercise", 101);
    trackFirstAttempt("exercise", 102);
    expect(events).toHaveLength(2);
    expect(events[0]?.event).toBe("first_attempt");
    expect(events[1]?.event).toBe("first_attempt");
  });

  it("flux réel: submit -> next exercise -> rewrite storage -> second submit n'émet pas", () => {
    sessionStorage.setItem(
      KEY_INTERLEAVED,
      JSON.stringify({
        plan: ["addition", "division"],
        completedCount: 0,
        length: 2,
        analytics: { firstAttemptTracked: false },
      })
    );

    trackFirstAttempt("interleaved", 101);
    expect(events).toHaveLength(1);

    const staleSessionData = {
      plan: ["addition", "division"],
      completedCount: 0,
      length: 2,
      analytics: { firstAttemptTracked: false },
    };

    let analytics = staleSessionData.analytics ?? { firstAttemptTracked: false };
    try {
      const currentRaw = sessionStorage.getItem(KEY_INTERLEAVED);
      if (currentRaw) {
        const current = JSON.parse(currentRaw) as {
          analytics?: { firstAttemptTracked?: boolean };
        };
        if (current.analytics?.firstAttemptTracked) {
          analytics = { ...analytics, firstAttemptTracked: true };
        }
      }
    } catch {
      // ignorer
    }
    sessionStorage.setItem(
      KEY_INTERLEAVED,
      JSON.stringify({
        plan: staleSessionData.plan,
        completedCount: 1,
        length: staleSessionData.length,
        analytics,
      })
    );

    trackFirstAttempt("interleaved", 102);
    expect(events).toHaveLength(1);
  });
});
