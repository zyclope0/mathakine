/** Tranches d'âge profil (F42), alignées backend `users.age_group`. */
export const USER_PROFILE_AGE_GROUPS = ["6-8", "9-11", "12-14", "15+"] as const;
export type UserProfileAgeGroup = (typeof USER_PROFILE_AGE_GROUPS)[number];
