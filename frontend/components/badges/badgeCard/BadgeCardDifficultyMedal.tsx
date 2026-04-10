"use client";

import Image from "next/image";
import { hasPresentationMedal, resolveMedalSvgPath } from "@/lib/badges/badgePresentation";

export function BadgeCardDifficultyMedal({
  difficulty,
  size = "sm",
}: {
  difficulty?: string | null | undefined;
  size?: "xs" | "sm";
}) {
  if (!hasPresentationMedal(difficulty)) return null;
  const src = resolveMedalSvgPath(difficulty);
  const cls = size === "xs" ? "h-4 w-4" : "h-3.5 w-3.5";
  const pixelSize = size === "xs" ? 16 : 14;
  return (
    <Image
      src={src}
      alt=""
      width={pixelSize}
      height={pixelSize}
      className={`${cls} object-contain inline-block shrink-0`}
      aria-hidden="true"
      sizes={`${pixelSize}px`}
    />
  );
}
