'use client';

import { use } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ChallengeSolver } from '@/components/challenges/ChallengeSolver';
import { useRouter } from 'next/navigation';
import { PageLayout, EmptyState } from '@/components/layout';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface ChallengePageProps {
  params: Promise<{ id: string }>;
}

export default function ChallengePage({ params }: ChallengePageProps) {
  const router = useRouter();
  const tError = useTranslations('challenges.error');
  const tSolver = useTranslations('challenges.solver');
  const { id } = use(params);
  const challengeId = parseInt(id, 10);

  if (isNaN(challengeId)) {
    return (
      <ProtectedRoute>
        <PageLayout>
          <EmptyState
            title={tError('invalidId')}
            description={tError('invalidIdMessage', { id })}
            action={
              <Button asChild variant="outline">
                <Link href="/challenges">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  {tSolver('back')}
                </Link>
              </Button>
            }
          />
        </PageLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <PageLayout>
        <div className="max-w-4xl mx-auto">
          <ChallengeSolver challengeId={challengeId} />
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
}

