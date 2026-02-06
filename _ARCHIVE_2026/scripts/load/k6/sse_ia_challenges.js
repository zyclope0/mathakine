/**
 * Scénario de charge : SSE IA Challenges
 * 
 * Objectif : 200 connexions simultanées GET /api/challenges/generate-ai-stream
 * Durée : 45 secondes par connexion
 * KPI ciblés :
 *   - CPU < 75%
 *   - Queue OpenAI stable
 *   - 0 drop SSE
 * 
 * Usage:
 *   k6 run --vus 200 --duration 60s sse_ia_challenges.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';
import { Counter } from 'k6/metrics';

// Métriques personnalisées
const sseSuccessRate = new Rate('sse_success_rate');
const sseConnections = new Counter('sse_connections');
const sseDropped = new Counter('sse_dropped');

// Configuration
export const options = {
  stages: [
    { duration: '10s', target: 200 },  // Montée rapide à 200 connexions
    { duration: '45s', target: 200 },    // Maintien 45 secondes (durée génération)
    { duration: '10s', target: 0 },     // Descente
  ],
  thresholds: {
    'sse_success_rate': ['rate>0.95'],        // > 95% succès
    'sse_dropped': ['count==0'],              // 0 connexion drop
    'http_req_failed{status:401}': ['rate==0'], // Aucun 401 (toutes authentifiées)
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

  // k6 stocke automatiquement les cookies dans la session
  return { cookies: loginResponse.cookies };
}

export default function (data) {
  // Paramètres de génération variés pour simuler un usage réel
  const challengeTypes = ['SEQUENCE', 'PATTERN', 'PUZZLE', 'CALCULATION', 'CHESS'];
  const difficulties = ['easy', 'medium', 'hard'];
  const ageGroups = ['GROUP_6_8', 'GROUP_10_12', 'GROUP_13_15'];

  const challengeType = challengeTypes[Math.floor(Math.random() * challengeTypes.length)];
  const difficulty = difficulties[Math.floor(Math.random() * difficulties.length)];
  const ageGroup = ageGroups[Math.floor(Math.random() * ageGroups.length)];

  // Construire l'URL avec les paramètres
  const url = `${BASE_URL}/api/challenges/generate-ai-stream?` +
    `challenge_type=${challengeType}&` +
    `difficulty=${difficulty}&` +
    `age_group=${ageGroup}`;

  const params = {
    headers: {
      'Accept': 'text/event-stream',
    },
    // k6 réutilise automatiquement les cookies de la session
    timeout: '60s', // Timeout de 60 secondes pour la connexion SSE
  };

  // GET /api/challenges/generate-ai-stream (SSE)
  const response = http.get(url, params);

  sseConnections.add(1);

  // Vérifications
  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'content-type is text/event-stream': (r) => {
      const contentType = r.headers['Content-Type'] || r.headers['content-type'];
      return contentType && contentType.includes('text/event-stream');
    },
    'has SSE data': (r) => {
      // Vérifier qu'on reçoit des données SSE (format: "data: {...}\n\n")
      return r.body && r.body.length > 0;
    },
    'authenticated (no 401)': (r) => r.status !== 401,
  });

  sseSuccessRate.add(success);

  // Si la connexion a échoué, compter comme drop
  if (!success || response.status >= 400) {
    sseDropped.add(1);
  }

  // Attendre la fin de la génération (simulation)
  // En réalité, k6 fermera la connexion après le timeout
  sleep(45);
}

export function teardown(data) {
  // Logout pour nettoyer les sessions
  // k6 réutilise automatiquement les cookies de la session
  const logoutResponse = http.post(
    `${BASE_URL}/api/auth/logout`,
    JSON.stringify({}),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  check(logoutResponse, {
    'logout successful': (r) => r.status === 200,
  });
}

