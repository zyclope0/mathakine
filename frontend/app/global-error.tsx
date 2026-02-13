"use client";

import * as Sentry from "@sentry/nextjs";
import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html lang="fr">
      <body style={{ fontFamily: "system-ui, sans-serif", padding: "2rem" }}>
        <h1>Une erreur s&apos;est produite</h1>
        <p>L&apos;application a rencontré un problème. Veuillez réessayer.</p>
        <button
          type="button"
          onClick={reset}
          style={{
            padding: "0.5rem 1rem",
            cursor: "pointer",
            background: "#0369a1",
            color: "white",
            border: "none",
            borderRadius: "4px",
          }}
        >
          Réessayer
        </button>
      </body>
    </html>
  );
}
