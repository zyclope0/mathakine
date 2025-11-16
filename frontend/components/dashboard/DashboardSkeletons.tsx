'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Skeleton pour les StatsCards (KPIs)
 */
export function StatsCardSkeleton() {
  return (
    <Card className="bg-card border-primary/20">
      <CardContent className="pt-6">
        <div className="text-center space-y-2">
          <div className="flex justify-center">
            <Skeleton variant="circular" width={32} height={32} />
          </div>
          <Skeleton className="h-9 w-20 mx-auto" />
          <Skeleton className="h-4 w-24 mx-auto" />
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton pour les graphiques
 */
export function ChartSkeleton() {
  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full flex items-center justify-center">
          <div className="w-full space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
            <Skeleton className="h-4 w-3/6" />
            <Skeleton className="h-4 w-2/6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton pour PerformanceByType
 */
export function PerformanceByTypeSkeleton() {
  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <Skeleton className="h-6 w-48" />
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="rounded-lg p-4 border bg-muted/50">
              <Skeleton className="h-5 w-20 mx-auto mb-3" />
              <Skeleton className="h-8 w-16 mx-auto mb-2" />
              <Skeleton className="h-2 w-full mb-2" />
              <Skeleton className="h-3 w-24 mx-auto" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton pour RecentActivity
 */
export function RecentActivitySkeleton() {
  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <Skeleton className="h-6 w-40" />
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-muted border">
              <Skeleton variant="circular" width={32} height={32} />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton pour LevelIndicator
 */
export function LevelIndicatorSkeleton() {
  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <Skeleton className="h-6 w-40" />
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <Skeleton variant="circular" width={64} height={64} />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-2 w-full" />
            <Skeleton className="h-4 w-24" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Skeleton pour Recommendations
 */
export function RecommendationsSkeleton() {
  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-8 w-24" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, index) => (
            <div key={index} className="p-4 rounded-lg bg-muted border animate-pulse">
              <div className="flex gap-2 mb-3">
                <Skeleton className="h-5 w-20 bg-muted-foreground/20" />
                <Skeleton className="h-5 w-16 bg-muted-foreground/20" />
              </div>
              <Skeleton className="h-4 w-3/4 bg-muted-foreground/20 mb-2" />
              <Skeleton className="h-3 w-full bg-muted-foreground/20 mb-2" />
              <Skeleton className="h-8 w-full bg-muted-foreground/20" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

