import {
  SOCIAL_SHARE_IMAGE_ALT,
  SOCIAL_SHARE_IMAGE_DIMENSIONS,
} from "@/lib/social/socialShareImageMeta";
import { renderSocialShareImageResponse } from "@/lib/social/renderSocialShareImageResponse";

export const alt = SOCIAL_SHARE_IMAGE_ALT;
export const size = SOCIAL_SHARE_IMAGE_DIMENSIONS;
export const contentType = "image/png";
export const runtime = "nodejs";

export default async function TwitterImage() {
  return renderSocialShareImageResponse();
}
