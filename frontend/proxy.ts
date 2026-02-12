import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  // Routes publiques qui ne nécessitent pas d'authentification
  const publicRoutes = ["/", "/login", "/register", "/forgot-password", "/about"];
  const { pathname } = request.nextUrl;

  // Si c'est une route publique, laisser passer
  if (publicRoutes.includes(pathname) || pathname.startsWith("/api/auth")) {
    return NextResponse.next();
  }

  // Pour les routes protégées, la vérification se fait côté client
  // via le composant ProtectedRoute
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
