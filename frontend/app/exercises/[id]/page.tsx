'use client';

import { use } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ExerciseSolver } from '@/components/exercises/ExerciseSolver';
import { useTranslations } from 'next-intl';
import { PageLayout, EmptyState } from '@/components/layout';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

interface ExercisePageProps {
  params: Promise<{ id: string }>;
}

export default function ExercisePage({ params }: ExercisePageProps) {
  const t = useTranslations('exercises.error');
  // Utiliser use() pour unwrap la Promise dans Next.js 15+
  const { id } = use(params);
  const exerciseId = parseInt(id, 10);

  if (isNaN(exerciseId)) {
    return (
      <ProtectedRoute>
        <PageLayout>
          <EmptyState
            title={t('invalidId')}
            description={t('invalidIdMessage', { id })}
            action={
              <Button asChild variant="outline">
                <Link href="/exercises">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Retour aux exercices
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
          <ExerciseSolver exerciseId={exerciseId} />
        </div>
      </PageLayout>
    </ProtectedRoute>
  );
}

