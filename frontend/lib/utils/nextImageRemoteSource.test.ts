import { describe, expect, it } from "vitest";
import { resolveNextImageRemoteDelivery } from "@/lib/utils/nextImageRemoteSource";

describe("resolveNextImageRemoteDelivery", () => {
  it("routes same-origin paths to next-image", () => {
    expect(resolveNextImageRemoteDelivery("/api/media/avatar.png")).toEqual({
      mode: "next-image",
      src: "/api/media/avatar.png",
    });
  });

  it("trims whitespace before resolving", () => {
    expect(resolveNextImageRemoteDelivery("  /x.jpg  ")).toEqual({
      mode: "next-image",
      src: "/x.jpg",
    });
  });

  it("keeps protocol-relative URLs on img", () => {
    expect(resolveNextImageRemoteDelivery("//cdn.example.com/a.png")).toEqual({
      mode: "img",
      src: "//cdn.example.com/a.png",
    });
  });

  it("routes http localhost to next-image", () => {
    expect(resolveNextImageRemoteDelivery("http://localhost:3000/a.png")).toEqual({
      mode: "next-image",
      src: "http://localhost:3000/a.png",
    });
  });

  it("routes https onrender.com app hosts to next-image", () => {
    expect(resolveNextImageRemoteDelivery("https://my-app.onrender.com/static/1.jpg")).toEqual({
      mode: "next-image",
      src: "https://my-app.onrender.com/static/1.jpg",
    });
  });

  it("routes https *.render.com hosts to next-image", () => {
    expect(resolveNextImageRemoteDelivery("https://assets.render.com/x.png")).toEqual({
      mode: "next-image",
      src: "https://assets.render.com/x.png",
    });
  });

  it("keeps apex render.com on img (not covered by **.render.com pattern intent)", () => {
    expect(resolveNextImageRemoteDelivery("https://render.com/logo.png").mode).toBe("img");
  });

  it("keeps arbitrary CDNs on img", () => {
    expect(resolveNextImageRemoteDelivery("https://cdn.example.com/a.webp")).toEqual({
      mode: "img",
      src: "https://cdn.example.com/a.webp",
    });
  });

  it("returns img for non-URL strings", () => {
    expect(resolveNextImageRemoteDelivery(":::not-a-url").mode).toBe("img");
  });

  it("returns img for empty after trim", () => {
    expect(resolveNextImageRemoteDelivery("   ").mode).toBe("img");
  });
});
