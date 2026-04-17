/**
 * Canonical locale cookie — readable by server (`cookies()` in RootLayout) and client.
 * Single string value: `fr` | `en` (aligned with `Locale` in localeStore).
 */
export const LOCALE_COOKIE_NAME = "mathakine_locale";

export type LocaleCode = "fr" | "en";

export function parseLocaleCookieValue(raw: string | undefined): LocaleCode | null {
  if (raw === "fr" || raw === "en") {
    return raw;
  }
  return null;
}

/**
 * Resolves the value for `<html lang>` from the raw cookie value (server or request).
 */
export function resolveLocaleForHtml(value: string | undefined | null): LocaleCode {
  return parseLocaleCookieValue(value ?? undefined) ?? "fr";
}

/**
 * Reads `mathakine_locale` from `document.cookie` (client only).
 */
export function getLocaleFromDocumentCookie(): LocaleCode | null {
  if (typeof document === "undefined") {
    return null;
  }
  const match = document.cookie.match(new RegExp(`(?:^|; )${LOCALE_COOKIE_NAME}=([^;]*)`));
  const raw = match?.[1] ? decodeURIComponent(match[1].trim()) : undefined;
  return parseLocaleCookieValue(raw);
}

/**
 * Persists locale for the next full page load (SSR reads this cookie).
 */
export function setLocaleCookieClient(locale: LocaleCode): void {
  if (typeof document === "undefined") {
    return;
  }
  const secure = typeof window !== "undefined" && window.location.protocol === "https:";
  const maxAgeSeconds = 60 * 60 * 24 * 365;
  document.cookie = `${LOCALE_COOKIE_NAME}=${locale}; Path=/; Max-Age=${maxAgeSeconds}; SameSite=Lax${secure ? "; Secure" : ""}`;
}
