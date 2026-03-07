interface LogoBadgeProps {
  className?: string;
  alt?: string;
}

/**
 * Badge Logo Mathakine — symbole M (deux pics + points) dans un cercle.
 * Utilise les tokens CSS du Design System (--logo-*, --primary).
 */
export function LogoBadge({ className = "", alt = "Mathakine" }: LogoBadgeProps) {
  return (
    <div
      className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-full border border-border/50 bg-card/40 shadow-[0_0_15px_color-mix(in_srgb,var(--primary)_20%,transparent)] backdrop-blur-md ${className}`}
      role="img"
      aria-label={alt}
    >
      <svg
        viewBox="5 15 90 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="h-8 w-8"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="badge-glass-base" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--logo-highlight, #ffffff)" stopOpacity="0.8" />
            <stop offset="100%" stopColor="var(--logo-base, var(--primary))" stopOpacity="0.2" />
          </linearGradient>
          <radialGradient id="badge-glow-grad" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0%" stopColor="var(--logo-glow, #fbbf24)" stopOpacity="0.8" />
            <stop offset="100%" stopColor="var(--logo-glow, #fbbf24)" stopOpacity="0" />
          </radialGradient>
          <filter id="badge-glow-filter" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        {/* Points décoratifs (accents) */}
        <circle cx="30" cy="40" r="3" fill="var(--logo-accents, var(--primary))" />
        <circle cx="70" cy="45" r="3" fill="var(--logo-accents, var(--primary))" />
        {/* Point lumineux au sommet du M */}
        <circle
          cx="50"
          cy="15"
          r="8"
          fill="url(#badge-glow-grad)"
          filter="url(#badge-glow-filter)"
        />
        <circle cx="50" cy="15" r="4" fill="var(--logo-highlight, #ffffff)" />
        {/* M — stroke épais */}
        <path
          d="M 10 90 L 30 25 L 50 85 L 70 25 L 90 90"
          stroke="url(#badge-glass-base)"
          strokeWidth="14"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* M — highlight fin */}
        <path
          d="M 10 90 L 30 25 L 50 85 L 70 25 L 90 90"
          stroke="var(--logo-highlight, #ffffff)"
          strokeWidth="1"
          fill="none"
          opacity="0.5"
        />
      </svg>
    </div>
  );
}
