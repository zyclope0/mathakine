/**
 * Résolution unique de l’URL du backend pour les routes API Next.js qui proxy vers Python.
 *
 * Priorité : `NEXT_PUBLIC_API_BASE_URL` → `NEXT_PUBLIC_API_URL` → en développement uniquement
 * `http://localhost:10000`.
 *
 * En production : erreur explicite si l’URL est :
 *   - absente / vide (après trim)
 *   - non parsable par `new URL()`
 *   - protocole non http/https
 *   - adresse loopback (localhost, 127.0.0.1, ::1)
 */
function trimOrEmpty(value: string | undefined): string {
  return String(value ?? "").trim();
}

const LOOPBACK_HOSTS = new Set(["localhost", "127.0.0.1", "::1", "[::1]"]);

export function getBackendUrl(): string {
  const base = trimOrEmpty(process.env.NEXT_PUBLIC_API_BASE_URL);
  const legacy = trimOrEmpty(process.env.NEXT_PUBLIC_API_URL);
  const isDev = process.env.NODE_ENV === "development";

  let url = base || legacy;
  if (!url && isDev) {
    url = "http://localhost:10000";
  }

  if (process.env.NODE_ENV === "production") {
    if (!url) {
      throw new Error(
        "NEXT_PUBLIC_API_BASE_URL (ou NEXT_PUBLIC_API_URL) doit être défini en production."
      );
    }

    let parsed: URL;
    try {
      parsed = new URL(url);
    } catch {
      throw new Error(
        `NEXT_PUBLIC_API_BASE_URL invalide en production : "${url}" n’est pas une URL absolue valide.`
      );
    }

    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      throw new Error(
        `NEXT_PUBLIC_API_BASE_URL invalide en production : le protocole doit être http ou https (reçu "${parsed.protocol}").`
      );
    }

    if (LOOPBACK_HOSTS.has(parsed.hostname)) {
      throw new Error(
        `NEXT_PUBLIC_API_BASE_URL ne peut pas pointer vers une adresse locale en production : "${url}".`
      );
    }
  }

  return url;
}
