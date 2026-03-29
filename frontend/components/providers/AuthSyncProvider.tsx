"use client";

import { useEffect, useRef } from "react";
import {
  getBackendUrlOrEmpty,
  refreshSessionViaHttpOnlyCookie,
} from "@/lib/auth/auth-session-sync";

/**
 * Au chargement en prod cross-domain : tente un refresh via cookie HttpOnly.
 * Si session valide, sync access_token sur le domaine frontend pour les routes Next.js.
 * refresh_token jamais lu par JS — cookie envoyé automatiquement avec credentials.
 */
export function AuthSyncProvider({ children }: { children: React.ReactNode }) {
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current || typeof window === "undefined") return;
    if (process.env.NODE_ENV !== "production" || !getBackendUrlOrEmpty()) return;

    hasRun.current = true;

    const apiBase = getBackendUrlOrEmpty();
    void refreshSessionViaHttpOnlyCookie({
      syncCsrfFromResponse: false,
      apiBaseOverride: apiBase,
    }).catch(() => {});
  }, []);

  return <>{children}</>;
}
