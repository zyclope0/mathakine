/**
 * Narrow translator shape for `useTranslations("homeLearner")` passed into presentational sections.
 * Aligné sur next-intl (valeurs `Record<string, string | number | Date>`).
 */
export type HomeLearnerNamespaceT = (
  key: string,
  values?: Record<string, string | number | Date>
) => string;
