import { describe, expect, it } from "vitest";
import { parseChatStreamEvent } from "./chat";

describe("parseChatStreamEvent", () => {
  it("parse chunk / done / error", () => {
    expect(parseChatStreamEvent({ type: "chunk", content: "x" })).toEqual({
      type: "chunk",
      content: "x",
    });
    expect(parseChatStreamEvent({ type: "image", url: "https://cdn.example.com/x.png" })).toEqual({
      type: "image",
      url: "https://cdn.example.com/x.png",
    });
    expect(parseChatStreamEvent({ type: "done" })).toEqual({ type: "done" });
    expect(parseChatStreamEvent({ type: "error", message: "oops" })).toEqual({
      type: "error",
      message: "oops",
    });
  });

  it("retourne null pour JSON inconnu", () => {
    expect(parseChatStreamEvent(null)).toBeNull();
    expect(parseChatStreamEvent({})).toBeNull();
    expect(parseChatStreamEvent({ type: "chunk" })).toBeNull();
  });
});
