interface LogoMathakineProps {
  className?: string;
  alt?: string;
}

/**
 * Logo Mathakine inline SVG — les var() CSS héritent du thème actif.
 * IDs préfixés pour éviter les conflits si plusieurs instances coexistent.
 */
export function LogoMathakine({ className = "", alt = "Mathakine" }: LogoMathakineProps) {
  return (
    <svg
      viewBox="0 0 400 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      role="img"
      aria-label={alt}
    >
      <defs>
        <linearGradient id="lm-glass-base" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--logo-highlight, #ffffff)" stopOpacity="0.8" />
          <stop offset="100%" stopColor="var(--logo-base, #8b5cf6)" stopOpacity="0.2" />
        </linearGradient>

        <radialGradient id="lm-glow-grad" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="var(--logo-glow, #fbbf24)" stopOpacity="0.8" />
          <stop offset="100%" stopColor="var(--logo-glow, #fbbf24)" stopOpacity="0" />
        </radialGradient>

        <filter id="lm-glow-filter" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* Lignes géométriques décoratives */}
      <g stroke="var(--logo-accents, #cbd5e1)" strokeWidth="1.5" fill="none" opacity="0.6">
        <path d="M 50 15 L 30 40 L 70 45 L 50 15" strokeDasharray="2 2" />
        <path d="M 70 45 L 90 30" strokeDasharray="2 2" />
      </g>
      <circle cx="30" cy="40" r="3" fill="var(--logo-accents, #cbd5e1)" />
      <circle cx="70" cy="45" r="3" fill="var(--logo-accents, #cbd5e1)" />
      <circle cx="90" cy="30" r="2.5" fill="var(--logo-accents, #cbd5e1)" />

      {/* Point lumineux au sommet du M */}
      <circle cx="50" cy="15" r="8" fill="url(#lm-glow-grad)" filter="url(#lm-glow-filter)" />
      <circle cx="50" cy="15" r="4" fill="var(--logo-highlight, #ffffff)" />

      {/* M — stroke épais en forme de W */}
      <path
        d="M 10 90 L 30 25 L 50 85 L 70 25 L 90 90"
        stroke="url(#lm-glass-base)"
        strokeWidth="14"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M 10 90 L 30 25 L 50 85 L 70 25 L 90 90"
        stroke="var(--logo-highlight, #ffffff)"
        strokeWidth="1"
        fill="none"
        opacity="0.5"
      />

      {/* Texte "athakine" */}
      <text
        x="105"
        y="85"
        fontFamily="system-ui, -apple-system, sans-serif"
        fontSize="68"
        fontWeight="800"
        fill="var(--logo-text, #e2e8f0)"
        letterSpacing="-0.04em"
      >
        athakine
      </text>
    </svg>
  );
}
