import type { LucideIcon } from "lucide-react";
import { Home } from "lucide-react";

export interface HeaderNavLabels {
  homeLearner: string;
  dashboard: string;
  exercises: string;
  challenges: string;
  badges: string;
  leaderboard: string;
}

export interface HeaderNavPrimaryItem {
  name: string;
  href: string;
  icon?: LucideIcon;
}

export interface HeaderNavSecondaryItem {
  name: string;
  href: string;
}

export interface HeaderNavFlags {
  isAuthenticated: boolean;
  hasFullAccess: boolean;
  isStudent: boolean;
}

/**
 * Builds primary/secondary nav items for the app shell header (desktop + mobile).
 * Mirrors previous inline logic in Header.tsx — no React, no i18n calls here.
 */
export function buildHeaderNavigation(
  flags: HeaderNavFlags,
  labels: HeaderNavLabels
): { navPrimary: HeaderNavPrimaryItem[]; navSecondary: HeaderNavSecondaryItem[] } {
  const { isAuthenticated, hasFullAccess, isStudent } = flags;

  const navPrimary: HeaderNavPrimaryItem[] = [];

  if (isAuthenticated) {
    if (hasFullAccess) {
      if (isStudent) {
        navPrimary.push({ name: labels.homeLearner, href: "/home-learner", icon: Home });
      } else {
        navPrimary.push({ name: labels.dashboard, href: "/dashboard" });
      }
    }
    navPrimary.push({ name: labels.exercises, href: "/exercises" });
    if (hasFullAccess) {
      navPrimary.push({ name: labels.challenges, href: "/challenges" });
    }
  }

  const navSecondary: HeaderNavSecondaryItem[] =
    isAuthenticated && hasFullAccess
      ? [
          { name: labels.badges, href: "/badges" },
          { name: labels.leaderboard, href: "/leaderboard" },
        ]
      : [];

  return { navPrimary, navSecondary };
}

export function isHeaderNavLinkActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname.startsWith(href);
}
