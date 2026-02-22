"use client";

import { useState, useCallback } from "react";
import * as Sentry from "@sentry/nextjs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageLayout } from "@/components/layout";
import { CheckCircle2, AlertCircle, Loader2, Send, Zap } from "lucide-react";

type StepStatus = "idle" | "pending" | "done" | "error";

/**
 * Page de test Sentry — vérifier que les erreurs remontent en production.
 * Accessible à /test-sentry
 */
export default function TestSentryPage() {
  const [status, setStatus] = useState<{ dsnPresent?: boolean; nodeEnv?: string } | null>(null);
  const [statusLoading, setStatusLoading] = useState(false);
  const [captureStep, setCaptureStep] = useState<StepStatus>("idle");
  const [lastEventId, setLastEventId] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    try {
      const res = await fetch("/api/sentry-status");
      const data = await res.json();
      setStatus({ dsnPresent: data.dsnPresent, nodeEnv: data.nodeEnv });
    } finally {
      setStatusLoading(false);
    }
  }, []);

  const handleCaptureException = useCallback(async () => {
    setCaptureStep("pending");
    const err = new Error(`Test Sentry prod — ${new Date().toISOString()}`);
    try {
      const eventId = Sentry.captureException(err);
      setLastEventId(eventId ?? null);
      await Sentry.flush(2000);
      setCaptureStep("done");
    } catch (e) {
      setCaptureStep("error");
      console.error("Sentry.captureException failed:", e);
    }
  }, []);

  const handleThrowError = useCallback(() => {
    throw new Error(`Test Sentry throw — ${new Date().toISOString()}`);
  }, []);

  return (
    <PageLayout>
      <div className="mx-auto max-w-2xl space-y-6 py-8">
        <h1 className="text-2xl font-bold">Test Sentry</h1>
        <p className="text-muted-foreground">
          Vérifie que les erreurs remontent correctement vers Sentry en production.
        </p>

        {/* Statut API */}
        <Card>
          <CardHeader>
            <CardTitle>1. Configuration</CardTitle>
            <CardDescription>
              Vérifier que le DSN est chargé au build (GET /api/sentry-status)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" onClick={fetchStatus} disabled={statusLoading}>
              {statusLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Récupérer le statut
            </Button>
            {status !== null && (
              <div className="flex items-center gap-2 rounded-md bg-muted/50 p-3">
                {status.dsnPresent ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-destructive" />
                )}
                <span>
                  DSN présent : <strong>{status.dsnPresent ? "Oui" : "Non"}</strong> — NODE_ENV :{" "}
                  <strong>{status.nodeEnv ?? "—"}</strong>
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Envoyer une erreur (sans crash) */}
        <Card>
          <CardHeader>
            <CardTitle>2. Envoyer une erreur test</CardTitle>
            <CardDescription>
              captureException envoie l&apos;erreur à Sentry sans faire planter la page
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <Button onClick={handleCaptureException} disabled={captureStep === "pending"}>
                {captureStep === "pending" ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                Envoyer une erreur à Sentry
              </Button>
            </div>
            <div className="flex items-center gap-2 rounded-md bg-muted/50 p-3">
              {captureStep === "idle" && (
                <span className="text-muted-foreground">Statut : en attente de clic</span>
              )}
              {captureStep === "pending" && (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Envoi en cours…</span>
                </>
              )}
              {captureStep === "done" && (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span>
                    Envoyé. Vérifie ton dashboard Sentry (Issues) dans ~10 secondes.
                    {lastEventId && <span className="ml-2 text-xs">Event ID: {lastEventId}</span>}
                  </span>
                </>
              )}
              {captureStep === "error" && (
                <>
                  <AlertCircle className="h-5 w-5 text-destructive" />
                  <span>Erreur lors de l&apos;envoi (voir console)</span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Lancer une erreur (crash) */}
        <Card>
          <CardHeader>
            <CardTitle>3. Lancer une erreur (crash)</CardTitle>
            <CardDescription>
              Throws déclenche l&apos;error boundary — Sentry doit capturer aussi
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="destructive" onClick={handleThrowError}>
              <Zap className="mr-2 h-4 w-4" />
              Lancer une erreur (crash)
            </Button>
            <p className="mt-2 text-sm text-muted-foreground">
              La page affichera l&apos;error boundary. Vérifie Sentry pour l&apos;erreur.
            </p>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  );
}
