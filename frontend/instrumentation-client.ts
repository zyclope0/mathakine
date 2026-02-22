import * as Sentry from "@sentry/nextjs";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
const isEnabled = process.env.NODE_ENV === "production" && !!dsn;
const tracesSampleRate = parseFloat(process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE || "0.1");
// Release pour corrélation erreurs ↔ déploiements (Render: SENTRY_RELEASE, Vercel: auto)
const release = process.env.SENTRY_RELEASE || process.env.NEXT_PUBLIC_SENTRY_RELEASE;

Sentry.init({
  dsn,
  environment: process.env.NODE_ENV,
  release: release || undefined,
  enabled: isEnabled,
  sendDefaultPii: false,
  tunnel: "/monitoring",
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : tracesSampleRate,
  integrations: [
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
