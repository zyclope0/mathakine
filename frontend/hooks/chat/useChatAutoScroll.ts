import { type RefObject, useEffect } from "react";

/**
 * Fait défiler un conteneur de messages vers le bas quand le contenu change.
 */
export function useChatAutoScroll(
  containerRef: RefObject<HTMLElement | null>,
  enabled: boolean,
  scrollDependency: unknown
): void {
  useEffect(() => {
    if (!enabled || !containerRef.current) return;
    const el = containerRef.current;
    const id = requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
    return () => cancelAnimationFrame(id);
  }, [containerRef, enabled, scrollDependency]);
}
