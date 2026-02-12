"use client";

import { useThemeStore } from "@/lib/stores/themeStore";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Palette } from "lucide-react";

const themes = [
  { id: "spatial" as const, name: "Spatial", icon: "🚀" },
  { id: "minimalist" as const, name: "Minimaliste", icon: "⚪" },
  { id: "ocean" as const, name: "Océan", icon: "🌊" },
  { id: "neutral" as const, name: "Neutre", icon: "⚫" },
] as const;

export function ThemeSelectorCompact() {
  const { theme, setTheme } = useThemeStore();
  const currentTheme = themes.find((t) => t.id === theme) || themes[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" aria-label="Changer le thème">
          <Palette className="h-4 w-4 mr-2" aria-hidden="true" />
          <span className="hidden sm:inline">{currentTheme.icon}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {themes.map((t) => (
          <DropdownMenuItem
            key={t.id}
            onClick={() => setTheme(t.id)}
            className={theme === t.id ? "bg-primary/10" : ""}
          >
            <span className="mr-2">{t.icon}</span>
            <span>{t.name}</span>
            {theme === t.id && <span className="ml-auto">✓</span>}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
