import type { AiGenerationRequestError } from "./postAiGenerationSse";

type TranslateAiGenerator = (key: string) => string;

/**
 * Libellés toast pour erreurs pré-fetch / HTTP issues de `postAiGenerationSse`.
 * Les clés sont sous `*.aiGenerator.*` (exercises ou challenges).
 */
export function getAiGenerationRequestErrorToast(
  error: AiGenerationRequestError,
  t: TranslateAiGenerator
): { title: string; description: string } {
  switch (error.code) {
    case "csrf_token_missing":
      return {
        title: t("aiGenerator.errorCsrfTitle"),
        description: t("aiGenerator.errorCsrfDescription"),
      };
    case "http_401":
      return {
        title: t("aiGenerator.errorSessionTitle"),
        description: t("aiGenerator.errorSessionDescription"),
      };
    case "http_403":
      return {
        title: t("aiGenerator.errorAccessTitle"),
        description: t("aiGenerator.errorAccessDescription"),
      };
    case "http_backend":
    default:
      return {
        title: t("aiGenerator.errorBackendTitle"),
        description: t("aiGenerator.errorBackendDescription"),
      };
  }
}
