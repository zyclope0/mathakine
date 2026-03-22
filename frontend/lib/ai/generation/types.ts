/**
 * Types partagés — flux POST + SSE génération IA (exercices / défis).
 * @see docs/03-PROJECT/evaluation/ — harness backend ; ici uniquement contrat client.
 */

/** Compatible avec `useTranslations` (next-intl) : pas de `boolean` dans les valeurs typées. */
export type AiGenerationSseTranslate = (
  key: string,
  values?: Record<string, string | number | Date>
) => string;
