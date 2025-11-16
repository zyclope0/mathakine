'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils/cn';

interface PageGridProps {
  children: ReactNode;
  columns?: {
    mobile?: number;
    tablet?: number;
    desktop?: number;
  };
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}

const gapClasses = {
  sm: 'gap-2',
  md: 'gap-4',
  lg: 'gap-6',
};

// Classes Tailwind statiques pour éviter les problèmes de purge
const gridColsClasses = {
  1: {
    mobile: 'grid-cols-1',
    tablet: 'md:grid-cols-1',
    desktop: 'lg:grid-cols-1',
  },
  2: {
    mobile: 'grid-cols-2',
    tablet: 'md:grid-cols-2',
    desktop: 'lg:grid-cols-2',
  },
  3: {
    mobile: 'grid-cols-3',
    tablet: 'md:grid-cols-3',
    desktop: 'lg:grid-cols-3',
  },
  4: {
    mobile: 'grid-cols-4',
    tablet: 'md:grid-cols-4',
    desktop: 'lg:grid-cols-4',
  },
} as const;

/**
 * PageGrid - Grille responsive standardisée
 * 
 * Garantit :
 * - Breakpoints cohérents
 * - Espacements standardisés
 * - Responsive par défaut
 */
export function PageGrid({
  children,
  columns = { mobile: 1, tablet: 2, desktop: 3 },
  gap = 'md',
  className,
}: PageGridProps) {
  const mobileCols = columns.mobile || 1;
  const tabletCols = columns.tablet || 2;
  const desktopCols = columns.desktop || 3;

  const mobileClass = gridColsClasses[mobileCols as keyof typeof gridColsClasses]?.mobile || 'grid-cols-1';
  const tabletClass = gridColsClasses[tabletCols as keyof typeof gridColsClasses]?.tablet || 'md:grid-cols-2';
  const desktopClass = gridColsClasses[desktopCols as keyof typeof gridColsClasses]?.desktop || 'lg:grid-cols-3';

  return (
    <div className={cn(
      'grid',
      mobileClass,
      tabletClass,
      desktopClass,
      gapClasses[gap],
      className
    )}>
      {children}
    </div>
  );
}
