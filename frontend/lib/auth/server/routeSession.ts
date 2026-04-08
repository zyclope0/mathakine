import { getBackendUrl } from "@/lib/api/backendUrl";
import {
  getRouteAccessRequirementsForPath,
  routeNeedsServerProfile,
  type RouteAccessRequirements,
  type RouteAccessUser,
} from "@/lib/auth/routeAccess";
import { validateAccessTokenWithBackend } from "@/lib/auth/server/validateTokenRuntime";
import { normalizeUserRole } from "@/lib/auth/userRoles";

interface LocalTokenPayload {
  exp?: number;
  role?: string;
  sub?: string;
  type?: string;
}

interface LocalTokenSession extends RouteAccessUser {
  username: string;
}

type SessionResolution =
  | { state: "authenticated"; user: RouteAccessUser }
  | { state: "unauthenticated"; user: null }
  | { state: "indeterminate"; user: null };

interface BackendCurrentUserResponse {
  access_scope?: "full" | "exercises_only";
  onboarding_completed_at?: string | null;
  role?: string | null;
}

function getJwtSecret(): string {
  return String(process.env.SECRET_KEY ?? "").trim();
}

function normalizeBase64Url(input: string): string {
  const padded = input.replace(/-/g, "+").replace(/_/g, "/");
  const remainder = padded.length % 4;
  if (remainder === 0) {
    return padded;
  }
  return `${padded}${"=".repeat(4 - remainder)}`;
}

function base64UrlToBytes(input: string): Uint8Array {
  const normalized = normalizeBase64Url(input);
  const binary = atob(normalized);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

function decodeJwtPart<T>(input: string): T | null {
  try {
    const bytes = base64UrlToBytes(input);
    const json = new TextDecoder().decode(bytes);
    return JSON.parse(json) as T;
  } catch {
    return null;
  }
}

async function verifyHs256Jwt(token: string, secret: string): Promise<LocalTokenPayload | null> {
  const tokenParts = token.split(".");
  if (tokenParts.length !== 3) {
    return null;
  }

  const encodedHeader = tokenParts[0];
  const encodedPayload = tokenParts[1];
  const encodedSignature = tokenParts[2];
  if (!encodedHeader || !encodedPayload || !encodedSignature) {
    return null;
  }

  const header = decodeJwtPart<{ alg?: string; typ?: string }>(encodedHeader);
  const payload = decodeJwtPart<LocalTokenPayload>(encodedPayload);
  if (!header || !payload || header.alg !== "HS256") {
    return null;
  }

  const signature = base64UrlToBytes(encodedSignature);
  const signatureBuffer = signature.buffer.slice(
    signature.byteOffset,
    signature.byteOffset + signature.byteLength
  ) as ArrayBuffer;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"]
  );

  const signingInput = new TextEncoder().encode(`${encodedHeader}.${encodedPayload}`);
  const isValid = await crypto.subtle.verify("HMAC", key, signatureBuffer, signingInput);
  if (!isValid) {
    return null;
  }

  if (payload.type !== "access" || !payload.sub || typeof payload.exp !== "number") {
    return null;
  }

  const nowInSeconds = Math.floor(Date.now() / 1000);
  if (payload.exp <= nowInSeconds) {
    return null;
  }

  return payload;
}

async function validateAccessTokenLocally(token: string): Promise<LocalTokenSession | null> {
  const secret = getJwtSecret();
  if (!secret) {
    return null;
  }

  try {
    const payload = await verifyHs256Jwt(token, secret);
    if (!payload?.sub) {
      return null;
    }

    return {
      isAuthenticated: true,
      role: normalizeUserRole(payload.role),
      username: payload.sub,
    };
  } catch {
    return null;
  }
}

async function validateAccessTokenViaBackend(token: string): Promise<boolean | null> {
  return validateAccessTokenWithBackend(getBackendUrl(), token, "routeSession");
}

async function fetchCurrentUserFromBackend(
  token: string
): Promise<RouteAccessUser | null | "error"> {
  try {
    const response = await fetch(`${getBackendUrl()}/api/users/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    });

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      return "error";
    }

    const user = (await response.json()) as BackendCurrentUserResponse;
    return {
      isAuthenticated: true,
      role: normalizeUserRole(user.role ?? null),
      access_scope: user.access_scope ?? null,
      onboarding_completed_at: user.onboarding_completed_at ?? null,
    };
  } catch {
    return "error";
  }
}

async function resolveAuthenticatedSession(
  token: string,
  requirements: RouteAccessRequirements
): Promise<SessionResolution> {
  const locallyValidatedSession = await validateAccessTokenLocally(token);
  if (!locallyValidatedSession) {
    const backendValidation = await validateAccessTokenViaBackend(token);
    if (backendValidation === false) {
      return { state: "unauthenticated", user: null };
    }
    if (backendValidation === null) {
      return { state: "indeterminate", user: null };
    }
  }

  if (
    !routeNeedsServerProfile(requirements) &&
    locallyValidatedSession &&
    locallyValidatedSession.role
  ) {
    return { state: "authenticated", user: locallyValidatedSession };
  }

  const backendUser = await fetchCurrentUserFromBackend(token);
  if (backendUser === null) {
    return { state: "unauthenticated", user: null };
  }
  if (backendUser === "error") {
    return { state: "indeterminate", user: null };
  }

  return { state: "authenticated", user: backendUser };
}

export async function resolveRouteAccessUser(
  pathname: string,
  accessToken: string | undefined
): Promise<SessionResolution> {
  const requirements = getRouteAccessRequirementsForPath(pathname);
  if (!requirements) {
    return { state: "indeterminate", user: null };
  }

  if (!accessToken) {
    return { state: "unauthenticated", user: null };
  }

  return resolveAuthenticatedSession(accessToken, requirements);
}
