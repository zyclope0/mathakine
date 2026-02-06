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
    const exerciseType = searchParams.get('exercise_type') || 'addition';
    // Support des deux paramètres : age_group (nouveau) et difficulty (legacy)
    const ageGroup = searchParams.get('age_group') || searchParams.get('difficulty') || '6-8';
    const prompt = searchParams.get('prompt') || '';

    // Construire l'URL du backend avec age_group
    const backendParams = new URLSearchParams({
      exercise_type: exerciseType,
      age_group: ageGroup,
    });
    if (prompt) {
      backendParams.append('prompt', prompt);
    }

    const backendUrl = `${getBackendUrl()}/api/exercises/generate-ai-stream?${backendParams.toString()}`;

    // Récupérer les cookies de la requête
    const cookies = request.headers.get('cookie') || '';

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

