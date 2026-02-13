import { NextResponse } from "next/server";

/**
 * Diagnostic Sentry - vérifier si les variables sont présentes au build.
 * GET /api/sentry-status
 */
export async function GET() {
  const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
  return NextResponse.json({
    dsnPresent: !!dsn,
    nodeEnv: process.env.NODE_ENV,
    tunnelRoute: "/monitoring",
  });
}
