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
import { Home, LogOut, User, Menu, X, Settings, ChevronDown, Shield } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils/cn";
import { useTranslations } from "next-intl";
import { motion, AnimatePresence } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

export function Header() {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const t = useTranslations("navigation");
  const tAuth = useTranslations("auth");
  const { shouldReduceMotion, createTransition } = useAccessibleAnimation();

  const isAdmin = user?.role === "archiviste";

  const navigation = [
    { name: t("home"), href: "/", icon: Home },
    ...(isAuthenticated
      ? [
          { name: t("dashboard"), href: "/dashboard" },
          { name: t("exercises"), href: "/exercises" },
          { name: t("challenges"), href: "/challenges" },
          { name: t("badges"), href: "/badges" },
          { name: t("leaderboard"), href: "/leaderboard" },
        ]
      : []),
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
        className="sticky top-0 z-40 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
        role="banner"
      >
        <nav className="container mx-auto px-4 sm:px-6 lg:px-8" aria-label="Navigation principale">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div className="flex items-center">
              <Link
                href="/"
                className="flex items-center space-x-2 text-xl font-bold text-foreground hover:text-primary-on-dark transition-colors"
                aria-label="Retour à l'accueil"
              >
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  Mathakine
                </span>
              </Link>
            </div>

            {/* Navigation Desktop */}
            <div className="hidden md:flex md:items-center md:space-x-4">
              {navigation.map((item) => {
                const Icon = "icon" in item ? item.icon : undefined;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "px-3 py-2 text-sm font-medium rounded-md transition-colors",
                      isActive(item.href)
                        ? "bg-primary/10 text-primary-on-dark"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent/10"
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
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div
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
                    const transition = createTransition({ duration: 0.15, delay: index * 0.05 });

                    return (
                      <motion.div
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
                      </motion.div>
                    );
                  })}
                  <motion.div
                    initial={!shouldReduceMotion ? { opacity: 0 } : false}
                    animate={!shouldReduceMotion ? { opacity: 1 } : false}
                    transition={createTransition({
                      duration: 0.15,
                      delay: navigation.length * 0.05,
                    })}
                    className="pt-2 border-t border-border"
                  >
                    <ThemeSelectorCompact />
                  </motion.div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </nav>
      </header>
    </>
  );
}
