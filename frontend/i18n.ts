import { getRequestConfig } from "next-intl/server";

// Can be imported from a shared config
export const locales = ["en", "fr"] as const;
export type Locale = (typeof locales)[number];

/** Normalise une locale (ex: "en-US" -> "en", "fr-FR" -> "fr") */
function normalizeLocale(locale: string | undefined): Locale {
  const base = (locale || "fr").split("-")[0]?.toLowerCase() || "fr";
  return locales.includes(base as Locale) ? (base as Locale) : "fr";
}

export default getRequestConfig(async ({ requestLocale }) => {
  // Sans routing par locale, requestLocale peut être undefined ou une variante (en-US, fr-FR)
  const rawLocale = typeof requestLocale === "object" && requestLocale && "then" in requestLocale
    ? await requestLocale
    : requestLocale;
  const validLocale = normalizeLocale(rawLocale);

  return {
    locale: validLocale,
    messages: (await import(`./messages/${validLocale}.json`)).default,
  };
});
