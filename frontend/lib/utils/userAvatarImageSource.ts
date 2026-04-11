/**
 * Choix du transport d'image pour {@link UserAvatar} lorsque `avatarUrl` est défini.
 *
 * **À maintenir aligné** avec `images.remotePatterns` dans `next.config.ts` : toute URL
 * absolue dont l'hôte n'est pas autorisée par Next pour le loader par défaut doit rester
 * sur `<img>` pour éviter une erreur runtime « hostname is not configured ».
 *
 * Hôtes HTTPS alignés sur `next.config.ts` : `*.render.com`, `*.onrender.com`, plus
 * `http://localhost` et chemins relatifs `/…` (mais jamais `//host/...`, qui reste
 * une URL absolue protocol-relative et doit donc éviter `next/image` hors allowlist).
 */

export type UserAvatarImageDelivery =
  | { readonly mode: "next-image"; readonly src: string }
  | { readonly mode: "img"; readonly src: string };

/**
 * Returns `next-image` only when `src` is safe for the default Next.js optimizer
 * given the project's `remotePatterns` (same-origin path, localhost HTTP, Render HTTPS).
 */
export function resolveUserAvatarImageDelivery(avatarUrl: string): UserAvatarImageDelivery {
  const trimmed = avatarUrl.trim();
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
    return { mode: "img", src: trimmed };
  }
  return { mode: "img", src: trimmed };
}
