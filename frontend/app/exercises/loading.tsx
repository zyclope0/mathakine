'use client';

import { LoadingState } from '@/components/layout';
import { useTranslations } from 'next-intl';

export default function ExercisesLoading() {
  const t = useTranslations('exercises');
  return <LoadingState message={t('list.loading')} />;
}

