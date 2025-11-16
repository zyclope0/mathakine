'use client';

import { BadgeCard } from './BadgeCard';
import type { Badge, UserBadge } from '@/types/api';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';

interface BadgeGridProps {
  badges: Badge[];
  earnedBadges: UserBadge[];
  isLoading?: boolean;
}

export function BadgeGrid({ badges, earnedBadges, isLoading }: BadgeGridProps) {
  const { shouldReduceMotion, createTransition } = useAccessibleAnimation();
  
  // Créer un map des badges obtenus pour accès rapide (par ID)
  const earnedBadgeMap = new Map<number, UserBadge>();
  earnedBadges.forEach((userBadge) => {
    earnedBadgeMap.set(userBadge.id, userBadge);
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Filtrer les badges invalides (sans nom ou code)
  const validBadges = badges.filter(badge => {
    return badge.name || badge.code;
  });

  if (validBadges.length === 0) {
    return (
      <div className="text-center py-12" role="status" aria-live="polite">
        <p className="text-muted-foreground text-base">
          Aucun badge disponible pour le moment.
        </p>
      </div>
    );
  }

  // Trier les badges : obtenus en premier, puis par catégorie et difficulté
  const sortedBadges = [...validBadges].sort((a, b) => {
    const aEarned = earnedBadgeMap.has(a.id);
    const bEarned = earnedBadgeMap.has(b.id);

    // Obtenus en premier
    if (aEarned && !bEarned) return -1;
    if (!aEarned && bEarned) return 1;

    // Puis par catégorie
    const categoryOrder = { progression: 0, mastery: 1, special: 2 };
    const categoryDiff = categoryOrder[a.category] - categoryOrder[b.category];
    if (categoryDiff !== 0) return categoryDiff;

    // Puis par difficulté
    const difficultyOrder = { bronze: 0, silver: 1, gold: 2 };
    return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
  });

  // Variantes pour le conteneur avec staggerChildren
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : 0.05,
        delayChildren: 0.1,
      },
    },
  };

  return (
    <motion.div
      className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
      variants={containerVariants}
      initial="hidden"
      animate="show"
      role="list"
      aria-label="Collection de badges"
    >
      {sortedBadges.map((badge, index) => {
        const userBadge = earnedBadgeMap.get(badge.id);
        return (
          <BadgeCard
            key={badge.id}
            badge={badge}
            userBadge={userBadge ?? null}
            isEarned={!!userBadge}
            index={index}
          />
        );
      })}
    </motion.div>
  );
}

