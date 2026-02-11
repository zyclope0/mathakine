/**
 * Endpoint de diagnostic : vérifie si le cookie access_token est présent.
 * Utilisé pour débugger les erreurs "Cookie manquant" en production.
 * Retourne 200 si le cookie existe, 401 sinon.
 */
import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const hasCookie = !!request.cookies.get('access_token')?.value;
  const status = hasCookie ? 200 : 401;
  return new Response(
    JSON.stringify({
      ok: hasCookie,
      has_access_token_cookie: hasCookie,
      hint: hasCookie
        ? 'Cookie présent - les requêtes proxy devraient fonctionner'
        : 'Cookie manquant - déconnectez-vous et reconnectez-vous, ou vérifiez que sync-cookie a été appelé après login',
    }),
    {
      status,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}
