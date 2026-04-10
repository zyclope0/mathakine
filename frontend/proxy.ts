import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  getProtectedRouteRedirect,
  getRouteAccessRequirementsForPath,
} from "@/lib/auth/routeAccess";
import { resolveRouteAccessUser } from "@/lib/auth/server/routeSession";
import { buildMiddlewareCspBundle, CSP_NONCE_REQUEST_HEADER } from "@/lib/security/middlewareCsp";

function nextWithCsp(request: NextRequest, csp: string, requestNonce: string): NextResponse {
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("Content-Security-Policy", csp);
  requestHeaders.set(CSP_NONCE_REQUEST_HEADER, requestNonce);
  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", csp);
  return response;
}

function redirectWithCsp(request: NextRequest, target: string, csp: string): NextResponse {
  const redirectUrl = new URL(target, request.url);
  const response = NextResponse.redirect(redirectUrl);
  response.headers.set("Content-Security-Policy", csp);
  return response;
}

export async function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const isDevelopment = process.env.NODE_ENV === "development";
  const { csp, requestNonce } = buildMiddlewareCspBundle(isDevelopment);

  const requirements = getRouteAccessRequirementsForPath(pathname);
  if (!requirements) {
    return nextWithCsp(request, csp, requestNonce);
  }

  const accessToken = request.cookies.get("access_token")?.value;
  const session = await resolveRouteAccessUser(pathname, accessToken);

  if (session.state === "indeterminate") {
    return nextWithCsp(request, csp, requestNonce);
  }

  const redirectTarget = getProtectedRouteRedirect(session.user, requirements);
  if (!redirectTarget) {
    return nextWithCsp(request, csp, requestNonce);
  }

  return redirectWithCsp(request, redirectTarget, csp);
}

/**
 * Page-like routes only: CSP + auth. Excludes APIs, Next static assets, image
 * optimizer, Sentry tunnel, well-known static filenames, and paths that look
 * like file extensions (e.g. `/icons/foo.png`).
 */
export const config = {
  matcher: [
    "/((?!api/|_next/static|_next/image|monitoring|favicon.ico|robots.txt|sitemap.xml|manifest.json|.*\\..*).*)",
  ],
};
