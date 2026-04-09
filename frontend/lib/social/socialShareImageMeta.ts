/**
 * Single source of truth for default Open Graph / Twitter card image metadata
 * (paired with `opengraph-image.tsx` / `twitter-image.tsx`).
 */

export const SOCIAL_SHARE_IMAGE_DIMENSIONS = {
  width: 1200,
  height: 630,
} as const;

export const SOCIAL_SHARE_IMAGE_ALT = "Mathakine";

/** Short baseline on the generated card (FR, stable product line). */
export const SOCIAL_SHARE_CARD_BASELINE_FR =
  "Exercices personnalisés, défis logiques et gamification.";

export const OPENGRAPH_IMAGE_PATH = "/opengraph-image" as const;
export const TWITTER_IMAGE_PATH = "/twitter-image" as const;

export function getDefaultOpenGraphImages(): Array<{
  url: typeof OPENGRAPH_IMAGE_PATH;
  width: number;
  height: number;
  alt: string;
}> {
  return [
    {
      url: OPENGRAPH_IMAGE_PATH,
      width: SOCIAL_SHARE_IMAGE_DIMENSIONS.width,
      height: SOCIAL_SHARE_IMAGE_DIMENSIONS.height,
      alt: SOCIAL_SHARE_IMAGE_ALT,
    },
  ];
}

export function getDefaultTwitterImages(): Array<typeof TWITTER_IMAGE_PATH> {
  return [TWITTER_IMAGE_PATH];
}
