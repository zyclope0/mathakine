import { describe, expect, it } from "vitest";

import { getSocialShareImageFonts } from "./socialShareImageFonts";

describe("socialShareImageFonts", () => {
  it("loads explicit regular and bold fonts for Satori", async () => {
    const fonts = await getSocialShareImageFonts();
    const [regularFont, boldFont] = fonts;

    expect(fonts).toHaveLength(2);
    expect(regularFont).toBeDefined();
    expect(boldFont).toBeDefined();

    if (!regularFont || !boldFont) {
      throw new Error("Expected regular and bold fonts to be loaded");
    }

    expect(regularFont).toMatchObject({
      name: "KaTeX Main",
      style: "normal",
      weight: 400,
    });
    expect(boldFont).toMatchObject({
      name: "KaTeX Main",
      style: "normal",
      weight: 700,
    });
    expect(regularFont.data.byteLength).toBeGreaterThan(0);
    expect(boldFont.data.byteLength).toBeGreaterThan(0);
  });
});
