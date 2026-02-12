"use client";

import { useLocaleStore, type Locale } from "@/lib/stores/localeStore";

const locales: Locale[] = ["fr", "en"];
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Languages } from "lucide-react";
import { useTranslations } from "next-intl";

const localeNames: Record<Locale, string> = {
  fr: "Français",
  en: "English",
};

const localeFlags: Record<Locale, string> = {
  fr: "🇫🇷",
  en: "🇬🇧",
};

export function LanguageSelector() {
  const { locale, setLocale } = useLocaleStore();
  const t = useTranslations("common");

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9"
          aria-label={t("selectLanguage") || "Choisir la langue"}
        >
          <Languages className="h-4 w-4" aria-hidden="true" />
          <span className="sr-only">{localeNames[locale]}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {locales.map((loc) => (
          <DropdownMenuItem
            key={loc}
            onClick={() => setLocale(loc)}
            className={locale === loc ? "bg-accent" : ""}
          >
            <span className="mr-2">{localeFlags[loc]}</span>
            {localeNames[loc]}
            {locale === loc && <span className="ml-auto text-xs text-muted-foreground">✓</span>}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
