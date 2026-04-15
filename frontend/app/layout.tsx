import type { Metadata } from "next";
import { JetBrains_Mono, Nunito } from "next/font/google";
import { headers } from "next/headers";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";
import { CSP_NONCE_REQUEST_HEADER } from "@/lib/security/middlewareCsp";
import { AccessibilityToolbar } from "@/components/accessibility/AccessibilityToolbar";
import { WCAGAudit } from "@/components/accessibility/WCAGAudit";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { AlphaBanner } from "@/components/layout/AlphaBanner";
import { UnverifiedBanner } from "@/components/layout/UnverifiedBanner";
import { LocaleInitializer } from "@/components/locale/LocaleInitializer";
import { InstallPrompt } from "@/components/pwa/InstallPrompt";
import { MaintenanceOverlay } from "@/components/layout/MaintenanceOverlay";
import { FeedbackFab } from "@/components/feedback/FeedbackFab";
import { ChatbotFloatingGlobal } from "@/components/chat/ChatbotFloatingGlobal";
import { PageTransition } from "@/components/layout/PageTransition";
import { SpatialBackground } from "@/components/spatial/SpatialBackground";
import {
  getDefaultOpenGraphImages,
  getDefaultTwitterImages,
} from "@/lib/social/socialShareImageMeta";

/** UI principale : Nunito (lisible, chaleureuse) — poids 400–800 via variable font. */
const nunito = Nunito({
  variable: "--font-nunito-sans",
  subsets: ["latin"],
  display: "swap",
});

/** Code / mono : distinct de la sans (pas de Geist dans le repo). */
const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

// Déterminer l'URL de base selon l'environnement
const getMetadataBase = (): string => {
  if (process.env.NODE_ENV === "production") {
    return process.env.NEXT_PUBLIC_SITE_URL || "https://mathakine-frontend.onrender.com";
  }
  return process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
};

const SITE_URL = getMetadataBase();

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "Mathakine - Apprentissage Mathématique Adaptatif",
  description:
    "Plateforme éducative mathématique adaptative pour enfants de 5 à 20 ans. Exercices personnalisés, défis logiques et gamification pour progresser en mathématiques.",
  keywords: [
    "mathématiques",
    "apprentissage adaptatif",
    "exercices mathématiques",
    "défis logiques",
    "mathélogique",
    "éducation",
    "enfants",
    "TSA",
    "TDAH",
    "accessibilité",
    "gamification",
    "badges",
    "progression",
    "plateforme éducative",
  ],
  authors: [{ name: "Mathakine" }],
  creator: "Mathakine",
  publisher: "Mathakine",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Mathakine",
  },
  icons: {
    icon: [
      { url: "/logo-m.svg", type: "image/svg+xml" },
      { url: "/icons/icon-192x192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512x512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [{ url: "/icons/icon-192x192.png", sizes: "192x192", type: "image/png" }],
  },
  openGraph: {
    type: "website",
    locale: "fr_FR",
    url: SITE_URL,
    title: "Mathakine - Apprentissage Mathématique Adaptatif",
    description:
      "Plateforme éducative mathématique adaptative pour enfants de 5 à 20 ans. Exercices personnalisés, défis logiques et gamification.",
    siteName: "Mathakine",
    images: getDefaultOpenGraphImages(),
  },
  twitter: {
    card: "summary_large_image",
    title: "Mathakine - Apprentissage Mathématique Adaptatif",
    description: "Plateforme éducative mathématique adaptative pour enfants de 5 à 20 ans.",
    images: getDefaultTwitterImages(),
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: SITE_URL,
  },
};

/**
 * CSP nonce (prod): static HTML cannot receive per-request nonces — force dynamic
 * rendering so Next applies the nonce from middleware (`proxy.ts`) to framework
 * inline scripts. See QF-07C / README_TECH (SSR cost).
 */
export const dynamic = "force-dynamic";

// Next.js 16 : themeColor et viewport doivent être dans generateViewport
export function generateViewport() {
  return {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
    viewportFit: "cover" as const,
    /* Aligné sur le thème spatial (--primary) pour éviter accent violet générique (barre d’adresse / PWA). */
    themeColor: [
      { media: "(prefers-color-scheme: light)", color: "#1a3fa8" },
      { media: "(prefers-color-scheme: dark)", color: "#1a3fa8" },
    ],
  };
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const headerList = await headers();
  const cspNonce = headerList.get(CSP_NONCE_REQUEST_HEADER) ?? undefined;

  return (
    <html lang="fr" suppressHydrationWarning nonce={cspNonce} data-scroll-behavior="smooth">
      <body className={`${nunito.variable} ${jetbrainsMono.variable} antialiased font-sans`}>
        <Providers>
          <SpatialBackground />
          <LocaleInitializer />
          <div className="flex min-h-screen flex-col">
            <Header />
            {/* Espaceur pour compenser le header fixe (h-16) */}
            <div className="h-16 shrink-0" aria-hidden="true" />
            <AlphaBanner />
            <UnverifiedBanner />
            <main
              id="main-content"
              className="flex-1 relative z-10"
              role="main"
              aria-label="Contenu principal"
            >
              <PageTransition>{children}</PageTransition>
            </main>
            <Footer />
          </div>
          <AccessibilityToolbar />
          <WCAGAudit />
          <ChatbotFloatingGlobal />
          <InstallPrompt />
          <MaintenanceOverlay />
          <FeedbackFab />
        </Providers>
      </body>
    </html>
  );
}
