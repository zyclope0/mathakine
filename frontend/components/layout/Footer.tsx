"use client";

import Link from "next/link";
import { Github, Mail, Heart } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = [
    { name: "À propos", href: "/about" },
    { name: "Contact", href: "/contact" },
    { name: "Documentation", href: "/docs" },
    { name: "Politique de confidentialité", href: "/privacy" },
  ];

  return (
    <footer
      className="relative z-10 border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
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
                <Github className="h-5 w-5" aria-hidden="true" />
              </a>
              <a
                href="mailto:contact@mathakine.fr"
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
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
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
            l'éducation
          </p>
        </div>
      </div>
    </footer>
  );
}
