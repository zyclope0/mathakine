import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  getProtectedRouteRedirect,
  getRouteAccessRequirementsForPath,
} from "@/lib/auth/routeAccess";
import { resolveRouteAccessUser } from "@/lib/auth/server/routeSession";

export async function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const requirements = getRouteAccessRequirementsForPath(pathname);

  if (!requirements) {
    return NextResponse.next();
  }

  const accessToken = request.cookies.get("access_token")?.value;
  const session = await resolveRouteAccessUser(pathname, accessToken);

  if (session.state === "indeterminate") {
    return NextResponse.next();
  }

  const redirectTarget = getProtectedRouteRedirect(session.user, requirements);
  if (!redirectTarget) {
    return NextResponse.next();
  }

  const redirectUrl = new URL(redirectTarget, request.url);
  return NextResponse.redirect(redirectUrl);
}

export const config = {
  matcher: ["/home-learner/:path*", "/dashboard/:path*", "/admin/:path*"],
};
