/**
 * Shared 1200×630 social preview image for Open Graph and Twitter.
 * Uses JSX supported by @vercel/og / Satori (no external images, no SVG filters).
 */

import { ImageResponse } from "next/og";

import {
  SOCIAL_SHARE_CARD_BASELINE_FR,
  SOCIAL_SHARE_IMAGE_DIMENSIONS,
} from "@/lib/social/socialShareImageMeta";
import { getSocialShareImageFonts } from "@/lib/social/socialShareImageFonts";

const BRAND = {
  bgFrom: "#0d0d1a",
  bgVia: "#1e1b4b",
  bgTo: "#312e81",
  monogramBorder: "#7c3aed",
  monogramInner: "#0d0d1a",
  monogramLetter: "#e9d5ff",
  accentDot: "#fbbf24",
  title: "#f8fafc",
  subtitle: "#c4b5fd",
} as const;

export async function renderSocialShareImageResponse(): Promise<ImageResponse> {
  const { width, height } = SOCIAL_SHARE_IMAGE_DIMENSIONS;
  const fonts = await getSocialShareImageFonts();

  return new ImageResponse(
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: `linear-gradient(125deg, ${BRAND.bgFrom} 0%, ${BRAND.bgVia} 45%, ${BRAND.bgTo} 100%)`,
        fontFamily: '"KaTeX Main", ui-sans-serif, system-ui, sans-serif',
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          gap: 52,
          padding: "56px 72px",
        }}
      >
        <div
          style={{
            position: "relative",
            display: "flex",
            width: 200,
            height: 200,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              position: "absolute",
              width: 200,
              height: 200,
              borderRadius: 44,
              background: BRAND.monogramInner,
              border: `4px solid ${BRAND.monogramBorder}`,
              boxShadow: "0 12px 40px rgba(124, 58, 237, 0.35)",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 36,
              left: 86,
              width: 28,
              height: 28,
              borderRadius: 14,
              background: BRAND.accentDot,
              boxShadow: "0 0 24px rgba(251, 191, 36, 0.7)",
            }}
          />
          <span
            style={{
              position: "relative",
              fontSize: 118,
              fontWeight: 800,
              lineHeight: 1,
              color: BRAND.monogramLetter,
              letterSpacing: "-0.04em",
              marginTop: 8,
            }}
          >
            M
          </span>
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 20,
            maxWidth: 780,
          }}
        >
          <div
            style={{
              fontSize: 96,
              fontWeight: 800,
              color: BRAND.title,
              letterSpacing: "-0.03em",
              lineHeight: 1.05,
            }}
          >
            Mathakine
          </div>
          <div
            style={{
              fontSize: 34,
              fontWeight: 500,
              color: BRAND.subtitle,
              lineHeight: 1.35,
            }}
          >
            {SOCIAL_SHARE_CARD_BASELINE_FR}
          </div>
        </div>
      </div>
    </div>,
    {
      width,
      height,
      fonts,
    }
  );
}
