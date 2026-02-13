"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

/**
 * Init Sentry côté client (fallback si instrumentation-client ne charge pas).
 * Garantit que Sentry est initialisé dès le premier render.
 */
export function SentryInit() {
  useEffect(() => {
    const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
    const isEnabled =
      process.env.NODE_ENV === "production" && !!dsn;
    const debugMode = process.env.NEXT_PUBLIC_SENTRY_DEBUG === "1";

    if (debugMode && typeof window !== "undefined") {
      console.log("[Sentry Init] Client:", {
        enabled: isEnabled,
        dsnPresent: !!dsn,
        env: process.env.NODE_ENV,
        tunnel: "/monitoring",
      });
    }

    // Init uniquement si pas déjà fait (Sentry.init est idempotent)
    if (dsn && isEnabled) {
      Sentry.init({
        dsn,
        environment: process.env.NODE_ENV,
        enabled: true,
        debug: debugMode,
        tunnel: "/monitoring",
        tracesSampleRate: 0.1,
        replaysSessionSampleRate: 0.1,
        replaysOnErrorSampleRate: 1.0,
        integrations: [
          Sentry.replayIntegration({
            maskAllText: true,
            blockAllMedia: true,
          }),
        ],
      });
    }
  }, []);

  return null;
}
