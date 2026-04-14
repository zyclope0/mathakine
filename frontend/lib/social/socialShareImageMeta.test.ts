import { describe, expect, it } from "vitest";

import {
  OPENGRAPH_IMAGE_PATH,
  SOCIAL_SHARE_IMAGE_ALT,
  SOCIAL_SHARE_IMAGE_DIMENSIONS,
  TWITTER_IMAGE_PATH,
  getDefaultOpenGraphImages,
  getDefaultTwitterImages,
} from "./socialShareImageMeta";

describe("socialShareImageMeta", () => {
  it("uses 1200×630 social dimensions", () => {
    expect(SOCIAL_SHARE_IMAGE_DIMENSIONS.width).toBe(1200);
    expect(SOCIAL_SHARE_IMAGE_DIMENSIONS.height).toBe(630);
  });

  it("exposes Open Graph metadata aligned with app route opengraph-image", () => {
    const images = getDefaultOpenGraphImages();
    expect(images).toHaveLength(1);
    expect(images[0]).toEqual({
      url: OPENGRAPH_IMAGE_PATH,
      width: 1200,
      height: 630,
      alt: SOCIAL_SHARE_IMAGE_ALT,
    });
  });

  it("exposes Twitter images path aligned with app route twitter-image", () => {
    expect(getDefaultTwitterImages()).toEqual([TWITTER_IMAGE_PATH]);
  });
});
