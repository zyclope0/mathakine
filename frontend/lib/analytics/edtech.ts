/**
 * Instrumentation EdTech — suivi CTR Quick Start, temps vers 1er attempt, conversion exercice/défi.
 * Léger : CustomEvent + envoi API fire-and-forget. Pas de blocage UX.
 *
 * Logique du temps vers 1er attempt :
 * - Référence = clic Quick Start (pas la vue dashboard) pour éviter décalages horaires et données aberrantes.
 * - On stocke le timestamp au clic, on calcule au submit. Temps = submit - clic.
 * - Plafond 24h : si > 24h entre clic et submit, on envoie null (session trop ancienne).
 */

const KEY_QUICK_START_CLICKED = "mathakine_quick_start_clicked_at";
const KEY_DASHBOARD_VIEWED = "mathakine_dashboard_viewed_at"; // conservé pour compat
const KEY_INTERLEAVED_SESSION = "interleaved_session";
const EVENT_NAME = "mathakine-edtech";
const MAX_TIME_MS = 24 * 60 * 60 * 1000; // 24h

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
 * Conservé pour compatibilité ; le temps vers 1er attempt utilise désormais le clic Quick Start.
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
  type: "exercise" | "challenge" | "interleaved";
  guided: boolean;
  targetId?: number;
}

/**
 * À appeler au clic sur un CTA Quick Start (exercice ou défi).
 * Stocke le timestamp pour le calcul du temps vers 1er attempt.
 */
export function trackQuickStartClick(payload: QuickStartClickPayload): void {
  if (isClient()) {
    try {
      sessionStorage.setItem(KEY_QUICK_START_CLICKED, String(Date.now()));
    } catch {
      // ignorer
    }
  }
  const p: Record<string, unknown> = { ...payload };
  dispatchEvent("quick_start_click", p);
  sendToBackend("quick_start_click", p);
}

export interface FirstAttemptPayload {
  type: "exercise" | "challenge" | "interleaved";
  targetId: number;
  timeToFirstAttemptMs: number | null;
}

/**
 * À appeler lors de la soumission (exercice ou défi).
 * Calcule timeToFirstAttemptMs si l'utilisateur est passé par un clic Quick Start.
 * Référence = clic Quick Start (pas dashboard view) pour éviter temps négatifs et décalages.
 *
 * Pour type="interleaved" : n'émet qu'une seule fois par session (premier exercice soumis).
 * Les exercices suivants de la même session n'émettent pas de first_attempt.
 */
export function trackFirstAttempt(
  type: "exercise" | "challenge" | "interleaved",
  targetId: number
): void {
  if (type === "interleaved" && isClient()) {
    try {
      const raw = sessionStorage.getItem(KEY_INTERLEAVED_SESSION);
      if (raw) {
        const data = JSON.parse(raw) as {
          analytics?: { firstAttemptTracked?: boolean };
          plan?: string[];
          completedCount?: number;
          length?: number;
        };
        if (data.analytics?.firstAttemptTracked) {
          return;
        }
      }
    } catch {
      // ignorer
    }
  }

  let timeToFirstAttemptMs: number | null = null;
  if (isClient()) {
    try {
      const stored = sessionStorage.getItem(KEY_QUICK_START_CLICKED);
      if (stored) {
        const clickedAt = parseInt(stored, 10);
        if (!isNaN(clickedAt)) {
          const ms = Date.now() - clickedAt;
          // Valide : >= 0 (pas de temps négatif), <= 24h (session fraîche)
          if (ms >= 0 && ms <= MAX_TIME_MS) {
            timeToFirstAttemptMs = ms;
          }
        }
        sessionStorage.removeItem(KEY_QUICK_START_CLICKED);
      }
    } catch {
      // ignorer
    }
  }

  const payload: FirstAttemptPayload = { type, targetId, timeToFirstAttemptMs };
  const p: Record<string, unknown> = { ...payload };
  dispatchEvent("first_attempt", p);
  sendToBackend("first_attempt", p);

  if (type === "interleaved" && isClient()) {
    try {
      const raw = sessionStorage.getItem(KEY_INTERLEAVED_SESSION);
      if (raw) {
        const data = JSON.parse(raw) as {
          analytics?: { firstAttemptTracked?: boolean };
          plan?: string[];
          completedCount?: number;
          length?: number;
        };
        sessionStorage.setItem(
          KEY_INTERLEAVED_SESSION,
          JSON.stringify({
            ...data,
            analytics: { ...data.analytics, firstAttemptTracked: true },
          })
        );
      }
    } catch {
      // ignorer
    }
  }
}
