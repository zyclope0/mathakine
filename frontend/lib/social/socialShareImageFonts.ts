import { readFile } from "node:fs/promises";
import { join } from "node:path";

interface SocialShareImageFont {
  name: string;
  data: ArrayBuffer;
  style: "normal";
  weight: 400 | 700;
}

let socialShareImageFontsPromise: Promise<SocialShareImageFont[]> | null = null;

function toArrayBuffer(buffer: Buffer<ArrayBufferLike>): ArrayBuffer {
  return buffer.buffer.slice(
    buffer.byteOffset,
    buffer.byteOffset + buffer.byteLength
  ) as ArrayBuffer;
}

export async function getSocialShareImageFonts(): Promise<SocialShareImageFont[]> {
  if (!socialShareImageFontsPromise) {
    socialShareImageFontsPromise = Promise.all([
      readFile(
        join(process.cwd(), "node_modules", "katex", "dist", "fonts", "KaTeX_Main-Regular.ttf")
      ),
      readFile(
        join(process.cwd(), "node_modules", "katex", "dist", "fonts", "KaTeX_Main-Bold.ttf")
      ),
    ]).then(([regularFont, boldFont]) => [
      {
        name: "KaTeX Main",
        data: toArrayBuffer(regularFont),
        style: "normal" as const,
        weight: 400 as const,
      },
      {
        name: "KaTeX Main",
        data: toArrayBuffer(boldFont),
        style: "normal" as const,
        weight: 700 as const,
      },
    ]);
  }

  return socialShareImageFontsPromise;
}
