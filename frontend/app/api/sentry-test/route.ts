import * as Sentry from "@sentry/nextjs";
import { NextResponse } from "next/server";

/**
 * Route de test Sentry - déclenche une erreur pour vérifier la remontée.
 * En prod : ajouter ?key=xxx avec SENTRY_TEST_KEY dans les env vars.
 * En dev : pas de clé requise.
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const key = searchParams.get("key");
  const testKey = process.env.SENTRY_TEST_KEY;
  const isDev = process.env.NODE_ENV === "development";

  if (!isDev && (!testKey || key !== testKey)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const testError = new Error("[Sentry Test] Erreur volontaire - serveur");
  Sentry.captureException(testError);
  throw testError;
}
