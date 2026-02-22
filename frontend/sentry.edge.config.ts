import * as Sentry from "@sentry/nextjs";

const dsn = process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN;
const tracesSampleRate = parseFloat(
  process.env.SENTRY_TRACES_SAMPLE_RATE || "0.1"
);
const release = process.env.SENTRY_RELEASE;

Sentry.init({
  dsn,
  environment: process.env.NODE_ENV,
  release: release || undefined,
  enabled: process.env.NODE_ENV === "production" && !!dsn,
  sendDefaultPii: false,
  tracesSampleRate,
});
