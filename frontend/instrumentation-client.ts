import * as Sentry from "@sentry/nextjs";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
const isEnabled = process.env.NODE_ENV === "production" && !!dsn;
const tracesSampleRate = parseFloat(process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE || "0.1");
const replaysSessionSampleRate = parseFloat(
  process.env.NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE || "0.1"
);
const replaysOnErrorSampleRate = parseFloat(
  process.env.NEXT_PUBLIC_SENTRY_REPLAYS_ON_ERROR_SAMPLE_RATE || "1.0"
);
// Release pour corrélation erreurs ↔ déploiements (Render: SENTRY_RELEASE, Vercel: auto)
const release =
  process.env.SENTRY_RELEASE ||
  process.env.NEXT_PUBLIC_SENTRY_RELEASE ||
  process.env.RENDER_GIT_COMMIT;

// Optional Sentry widgets that inject inline script/style are not enabled; if added later,
// read the internal `x-nonce` request header via `headers()` from a nested async layout (see `middlewareCsp.ts`).
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
  replaysSessionSampleRate,
  replaysOnErrorSampleRate,
});

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
