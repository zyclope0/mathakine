"use client";

import dynamic from "next/dynamic";
import { ChartSkeleton } from "@/components/dashboard/DashboardSkeletons";
import type { ProgressByCategory } from "@/hooks/useProgressStats";

function VolumeChartLoading() {
  return <ChartSkeleton />;
}

const VolumeByTypeChart = dynamic(
  () => import("./VolumeByTypeChart").then((mod) => ({ default: mod.VolumeByTypeChart })),
  {
    loading: () => <VolumeChartLoading />,
    ssr: false,
  }
);

interface VolumeByTypeChartLazyProps {
  categoryData: Record<string, ProgressByCategory>;
}

export function VolumeByTypeChartLazy(props: VolumeByTypeChartLazyProps) {
  return <VolumeByTypeChart {...props} />;
}
