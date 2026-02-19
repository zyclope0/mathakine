"use client";

import { NextIntlClientProvider } from "next-intl";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useEffect } from "react";
import frMessages from "@/messages/fr.json";
import enMessages from "@/messages/en.json";

const messageModules: Record<string, typeof frMessages> = {
  fr: frMessages as typeof frMessages,
  en: enMessages as typeof frMessages,
};

interface NextIntlProviderProps {
  children: React.ReactNode;
}

export function NextIntlProvider({ children }: NextIntlProviderProps) {
  const { locale } = useLocaleStore();
  const messages = messageModules[locale] ?? frMessages;

  // Mettre à jour l'attribut lang du document
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = locale;
    }
  }, [locale]);

  return (
    <NextIntlClientProvider
      locale={locale}
      messages={messages}
      timeZone="Europe/Paris"
      getMessageFallback={({ namespace, key }) => {
        if (process.env.NODE_ENV === "development") {
          console.warn(`[next-intl] Missing: ${namespace ?? ""}.${key}`);
        }
        return namespace ? `${namespace}.${key}` : key;
      }}
    >
      {children}
    </NextIntlClientProvider>
  );
}
