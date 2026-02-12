"use client";

import { useTranslations } from "next-intl";

/**
 * Hook pour obtenir les traductions dynamiques des types de challenges
 *
 * @returns Fonction qui prend un type de challenge et retourne son libellé traduit
 *
 * @example
 * const getTypeDisplay = useChallengeTypeDisplay();
 * <span>{getTypeDisplay('sequence')}</span> // → "Séquence" (FR) ou "Sequence" (EN)
 */
export function useChallengeTypeDisplay() {
  const t = useTranslations("challenges");

  return (type: string | null | undefined): string => {
    if (!type) return t("types.sequence"); // fallback

    const normalizedType = type.toLowerCase();

    // Utiliser une clé dynamique avec fallback sur la valeur brute
    try {
      return t(`types.${normalizedType}`);
    } catch {
      // Si la clé n'existe pas, retourner la valeur capitalisée
      return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
    }
  };
}

/**
 * Hook pour obtenir les traductions dynamiques des types d'exercices
 *
 * @returns Fonction qui prend un type d'exercice et retourne son libellé traduit
 *
 * @example
 * const getTypeDisplay = useExerciseTypeDisplay();
 * <span>{getTypeDisplay('addition')}</span> // → "Addition" (FR/EN)
 */
export function useExerciseTypeDisplay() {
  const t = useTranslations("exercises");

  return (type: string | null | undefined): string => {
    if (!type) return t("types.divers"); // fallback

    const normalizedType = type.toLowerCase();

    try {
      return t(`types.${normalizedType}`);
    } catch {
      return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
    }
  };
}

/**
 * Hook pour obtenir les traductions dynamiques des groupes d'âge
 * Utilisable pour challenges ET exercices (mêmes groupes d'âge)
 *
 * @returns Fonction qui prend un groupe d'âge et retourne son libellé traduit
 *
 * @example
 * const getAgeDisplay = useAgeGroupDisplay();
 * <span>{getAgeDisplay('6-8')}</span> // → "6-8 ans" (FR) ou "6-8 years" (EN)
 */
export function useAgeGroupDisplay() {
  const t = useTranslations("challenges");

  return (ageGroup: string | null | undefined): string => {
    if (!ageGroup) return t("ageGroups.tous-ages"); // fallback

    // Normaliser le groupe d'âge (gérer les formats legacy)
    const normalizedGroup = normalizeAgeGroupKey(ageGroup);

    try {
      return t(`ageGroups.${normalizedGroup}`);
    } catch {
      // Si la clé n'existe pas, retourner la valeur brute
      return ageGroup;
    }
  };
}

/**
 * Normalise les clés de groupe d'âge pour correspondre aux traductions
 * Gère les formats legacy (GROUP_6_8, 6_8, etc.)
 */
function normalizeAgeGroupKey(ageGroup: string): string {
  const normalized = ageGroup.toLowerCase().trim();

  // Mapping des formats legacy vers les nouvelles clés
  const legacyMapping: Record<string, string> = {
    group_6_8: "6-8",
    "6_8": "6-8",
    group_9_11: "9-11",
    "9_11": "9-11",
    group_12_14: "12-14",
    "12_14": "12-14",
    group_15_17: "15-17",
    "15_17": "15-17",
    adult: "adulte",
    adults: "adulte",
    all: "tous-ages",
    all_ages: "tous-ages",
    "tous ages": "tous-ages",
  };

  return legacyMapping[normalized] || normalized;
}

/**
 * Exporte les hooks challenges ensemble pour un import unique
 */
export function useChallengeTranslations() {
  return {
    getTypeDisplay: useChallengeTypeDisplay(),
    getAgeDisplay: useAgeGroupDisplay(),
  };
}

/**
 * Exporte les hooks exercices ensemble pour un import unique
 */
export function useExerciseTranslations() {
  return {
    getTypeDisplay: useExerciseTypeDisplay(),
    getAgeDisplay: useAgeGroupDisplay(),
  };
}
