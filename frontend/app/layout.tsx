import type { Metadata } from "next";
import { Exo_2 } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";
import { AccessibilityToolbar } from "@/components/accessibility/AccessibilityToolbar";
import { WCAGAudit } from "@/components/accessibility/WCAGAudit";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { AlphaBanner } from "@/components/layout/AlphaBanner";
import { LocaleInitializer } from "@/components/locale/LocaleInitializer";
import { InstallPrompt } from "@/components/pwa/InstallPrompt";
import { PageTransition } from "@/components/layout/PageTransition";
import { SpatialBackground } from "@/components/spatial/SpatialBackground";

const exo2 = Exo_2({
  variable: "--font-exo-2",
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
  metadataBase: new URL(getMetadataBase()),
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
    images: [
      {
        url: "/icons/icon-512x512.png",
        width: 512,
        height: 512,
        alt: "Logo Mathakine",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Mathakine - Apprentissage Mathématique Adaptatif",
    description: "Plateforme éducative mathématique adaptative pour enfants de 5 à 20 ans.",
    images: ["/icons/icon-512x512.png"],
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

// Next.js 16 : themeColor et viewport doivent être dans generateViewport
export function generateViewport() {
  return {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
    viewportFit: "cover" as const,
    themeColor: [
      { media: "(prefers-color-scheme: light)", color: "#8b5cf6" },
      { media: "(prefers-color-scheme: dark)", color: "#8b5cf6" },
    ],
  };
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={`${exo2.variable} antialiased`}>
        <Providers>
          <SpatialBackground />
          <LocaleInitializer />
          <div className="flex min-h-screen flex-col">
            <Header />
            <AlphaBanner />
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
          <InstallPrompt />
        </Providers>
      </body>
    </html>
  );
}
