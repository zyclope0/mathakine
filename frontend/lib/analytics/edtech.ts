/**
 * Instrumentation EdTech — suivi CTR Quick Start, temps vers 1er attempt, conversion exercice/défi.
 * Léger : CustomEvent + envoi API fire-and-forget. Pas de blocage UX.
 *
 * Logique du temps vers 1er attempt :
 * - Référence = clic Quick Start (pas la vue dashboard) pour éviter décalages horaires et données aberrantes.
 * - On stocke le timestamp au clic, on calcule au submit. Temps = submit - clic.
 * - Plafond 24h : si > 24h entre clic et submit, on envoie null (session trop ancienne).
 */

import {
  getSessionString,
  isSessionStorageAvailable,
  readSessionJson,
  removeSessionKey,
  setSessionString,
  STORAGE_KEYS,
  writeSessionJson,
} from "@/lib/storage";

const EVENT_NAME = "mathakine-edtech";
const MAX_TIME_MS = 24 * 60 * 60 * 1000; // 24h

interface InterleavedSessionPayload {
  analytics?: { firstAttemptTracked?: boolean };
  plan?: string[];
  completedCount?: number;
  length?: number;
}

function asInterleavedSessionPayload(raw: unknown): InterleavedSessionPayload | null {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) {
    return null;
  }
  return raw as InterleavedSessionPayload;
}

/**
 * Envoie l'événement au backend (fire-and-forget).
 */
function sendToBackend(event: string, payload: Record<string, unknown>): void {
  if (!isSessionStorageAvailable()) return;
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
  if (!isSessionStorageAvailable()) return;
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
  if (!isSessionStorageAvailable()) return;
  setSessionString(STORAGE_KEYS.edtechDashboardViewedAt, String(Date.now()));
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
  if (isSessionStorageAvailable()) {
    setSessionString(STORAGE_KEYS.edtechQuickStartClickedAt, String(Date.now()));
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
  if (type === "interleaved" && isSessionStorageAvailable()) {
    const data = asInterleavedSessionPayload(
      readSessionJson(STORAGE_KEYS.edtechInterleavedSession)
    );
    if (data?.analytics?.firstAttemptTracked) {
      return;
    }
  }

  let timeToFirstAttemptMs: number | null = null;
  if (isSessionStorageAvailable()) {
    const stored = getSessionString(STORAGE_KEYS.edtechQuickStartClickedAt);
    if (stored) {
      const clickedAt = parseInt(stored, 10);
      if (!isNaN(clickedAt)) {
        const ms = Date.now() - clickedAt;
        if (ms >= 0 && ms <= MAX_TIME_MS) {
          timeToFirstAttemptMs = ms;
        }
      }
      removeSessionKey(STORAGE_KEYS.edtechQuickStartClickedAt);
    }
  }

  const payload: FirstAttemptPayload = { type, targetId, timeToFirstAttemptMs };
  const p: Record<string, unknown> = { ...payload };
  dispatchEvent("first_attempt", p);
  sendToBackend("first_attempt", p);

  if (type === "interleaved" && isSessionStorageAvailable()) {
    const data = asInterleavedSessionPayload(
      readSessionJson(STORAGE_KEYS.edtechInterleavedSession)
    );
    if (data) {
      writeSessionJson(STORAGE_KEYS.edtechInterleavedSession, {
        ...data,
        analytics: { ...data.analytics, firstAttemptTracked: true },
      });
    }
  }
}
