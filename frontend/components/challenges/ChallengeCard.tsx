'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { getChallengeTypeDisplay, getAgeGroupDisplay, getAgeGroupColor } from '@/lib/constants/challenges';
import type { Challenge } from '@/types/api';
import { Clock, Users, TrendingUp, Eye, ArrowRight, CheckCircle2, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';
import { useCompletedChallenges } from '@/hooks/useCompletedItems';
import { useTranslations } from 'next-intl';

interface ChallengeCardProps {
  challenge: Challenge;
}

export function ChallengeCard({ challenge }: ChallengeCardProps) {
  const { createVariants, createTransition, shouldReduceMotion } = useAccessibleAnimation();
  const t = useTranslations('challenges');
  const { isCompleted } = useCompletedChallenges();
  const typeDisplay = getChallengeTypeDisplay(challenge.challenge_type);
  const ageGroupDisplay = getAgeGroupDisplay(challenge.age_group);
  const ageGroupColor = getAgeGroupColor(challenge.age_group);
  const completed = isCompleted(challenge.id);

  // Variantes d'animation avec garde-fous
  const variants = createVariants({
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
  });

  const transition = createTransition({ duration: 0.2 });

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={transition}
      whileHover={!shouldReduceMotion ? { y: -4 } : {}}
    >
    <Card 
      className="card-spatial-depth relative"
      role="article"
      aria-labelledby={`challenge-title-${challenge.id}`}
      aria-describedby={`challenge-description-${challenge.id}`}
    >
      {completed && (
        <Badge 
          variant="default"
          className="absolute top-2 right-2 z-10 bg-green-500/90 text-white border-green-600 shadow-lg"
          aria-label={t('card.completed', { default: 'Défi résolu' })}
        >
          <CheckCircle2 className="h-3 w-3 mr-1" aria-hidden="true" />
          {t('card.completed', { default: 'Résolu' })}
        </Badge>
      )}
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle 
              id={`challenge-title-${challenge.id}`}
              className="text-lg mb-2 flex items-center gap-2"
            >
              {challenge.tags && challenge.tags.includes('ai') && (
                <Sparkles className="h-4 w-4 text-primary-on-dark" aria-hidden="true" />
              )}
              {challenge.title}
            </CardTitle>
            <CardDescription 
              id={`challenge-description-${challenge.id}`}
              className="line-clamp-2"
            >
              {challenge.description}
            </CardDescription>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 mt-3">
          <Badge 
            variant="outline" 
            className={`badge-sweep ${ageGroupColor}`}
            aria-label={`Groupe d'âge: ${ageGroupDisplay}`}
          >
            {ageGroupDisplay}
          </Badge>
          <Badge 
            variant="outline"
            className="badge-sweep"
            aria-label={`Type: ${typeDisplay}`}
          >
            {typeDisplay}
          </Badge>
          {challenge.difficulty_rating && (
            <Badge 
              variant="outline" 
              className="badge-sweep bg-purple-500/20 text-purple-400 border-purple-500/30"
              aria-label={`Difficulté: ${challenge.difficulty_rating.toFixed(1)} sur 5`}
            >
              ⭐ {challenge.difficulty_rating.toFixed(1)}/5
            </Badge>
          )}
          {challenge.tags && challenge.tags.includes('ai') && (
            <Badge 
              variant="outline" 
              className="badge-ai-pulse bg-primary/10 text-primary-on-dark border-primary/30"
              aria-label={t('card.aiGenerated', { default: 'Généré par intelligence artificielle' })}
            >
              IA
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
          <div className="flex items-center gap-4" role="group" aria-label="Informations sur le défi">
            {challenge.estimated_time_minutes && (
              <div className="flex items-center gap-1" aria-label={`Temps estimé: ${challenge.estimated_time_minutes} minutes`}>
                <Clock className="h-4 w-4" aria-hidden="true" />
                <span>{challenge.estimated_time_minutes} min</span>
              </div>
            )}
            <div className="flex items-center gap-1" aria-label={`${challenge.view_count || 0} vue${(challenge.view_count || 0) > 1 ? 's' : ''}`}>
              <Eye className="h-4 w-4" aria-hidden="true" />
              <span>{challenge.view_count || 0}</span>
            </div>
            {challenge.success_rate !== undefined && challenge.success_rate !== null && challenge.success_rate > 0 && (
              <div className="flex items-center gap-1" aria-label={`Taux de réussite: ${Math.round(challenge.success_rate * 100)}%`}>
                <TrendingUp className="h-4 w-4" aria-hidden="true" />
                <span>{Math.round(challenge.success_rate * 100)}%</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button asChild className="btn-cta-primary flex-1">
            <Link 
              href={`/challenge/${challenge.id}`}
              aria-label={`Résoudre le défi: ${challenge.title}`}
            >
              Résoudre
              <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
    </motion.div>
  );
}

