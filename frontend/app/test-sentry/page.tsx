"use client";

import { useState, useEffect } from "react";
import * as Sentry from "@sentry/nextjs";
import { PageLayout, PageHeader, PageSection } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Feedback } from "@/components/ui/feedback";
import { CheckCircle2, XCircle, Loader2, Bug, Send } from "lucide-react";

interface SentryStatus {
  dsnPresent: boolean;
  nodeEnv: string;
  tunnelRoute: string;
  metricsSent: boolean;
}

/**
 * Page de test Sentry — envoi d'une erreur contrôlée et suivi.
 * À retirer après validation en prod.
 */
export default function TestSentryPage() {
  const [status, setStatus] = useState<SentryStatus | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [step, setStep] = useState<string | null>(null);
  const [result, setResult] = useState<"idle" | "sending" | "sent" | "error">("idle");

  useEffect(() => {
    fetch("/api/sentry-status")
      .then((r) => r.json())
      .then(setStatus)
      .catch((err) => setStatusError(err.message));
  }, []);

  const handleSendTestError = async () => {
    setResult("sending");
    setStep("1. Capture de l'erreur...");

    const testError = new Error(
      `[Test Sentry] ${new Date().toISOString()} — Bouton de test manuel`
    );
    testError.name = "TestSentryManual";

    try {
      Sentry.captureException(testError);
      setStep("2. Envoi à Sentry (flush)...");
      await Sentry.flush(3000);
      setStep("3. Terminé.");
      setResult("sent");
    } catch (err) {
      setStep(`Erreur: ${err instanceof Error ? err.message : String(err)}`);
      setResult("error");
    }
  };

  const handleThrowError = () => {
    setStep("Lancement d'une erreur non gérée...");
    throw new Error("[Test Sentry] Erreur throw — test error boundary");
  };

  return (
    <PageLayout maxWidth="lg">
      <PageHeader
        title="Test Sentry"
        description="Vérifier que les erreurs sont bien envoyées au monitoring"
      />

      <PageSection>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bug className="h-5 w-5" />
              Statut Sentry
            </CardTitle>
            <CardDescription>
              État au build / runtime — GET /api/sentry-status
            </CardDescription>
          </CardHeader>
          <CardContent>
            {statusError && (
              <Feedback type="error" message={`Impossible de récupérer le statut: ${statusError}`} />
            )}
            {status && (
              <pre className="rounded-lg bg-muted p-4 text-sm overflow-x-auto">
                {JSON.stringify(status, null, 2)}
              </pre>
            )}
            {status?.dsnPresent === false && (
              <Feedback
                type="error"
                message="DSN absent — NEXT_PUBLIC_SENTRY_DSN non défini au build. Rebuilder le frontend."
                className="mt-4"
              />
            )}
            {status?.dsnPresent && (
              <p className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                Sentry configuré — tunnel: {status.tunnelRoute}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Send className="h-5 w-5" />
              Envoyer une erreur test
            </CardTitle>
            <CardDescription>
              captureException + flush — l&apos;erreur doit apparaître dans Sentry (Issues) en ~10 s
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={handleSendTestError}
              disabled={result === "sending" || !status?.dsnPresent}
            >
              {result === "sending" ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Envoi en cours...
                </>
              ) : (
                "Envoyer une erreur test"
              )}
            </Button>

            {step && (
              <p className="text-sm text-muted-foreground font-mono">{step}</p>
            )}

            {result === "sent" && (
              <Feedback
                type="success"
                message="Erreur envoyée. Vérifie ton dashboard Sentry → Issues (filtre: TestSentryManual ou «Test Sentry»)."
              />
            )}
            {result === "error" && (
              <Feedback type="error" message="Échec de l'envoi — voir console / Network." />
            )}
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Test error boundary (crash)</CardTitle>
            <CardDescription>
              Lance une erreur non gérée — la page affichera l&apos;error boundary et Sentry doit capturer.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              onClick={handleThrowError}
              disabled={!status?.dsnPresent}
            >
              Throw error (test crash)
            </Button>
          </CardContent>
        </Card>
      </PageSection>
    </PageLayout>
  );
}
