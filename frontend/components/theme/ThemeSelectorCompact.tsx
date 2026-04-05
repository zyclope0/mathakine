"use client";

import { useTranslations } from "next-intl";
import { useThemeStore } from "@/lib/stores/themeStore";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Palette } from "lucide-react";

const themeIds = [
  { id: "spatial" as const, icon: "🚀" },
  { id: "minimalist" as const, icon: "⚪" },
  { id: "ocean" as const, icon: "🌊" },
  { id: "dune" as const, icon: "🏜️" },
  { id: "forest" as const, icon: "🌲" },
  { id: "aurora" as const, icon: "🌸" },
  { id: "dino" as const, icon: "🦖" },
  { id: "unicorn" as const, icon: "🦄" },
] as const;

export function ThemeSelectorCompact() {
  const t = useTranslations("theme");
  const { theme, setTheme } = useThemeStore();
  const currentTheme = themeIds.find((th) => th.id === theme) || themeIds[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" aria-label="Changer le thème" title="Changer le thème">
          <Palette className="h-4 w-4 mr-1.5" aria-hidden="true" />
          <span className="hidden sm:inline" aria-hidden="true">
            {currentTheme.icon}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {themeIds.map((th) => (
          <DropdownMenuItem
            key={th.id}
            onClick={() => setTheme(th.id)}
            className={theme === th.id ? "bg-primary/10" : ""}
          >
            <span className="mr-2">{th.icon}</span>
            <span>{t(th.id)}</span>
            {theme === th.id && <span className="ml-auto">✓</span>}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
