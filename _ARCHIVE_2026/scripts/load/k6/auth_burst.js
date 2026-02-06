/**
 * Scénario de charge : Auth Burst
 * 
 * Objectif : 300 connexions/min sur POST /api/auth/login
 * KPI ciblés :
 *   - p95 < 400ms
 *   - Taux succès > 99%
 * 
 * Usage:
 *   k6 run --vus 5 --duration 60s auth_burst.js
 *   (5 VU * 60s = 300 requêtes/min)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métriques personnalisées
const successRate = new Rate('success_rate');

// Configuration
export const options = {
  stages: [
    { duration: '10s', target: 5 },   // Montée progressive
    { duration: '50s', target: 5 },   // Charge stable (5 VU = 300 req/min)
    { duration: '10s', target: 0 },   // Descente
  ],
  thresholds: {
    'http_req_duration': ['p(95)<400'],      // p95 < 400ms
    'success_rate': ['rate>0.99'],           // > 99% succès
    'http_req_failed': ['rate<0.01'],        // < 1% échecs
  },
};

// URL du backend (configurable via variable d'environnement)
const BASE_URL = __ENV.BACKEND_URL || 'http://localhost:10000';

// Credentials de test (utiliser un compte de test dédié)
const TEST_USERNAME = __ENV.TEST_USERNAME || 'ObiWan';
const TEST_PASSWORD = __ENV.TEST_PASSWORD || 'HelloThere123!';

export default function () {
  // POST /api/auth/login
  const loginPayload = JSON.stringify({
    username: TEST_USERNAME,
    password: TEST_PASSWORD,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = http.post(`${BASE_URL}/api/auth/login`, loginPayload, params);

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
    'has user data': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.user !== undefined && body.user.id !== undefined;
      } catch (e) {
        return false;
      }
    },
    'response time < 400ms': (r) => r.timings.duration < 400,
  });

  successRate.add(success);

  // Attendre avant la prochaine requête (pour atteindre 300 req/min)
  // 5 VU * 12 req/min = 60 req/min par VU = 1 req toutes les 5 secondes
  sleep(5);
}

// Note: Pour utiliser handleSummary avec textSummary, installer k6 avec:
// import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
// export function handleSummary(data) {
//   return {
//     'stdout': textSummary(data, { indent: ' ', enableColors: true }),
//     'results/auth_burst_summary.json': JSON.stringify(data),
//   };
// }

