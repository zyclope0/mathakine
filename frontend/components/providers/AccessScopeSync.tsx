"use client";

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { usePathname, useRouter } from "next/navigation";

const FULL_ACCESS_PATHS = [
  "/dashboard",
  "/challenges",
  "/badges",
  "/leaderboard",
];
const FULL_ACCESS_PREFIX = "/challenge/";

/**
 * Écoute les 403 EMAIL_VERIFICATION_REQUIRED (access_scope limité).
 * Invalide le cache utilisateur et redirige vers /exercises pour éviter
 * l'affichage "Erreur de chargement" sur les pages restreintes.
 */
export function AccessScopeSync() {
  const queryClient = useQueryClient();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (typeof window === "undefined") return;

    const handleAccessScopeLimited = () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
      const isFullAccessPath =
        FULL_ACCESS_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`)) ||
        pathname.startsWith(FULL_ACCESS_PREFIX);
      if (isFullAccessPath) {
        router.replace("/exercises");
      }
    };

    window.addEventListener("access-scope-limited", handleAccessScopeLimited);
    return () => window.removeEventListener("access-scope-limited", handleAccessScopeLimited);
  }, [queryClient, pathname, router]);

  return null;
}
