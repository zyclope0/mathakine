import { cn } from "@/lib/utils/cn";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
  variant?: "default" | "text" | "circular" | "rectangular";
  width?: string | number;
  height?: string | number;
}

/**
 * Skeleton - Composant pour afficher un placeholder de chargement
 *
 * Variantes :
 * - default : Rectangle arrondi
 * - text : Ligne de texte
 * - circular : Cercle (pour avatars)
 * - rectangular : Rectangle sans arrondi
 */
export function Skeleton({
  className,
  variant = "default",
  width,
  height,
  style,
  ...props
}: SkeletonProps) {
  const baseClasses = "animate-pulse bg-muted relative overflow-hidden";

  const variantClasses = {
    default: "rounded-md",
    text: "rounded-md h-4",
    circular: "rounded-full",
    rectangular: "rounded-none",
  };

  const customStyle = {
    ...style,
    ...(width && { width: typeof width === "number" ? `${width}px` : width }),
    ...(height && { height: typeof height === "number" ? `${height}px` : height }),
  };

  return (
    <div
      className={cn(baseClasses, variantClasses[variant], className)}
      style={customStyle}
      aria-hidden="true"
      {...props}
    >
      {/* Shimmer effect */}
      <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </div>
  );
}

/**
 * SkeletonText - Composant pour afficher plusieurs lignes de texte skeleton
 */
interface SkeletonTextProps {
  lines?: number;
  className?: string;
  lastLineWidth?: string;
}

export function SkeletonText({ lines = 3, className, lastLineWidth = "60%" }: SkeletonTextProps) {
  return (
    <div className={cn("space-y-2", className)} aria-hidden="true">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          variant="text"
          style={index === lines - 1 ? { width: lastLineWidth } : undefined}
        />
      ))}
    </div>
  );
}

/**
 * SkeletonCard - Composant pour afficher une card skeleton complète
 */
interface SkeletonCardProps {
  className?: string;
  showAvatar?: boolean;
  lines?: number;
}

export function SkeletonCard({ className, showAvatar = false, lines = 3 }: SkeletonCardProps) {
  return (
    <div className={cn("rounded-xl border bg-card p-6 shadow-sm", className)} aria-hidden="true">
      <div className="flex items-start gap-4">
        {showAvatar && <Skeleton variant="circular" width={48} height={48} />}
        <div className="flex-1 space-y-3">
          <Skeleton variant="text" height={20} width="80%" />
          <SkeletonText lines={lines} lastLineWidth="60%" />
        </div>
      </div>
    </div>
  );
}
