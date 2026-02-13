"use client";

import { useEffect, useRef } from "react";
import { syncAccessTokenToFrontend } from "@/lib/api/client";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "development" ? "http://localhost:10000" : "");

/**
 * Au chargement en prod cross-domain : tente un refresh via cookie HttpOnly.
 * Si session valide, sync access_token sur le domaine frontend pour les routes Next.js.
 * refresh_token jamais lu par JS — cookie envoyé automatiquement avec credentials.
 */
export function AuthSyncProvider({ children }: { children: React.ReactNode }) {
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current || typeof window === "undefined") return;
    if (process.env.NODE_ENV !== "production" || !API_BASE_URL) return;

    hasRun.current = true;

    fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
      credentials: "include", // Cookie refresh_token (HttpOnly) envoyé automatiquement
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.access_token) {
          syncAccessTokenToFrontend(data.access_token);
        }
      })
      .catch(() => {});
  }, []);

  return <>{children}</>;
}
