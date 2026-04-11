/**
 * Choix du transport d’image pour {@link UserAvatar} lorsque `avatarUrl` est défini.
 *
 * Délègue à {@link resolveNextImageRemoteDelivery} — **garder les deux alignés** avec
 * `images.remotePatterns` dans `next.config.ts`.
 */

import {
  resolveNextImageRemoteDelivery,
  type NextImageRemoteDelivery,
} from "@/lib/utils/nextImageRemoteSource";

export type UserAvatarImageDelivery = NextImageRemoteDelivery;

export function resolveUserAvatarImageDelivery(avatarUrl: string): UserAvatarImageDelivery {
  return resolveNextImageRemoteDelivery(avatarUrl);
}
