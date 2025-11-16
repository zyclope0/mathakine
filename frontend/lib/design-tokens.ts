/**
 * Design Tokens - Mathakine
 * 
 * Système de tokens de design pour garantir la cohérence UI/UX
 * Basé sur les best practices académiques UI/UX
 */

/**
 * Espacements (8px base unit)
 */
export const spacing = {
  xs: '0.5rem',    // 8px
  sm: '0.75rem',   // 12px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
} as const;

/**
 * Typographie
 */
export const typography = {
  // Tailles
  sizes: {
    xs: '0.75rem',   // 12px
    sm: '0.875rem',  // 14px
    base: '1rem',    // 16px
    lg: '1.125rem',  // 18px
    xl: '1.25rem',   // 20px
    '2xl': '1.5rem', // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
  },
  // Line heights
  lineHeights: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  },
  // Font weights
  weights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
} as const;

/**
 * Breakpoints Responsive
 */
export const breakpoints = {
  sm: '640px',   // Mobile landscape / Tablet portrait
  md: '768px',   // Tablet landscape
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
  '2xl': '1536px', // Extra large desktop
} as const;

/**
 * Layout
 */
export const layout = {
  // Container max widths
  container: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
    default: '1280px', // max-w-7xl
  },
  // Padding
  padding: {
    page: {
      mobile: spacing.md,    // 16px
      tablet: spacing.lg,    // 24px
      desktop: spacing.xl,   // 32px
    },
    section: {
      mobile: spacing.md,    // 16px
      desktop: spacing.lg,   // 24px
    },
  },
  // Gaps
  gap: {
    section: spacing.lg,     // 24px
    grid: spacing.md,        // 16px
    card: spacing.md,        // 16px
  },
} as const;

/**
 * Grilles Responsive
 */
export const grids = {
  // Colonnes par breakpoint
  cards: {
    mobile: 1,
    tablet: 2,
    desktop: 3,
  },
  // Gaps
  gap: {
    mobile: spacing.md,      // 16px
    tablet: spacing.md,      // 16px
    desktop: spacing.md,     // 16px
  },
} as const;

/**
 * États
 */
export const states = {
  // Loading
  loading: {
    spinnerSize: '2rem',      // 32px
    minHeight: '12rem',       // 192px
  },
  // Empty
  empty: {
    iconSize: '4rem',         // 64px
    minHeight: '12rem',       // 192px
  },
} as const;

/**
 * Animations
 */
export const animations = {
  // Durées
  durations: {
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
  },
  // Easing
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeOut: 'ease-out',
    easeIn: 'ease-in',
  },
} as const;

/**
 * Z-index Layers
 */
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  accessibilityToolbar: 50,
} as const;

/**
 * Border Radius
 */
export const borderRadius = {
  none: '0',
  sm: '0.125rem',   // 2px
  md: '0.375rem',   // 6px
  lg: '0.5rem',     // 8px
  xl: '0.625rem',   // 10px
  '2xl': '0.75rem', // 12px
  full: '9999px',
} as const;

/**
 * Shadows
 */
export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  card: '0 4px 12px rgba(124, 58, 237, 0.15)',
} as const;

