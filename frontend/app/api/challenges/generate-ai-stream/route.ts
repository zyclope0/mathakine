/**
 * Route API Next.js pour proxy SSE vers le backend
 * Permet de transmettre les cookies d'authentification
 */
import { NextRequest } from 'next/server';

// URL du backend
// En développement: peut utiliser localhost par défaut
// En production: DOIT être définie via NEXT_PUBLIC_API_BASE_URL
const BACKEND_URL = 
  process.env.NEXT_PUBLIC_API_BASE_URL || 
  process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'development' ? 'http://localhost:10000' : '');

// Validation en production uniquement (au runtime, pas au build)
function getBackendUrl(): string {
  const url = BACKEND_URL || (process.env.NODE_ENV === 'development' ? 'http://localhost:10000' : '');
  
  if (process.env.NODE_ENV === 'production') {
    if (!url || url.includes('localhost')) {
      throw new Error(
        'NEXT_PUBLIC_API_BASE_URL doit être défini en production et ne peut pas être localhost'
      );
    }
  }
  
  return url;
}

export async function GET(request: NextRequest) {
  try {
    // Récupérer les paramètres de la requête
    const searchParams = request.nextUrl.searchParams;
    const challengeType = searchParams.get('challenge_type') || 'sequence';
    const ageGroup = searchParams.get('age_group') || '10-12';
    const prompt = searchParams.get('prompt') || '';

    // Construire l'URL du backend
    const backendParams = new URLSearchParams({
      challenge_type: challengeType,
      age_group: ageGroup,
    });
    if (prompt) {
      backendParams.append('prompt', prompt);
    }

    const backendUrl = `${getBackendUrl()}/api/challenges/generate-ai-stream?${backendParams.toString()}`;

    // Récupérer les cookies de la requête (tous les cookies disponibles)
    const cookies = request.cookies.getAll()
      .map(cookie => `${cookie.name}=${cookie.value}`)
      .join('; ');

    // Debug: Vérifier si les cookies d'authentification sont présents
    const hasAuthCookie = request.cookies.get('access_token');
    if (process.env.NODE_ENV === 'development') {
      console.log('[AI Stream Proxy] Auth cookie present:', !!hasAuthCookie);
    }

    // Si pas de cookie d'authentification, retourner une erreur immédiatement
    if (!hasAuthCookie) {
      return new Response(
        `data: ${JSON.stringify({ type: 'error', message: 'Non authentifié' })}\n\n`,
        {
          status: 200, // 200 pour que EventSource reçoive le message
          headers: {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
          },
        }
      );
    }

    // Créer un stream vers le backend
    const backendResponse = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Cookie': cookies,
      },
      // Ne pas suivre les redirections automatiquement
      redirect: 'manual',
    });

    if (!backendResponse.ok && backendResponse.status !== 200) {
      return new Response(
        JSON.stringify({ 
          error: `Backend error: ${backendResponse.status} ${backendResponse.statusText}` 
        }),
        {
          status: backendResponse.status,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }

    // Retourner le stream SSE directement
    return new Response(backendResponse.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
      },
    });
  } catch (error) {
    // Logger l'erreur de manière sécurisée
    if (process.env.NODE_ENV === 'development') {
      console.error('Erreur proxy SSE:', error);
    }
    return new Response(
      JSON.stringify({ 
        error: 'Erreur lors de la connexion au backend',
        details: error instanceof Error ? error.message : String(error)
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}

