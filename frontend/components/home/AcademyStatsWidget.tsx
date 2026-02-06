'use client';

import { useAcademyStats } from '@/hooks/useAcademyStats';
import { Card, CardContent } from '@/components/ui/card';
import { BookOpen, Sparkles, Target, Users } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils/cn';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';

/**
 * Widget affichant les statistiques globales de l'Académie
 * 
 * Affiche sur la page d'accueil :
 * - Nombre total d'épreuves disponibles
 * - Taux de maîtrise global
 * - Nombre d'épreuves générées par IA
 * - Citation de sagesse
 */
export function AcademyStatsWidget() {
  const { stats, isLoading, error } = useAcademyStats();
  const { shouldReduceMotion } = useAccessibleAnimation();

  // Ne rien afficher en cas d'erreur (widget optionnel)
  if (error || (!isLoading && !stats)) {
    return null;
  }

  // Skeleton loader
  if (isLoading) {
    return (
      <Card className="bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5 border-primary/10">
        <CardContent className="py-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="text-center space-y-2">
                <Skeleton className="h-8 w-8 mx-auto rounded-full" />
                <Skeleton className="h-6 w-12 mx-auto" />
                <Skeleton className="h-4 w-20 mx-auto" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const { academy_statistics, global_performance, sage_wisdom } = stats!;

  const statItems = [
    {
      icon: BookOpen,
      value: academy_statistics.total_challenges,
      label: 'Épreuves',
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      icon: Target,
      value: `${Math.round(global_performance.mastery_rate)}%`,
      label: 'Maîtrise',
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      icon: Sparkles,
      value: academy_statistics.ai_generated,
      label: 'Créées par IA',
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      icon: Users,
      value: global_performance.total_attempts,
      label: 'Tentatives',
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
    },
  ];

  return (
    <Card 
      className={cn(
        "bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5 border-primary/10",
        !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4"
      )}
    >
      <CardContent className="py-6 space-y-4">
        {/* Titre */}
        <div className="text-center">
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            L'Académie en chiffres
          </h3>
        </div>

        {/* Stats en grille */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {statItems.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.label} className="text-center space-y-1">
                <div className={cn(
                  "mx-auto flex h-10 w-10 items-center justify-center rounded-full",
                  item.bgColor
                )}>
                  <Icon className={cn("h-5 w-5", item.color)} aria-hidden="true" />
                </div>
                <div className="text-xl md:text-2xl font-bold">{item.value}</div>
                <div className="text-xs text-muted-foreground">{item.label}</div>
              </div>
            );
          })}
        </div>

        {/* Citation de sagesse */}
        {sage_wisdom && (
          <div className="text-center pt-2 border-t border-primary/10">
            <p className="text-sm italic text-muted-foreground">
              "{sage_wisdom}"
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
