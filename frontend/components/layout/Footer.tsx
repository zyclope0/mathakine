"use client";

import Link from "next/link";
import { Mail, Heart, Sparkles } from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils";

function GitHubMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" className={className}>
      <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.426 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.009-.866-.014-1.699-2.782.605-3.369-1.344-3.369-1.344-.455-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.004.07 1.532 1.033 1.532 1.033.893 1.531 2.341 1.089 2.91.833.091-.647.35-1.089.636-1.339-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.31.678.92.678 1.855 0 1.339-.012 2.419-.012 2.747 0 .268.18.58.688.481A10.019 10.019 0 0 0 22 12.017C22 6.484 17.523 2 12 2Z" />
    </svg>
  );
}

export function Footer() {
  const t = useTranslations("navigation");
  const currentYear = new Date().getFullYear();

  const footerLinks = [
    { name: t("changelog"), href: "/changelog" },
    { name: t("about"), href: "/about" },
    { name: t("contact"), href: "/contact" },
    { name: t("documentation"), href: "/docs" },
    { name: t("privacy"), href: "/privacy" },
  ];

  return (
    <footer
      className="relative z-0 border-t border-border bg-background/95 backdrop-blur-sm supports-[backdrop-filter]:bg-background/60"
      role="contentinfo"
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo et description */}
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-lg font-bold mb-2 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Mathakine
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Plateforme éducative mathématique adaptative. Apprendre les mathématiques de manière
              ludique et immersive.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/mathakine"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
                aria-label="GitHub"
              >
                <GitHubMark className="h-5 w-5" />
              </a>
              <a
                href={`mailto:${process.env.NEXT_PUBLIC_CONTACT_EMAIL || process.env.NEXT_PUBLIC_FEEDBACK_EMAIL || "webmaster@mathakine.fun"}`}
                className="text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Email"
              >
                <Mail className="h-5 w-5" aria-hidden="true" />
              </a>
            </div>
          </div>

          {/* Liens rapides */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Liens rapides</h4>
            <ul className="space-y-2">
              {footerLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className={cn(
                      "text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1.5",
                      link.href === "/changelog" && "font-medium"
                    )}
                  >
                    {link.href === "/changelog" && (
                      <Sparkles className="h-3.5 w-3.5 text-primary shrink-0" aria-hidden />
                    )}
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Ressources */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Ressources</h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/exercises"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Exercices
                </Link>
              </li>
              <li>
                <Link
                  href="/challenges"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Défis logiques
                </Link>
              </li>
              <li>
                <Link
                  href="/badges"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Badges
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-8 border-t border-border flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground">
            © {currentYear} Mathakine. Tous droits réservés.
          </p>
          <p className="text-sm text-muted-foreground flex items-center gap-1">
            Fait avec <Heart className="h-4 w-4 text-primary-on-dark" aria-hidden="true" /> pour
            l&apos;éducation
          </p>
        </div>
      </div>
    </footer>
  );
}
