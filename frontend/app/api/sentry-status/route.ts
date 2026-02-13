import * as Sentry from "@sentry/nextjs";
import { NextResponse } from "next/server";

/**
 * Diagnostic Sentry - vérifier si les variables sont présentes au build.
 * Envoie une métrique de test (au cas où Sentry Metrics fonctionne).
 * GET /api/sentry-status
 */
export async function GET() {
  const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
  if (dsn && process.env.NODE_ENV === "production") {
    Sentry.metrics.count("test_metric", 1);
    await Sentry.flush(2000);
  }
  return NextResponse.json({
    dsnPresent: !!dsn,
    nodeEnv: process.env.NODE_ENV,
    tunnelRoute: "/monitoring",
    metricsSent: !!dsn && process.env.NODE_ENV === "production",
  });
}
