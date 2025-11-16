'use client';

import { Button } from '@/components/ui/button';
import { Sun, Moon } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useThemeStore } from '@/lib/stores/themeStore';

/**
 * Toggle pour basculer entre mode clair et sombre
 * Ajoute/enlève la classe `.dark` sur document.documentElement
 * pour activer les variantes dark: spécifiques à chaque thème
 */
export function DarkModeToggle() {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);
  const { theme } = useThemeStore();

  useEffect(() => {
    setMounted(true);
    // Vérifier la préférence stockée ou système
    const stored = localStorage.getItem('dark-mode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldBeDark = stored !== null ? stored === 'true' : prefersDark;
    
    setIsDark(shouldBeDark);
    if (shouldBeDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  // Réappliquer le dark mode quand le thème change
  useEffect(() => {
    if (mounted) {
      const stored = localStorage.getItem('dark-mode');
      const isDarkMode = stored === 'true';
      
      if (isDarkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  }, [theme, mounted]);

  const toggleDarkMode = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    localStorage.setItem('dark-mode', String(newIsDark));
    
    if (newIsDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // Éviter le flash de contenu non stylé (hydration mismatch)
  if (!mounted) {
    return (
      <Button
        variant="ghost"
        size="sm"
        className="h-9 w-9 p-0"
        aria-label="Changer le thème clair/sombre"
        disabled
      >
        <Moon className="h-4 w-4" aria-hidden="true" />
      </Button>
    );
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleDarkMode}
      aria-label={isDark ? 'Passer en mode clair' : 'Passer en mode sombre'}
      title={isDark ? 'Mode sombre actif' : 'Mode clair actif'}
      className="h-9 w-9 p-0"
    >
      {isDark ? (
        <Sun className="h-4 w-4" aria-hidden="true" />
      ) : (
        <Moon className="h-4 w-4" aria-hidden="true" />
      )}
    </Button>
  );
}

