"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { ThemeSelectorCompact } from "@/components/theme/ThemeSelectorCompact";
import { DarkModeToggle } from "@/components/theme/DarkModeToggle";
import { LanguageSelector } from "@/components/locale/LanguageSelector";
import { Menu, X } from "lucide-react";
import { LogoMathakine } from "@/components/LogoMathakine";
import { useState, useMemo, useCallback } from "react";
import { useTranslations } from "next-intl";
import { isAdminRole, isApprenantRole } from "@/lib/auth/userRoles";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { useChatStore } from "@/lib/stores/chatStore";
import { HeaderDesktopNav } from "@/components/layout/HeaderDesktopNav";
import { HeaderUserMenu } from "@/components/layout/HeaderUserMenu";
import { HeaderMobileMenu } from "@/components/layout/HeaderMobileMenu";
import { buildHeaderNavigation, isHeaderNavLinkActive } from "@/lib/layout/headerNavigation";
import { FeedbackTrigger } from "@/components/feedback/FeedbackTrigger";

export function Header() {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useAuth();
  const { setOpen: setChatOpen } = useChatStore();
  const tHome = useTranslations("home");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const t = useTranslations("navigation");
  const tAuth = useTranslations("auth");
  const { shouldReduceMotion, createTransition } = useAccessibleAnimation();

  const isAdmin = isAdminRole(user?.role);
  const isStudent = isApprenantRole(user?.role);
  // Non vérifié : menu restreint sauf si access_scope === "full" (période de grâce).
  // Évite d'afficher le menu complet quand access_scope est undefined (chargement, cache).
  const hasFullAccess = user?.is_email_verified === true || user?.access_scope === "full";

  const navLabels = useMemo(
    () => ({
      homeLearner: t("homeLearner"),
      dashboard: t("dashboard"),
      exercises: t("exercises"),
      challenges: t("challenges"),
      badges: t("badges"),
      leaderboard: t("leaderboard"),
    }),
    [t]
  );

  const { navPrimary, navSecondary } = useMemo(
    () => buildHeaderNavigation({ isAuthenticated, hasFullAccess, isStudent }, navLabels),
    [isAuthenticated, hasFullAccess, isStudent, navLabels]
  );

  const isActive = useCallback((href: string) => isHeaderNavLinkActive(pathname, href), [pathname]);

  const onOpenAssistant = useCallback(() => setChatOpen(true), [setChatOpen]);

  return (
    <>
      {/* Skip link pour navigation clavier (WCAG 2.1 AAA) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:outline-4 focus:outline-solid focus:outline-ring focus:outline-offset-2"
        aria-label="Aller au contenu principal"
      >
        Aller au contenu principal
      </a>
      <header className="header-app-shell fixed top-0 left-0 right-0 z-40 w-full" role="banner">
        <nav className="container mx-auto px-4 sm:px-6 lg:px-8" aria-label="Navigation principale">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center">
              <Link
                href="/"
                className="flex items-center transition-opacity hover:opacity-80"
                aria-label="Retour à l'accueil — Mathakine"
              >
                <LogoMathakine className="h-8 w-auto" />
              </Link>
            </div>

            <HeaderDesktopNav
              navPrimary={navPrimary}
              navSecondary={navSecondary}
              isActive={isActive}
              showAssistantCta={isAuthenticated}
              ctaAssistantLabel={tHome("hero.ctaAssistant")}
              onOpenAssistant={onOpenAssistant}
            />

            {/* Actions droite */}
            <div className="flex items-center gap-2">
              <LanguageSelector />
              <ThemeSelectorCompact />
              <DarkModeToggle />

              <span className="hidden md:inline-flex md:items-center">
                <FeedbackTrigger componentId="header-nav" variant="ghost" layout="icon" />
              </span>

              {isAuthenticated ? (
                <HeaderUserMenu
                  user={user}
                  userMenuAriaLabel={`Menu utilisateur : ${user?.username}`}
                  onLogout={logout}
                  profileLabel={t("profile")}
                  settingsLabel={t("settings")}
                  dashboardLabel={t("dashboard")}
                  adminLabel={t("admin")}
                  logoutLabel={tAuth("logout")}
                  hasFullAccess={hasFullAccess}
                  isStudent={isStudent}
                  isAdmin={isAdmin}
                />
              ) : (
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" asChild>
                    <Link href="/login">{tAuth("login.title")}</Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link href="/register">{tAuth("register.title")}</Link>
                  </Button>
                </div>
              )}

              {/* Menu mobile */}
              <Button
                variant="ghost"
                size="sm"
                className="md:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label={mobileMenuOpen ? "Fermer le menu" : "Ouvrir le menu"}
                aria-expanded={mobileMenuOpen}
                aria-controls="mobile-nav-menu"
              >
                {mobileMenuOpen ? (
                  <X className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Menu className="h-5 w-5" aria-hidden="true" />
                )}
              </Button>
            </div>
          </div>

          <HeaderMobileMenu
            open={mobileMenuOpen}
            navPrimary={navPrimary}
            navSecondary={navSecondary}
            isActive={isActive}
            onNavigate={() => setMobileMenuOpen(false)}
            shouldReduceMotion={shouldReduceMotion}
            createTransition={createTransition}
            showAssistantCta={isAuthenticated}
            ctaAssistantLabel={tHome("hero.ctaAssistant")}
            onOpenAssistant={onOpenAssistant}
          />
        </nav>
      </header>
    </>
  );
}
