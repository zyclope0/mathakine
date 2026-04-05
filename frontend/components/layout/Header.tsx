"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { ThemeSelectorCompact } from "@/components/theme/ThemeSelectorCompact";
import { DarkModeToggle } from "@/components/theme/DarkModeToggle";
import { LanguageSelector } from "@/components/locale/LanguageSelector";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Home,
  LogOut,
  User,
  Menu,
  X,
  Settings,
  ChevronDown,
  Shield,
  MessageCircle,
} from "lucide-react";
import { LogoMathakine } from "@/components/LogoMathakine";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";
import { AnimatePresence, LazyMotion, domAnimation, m } from "framer-motion";
import { isAdminRole, isApprenantRole } from "@/lib/auth/userRoles";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { useChatStore } from "@/lib/stores/chatStore";

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

  // Navigation principale — primaire (actions fréquentes) + secondaire (consultation)
  // "Accueil" supprimé : le logo remplit ce rôle (doublon)
  const navPrimary = [
    ...(isAuthenticated
      ? [
          // Apprenant → page dédiée ; adulte → dashboard analytique
          ...(hasFullAccess
            ? [
                isStudent
                  ? { name: t("homeLearner"), href: "/home-learner", icon: Home }
                  : { name: t("dashboard"), href: "/dashboard" },
              ]
            : []),
          { name: t("exercises"), href: "/exercises" },
          ...(hasFullAccess ? [{ name: t("challenges"), href: "/challenges" }] : []),
        ]
      : []),
  ];

  // Secondaire : consultation, pas actions principales
  const navSecondary = isAuthenticated && hasFullAccess
    ? [
        { name: t("badges"), href: "/badges" },
        { name: t("leaderboard"), href: "/leaderboard" },
      ]
    : [];

  // Assistant toujours en fin, comme affordance globale
  const navigation = [
    ...navPrimary,
    ...navSecondary,
    { name: tHome("hero.ctaAssistant"), href: "#", icon: MessageCircle, isAssistant: true },
  ];

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  };

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
      <header
        className="fixed top-0 left-0 right-0 z-40 w-full border-b border-border bg-background"
        role="banner"
      >
        <nav className="container mx-auto px-4 sm:px-6 lg:px-8" aria-label="Navigation principale">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center">
              <Link
                href="/"
                className="flex items-center transition-opacity hover:opacity-80"
                aria-label="Retour à l'accueil — Mathakine"
              >
                <LogoMathakine className="h-8 w-auto" alt="" />
              </Link>
            </div>

            {/* Navigation Desktop */}
            <div className="hidden md:flex md:items-center md:space-x-1">
              {/* Primaire : poids fort, hiérarchie principale */}
              {navPrimary.map((item) => {
                const Icon = "icon" in item ? item.icon : undefined;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "px-3 py-2 text-sm font-medium rounded-md transition-colors",
                      isActive(item.href)
                        ? "bg-primary/10 text-primary-on-dark"
                        : "text-foreground/80 hover:text-foreground hover:bg-accent/10"
                    )}
                    aria-current={isActive(item.href) ? "page" : undefined}
                  >
                    <span className="flex items-center gap-2">
                      {Icon && <Icon className="h-4 w-4" aria-hidden="true" />}
                      {item.name}
                    </span>
                  </Link>
                );
              })}

              {/* Séparateur visuel primaire / secondaire */}
              {navSecondary.length > 0 && (
                <span className="mx-1 h-4 w-px bg-border" aria-hidden="true" />
              )}

              {/* Secondaire : ton atténué, consultation */}
              {navSecondary.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "px-3 py-2 text-sm rounded-md transition-colors",
                    isActive(item.href)
                      ? "bg-primary/10 text-primary-on-dark font-medium"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent/10"
                  )}
                  aria-current={isActive(item.href) ? "page" : undefined}
                >
                  {item.name}
                </Link>
              ))}

              {/* Séparateur avant Assistant */}
              <span className="mx-1 h-4 w-px bg-border" aria-hidden="true" />

              {/* Assistant — affordance globale */}
              <Button
                variant="outline"
                size="sm"
                className="gap-2 border-primary/30 bg-primary/5 hover:bg-primary/10 hover:border-primary/50 text-foreground font-medium ml-1"
                onClick={() => setChatOpen(true)}
                aria-haspopup="dialog"
                aria-label={tHome("hero.ctaAssistant")}
              >
                <MessageCircle className="h-4 w-4" aria-hidden="true" />
                {tHome("hero.ctaAssistant")}
              </Button>
            </div>

            {/* Actions droite */}
            <div className="flex items-center gap-2">
              <LanguageSelector />
              <ThemeSelectorCompact />
              <DarkModeToggle />

              {isAuthenticated ? (
                <div className="flex items-center gap-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="flex items-center gap-2 h-9 px-3"
                        aria-label={`Menu utilisateur: ${user?.username}`}
                        aria-haspopup="true"
                      >
                        <div className="flex items-center gap-2">
                          <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
                            <User className="h-4 w-4 text-primary" aria-hidden="true" />
                          </div>
                          <span className="hidden sm:inline text-sm font-medium">
                            {user?.username}
                          </span>
                          <ChevronDown
                            className="h-3 w-3 text-muted-foreground hidden sm:inline"
                            aria-hidden="true"
                          />
                        </div>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-56">
                      <DropdownMenuLabel className="font-normal">
                        <div className="flex flex-col space-y-1">
                          <p className="text-sm font-medium leading-none">{user?.username}</p>
                          {user?.email && (
                            <p className="text-xs leading-none text-muted-foreground truncate">
                              {user.email}
                            </p>
                          )}
                        </div>
                      </DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link href="/profile" className="flex items-center cursor-pointer">
                          <User className="mr-2 h-4 w-4" />
                          <span>{t("profile")}</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href="/settings" className="flex items-center cursor-pointer">
                          <Settings className="mr-2 h-4 w-4" />
                          <span>{t("settings")}</span>
                        </Link>
                      </DropdownMenuItem>
                      {hasFullAccess && isStudent && (
                        <DropdownMenuItem asChild>
                          <Link href="/dashboard" className="flex items-center cursor-pointer">
                            <Home className="mr-2 h-4 w-4" />
                            <span>{t("dashboard")}</span>
                          </Link>
                        </DropdownMenuItem>
                      )}
                      {isAdmin && (
                        <DropdownMenuItem asChild>
                          <Link href="/admin" className="flex items-center cursor-pointer">
                            <Shield className="mr-2 h-4 w-4" />
                            <span>{t("admin")}</span>
                          </Link>
                        </DropdownMenuItem>
                      )}
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={() => logout()} variant="destructive">
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>{tAuth("logout")}</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
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
                aria-label="Ouvrir le menu"
                aria-expanded={mobileMenuOpen}
              >
                {mobileMenuOpen ? (
                  <X className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Menu className="h-5 w-5" aria-hidden="true" />
                )}
              </Button>
            </div>
          </div>

          {/* Menu mobile déroulant */}
          <LazyMotion features={domAnimation}>
            <AnimatePresence>
              {mobileMenuOpen && (
                <m.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="md:hidden border-t border-border overflow-hidden"
                  role="menu"
                >
                  <div className="space-y-2 py-4">
                    {navigation.map((item, index) => {
                      const Icon = "icon" in item ? item.icon : undefined;
                      const isAssistant = "isAssistant" in item && item.isAssistant;
                      const transition = createTransition({ duration: 0.15, delay: index * 0.05 });

                      if (isAssistant) {
                        return (
                          <m.div
                            key="assistant"
                            initial={!shouldReduceMotion ? { opacity: 0, x: -10 } : false}
                            animate={!shouldReduceMotion ? { opacity: 1, x: 0 } : false}
                            transition={transition}
                          >
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full justify-start gap-2 border-primary/30 bg-primary/5 hover:bg-primary/10"
                              onClick={() => {
                                setChatOpen(true);
                                setMobileMenuOpen(false);
                              }}
                              aria-haspopup="dialog"
                              role="menuitem"
                            >
                              {Icon && <Icon className="h-4 w-4" aria-hidden="true" />}
                              {item.name}
                            </Button>
                          </m.div>
                        );
                      }

                      return (
                        <m.div
                          key={item.href}
                          initial={!shouldReduceMotion ? { opacity: 0, x: -10 } : false}
                          animate={!shouldReduceMotion ? { opacity: 1, x: 0 } : false}
                          transition={transition}
                        >
                          <Link
                            href={item.href}
                            onClick={() => setMobileMenuOpen(false)}
                            className={cn(
                              "flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md transition-colors",
                              isActive(item.href)
                                ? "bg-primary/10 text-primary-on-dark"
                                : "text-muted-foreground hover:text-foreground hover:bg-accent/10"
                            )}
                            role="menuitem"
                            aria-current={isActive(item.href) ? "page" : undefined}
                          >
                            {Icon && <Icon className="h-4 w-4" aria-hidden="true" />}
                            {item.name}
                          </Link>
                        </m.div>
                      );
                    })}
                    <m.div
                      initial={!shouldReduceMotion ? { opacity: 0 } : false}
                      animate={!shouldReduceMotion ? { opacity: 1 } : false}
                      transition={createTransition({
                        duration: 0.15,
                        delay: navigation.length * 0.05,
                      })}
                      className="pt-2 border-t border-border"
                    >
                      <ThemeSelectorCompact />
                    </m.div>
                  </div>
                </m.div>
              )}
            </AnimatePresence>
          </LazyMotion>
        </nav>
      </header>
    </>
  );
}
