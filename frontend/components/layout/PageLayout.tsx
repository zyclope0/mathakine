'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils/cn';

interface PageLayoutProps {
  children: ReactNode;
  className?: string;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

const maxWidthClasses = {
  sm: 'max-w-2xl',
  md: 'max-w-4xl',
  lg: 'max-w-6xl',
  xl: 'max-w-7xl',
  '2xl': 'max-w-[1536px]',
  full: 'max-w-full',
};

/**
 * PageLayout - Layout standardisé pour toutes les pages
 * 
 * Garantit :
 * - Padding responsive cohérent
 * - Container avec max-width
 * - Espacements verticaux standardisés
 */
export function PageLayout({ 
  children, 
  className,
  maxWidth = 'xl',
}: PageLayoutProps) {
  return (
    <div className={cn('min-h-screen p-3 sm:p-4 md:p-5 lg:p-6 relative z-10', className)}>
      <div className={cn(
        'mx-auto space-y-3 md:space-y-4 lg:space-y-5',
        maxWidthClasses[maxWidth]
      )}>
        {children}
      </div>
    </div>
  );
}

