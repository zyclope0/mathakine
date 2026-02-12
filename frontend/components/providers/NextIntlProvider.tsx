"use client";

import { NextIntlClientProvider } from "next-intl";
import { useLocaleStore } from "@/lib/stores/localeStore";
import { useEffect, useState } from "react";

interface NextIntlProviderProps {
  children: React.ReactNode;
}

export function NextIntlProvider({ children }: NextIntlProviderProps) {
  const { locale } = useLocaleStore();
  const [messages, setMessages] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(true);

  // Charger les messages selon la locale
  useEffect(() => {
    setIsLoading(true);

    // Utiliser import dynamique pour forcer le rechargement
    import(`@/messages/${locale}.json`)
      .then((mod) => {
        setMessages(mod.default);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error(`Failed to load messages for locale ${locale}:`, err);
        // Fallback vers français en cas d'erreur
        import("@/messages/fr.json")
          .then((mod) => {
            setMessages(mod.default);
            setIsLoading(false);
          })
          .catch((fallbackErr) => {
            console.error("Failed to load fallback messages:", fallbackErr);
            setIsLoading(false);
          });
      });
  }, [locale]);

  // Mettre à jour l'attribut lang du document
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = locale;
    }
  }, [locale]);

  // Afficher un spinner pendant le chargement initial
  if (isLoading && Object.keys(messages).length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      {children}
    </NextIntlClientProvider>
  );
}
