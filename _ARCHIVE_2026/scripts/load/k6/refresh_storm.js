/**
 * Scénario de charge : Refresh Storm
 * 
 * Objectif : 150 req/min sur POST /api/auth/refresh
 * KPI ciblés :
 *   - p95 < 250ms
 *   - Aucun 5xx
 *   - Invalid token → 401 (pas de fallback)
 * 
 * Usage:
 *   k6 run --vus 3 --duration 60s refresh_storm.js
 *   (3 VU * 50 req/min = 150 requêtes/min)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métriques personnalisées
const successRate = new Rate('success_rate');
const refreshSuccessRate = new Rate('refresh_success_rate');

// Configuration
export const options = {
  stages: [
    { duration: '10s', target: 3 },   // Montée progressive
    { duration: '50s', target: 3 },   // Charge stable (3 VU = 150 req/min)
    { duration: '10s', target: 0 },   // Descente
  ],
  thresholds: {
    'http_req_duration': ['p(95)<250'],      // p95 < 250ms
    'refresh_success_rate': ['rate>0.99'],   // > 99% succès refresh
    'http_req_failed{status:5xx}': ['rate==0'], // Aucun 5xx
  },
};

// URL du backend
const BASE_URL = __ENV.BACKEND_URL || 'http://localhost:10000';

// Credentials de test
const TEST_USERNAME = __ENV.TEST_USERNAME || 'ObiWan';
const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'HelloThere123!';

export function setup() {
  // Setup : Login initial pour obtenir les cookies
  const loginPayload = JSON.stringify({
    username: TEST_USERNAME,
    password: TEST_PASSWORD,
  });

  const loginResponse = http.post(
    `${BASE_URL}/api/auth/login`,
    loginPayload,
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  if (loginResponse.status !== 200) {
    throw new Error(`Setup failed: Login returned ${loginResponse.status}`);
  }

  // Extraire les cookies de la réponse
  // k6 stocke automatiquement les cookies dans la session
  return { cookies: loginResponse.cookies };
}

export default function (data) {
  // POST /api/auth/refresh avec cookies HTTP-only uniquement
  // Note: k6 gère automatiquement les cookies de la session précédente
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    // k6 réutilise automatiquement les cookies de la session
  };

  // IMPORTANT: Ne PAS envoyer refresh_token dans le body
  // Le refresh_token doit être uniquement dans les cookies HTTP-only
  const response = http.post(`${BASE_URL}/api/auth/refresh`, JSON.stringify({}), params);

  // Vérifications
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'has access_token': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.access_token !== undefined;
      } catch (e) {
        return false;
      }
    },
    'no 5xx errors': (r) => r.status < 500,
    'response time < 250ms': (r) => r.timings.duration < 250,
  });

  refreshSuccessRate.add(success);

  // Test avec token invalide (doit retourner 401, pas de fallback)
  if (Math.random() < 0.1) { // 10% des requêtes testent un token invalide
    const invalidParams = {
      headers: {
        'Content-Type': 'application/json',
      },
      cookies: {
        refresh_token: 'invalid_token_should_fail',
      },
    };

    const invalidResponse = http.post(
      `${BASE_URL}/api/auth/refresh`,
      JSON.stringify({}),
      invalidParams
    );

    check(invalidResponse, {
      'invalid token returns 401': (r) => r.status === 401,
      'no fallback with invalid token': (r) => {
        // Vérifier qu'on ne reçoit pas un nouveau refresh_token malgré le token invalide
        try {
          const body = JSON.parse(r.body);
          return body.refresh_token === undefined;
        } catch (e) {
          return true; // Si erreur de parsing, c'est OK
        }
      },
    });
  }

  // Attendre avant la prochaine requête (pour atteindre 150 req/min)
  // 3 VU * 50 req/min = 50 req/min par VU = 1 req toutes les 1.2 secondes
  sleep(1.2);
}

