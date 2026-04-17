/**
 * Canonical locale cookie readable by both SSR (`cookies()` / `headers()`) and client runtime.
 * Single string value: `fr` | `en`.
 */
export const LOCALE_COOKIE_NAME = "mathakine_locale";

export const SUPPORTED_LOCALES = ["fr", "en"] as const;

export type LocaleCode = (typeof SUPPORTED_LOCALES)[number];

export function parseLocaleCookieValue(raw: string | undefined): LocaleCode | null {
  if (raw === "fr" || raw === "en") {
    return raw;
  }

  return null;
}

/**
 * Resolves the best supported locale from an Accept-Language header.
 * Example: `en-US,en;q=0.9,fr;q=0.8` -> `en`
 */
export function parseAcceptLanguageHeader(raw: string | null | undefined): LocaleCode | null {
  if (!raw) {
    return null;
  }

  const candidates = raw
    .split(",")
    .map((entry) => {
      const [languageTag, ...params] = entry.trim().split(";");
      const baseLocale = languageTag?.trim().split("-")[0];
      const qualityParam = params.find((param) => param.trim().startsWith("q="));
      const qualityValue = qualityParam ? Number(qualityParam.trim().slice(2)) : 1;

      return {
        locale: parseLocaleCookieValue(baseLocale),
        quality: Number.isFinite(qualityValue) ? qualityValue : 0,
      };
    })
    .filter((entry): entry is { locale: LocaleCode; quality: number } => entry.locale !== null)
    .sort((a, b) => b.quality - a.quality);

  return candidates[0]?.locale ?? null;
}

/**
 * Canonical SSR locale resolution.
 * Priority: explicit cookie, then Accept-Language, then default `fr`.
 */
export function resolveRequestLocale(options: {
  cookieLocale?: string | null | undefined;
  acceptLanguage?: string | null | undefined;
}): LocaleCode {
  return (
    parseLocaleCookieValue(options.cookieLocale ?? undefined) ??
    parseAcceptLanguageHeader(options.acceptLanguage) ??
    "fr"
  );
}

/**
 * Resolves the value for `<html lang>` from server-readable request inputs.
 */
export function resolveLocaleForHtml(
  value: string | undefined | null,
  acceptLanguage?: string | null
): LocaleCode {
  return resolveRequestLocale({ cookieLocale: value, acceptLanguage });
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
