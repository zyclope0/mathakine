import * as Sentry from "@sentry/nextjs";
import { NextResponse } from "next/server";

/**
 * Diagnostic Sentry - vérifier si les variables sont présentes au build.
 * Envoie une métrique de test (au cas où Sentry Metrics fonctionne).
 * GET /api/sentry-status
 */
export async function GET() {
  const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
  const release =
    process.env.SENTRY_RELEASE ||
    process.env.NEXT_PUBLIC_SENTRY_RELEASE ||
    process.env.RENDER_GIT_COMMIT ||
    null;
  const tracesSampleRate = process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE || "0.1";
  const replaysSessionSampleRate =
    process.env.NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE || "0.1";
  const replaysOnErrorSampleRate =
    process.env.NEXT_PUBLIC_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE || "1.0";
  if (dsn && process.env.NODE_ENV === "production") {
    Sentry.metrics.count("test_metric", 1);
    await Sentry.flush(2000);
  }
  return NextResponse.json({
    dsnPresent: !!dsn,
    nodeEnv: process.env.NODE_ENV,
    release,
    tracesSampleRate,
    replaysSessionSampleRate,
    replaysOnErrorSampleRate,
    tunnelRoute: "/monitoring",
    metricsSent: !!dsn && process.env.NODE_ENV === "production",
  });
}
