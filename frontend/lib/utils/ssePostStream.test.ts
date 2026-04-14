import { describe, expect, it } from "vitest";
import { consumeSseJsonEvents } from "./ssePostStream";

describe("consumeSseJsonEvents", () => {
  it("parse les lignes data: JSON et appelle onEvent", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"type":"status","message":"hello"}\n\n'));
        controller.close();
      },
    });
    const response = new Response(stream);
    const types: string[] = [];
    await consumeSseJsonEvents(response, (data) => {
      if (typeof data.type === "string") types.push(data.type);
    });
    expect(types).toEqual(["status"]);
  });

  it("lève AbortError si signal aborted avant lecture", async () => {
    const stream = new ReadableStream<Uint8Array>({
      start() {
        /* never enqueues */
      },
    });
    const response = new Response(stream);
    const ac = new AbortController();
    ac.abort();
    await expect(
      consumeSseJsonEvents(response, () => undefined, { signal: ac.signal })
    ).rejects.toMatchObject({ name: "AbortError" });
  });
});
