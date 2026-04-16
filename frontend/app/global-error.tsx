"use client";

import * as Sentry from "@sentry/nextjs";
import { createTranslator } from "next-intl";
import { useEffect, useState } from "react";

import enMessages from "@/messages/en.json";
import frMessages from "@/messages/fr.json";

type UiLocale = "fr" | "en";

function readPersistedLocale(): UiLocale {
  if (typeof window === "undefined") return "fr";
  try {
    const raw = window.localStorage.getItem("locale-preferences");
    if (!raw) return "fr";
    const parsed = JSON.parse(raw) as { state?: { locale?: string } };
    return parsed.state?.locale === "en" ? "en" : "fr";
  } catch {
    /* swallowed: localStorage unavailable or invalid JSON, "fr" default used */
    return "fr";
  }
}

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const [locale] = useState<UiLocale>(() => readPersistedLocale());
  const messages = locale === "en" ? enMessages : frMessages;
  const t = createTranslator({ locale, messages, namespace: "errors" });

  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = locale;
    }
  }, [locale]);

  return (
    <html lang={locale}>
      <body style={{ fontFamily: "system-ui, sans-serif", padding: "2rem" }}>
        <h1>{t("generic")}</h1>
        <p>{t("global.description")}</p>
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
          {t("500.retry")}
        </button>
      </body>
    </html>
  );
}
