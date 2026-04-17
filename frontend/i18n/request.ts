import { cookies, headers } from "next/headers";
import { notFound } from "next/navigation";
import { getRequestConfig } from "next-intl/server";
import { LOCALE_COOKIE_NAME, SUPPORTED_LOCALES, resolveRequestLocale } from "@/lib/localeCookie";

export const locales = SUPPORTED_LOCALES;
export type Locale = (typeof locales)[number];

export default getRequestConfig(async ({ locale }) => {
  const cookieStore = await cookies();
  const headerList = await headers();
  const validLocale =
    locale ||
    resolveRequestLocale({
      cookieLocale: cookieStore.get(LOCALE_COOKIE_NAME)?.value,
      acceptLanguage: headerList.get("accept-language"),
    });

  if (!locales.includes(validLocale as Locale)) notFound();

  return {
    locale: validLocale,
    messages: (await import(`../messages/${validLocale}.json`)).default,
    timeZone: "Europe/Paris",
  };
});
