'use client';

import dynamic from 'next/dynamic';
import { ChartSkeleton } from '@/components/dashboard/DashboardSkeletons';

// Composant de chargement avec skeleton
function ProgressChartLoading() {
  return <ChartSkeleton />;
}

// Lazy load Recharts pour réduire le bundle initial
const ProgressChart = dynamic(() => import('./ProgressChart').then(mod => ({ default: mod.ProgressChart })), {
  loading: () => <ProgressChartLoading />,
  ssr: false, // Désactiver SSR pour les graphiques (non critiques pour SEO)
});

interface ProgressChartLazyProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
    }>;
  };
}

export function ProgressChartLazy(props: ProgressChartLazyProps) {
  return <ProgressChart {...props} />;
}

