import * as Sentry from "@sentry/nextjs";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
const isEnabled =
  process.env.NODE_ENV === "production" && !!dsn;
const debugMode = process.env.NEXT_PUBLIC_SENTRY_DEBUG === "1";

if (typeof window !== "undefined" && debugMode) {
  console.log("[Sentry] init:", {
    enabled: isEnabled,
    dsnPresent: !!dsn,
    env: process.env.NODE_ENV,
    tunnel: "/monitoring",
  });
}

Sentry.init({
  dsn,
  environment: process.env.NODE_ENV,
  enabled: isEnabled,
  debug: debugMode,
  sendDefaultPii: false,
  tunnel: "/monitoring",
  tracesSampleRate: process.env.NODE_ENV === "development" ? 1.0 : 0.1,
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
