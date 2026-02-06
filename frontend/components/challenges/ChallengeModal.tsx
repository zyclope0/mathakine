'use client';

import { useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useChallenge } from '@/hooks/useChallenge';
import { getChallengeTypeDisplay, getAgeGroupDisplay, getAgeGroupColor } from '@/lib/constants/challenges';
import { formatSuccessRate } from '@/lib/utils/format';
import { Loader2, XCircle, ArrowRight, Clock, Eye, TrendingUp, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTranslations } from 'next-intl';
import Link from 'next/link';

interface ChallengeModalProps {
  challengeId: number | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onChallengeCompleted?: () => void;
}

export function ChallengeModal({
  challengeId,
  open,
  onOpenChange,
  onChallengeCompleted,
}: ChallengeModalProps) {
  const { challenge, isLoading, error } = useChallenge(challengeId || 0);
  const t = useTranslations('challenges.modal');
  const tc = useTranslations('common');

  // Fermer la modal proprement
  const handleClose = () => {
    onOpenChange(false);
  };

  if (!challengeId) {
    return null;
  }

  const typeDisplay = challenge ? getChallengeTypeDisplay(challenge.challenge_type) : '';
  const ageGroupDisplay = challenge ? getAgeGroupDisplay(challenge.age_group) : '';
  const ageGroupColor = challenge ? getAgeGroupColor(challenge.age_group) : '';

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          {isLoading ? (
            <DialogTitle>{t('loading')}</DialogTitle>
          ) : error ? (
            <DialogTitle>{t('errorTitle')}</DialogTitle>
          ) : challenge ? (
            <>
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <DialogTitle className="text-xl">{challenge.title}</DialogTitle>
                  {challenge.tags?.includes('ai') && (
                    <Sparkles className="h-4 w-4 text-amber-500" />
                  )}
                </div>
                <div className="flex gap-2">
                  {ageGroupDisplay && (
                    <Badge variant="outline" className={ageGroupColor}>
                      {ageGroupDisplay}
                    </Badge>
                  )}
                  <Badge variant="outline">{typeDisplay}</Badge>
                </div>
              </div>
              <DialogDescription className="text-base mt-3">
                {challenge.description}
              </DialogDescription>
            </>
          ) : (
            <DialogTitle>{t('title')}</DialogTitle>
          )}
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center min-h-[200px]">
            <div className="text-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
              <p className="text-muted-foreground">{t('loading')}</p>
            </div>
          </div>
        ) : error ? (
          <div className="text-center space-y-4 py-8">
            <XCircle className="h-12 w-12 text-destructive mx-auto" />
            <div>
              <p className="text-muted-foreground mt-2">
                {error.status === 404
                  ? t('notFound')
                  : error.message || t('loadError')}
              </p>
            </div>
          </div>
        ) : challenge ? (
          <div className="space-y-6 py-4">
            {/* Question preview */}
            {challenge.question && (
              <div className="p-4 rounded-lg bg-muted/50 border">
                <p className="font-medium mb-2">{t('question')}</p>
                <p className="text-muted-foreground">{challenge.question}</p>
              </div>
            )}

            {/* Infos du challenge */}
            <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
              {challenge.estimated_time_minutes && (
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{challenge.estimated_time_minutes} min</span>
                </div>
              )}
              <div className="flex items-center gap-1">
                <Eye className="h-4 w-4" />
                <span>{challenge.view_count || 0} vues</span>
              </div>
              {formatSuccessRate(challenge.success_rate) && (
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" />
                  <span>{formatSuccessRate(challenge.success_rate)} {t('successRate')}</span>
                </div>
              )}
              {challenge.difficulty_rating && (
                <div className="flex items-center gap-1">
                  <span>⭐ {challenge.difficulty_rating.toFixed(1)}/5</span>
                </div>
              )}
            </div>

            {/* Bouton pour résoudre */}
            <div className="flex gap-3 pt-4 border-t">
              <Button
                variant="outline"
                onClick={handleClose}
                className="flex-1"
              >
                {tc('close')}
              </Button>
              <Button asChild className="flex-1 btn-cta-primary">
                <Link href={`/challenge/${challenge.id}`}>
                  {t('solveChallenge')}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
