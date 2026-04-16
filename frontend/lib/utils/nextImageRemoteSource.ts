/**
 * Choix `next/image` vs `<img>` pour une URL distante ou relative.
 *
 * **À maintenir aligné** avec `images.remotePatterns` dans `next.config.ts`.
 * Les URL absolues hors liste restent en `<img>` pour éviter l’erreur runtime
 * « hostname is not configured ».
 */

export type NextImageRemoteDelivery =
  | { readonly mode: "next-image"; readonly src: string }
  | { readonly mode: "img"; readonly src: string };

/**
 * Returns `next-image` only when `src` is allowed by the default Next.js optimizer
 * for this project’s `remotePatterns` (same-origin path, localhost HTTP, Render hosts).
 */
export function resolveNextImageRemoteDelivery(
  absoluteOrRelativeUrl: string
): NextImageRemoteDelivery {
  const trimmed = absoluteOrRelativeUrl.trim();
  if (trimmed === "") {
    return { mode: "img", src: trimmed };
  }
  if (trimmed.startsWith("/") && !trimmed.startsWith("//")) {
    return { mode: "next-image", src: trimmed };
  }
  try {
    const parsed = new URL(trimmed);
    if (parsed.protocol === "http:" && parsed.hostname === "localhost") {
      return { mode: "next-image", src: trimmed };
    }
    if (
      parsed.protocol === "https:" &&
      (parsed.hostname.endsWith(".render.com") || parsed.hostname.endsWith(".onrender.com"))
    ) {
      return { mode: "next-image", src: trimmed };
    }
  } catch {
    /* swallowed: unparseable src URL, native <img> fallback used */
    return { mode: "img", src: trimmed };
  }
  return { mode: "img", src: trimmed };
}
