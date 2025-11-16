'use client';

import { useThemeStore } from '@/lib/stores/themeStore';
import { DarkModeToggle } from './DarkModeToggle';
import { ThemeSelectorCompact } from './ThemeSelectorCompact';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useState } from 'react';
import { CheckCircle2, XCircle, AlertCircle, Info } from 'lucide-react';

/**
 * Composant de démonstration et test des thèmes
 * Permet de vérifier visuellement tous les thèmes avec leurs variantes dark
 */
export function ThemeShowcase() {
  const { theme } = useThemeStore();
  const [testInput, setTestInput] = useState('');

  const themes = [
    { id: 'spatial' as const, name: 'Spatial', icon: '🚀' },
    { id: 'minimalist' as const, name: 'Minimaliste', icon: '⚪' },
    { id: 'ocean' as const, name: 'Océan', icon: '🌊' },
    { id: 'neutral' as const, name: 'Neutre', icon: '⚫' },
  ];

  const currentTheme = themes.find((t) => t.id === theme) || themes[0] || { id: 'spatial' as const, name: 'Spatial', icon: '🚀' };

  return (
    <div className="space-y-8 p-6">
      {/* En-tête avec contrôles */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">Test des Thèmes</h1>
          <p className="text-muted-foreground">
            Thème actuel : <span className="font-semibold">{currentTheme.icon} {currentTheme.name}</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ThemeSelectorCompact />
          <DarkModeToggle />
        </div>
      </div>

      {/* Grille de test pour chaque thème */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {themes.map((t) => (
          <ThemeCard key={t.id} themeId={t.id} themeName={t.name} icon={t.icon} isActive={theme === t.id} />
        ))}
      </div>

      {/* Zone de test interactive */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Zone de Test Interactive</h2>
        
        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-2">Card Standard</h3>
            <p className="text-sm text-muted-foreground">
              Contenu de la carte avec texte secondaire pour tester le contraste.
            </p>
          </Card>
          
          <Card className="p-4 border-primary">
            <h3 className="font-semibold mb-2 text-primary">Card avec Border Primary</h3>
            <p className="text-sm text-muted-foreground">
              Carte avec bordure colorée pour tester les couleurs primaires.
            </p>
          </Card>
          
          <Card className="p-4 bg-accent/10">
            <h3 className="font-semibold mb-2 text-accent">Card avec Accent</h3>
            <p className="text-sm text-muted-foreground">
              Carte avec fond accent pour tester les couleurs d'accentuation.
            </p>
          </Card>
        </div>

        {/* Boutons */}
        <div className="flex flex-wrap gap-2">
          <Button>Bouton Primary</Button>
          <Button variant="secondary">Bouton Secondary</Button>
          <Button variant="outline">Bouton Outline</Button>
          <Button variant="ghost">Bouton Ghost</Button>
          <Button variant="destructive">Bouton Destructive</Button>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2">
          <Badge>Badge Default</Badge>
          <Badge variant="secondary">Badge Secondary</Badge>
          <Badge variant="outline">Badge Outline</Badge>
          <Badge variant="destructive">Badge Destructive</Badge>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Input Standard</label>
            <Input placeholder="Tapez quelque chose..." value={testInput} onChange={(e) => setTestInput(e.target.value)} />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Input Disabled</label>
            <Input placeholder="Désactivé" disabled />
          </div>
        </div>

        {/* Icônes et états */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center gap-2 p-3 rounded-md bg-green-500/10 text-green-500 dark:bg-green-400/10 dark:text-green-400">
            <CheckCircle2 className="h-5 w-5" />
            <span className="text-sm font-medium">Succès</span>
          </div>
          <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive">
            <XCircle className="h-5 w-5" />
            <span className="text-sm font-medium">Erreur</span>
          </div>
          <div className="flex items-center gap-2 p-3 rounded-md bg-yellow-500/10 text-yellow-500 dark:bg-yellow-400/10 dark:text-yellow-400">
            <AlertCircle className="h-5 w-5" />
            <span className="text-sm font-medium">Avertissement</span>
          </div>
          <div className="flex items-center gap-2 p-3 rounded-md bg-blue-500/10 text-blue-500 dark:bg-blue-400/10 dark:text-blue-400">
            <Info className="h-5 w-5" />
            <span className="text-sm font-medium">Information</span>
          </div>
        </div>

        {/* Texte et contrastes */}
        <div className="space-y-4">
          <h3 className="text-xl font-bold">Test de Typographie</h3>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold">Titre H1</h1>
            <h2 className="text-3xl font-semibold">Titre H2</h2>
            <h3 className="text-2xl font-medium">Titre H3</h3>
            <p className="text-base">
              Paragraphe standard avec du texte pour tester la lisibilité et le contraste.
            </p>
            <p className="text-sm text-muted-foreground">
              Texte secondaire (muted) pour tester le contraste avec le fond.
            </p>
            <p className="text-xs text-muted-foreground">
              Texte très petit pour tester le contraste minimal requis.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ThemeCard({ themeId, themeName, icon, isActive }: { themeId: string; themeName: string; icon: string; isActive: boolean }) {
  const { setTheme } = useThemeStore();

  return (
    <Card 
      className={`p-4 cursor-pointer transition-all ${isActive ? 'ring-2 ring-primary' : 'hover:border-primary/50'}`}
      onClick={() => setTheme(themeId as any)}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-2xl">{icon}</span>
        {isActive && <Badge variant="outline" className="text-xs">Actif</Badge>}
      </div>
      <h3 className="font-semibold mb-2">{themeName}</h3>
      <div className="space-y-1 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-primary"></div>
          <span className="text-muted-foreground">Primary</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-secondary"></div>
          <span className="text-muted-foreground">Secondary</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-accent"></div>
          <span className="text-muted-foreground">Accent</span>
        </div>
      </div>
    </Card>
  );
}

