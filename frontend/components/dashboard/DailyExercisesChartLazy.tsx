"use client";

import dynamic from "next/dynamic";
import { ChartSkeleton } from "@/components/dashboard/DashboardSkeletons";

// Composant de chargement avec skeleton
function DailyExercisesChartLoading() {
  return <ChartSkeleton />;
}

// Lazy load Recharts pour réduire le bundle initial
const DailyExercisesChart = dynamic(
  () => import("./DailyExercisesChart").then((mod) => ({ default: mod.DailyExercisesChart })),
  {
    loading: () => <DailyExercisesChartLoading />,
    ssr: false, // Désactiver SSR pour les graphiques (non critiques pour SEO)
  }
);

interface DailyExercisesChartLazyProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      borderColor?: string;
      backgroundColor?: string;
    }>;
  };
}

export function DailyExercisesChartLazy(props: DailyExercisesChartLazyProps) {
  return <DailyExercisesChart {...props} />;
}
