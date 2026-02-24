/**
 * Instrumentation EdTech — suivi CTR Quick Start, temps vers 1er attempt, conversion exercice/défi.
 * Léger : CustomEvent + envoi API fire-and-forget. Pas de blocage UX.
 */

const KEY_DASHBOARD_VIEWED = "mathakine_dashboard_viewed_at";
const EVENT_NAME = "mathakine-edtech";

function isClient(): boolean {
  return typeof window !== "undefined" && typeof sessionStorage !== "undefined";
}

/**
 * Envoie l'événement au backend (fire-and-forget).
 */
function sendToBackend(event: string, payload: Record<string, unknown>): void {
  if (!isClient()) return;
  import("@/lib/api/client")
    .then(({ api }) => {
      api.post("/api/analytics/event", { event, payload }).catch(() => {});
    })
    .catch(() => {});
}

/**
 * Dispatch CustomEvent pour intégrations externes (GA, Plausible, etc.).
 */
function dispatchEvent(event: string, payload: Record<string, unknown>): void {
  if (!isClient()) return;
  window.dispatchEvent(
    new CustomEvent(EVENT_NAME, {
      detail: { event, payload },
    })
  );
}

/**
 * À appeler quand le bloc Quick Start est affiché (entrée sur le dashboard overview).
 */
export function trackDashboardView(): void {
  if (!isClient()) return;
  try {
    sessionStorage.setItem(KEY_DASHBOARD_VIEWED, String(Date.now()));
  } catch {
    // sessionStorage désactivé, ignorer
  }
}

export interface QuickStartClickPayload {
  type: "exercise" | "challenge";
  guided: boolean;
  targetId?: number;
}

/**
 * À appeler au clic sur un CTA Quick Start (exercice ou défi).
 */
export function trackQuickStartClick(payload: QuickStartClickPayload): void {
  const p: Record<string, unknown> = { ...payload };
  dispatchEvent("quick_start_click", p);
  sendToBackend("quick_start_click", p);
}

export interface FirstAttemptPayload {
  type: "exercise" | "challenge";
  targetId: number;
  timeToFirstAttemptMs: number | null;
}

/**
 * À appeler lors de la première soumission (exercice ou défi) après une visite du dashboard.
 * Calcule time_to_first_attempt si timestamp dashboard disponible.
 */
export function trackFirstAttempt(type: "exercise" | "challenge", targetId: number): void {
  let timeToFirstAttemptMs: number | null = null;
  if (isClient()) {
    try {
      const stored = sessionStorage.getItem(KEY_DASHBOARD_VIEWED);
      if (stored) {
        const viewedAt = parseInt(stored, 10);
        if (!isNaN(viewedAt)) {
          timeToFirstAttemptMs = Date.now() - viewedAt;
        }
        sessionStorage.removeItem(KEY_DASHBOARD_VIEWED);
      }
    } catch {
      // ignorer
    }
  }

  const payload: FirstAttemptPayload = { type, targetId, timeToFirstAttemptMs };
  const p: Record<string, unknown> = { ...payload };
  dispatchEvent("first_attempt", p);
  sendToBackend("first_attempt", p);
}
