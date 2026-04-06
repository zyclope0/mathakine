"use client";

import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Settings } from "lucide-react";
import { useTranslations } from "next-intl";
import { VALID_PROFILE_THEMES, type ValidProfileTheme } from "@/lib/profile/profilePage";
import type { AccessibilitySettingsState } from "@/hooks/useProfilePageController";

// Emoji associé à chaque thème — stable et purement visuel
const THEME_EMOJI: Record<ValidProfileTheme, string> = {
  spatial: "🚀",
  minimalist: "⚪",
  ocean: "🌊",
  dune: "🏜️",
  forest: "🌲",
  aurora: "🌸",
  dino: "🦖",
  unicorn: "🦄",
};

interface ProfileAccessibilitySectionProps {
  accessibilitySettings: AccessibilitySettingsState;
  onThemeChange: (theme: ValidProfileTheme) => void;
  onToggle: (field: "high_contrast" | "large_text" | "reduce_motion", checked: boolean) => void;
}

/**
 * Section accessibilité / thème.
 * Composant purement visuel + callbacks.
 *
 * FFI-L11.
 */
export function ProfileAccessibilitySection({
  accessibilitySettings,
  onThemeChange,
  onToggle,
}: ProfileAccessibilitySectionProps) {
  const tAccessibility = useTranslations("profile.accessibility");
  const tTheme = useTranslations("theme");

  return (
    <div className="animate-fade-in-up">
      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Settings className="h-5 w-5 text-primary" />
            {tAccessibility("title")}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="flex flex-col">
            {/* Sélection de thème */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
              <div className="flex flex-col gap-1 pr-4">
                <Label htmlFor="theme" className="text-sm font-medium text-foreground">
                  {tAccessibility("theme")}
                </Label>
                <p className="text-xs text-muted-foreground">
                  {tAccessibility("themeDescription")}
                </p>
              </div>
              <Select
                value={accessibilitySettings.preferred_theme}
                onValueChange={(value) => onThemeChange(value as ValidProfileTheme)}
              >
                <SelectTrigger
                  id="theme"
                  className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                  aria-label={tAccessibility("theme")}
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {VALID_PROFILE_THEMES.map((theme) => (
                    <SelectItem key={theme} value={theme}>
                      <span className="flex items-center gap-2">
                        <span>{THEME_EMOJI[theme]}</span>
                        <span>{tTheme(theme)}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Contraste élevé */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
              <div className="flex flex-col gap-1 pr-4">
                <Label htmlFor="high_contrast" className="text-sm font-medium text-foreground">
                  {tAccessibility("highContrast")}
                </Label>
                <p className="text-xs text-muted-foreground">
                  {tAccessibility("highContrastDescription")}
                </p>
              </div>
              <Switch
                id="high_contrast"
                checked={accessibilitySettings.high_contrast}
                onCheckedChange={(checked) => onToggle("high_contrast", checked)}
                aria-label={tAccessibility("highContrast")}
                className="mt-3 sm:mt-0 shrink-0"
              />
            </div>

            {/* Texte large */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
              <div className="flex flex-col gap-1 pr-4">
                <Label htmlFor="large_text" className="text-sm font-medium text-foreground">
                  {tAccessibility("largeText")}
                </Label>
                <p className="text-xs text-muted-foreground">
                  {tAccessibility("largeTextDescription")}
                </p>
              </div>
              <Switch
                id="large_text"
                checked={accessibilitySettings.large_text}
                onCheckedChange={(checked) => onToggle("large_text", checked)}
                aria-label={tAccessibility("largeText")}
                className="mt-3 sm:mt-0 shrink-0"
              />
            </div>

            {/* Réduire les animations */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
              <div className="flex flex-col gap-1 pr-4">
                <Label htmlFor="reduce_motion" className="text-sm font-medium text-foreground">
                  {tAccessibility("reduceMotion")}
                </Label>
                <p className="text-xs text-muted-foreground">
                  {tAccessibility("reduceMotionDescription")}
                </p>
              </div>
              <Switch
                id="reduce_motion"
                checked={accessibilitySettings.reduce_motion}
                onCheckedChange={(checked) => onToggle("reduce_motion", checked)}
                aria-label={tAccessibility("reduceMotion")}
                className="mt-3 sm:mt-0 shrink-0"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
