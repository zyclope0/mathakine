'use client';

import { cn } from '@/lib/utils/cn';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
};

/**
 * LoadingState - État de chargement standardisé
 * 
 * Garantit :
 * - Spinner centré
 * - Message optionnel
 * - Espacements cohérents
 */
export function LoadingState({
  message,
  className,
  size = 'md',
}: LoadingStateProps) {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center py-12',
      'min-h-[12rem]',
      className
    )}>
      <Loader2 
        className={cn(
          'animate-spin text-primary mb-4',
          sizeClasses[size]
        )} 
        aria-hidden="true"
      />
      {message && (
        <p className="text-sm text-muted-foreground">
          {message}
        </p>
      )}
      <span className="sr-only">Chargement en cours</span>
    </div>
  );
}

