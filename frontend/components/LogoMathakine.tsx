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
        <linearGradient id="lm-layer-back" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--logo-base, #6366f1)" stopOpacity="0.9" />
          <stop offset="100%" stopColor="var(--logo-base, #6366f1)" stopOpacity="0.2" />
        </linearGradient>

        <linearGradient id="lm-layer-front" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0%" stopColor="var(--logo-highlight, #22d3ee)" stopOpacity="0.9" />
          <stop offset="100%" stopColor="var(--logo-base, #6366f1)" stopOpacity="0.4" />
        </linearGradient>

        <radialGradient id="lm-glow" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0%" stopColor="var(--logo-glow, #fbbf24)" stopOpacity="0.8" />
          <stop offset="100%" stopColor="var(--logo-glow, #fbbf24)" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Lignes géométriques décoratives */}
      <g stroke="var(--logo-accents, #94a3b8)" strokeWidth="1.5" opacity="0.6">
        <line x1="50" y1="12" x2="30" y2="35" strokeDasharray="2 2" />
        <line x1="50" y1="12" x2="70" y2="35" strokeDasharray="2 2" />
        <line x1="30" y1="35" x2="50" y2="52" strokeDasharray="2 2" />
        <line x1="70" y1="35" x2="50" y2="52" strokeDasharray="2 2" />
      </g>
      <circle cx="30" cy="35" r="2.5" fill="var(--logo-accents, #94a3b8)" />
      <circle cx="70" cy="35" r="2.5" fill="var(--logo-accents, #94a3b8)" />
      <circle cx="50" cy="52" r="2.5" fill="var(--logo-accents, #94a3b8)" />

      {/* Point lumineux au sommet du M */}
      <circle cx="50" cy="12" r="9" fill="url(#lm-glow)" />
      <circle cx="50" cy="12" r="3" fill="var(--logo-highlight, #ffffff)" />

      {/* M — jambes gauche et droite */}
      <path d="M 10 90 L 35 25 L 50 60 L 25 90 Z" fill="url(#lm-layer-back)" />
      <path d="M 90 90 L 65 25 L 50 60 L 75 90 Z" fill="url(#lm-layer-back)" />

      {/* M — face avant centrale */}
      <path d="M 18 90 L 50 28 L 82 90 L 67 90 L 50 55 L 33 90 Z" fill="url(#lm-layer-front)" />
      <path
        d="M 18 90 L 50 28 L 82 90 L 67 90 L 50 55 L 33 90 Z"
        stroke="var(--logo-highlight, #ffffff)"
        strokeWidth="0.5"
        strokeOpacity="0.6"
        fill="none"
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
