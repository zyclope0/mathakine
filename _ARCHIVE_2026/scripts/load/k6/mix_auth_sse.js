/**
 * Scénario de charge : Mix Auth + SSE
 * 
 * Objectif : 100 utilisateurs authentifiés déclenchent SSE après login
 * KPI ciblés :
 *   - Pas de fuite mémoire
 *   - Latence stable
 *   - Tous les utilisateurs peuvent se connecter et générer
 * 
 * Usage:
 *   k6 run --vus 100 --duration 120s mix_auth_sse.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';
import { Counter } from 'k6/metrics';

// Métriques personnalisées
const loginSuccessRate = new Rate('login_success_rate');
const sseSuccessRate = new Rate('sse_success_rate');
const usersCompleted = new Counter('users_completed');

// Configuration
export const options = {
  stages: [
    { duration: '20s', target: 100 },  // Montée progressive à 100 utilisateurs
    { duration: '80s', target: 100 },    // Charge stable
    { duration: '20s', target: 0 },      // Descente
  ],
  thresholds: {
    'login_success_rate': ['rate>0.99'],      // > 99% succès login
    'sse_success_rate': ['rate>0.95'],        // > 95% succès SSE
    'users_completed': ['count>90'],          // Au moins 90 utilisateurs complètent le scénario
  },
};

// URL du backend
const BASE_URL = __ENV.BACKEND_URL || 'http://localhost:10000';

// Credentials de test (utiliser plusieurs comptes si disponibles)
const TEST_USERNAME = __ENV.TEST_USERNAME || 'ObiWan';
const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'HelloThere123!';

export default function () {
  // Étape 1 : Login
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

  const loginSuccess = check(loginResponse, {
    'login status is 200': (r) => r.status === 200,
    'login has access_token': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.access_token !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  loginSuccessRate.add(loginSuccess);

  if (!loginSuccess) {
    return; // Si le login échoue, arrêter ce VU
  }

  // Extraire les cookies de la session
  const sessionCookies = loginResponse.cookies;

  // Attendre un peu avant de déclencher SSE
  sleep(1);

  // Étape 2 : Génération SSE
  const challengeTypes = ['SEQUENCE', 'PATTERN', 'PUZZLE'];
  const difficulty = 'medium';
  const ageGroup = 'GROUP_10_12';

  const url = `${BASE_URL}/api/challenges/generate-ai-stream?` +
    `challenge_type=${challengeTypes[Math.floor(Math.random() * challengeTypes.length)]}&` +
    `difficulty=${difficulty}&` +
    `age_group=${ageGroup}`;

  const sseParams = {
    headers: {
      'Accept': 'text/event-stream',
    },
    cookies: sessionCookies,
    timeout: '30s',
  };

  const sseResponse = http.get(url, sseParams);

  const sseSuccess = check(sseResponse, {
    'SSE status is 200': (r) => r.status === 200,
    'SSE has data': (r) => r.body && r.body.length > 0,
    'SSE authenticated': (r) => r.status !== 401,
  });

  sseSuccessRate.add(sseSuccess);

  // Étape 3 : Refresh token (optionnel, simule une session longue)
  if (Math.random() < 0.3) { // 30% des utilisateurs rafraîchissent leur token
    const refreshResponse = http.post(
      `${BASE_URL}/api/auth/refresh`,
      JSON.stringify({}),
      {
        headers: { 'Content-Type': 'application/json' },
        cookies: sessionCookies,
      }
    );

    check(refreshResponse, {
      'refresh status is 200': (r) => r.status === 200,
    });
  }

  // Étape 4 : Logout
  const logoutResponse = http.post(
    `${BASE_URL}/api/auth/logout`,
    JSON.stringify({}),
    {
      headers: { 'Content-Type': 'application/json' },
      cookies: sessionCookies,
    }
  );

  check(logoutResponse, {
    'logout status is 200': (r) => r.status === 200,
  });

  // Compter les utilisateurs qui ont complété le scénario
  if (loginSuccess && sseSuccess) {
    usersCompleted.add(1);
  }

  // Attendre avant la prochaine itération
  sleep(2);
}

