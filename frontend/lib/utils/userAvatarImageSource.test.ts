import { describe, expect, it } from "vitest";
import { resolveNextImageRemoteDelivery } from "@/lib/utils/nextImageRemoteSource";
import { resolveUserAvatarImageDelivery } from "@/lib/utils/userAvatarImageSource";

describe("resolveUserAvatarImageDelivery", () => {
  it("delegates to resolveNextImageRemoteDelivery", () => {
    const samples = [
      "/a.png",
      "https://cdn.example.com/x.webp",
      "https://app.onrender.com/i.jpg",
      "   ",
    ];
    for (const url of samples) {
      expect(resolveUserAvatarImageDelivery(url)).toEqual(resolveNextImageRemoteDelivery(url));
    }
  });
});
