'use client';

import { useThemeStore } from '@/lib/stores/themeStore';
import { Button } from '@/components/ui/button';

const themes = [
  { id: 'spatial' as const, name: 'Spatial', icon: '🚀' },
  { id: 'minimalist' as const, name: 'Minimaliste', icon: '⚪' },
  { id: 'ocean' as const, name: 'Océan', icon: '🌊' },
  { id: 'neutral' as const, name: 'Neutre', icon: '⚫' },
] as const;

export function ThemeSelector() {
  const { theme, setTheme } = useThemeStore();

  return (
    <div className="flex flex-wrap gap-2">
      {themes.map((t) => (
        <Button
          key={t.id}
          variant={theme === t.id ? 'default' : 'outline'}
          onClick={() => setTheme(t.id)}
          aria-label={`Changer le thème vers ${t.name}`}
          className="gap-2"
        >
          <span>{t.icon}</span>
          <span>{t.name}</span>
        </Button>
      ))}
    </div>
  );
}

