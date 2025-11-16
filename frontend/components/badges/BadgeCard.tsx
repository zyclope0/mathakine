'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge as BadgeComponent } from '@/components/ui/badge';
import { Trophy, Lock, CheckCircle } from 'lucide-react';
import type { Badge, UserBadge } from '@/types/api';
import { cn } from '@/lib/utils/cn';
import { motion } from 'framer-motion';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';

interface BadgeCardProps {
  badge: Badge;
  userBadge?: UserBadge | null;
  isEarned: boolean;
  index?: number;
}

const defaultDifficultyColor = {
  bg: 'bg-amber-500/20',
  text: 'text-amber-400',
  border: 'border-amber-500/30',
};

const difficultyColors: Record<string, { bg: string; text: string; border: string }> = {
  bronze: defaultDifficultyColor,
  silver: {
    bg: 'bg-gray-400/20',
    text: 'text-gray-300',
    border: 'border-gray-400/30',
  },
  gold: {
    bg: 'bg-yellow-500/20',
    text: 'text-yellow-400',
    border: 'border-yellow-500/30',
  },
};

const categoryIcons: Record<string, string> = {
  progression: '📈',
  mastery: '⭐',
  special: '✨',
};

export function BadgeCard({ badge, userBadge, isEarned, index = 0 }: BadgeCardProps) {
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();
  
  const getDifficultyColor = (difficulty: string | null | undefined): { bg: string; text: string; border: string } => {
    if (!difficulty) return defaultDifficultyColor;
    const color = difficultyColors[difficulty];
    if (color) {
      return color;
    }
    return defaultDifficultyColor;
  };
  
  const getCategoryIcon = (category: string | null | undefined): string => {
    if (!category) return '🏆';
    const icon = categoryIcons[category];
    return icon ?? '🏆';
  };
  
  const difficultyColor = getDifficultyColor(badge.difficulty);
  const categoryIcon = getCategoryIcon(badge.category);

  // Variantes d'animation avec garde-fous
  const variants = createVariants({
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  });

  const transition = createTransition({
    duration: 0.3,
    delay: index * 0.05,
  });

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={transition}
    >
      <Card
        className={cn(
          'card-spatial-depth relative overflow-hidden transition-all duration-300',
          isEarned 
            ? 'border-primary/50 shadow-lg shadow-primary/20 hover:scale-105' 
            : 'opacity-75 border-muted hover:opacity-90'
        )}
        role="article"
        aria-label={`Badge ${badge.name}${isEarned ? ' obtenu' : ' verrouillé'}`}
      >
        {/* Indicateur obtenu */}
        {isEarned && (
          <div className="absolute top-3 right-3 z-10" aria-label="Badge obtenu">
            <CheckCircle className="h-7 w-7 text-green-500 drop-shadow-lg" aria-hidden="true" />
          </div>
        )}

        {/* Indicateur verrouillé */}
        {!isEarned && (
          <div className="absolute top-3 right-3 z-10" aria-label="Badge verrouillé">
            <Lock className="h-7 w-7 text-muted-foreground/60" aria-hidden="true" />
          </div>
        )}

        <CardHeader className="pb-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg md:text-xl flex items-center gap-2 font-bold">
                <span className="text-3xl shrink-0" aria-hidden="true">{categoryIcon}</span>
                <span className="break-words">{badge.name || badge.code || 'Badge sans nom'}</span>
              </CardTitle>
              {badge.star_wars_title && (
                <CardDescription className="mt-2 text-primary-on-dark italic text-sm">
                  {badge.star_wars_title}
                </CardDescription>
              )}
            </div>
            <BadgeComponent
              variant="outline"
              className={cn(
                'badge-sweep shrink-0 text-lg',
                difficultyColor.bg,
                difficultyColor.text,
                difficultyColor.border
              )}
              aria-label={`Difficulté: ${badge.difficulty}`}
            >
              {badge.difficulty === 'bronze' && '🥉'}
              {badge.difficulty === 'silver' && '🥈'}
              {badge.difficulty === 'gold' && '🥇'}
            </BadgeComponent>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {badge.description ? (
            <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
              {badge.description}
            </p>
          ) : (
            <p className="text-sm md:text-base text-muted-foreground/60 italic leading-relaxed">
              Description non disponible
            </p>
          )}

          <div className="flex items-center justify-between pt-3 border-t border-border/50">
            <div className="flex items-center gap-2 text-base font-semibold">
              <Trophy className="h-5 w-5 text-yellow-500" aria-hidden="true" />
              <span className="text-foreground">{badge.points_reward}</span>
              <span className="text-muted-foreground text-sm">pts</span>
            </div>

            {isEarned && userBadge?.earned_at && (
              <div className="text-xs text-muted-foreground bg-green-500/10 px-2 py-1 rounded">
                Obtenu le {new Date(userBadge.earned_at as string).toLocaleDateString('fr-FR')}
              </div>
            )}
          </div>
        </CardContent>

        {/* Effet de brillance pour les badges obtenus (désactivé si reduced motion) */}
        {isEarned && !shouldReduceMotion && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full animate-shimmer pointer-events-none" />
        )}
      </Card>
    </motion.div>
  );
}

