"use client";

/**
 * Language + timezone + save (general settings).
 * FFI-L13 lot B.
 */

import { useTranslations } from "next-intl";
import { Globe } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { SaveButton } from "@/components/settings/SaveButton";
import type { LanguageSettingsState } from "@/lib/settings/settingsPage";
import type { Dispatch, SetStateAction } from "react";

const LANGUAGES = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
] as const;

const TIMEZONES = [
  { value: "UTC", label: "UTC (Coordinated Universal Time)" },
  { value: "Europe/Paris", label: "Europe/Paris (CET/CEST)" },
  { value: "America/New_York", label: "America/New_York (EST/EDT)" },
  { value: "America/Los_Angeles", label: "America/Los_Angeles (PST/PDT)" },
  { value: "Asia/Tokyo", label: "Asia/Tokyo (JST)" },
  { value: "Australia/Sydney", label: "Australia/Sydney (AEDT/AEST)" },
] as const;

export interface SettingsGeneralSectionProps {
  languageSettings: LanguageSettingsState;
  setLanguageSettings: Dispatch<SetStateAction<LanguageSettingsState>>;
  onSaveLanguage: () => void;
  isUpdatingSettings: boolean;
}

export function SettingsGeneralSection({
  languageSettings,
  setLanguageSettings,
  onSaveLanguage,
  isUpdatingSettings,
}: SettingsGeneralSectionProps) {
  const tLanguage = useTranslations("settings.language");

  return (
    <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
      <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Globe className="h-5 w-5 text-primary" />
          {tLanguage("title")}
        </CardTitle>
        <CardDescription className="mt-1">{tLanguage("description")}</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div className="flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
            <div className="flex flex-col gap-1 pr-4">
              <Label htmlFor="language" className="text-sm font-medium text-foreground">
                {tLanguage("language")}
              </Label>
              <p className="text-xs text-muted-foreground">{tLanguage("languageDescription")}</p>
            </div>
            <Select
              value={languageSettings.language_preference}
              onValueChange={(value) =>
                setLanguageSettings((prev) => ({ ...prev, language_preference: value }))
              }
            >
              <SelectTrigger id="language" className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
            <div className="flex flex-col gap-1 pr-4">
              <Label htmlFor="timezone" className="text-sm font-medium text-foreground">
                {tLanguage("timezone")}
              </Label>
              <p className="text-xs text-muted-foreground">{tLanguage("timezoneDescription")}</p>
            </div>
            <Select
              value={languageSettings.timezone}
              onValueChange={(value) =>
                setLanguageSettings((prev) => ({ ...prev, timezone: value }))
              }
            >
              <SelectTrigger id="timezone" className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TIMEZONES.map((tz) => (
                  <SelectItem key={tz.value} value={tz.value}>
                    {tz.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex justify-end pt-6">
            <SaveButton onClick={onSaveLanguage} isLoading={isUpdatingSettings} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
