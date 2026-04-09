import enMessages from "@/messages/en.json";
import frMessages from "@/messages/fr.json";

export type ChatProxyLocale = "fr" | "en";

export type ChatProxyCopy = (typeof frMessages)["apiChat"]["proxy"];

/**
 * Resolves locale for Next.js chat proxy responses from the incoming request.
 * Matches the forwarded `Accept-Language` convention used for backend calls.
 */
export function resolveChatProxyLocale(acceptLanguageHeader: string | null): ChatProxyLocale {
  if (!acceptLanguageHeader) return "fr";
  const first = acceptLanguageHeader.split(",")[0]?.trim().toLowerCase() ?? "";
  return first.startsWith("en") ? "en" : "fr";
}

export function getChatProxyCopy(locale: ChatProxyLocale): ChatProxyCopy {
  return locale === "en" ? enMessages.apiChat.proxy : frMessages.apiChat.proxy;
}
