"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, Home, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  const t = useTranslations("errors.500");

  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.error("Application error:", error);
    }
    if (process.env.NEXT_PUBLIC_SENTRY_DEBUG === "1") {
      console.log("[Sentry] captureException appelé:", error.message);
    }
    Sentry.captureException(error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md border-destructive">
        <CardHeader>
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-destructive" aria-hidden="true" />
            <CardTitle className="text-destructive">{t("title")}</CardTitle>
          </div>
          <CardDescription>{t("message")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {process.env.NODE_ENV === "development" && error.message && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm">
              <p className="font-semibold text-destructive">Détails (dev uniquement):</p>
              <p className="mt-1 text-muted-foreground">{error.message}</p>
              {error.digest && (
                <p className="mt-1 text-xs text-muted-foreground">Digest: {error.digest}</p>
              )}
            </div>
          )}

          <div className="flex flex-col gap-2 sm:flex-row">
            <Button onClick={reset} variant="default" className="flex-1">
              <RefreshCw className="mr-2 h-4 w-4" />
              {t("retry")}
            </Button>
            <Button asChild variant="outline" className="flex-1">
              <Link href="/">
                <Home className="mr-2 h-4 w-4" />
                {t("backHome")}
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
