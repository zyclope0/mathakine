/**
 * FFI-L17A + FFI-L17B — single source of truth for frontend architecture guardrails.
 * Node/test consumption only: do not import from client components (keeps bundle clean).
 *
 * Line budgets: physical line count === split(/\r?\n/).length (wc -l style), including blanks.
 */

export type ProtectedSurfaceCategory =
  | "page-container"
  | "shell-facade"
  | "shared-facade"
  | "chat-shell";

export interface ProtectedFrontendSurface {
  /** Path relative to the frontend package root (directory containing package.json). */
  relativePath: string;
  maxLines: number;
  category: ProtectedSurfaceCategory;
  reason: string;
}

export interface AllowedDenseException {
  relativePath: string;
  maxLines: number;
  reason: string;
  /** Optional follow-up when a deeper split is planned. */
  followUpLotHint?: string;
}

export interface RequiredArchitectureSeam {
  relativePath: string;
  role: string;
}

/** Canonical lib files that anchor shared contracts (constants, pure helpers, HTTP, roles). FFI-L17B */
export interface RequiredCanonicalLibFile {
  relativePath: string;
  role: string;
}

/**
 * Human-readable ownership rules (mirrored in docs/04-FRONTEND/ARCHITECTURE.md).
 * Kept here so tests can assert the contract is non-empty and docs drift is noticed in review.
 */
export interface OwnershipRuleGroup {
  readonly id: string;
  readonly summary: string;
  readonly bullets: readonly string[];
}

/** Facades and thin containers delivered by FFI-L11–L16; must not silently regrow. */
export const PROTECTED_FRONTEND_SURFACES: readonly ProtectedFrontendSurface[] = [
  {
    relativePath: "app/profile/page.tsx",
    maxLines: 220,
    category: "page-container",
    reason: "FFI-L11: thin page + useProfilePageController + sections",
  },
  {
    relativePath: "app/settings/page.tsx",
    maxLines: 170,
    category: "page-container",
    reason: "FFI-L13: thin page + useSettingsPageController + sections",
  },
  {
    relativePath: "app/badges/page.tsx",
    maxLines: 300,
    category: "page-container",
    reason: "FFI-L12: thin page + useBadgesPageController + sections",
  },
  {
    relativePath: "app/admin/content/page.tsx",
    maxLines: 90,
    category: "page-container",
    reason: "FFI-L14: thin admin content shell + controller + domain sections",
  },
  {
    relativePath: "app/dashboard/page.tsx",
    maxLines: 220,
    category: "page-container",
    reason: "FFI-L20A: thin dashboard shell + useDashboardPageController + tab sections",
  },
  {
    relativePath: "app/exercises/page.tsx",
    maxLines: 340,
    category: "page-container",
    reason: "FFI-L15: shared list controller + domain-specific chrome",
  },
  {
    relativePath: "app/challenges/page.tsx",
    maxLines: 320,
    category: "page-container",
    reason: "FFI-L15: shared list controller + domain-specific chrome",
  },
  {
    relativePath: "components/layout/Header.tsx",
    maxLines: 220,
    category: "shell-facade",
    reason: "FFI-L16: shell orchestrates HeaderDesktopNav / HeaderUserMenu / HeaderMobileMenu",
  },
  {
    relativePath: "components/shared/ContentListProgressiveFilterToolbar.tsx",
    maxLines: 240,
    category: "shared-facade",
    reason: "FFI-L15: progressive filter facade; subcomponents hold detail",
  },
  {
    relativePath: "components/shared/ContentListResultsSection.tsx",
    maxLines: 160,
    category: "shared-facade",
    reason: "FFI-L15: shared results shell for exercises/challenges lists",
  },
  {
    relativePath: "components/challenges/ChallengeSolverCommandBar.tsx",
    maxLines: 190,
    category: "shared-facade",
    reason:
      "FFI-L18B: solver command bar facade; interaction blocks are ChallengeSolver* subcomponents",
  },
  {
    relativePath: "components/profile/ProfileLearningPreferencesSection.tsx",
    maxLines: 160,
    category: "shared-facade",
    reason: "FFI-L18A: learning preferences section facade; field blocks are subcomponents",
  },
  {
    relativePath: "components/chat/ChatbotFloating.tsx",
    maxLines: 280,
    category: "chat-shell",
    reason: "FFI-L16: global chat drawer shell under components/chat",
  },
  {
    relativePath: "components/chat/ChatbotFloatingGlobal.tsx",
    maxLines: 60,
    category: "chat-shell",
    reason: "FFI-L16: global FAB mount for assistant",
  },
  {
    relativePath: "components/exercises/ExerciseSolver.tsx",
    maxLines: 380,
    category: "shared-facade",
    reason:
      "FFI-L20B: exercise solver facade; runtime in useExerciseSolverController + exerciseSolverFlow",
  },
  {
    relativePath: "components/providers/Providers.tsx",
    maxLines: 90,
    category: "shell-facade",
    reason:
      "FFI-L20C: root provider composition; theme/a11y sync in ThemeBootstrap + Accessibility*",
  },
  {
    relativePath: "components/badges/BadgeCard.tsx",
    maxLines: 520,
    category: "shared-facade",
    reason:
      "FFI-L20D: badge card presentation; difficulty/rarity/progress derivations in lib/badges/badgePresentation",
  },
  {
    relativePath: "components/badges/BadgesProgressTabsSection.tsx",
    maxLines: 280,
    category: "shared-facade",
    reason:
      "FFI-L20D: badges progress tabs; shared medal + motivation helpers from badgePresentation",
  },
];

/** Dense seams explicitly tolerated until a dedicated split lot (not FFI-L17). */
export const ALLOWED_DENSE_EXCEPTIONS: readonly AllowedDenseException[] = [];

/** Files that must exist: they materialize prior refactors (hooks, admin domains, shell, chat). */
export const REQUIRED_ARCHITECTURE_SEAMS: readonly RequiredArchitectureSeam[] = [
  {
    relativePath: "hooks/useProfilePageController.ts",
    role: "FFI-L11 profile page runtime",
  },
  {
    relativePath: "hooks/useSettingsPageController.ts",
    role: "FFI-L13 settings page runtime",
  },
  {
    relativePath: "hooks/useBadgesPageController.ts",
    role: "FFI-L12 badges page runtime",
  },
  {
    relativePath: "hooks/useAdminContentPageController.ts",
    role: "FFI-L14 admin content shell runtime",
  },
  {
    relativePath: "hooks/useContentListPageController.ts",
    role: "FFI-L15 shared exercises/challenges list runtime",
  },
  {
    relativePath: "hooks/useDashboardPageController.ts",
    role: "FFI-L20A dashboard page runtime",
  },
  {
    relativePath: "hooks/useExerciseSolverController.ts",
    role: "FFI-L20B exercise solver runtime (sessions, review, navigation glue)",
  },
  {
    relativePath: "hooks/useAuth.ts",
    role: "FFI-L20C auth hook facade (React Query + sync + routing + toasts)",
  },
  {
    relativePath: "components/providers/ThemeBootstrap.tsx",
    role: "FFI-L20C theme bootstrap + DOM theme application",
  },
  {
    relativePath: "components/providers/AccessibilityDomSync.tsx",
    role: "FFI-L20C accessibility flags to documentElement",
  },
  {
    relativePath: "components/providers/AccessibilityHotkeys.tsx",
    role: "FFI-L20C global accessibility keyboard shortcuts",
  },
  {
    relativePath: "hooks/chat/useGuestChatAccess.ts",
    role: "FFI-L16 guest chat session quota (sessionStorage)",
  },
  {
    relativePath: "components/admin/content/AdminExercisesSection.tsx",
    role: "FFI-L14 admin content domain — exercises",
  },
  {
    relativePath: "components/admin/content/AdminChallengesSection.tsx",
    role: "FFI-L14 admin content domain — challenges",
  },
  {
    relativePath: "components/admin/content/AdminBadgesSection.tsx",
    role: "FFI-L14 admin content domain — badges",
  },
  {
    relativePath: "components/layout/HeaderDesktopNav.tsx",
    role: "FFI-L16 shell — desktop navigation + authenticated Assistant CTA",
  },
  {
    relativePath: "components/layout/HeaderUserMenu.tsx",
    role: "FFI-L16 shell — user menu",
  },
  {
    relativePath: "components/layout/HeaderMobileMenu.tsx",
    role: "FFI-L16 shell — mobile drawer",
  },
  {
    relativePath: "components/chat/ChatbotFloating.tsx",
    role: "FFI-L16 global chat drawer UI",
  },
  {
    relativePath: "components/chat/ChatbotFloatingGlobal.tsx",
    role: "FFI-L16 global FAB + drawer mount",
  },
];

/** Global chatbot must not move back under home (FFI-L16 ownership). */
export const CHATBOT_FLOATING_GLOBAL_CANONICAL = "components/chat/ChatbotFloatingGlobal.tsx";

export const CHATBOT_FLOATING_GLOBAL_FORBIDDEN_HOME = "components/home/ChatbotFloatingGlobal.tsx";

/**
 * Global assistant mount must live only under components/chat/ (FFI-L16 + FFI-L17B).
 * Layout/home must not host a duplicate FloatingGlobal.
 */
export const FORBIDDEN_CHATBOT_FLOATING_GLOBAL_PATHS: readonly string[] = [
  CHATBOT_FLOATING_GLOBAL_FORBIDDEN_HOME,
  "components/layout/ChatbotFloatingGlobal.tsx",
];

/**
 * Lib-layer sources of truth that must remain present (rename = update this list in the same PR).
 */
export const REQUIRED_CANONICAL_LIB_FILES: readonly RequiredCanonicalLibFile[] = [
  { relativePath: "lib/api/client.ts", role: "Central HTTP client, CSRF, auth headers" },
  { relativePath: "lib/auth/userRoles.ts", role: "Canonical roles + NI-13 alignment" },
  { relativePath: "lib/constants/exercises.ts", role: "Shared exercise labels / maps" },
  { relativePath: "lib/constants/challenges.ts", role: "Shared challenge labels / maps" },
  { relativePath: "lib/constants/badges.ts", role: "Shared badge-related constants" },
  {
    relativePath: "lib/constants/contentListOrder.ts",
    role: "Shared content-list ordering (FFI-L15)",
  },
  { relativePath: "lib/profile/profilePage.ts", role: "Pure profile page helpers (FFI-L11)" },
  {
    relativePath: "lib/profile/profileLearningPreferences.ts",
    role: "Pure learning preferences helpers (FFI-L18A)",
  },
  { relativePath: "lib/settings/settingsPage.ts", role: "Pure settings page helpers (FFI-L13)" },
  { relativePath: "lib/badges/badgesPage.ts", role: "Pure badges page helpers (FFI-L12)" },
  {
    relativePath: "lib/admin/content/adminContentPage.ts",
    role: "Pure admin content shell helpers (FFI-L14)",
  },
  {
    relativePath: "lib/challenges/challengeSolver.ts",
    role: "Pure challenge solver helpers (FFI-L10)",
  },
  {
    relativePath: "lib/challenges/challengeSolverCommandBar.ts",
    role: "Pure command bar branch helpers (FFI-L18B)",
  },
  { relativePath: "lib/contentList/pageHelpers.ts", role: "Shared list page helpers (FFI-L15)" },
  {
    relativePath: "lib/layout/headerNavigation.ts",
    role: "Shell navigation config / helpers (FFI-L16)",
  },
  {
    relativePath: "lib/exercises/exerciseSolverFlow.ts",
    role: "Pure exercise solver flow helpers (FFI-L20B)",
  },
  {
    relativePath: "lib/badges/types.ts",
    role: "Shared badge progress / rarity contracts (FFI-L20D)",
  },
  {
    relativePath: "lib/badges/badgePresentation.ts",
    role: "Pure badge UI presentation helpers — difficulty, medals, sort, motivation (FFI-L20D)",
  },
  {
    relativePath: "lib/auth/types.ts",
    role: "Shared frontend auth payload/response types (FFI-L20C)",
  },
  {
    relativePath: "lib/auth/authLoginFlow.ts",
    role: "Pure auth flow helpers for useAuth (FFI-L20C)",
  },
  {
    relativePath: "lib/auth/postLoginRedirect.ts",
    role: "Post-login path override seam (register auto-login) (FFI-L20C)",
  },
];

/** Active ownership conventions (FFI-L17B). */
export const OWNERSHIP_RULE_GROUPS: readonly OwnershipRuleGroup[] = [
  {
    id: "constants-and-pure-helpers",
    summary: "Centralised contracts and pure domain logic",
    bullets: [
      "Cross-route constants and label/type maps belong in lib/constants/* — do not duplicate the same maps inside pages or facades.",
      "Pure, testable domain logic belongs in lib/<domain>/* (e.g. lib/profile/, lib/challenges/challengeSolver.ts, lib/contentList/).",
      "Validation schemas stay under lib/validation/* when shared; keep page-specific glue out of lib unless reused.",
    ],
  },
  {
    id: "runtime-vs-view",
    summary: "Where state and UI split",
    bullets: [
      "Page-local orchestration and derived state live in hooks/* controllers (use*PageController, useContentListPageController, etc.).",
      "components/* hold presentation: favour props-in / events-out; avoid embedding large imperative workflows inline in JSX.",
      "App Router pages under app/*/page.tsx stay thin: compose hooks + section components rather than growing god-pages.",
    ],
  },
  {
    id: "facades",
    summary: "Shared and shell facades",
    bullets: [
      "Shared facades (e.g. ContentListProgressiveFilterToolbar) orchestrate subcomponents; they must not absorb domain-specific business rules that belong in hooks or lib/.",
      "Shell navigation stays under components/layout/*; global assistant UI stays under components/chat/* (see chatbot paths below).",
    ],
  },
  {
    id: "admin-and-content-list",
    summary: "Admin + learner lists",
    bullets: [
      "Admin content domains remain in components/admin/content/* sections; the page shell stays a thin entry (FFI-L14).",
      "Exercises/challenges list pages share the content-list controller and shared shells; keep domain-specific cards/modals/generators in their domains.",
    ],
  },
  {
    id: "ffi-l18-follow-up",
    summary: "Post–FFI-L18 challenge solver",
    bullets: [
      "ChallengeSolverCommandBar is a thin facade (FFI-L18B); interaction blocks live under components/challenges/ChallengeSolver*.tsx; regrowth guarded by PROTECTED_FRONTEND_SURFACES.",
      "Do not grow other protected surfaces to compensate; split along hook + section boundaries instead.",
    ],
  },
  {
    id: "ffi-l20c-auth-kernel",
    summary: "Auth hook + root providers (FFI-L20C)",
    bullets: [
      "Shared auth payload/response types and pure flow branches live under lib/auth/types.ts and lib/auth/authLoginFlow.ts; post-login redirect override lives in lib/auth/postLoginRedirect.ts (not a React store).",
      "hooks/useAuth.ts remains the single public hook facade for login/register/logout/forgot-password and React Query cache wiring.",
      "components/providers/Providers.tsx composes root providers only; theme DOM sync, accessibility class sync, and global a11y hotkeys live in ThemeBootstrap / AccessibilityDomSync / AccessibilityHotkeys.",
    ],
  },
  {
    id: "ffi-l20d-badges-domain",
    summary: "Badges presentation contracts (FFI-L20D)",
    bullets: [
      "Shared badge progress and API-shaped items live in lib/badges/types.ts (re-exported from useBadgesProgress / badgesPage where needed).",
      "Pure presentation logic — difficulty classes, medal SVG paths, grid sort, locked/in-progress motivation branches — lives in lib/badges/badgePresentation.ts.",
      "BadgeCard and BadgesProgressTabsSection remain view-first; they consume helpers instead of duplicating medal paths or >=50% motivation rules.",
    ],
  },
];

export function collectMissingSeams(fileExists: (relativePath: string) => boolean): string[] {
  const issues: string[] = [];
  for (const seam of REQUIRED_ARCHITECTURE_SEAMS) {
    if (!fileExists(seam.relativePath)) {
      issues.push(
        `Missing required seam: ${seam.relativePath} (${seam.role}). Restore or update REQUIRED_ARCHITECTURE_SEAMS if renamed intentionally.`
      );
    }
  }
  return issues;
}

export function collectProtectedBudgetViolations(
  lineCounts: Readonly<Record<string, number>>
): string[] {
  const issues: string[] = [];
  for (const s of PROTECTED_FRONTEND_SURFACES) {
    const n = lineCounts[s.relativePath];
    if (n === undefined) {
      issues.push(
        `No line count recorded for protected surface ${s.relativePath} (${s.category}).`
      );
      continue;
    }
    if (n > s.maxLines) {
      issues.push(
        `${s.relativePath}: ${n} lines exceeds budget ${s.maxLines} [${s.category}]. Intent: ${s.reason}. Extract hook, sections, or pure helpers instead of growing this file.`
      );
    }
  }
  return issues;
}

export function collectDenseExceptionViolations(
  lineCounts: Readonly<Record<string, number>>,
  fileExists: (relativePath: string) => boolean
): string[] {
  const issues: string[] = [];
  for (const ex of ALLOWED_DENSE_EXCEPTIONS) {
    if (!fileExists(ex.relativePath)) {
      issues.push(
        `Documented dense exception missing: ${ex.relativePath}. If removed, delete from ALLOWED_DENSE_EXCEPTIONS or replace with new seam.`
      );
      continue;
    }
    const n = lineCounts[ex.relativePath];
    if (n === undefined) {
      issues.push(`No line count recorded for dense exception ${ex.relativePath}.`);
      continue;
    }
    if (n > ex.maxLines) {
      issues.push(
        `${ex.relativePath}: ${n} lines exceeds tolerated budget ${ex.maxLines}. ${ex.reason}${ex.followUpLotHint ? ` Planned follow-up: ${ex.followUpLotHint}.` : ""}`
      );
    }
  }
  return issues;
}

export function collectChatbotGlobalOwnershipViolations(
  fileExists: (relativePath: string) => boolean
): string[] {
  const issues: string[] = [];
  if (!fileExists(CHATBOT_FLOATING_GLOBAL_CANONICAL)) {
    issues.push(
      `ChatbotFloatingGlobal must exist at ${CHATBOT_FLOATING_GLOBAL_CANONICAL} (FFI-L16).`
    );
  }
  for (const badPath of FORBIDDEN_CHATBOT_FLOATING_GLOBAL_PATHS) {
    if (fileExists(badPath)) {
      issues.push(
        `Forbidden: ${badPath} — global ChatbotFloatingGlobal must only live under components/chat/ (FFI-L16).`
      );
    }
  }
  return issues;
}

export function collectMissingCanonicalLibFiles(
  fileExists: (relativePath: string) => boolean
): string[] {
  const issues: string[] = [];
  for (const f of REQUIRED_CANONICAL_LIB_FILES) {
    if (!fileExists(f.relativePath)) {
      issues.push(
        `Missing canonical lib file: ${f.relativePath} (${f.role}). Restore or update REQUIRED_CANONICAL_LIB_FILES in the same PR if renamed.`
      );
    }
  }
  return issues;
}
