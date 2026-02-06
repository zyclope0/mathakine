'use client';

import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils/cn';
import { useExerciseTypeDisplay } from '@/hooks/useChallengeTranslations';
import { useTranslations } from 'next-intl';

interface PerformanceByTypeProps {
  performance: {
    [key: string]: {
      completed: number;
      correct: number;
      success_rate: number;
    };
  };
}

// Couleurs dynamiques pour tous les types d'exercices
const getTypeColor = (type: string): { bg: string; text: string; border: string } => {
  const typeLower = type.toLowerCase();
  
  // Mapping des couleurs par type
  const colorMap: Record<string, { bg: string; text: string; border: string }> = {
    addition: {
      bg: 'bg-green-500/20',
      text: 'text-green-300',
      border: 'border-green-500/30',
    },
    soustraction: {
      bg: 'bg-red-500/20',
      text: 'text-red-300',
      border: 'border-red-500/30',
    },
    subtraction: {
      bg: 'bg-red-500/20',
      text: 'text-red-300',
      border: 'border-red-500/30',
    },
    multiplication: {
      bg: 'bg-yellow-500/20',
      text: 'text-yellow-300',
      border: 'border-yellow-500/30',
    },
    division: {
      bg: 'bg-blue-500/20',
      text: 'text-blue-300',
      border: 'border-blue-500/30',
    },
    mixte: {
      bg: 'bg-purple-500/20',
      text: 'text-purple-300',
      border: 'border-purple-500/30',
    },
    fractions: {
      bg: 'bg-pink-500/20',
      text: 'text-pink-300',
      border: 'border-pink-500/30',
    },
    geometrie: {
      bg: 'bg-cyan-500/20',
      text: 'text-cyan-300',
      border: 'border-cyan-500/30',
    },
    geometry: {
      bg: 'bg-cyan-500/20',
      text: 'text-cyan-300',
      border: 'border-cyan-500/30',
    },
    texte: {
      bg: 'bg-indigo-500/20',
      text: 'text-indigo-300',
      border: 'border-indigo-500/30',
    },
    text: {
      bg: 'bg-indigo-500/20',
      text: 'text-indigo-300',
      border: 'border-indigo-500/30',
    },
    divers: {
      bg: 'bg-orange-500/20',
      text: 'text-orange-300',
      border: 'border-orange-500/30',
    },
  };
  
  return colorMap[typeLower] || {
    bg: 'bg-gray-500/20',
    text: 'text-gray-300',
    border: 'border-gray-500/30',
  };
};

export function PerformanceByType({ performance }: PerformanceByTypeProps) {
  const t = useTranslations('dashboard');
  const getTypeDisplay = useExerciseTypeDisplay();
  
  // Memoization du tri des types pour éviter les recalculs inutiles
  // Trier les types par nombre d'exercices complétés (décroissant)
  // Prioriser les types avec le plus d'activité
  const sortedTypes = useMemo(() => {
    return Object.entries(performance)
      .map(([type, stats]) => ({
        type,
        typeKey: type.toLowerCase(),
        stats: stats || { completed: 0, correct: 0, success_rate: 0 },
      }))
      .filter(({ stats }) => stats.completed > 0) // Filtrer les types sans données
      .sort((a, b) => b.stats.completed - a.stats.completed); // Trier par completed décroissant
  }, [performance]);

  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <CardTitle className="text-xl text-foreground">
          {t('performanceByType.title', { default: 'Performance par type' })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {sortedTypes.length > 0 ? (
            sortedTypes.map(({ type, typeKey, stats }) => {
              const colors = getTypeColor(typeKey);
              const label = getTypeDisplay(typeKey);

              // Badge pour performance exceptionnelle (>90%)
              const isExcellent = stats.success_rate >= 90;
              
              return (
                <div
                  key={type}
                  className={cn(
                    'rounded-lg p-4 text-center border transition-all',
                    colors.bg,
                    colors.border,
                    isExcellent && 'border-2 shadow-lg shadow-primary/20',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2'
                  )}
                  tabIndex={0}
                  role="article"
                  aria-label={`Performance ${label}: ${stats.success_rate}%`}
                >
                  <div className="flex items-center justify-center gap-2 mb-3">
                    <Badge variant="outline" className={cn(colors.text, colors.border)}>
                      {label}
                    </Badge>
                    {isExcellent && (
                      <Badge className="bg-success/20 text-success text-xs">
                        {t('performanceByType.excellent', { default: 'Excellent !' })}
                      </Badge>
                    )}
                  </div>
                  <div className={cn('text-2xl font-bold mb-2', colors.text)}>
                    {stats.success_rate}%
                  </div>
                  <Progress value={stats.success_rate} className="h-2 mb-2" />
                  <div className="text-xs text-muted-foreground">
                    {stats.correct}/{stats.completed} {t('performanceByType.completed', { default: 'réussis' })}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-full text-center py-8 text-muted-foreground">
              {t('performanceByType.empty', { default: 'Aucune donnée de performance disponible' })}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

