/**
 * k6 Load Test Template
 *
 * Starter script with staged ramp-up, performance budget thresholds,
 * custom metrics, tagged scenarios, and parameterized data.
 *
 * Usage:
 *   k6 run template-k6-load-test.js
 *   k6 run --env BASE_URL=https://staging.example.com template-k6-load-test.js
 *   k6 run --out json=results.json template-k6-load-test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

// Custom metrics
const errorRate = new Rate('custom_error_rate');
const searchLatency = new Trend('custom_search_latency', true);
const checkoutLatency = new Trend('custom_checkout_latency', true);

// ---------------------------------------------------------------------------
// Options: stages, thresholds (performance budgets), and scenarios
// ---------------------------------------------------------------------------

export const options = {
  // Option A: Simple staged ramp-up (uncomment to use)
  stages: [
    { duration: '1m', target: 20 },   // ramp up
    { duration: '3m', target: 20 },   // hold at target
    { duration: '1m', target: 50 },   // ramp to peak
    { duration: '3m', target: 50 },   // hold at peak
    { duration: '1m', target: 0 },    // ramp down
  ],

  // Option B: Named scenarios with independent VU profiles (uncomment to use)
  // scenarios: {
  //   browse: {
  //     executor: 'ramping-vus',
  //     startVUs: 0,
  //     stages: [
  //       { duration: '2m', target: 30 },
  //       { duration: '5m', target: 30 },
  //       { duration: '1m', target: 0 },
  //     ],
  //     exec: 'browseFlow',
  //     tags: { scenario: 'browse' },
  //   },
  //   checkout: {
  //     executor: 'ramping-vus',
  //     startVUs: 0,
  //     stages: [
  //       { duration: '2m', target: 5 },
  //       { duration: '5m', target: 5 },
  //       { duration: '1m', target: 0 },
  //     ],
  //     exec: 'checkoutFlow',
  //     tags: { scenario: 'checkout' },
  //   },
  // },

  // Performance budgets — test fails (non-zero exit) when any threshold breaches
  thresholds: {
    // Global latency budgets
    http_req_duration: [
      'p(50)<200',    // p50 under 200ms
      'p(95)<500',    // p95 under 500ms
      'p(99)<1000',   // p99 under 1s
    ],

    // Error rate budget
    http_req_failed: ['rate<0.01'],    // < 1% HTTP errors
    custom_error_rate: ['rate<0.01'],  // < 1% application errors

    // Per-endpoint budgets (tagged requests)
    'http_req_duration{name:search}': ['p(95)<300'],
    'http_req_duration{name:checkout}': ['p(95)<800'],

    // Custom metric budgets
    custom_search_latency: ['p(95)<300'],
    custom_checkout_latency: ['p(95)<800'],
  },
};

// ---------------------------------------------------------------------------
// Setup: runs once before all VUs (auth tokens, shared data)
// ---------------------------------------------------------------------------

export function setup() {
  // Example: obtain an auth token
  // const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
  //   email: 'loadtest@example.com',
  //   password: __ENV.TEST_PASSWORD || 'testpassword',
  // }), { headers: { 'Content-Type': 'application/json' } });
  //
  // return { token: loginRes.json('access_token') };

  return {};
}

// ---------------------------------------------------------------------------
// Default function: runs per VU iteration
// ---------------------------------------------------------------------------

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    // Authorization: `Bearer ${data.token}`,
  };

  // --- Step 1: Browse homepage ---
  const homeRes = http.get(`${BASE_URL}/`, {
    tags: { name: 'homepage' },
  });

  check(homeRes, {
    'homepage 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(randomIntBetween(1, 3));

  // --- Step 2: Search ---
  const searchTerms = ['widget', 'gadget', 'service', 'premium', 'starter'];
  const query = searchTerms[Math.floor(Math.random() * searchTerms.length)];

  const searchRes = http.get(`${BASE_URL}/api/search?q=${query}&limit=20`, {
    headers,
    tags: { name: 'search' },
  });

  check(searchRes, {
    'search 200': (r) => r.status === 200,
    'search has results': (r) => {
      try { return r.json('results').length > 0; }
      catch { return false; }
    },
  }) || errorRate.add(1);

  searchLatency.add(searchRes.timings.duration);
  sleep(randomIntBetween(2, 5));

  // --- Step 3: View item detail ---
  const itemRes = http.get(`${BASE_URL}/api/items/1`, {
    headers,
    tags: { name: 'item_detail' },
  });

  check(itemRes, {
    'item detail 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(randomIntBetween(1, 3));

  // --- Step 4: Checkout (10% of users) ---
  if (Math.random() < 0.1) {
    const checkoutRes = http.post(`${BASE_URL}/api/checkout`, JSON.stringify({
      items: [{ id: 1, quantity: 1 }],
    }), {
      headers,
      tags: { name: 'checkout' },
    });

    check(checkoutRes, {
      'checkout 200/201': (r) => r.status === 200 || r.status === 201,
    }) || errorRate.add(1);

    checkoutLatency.add(checkoutRes.timings.duration);
  }

  sleep(randomIntBetween(1, 2));
}

// ---------------------------------------------------------------------------
// Named scenario functions (used with scenarios config above)
// ---------------------------------------------------------------------------

export function browseFlow(data) {
  const headers = { 'Content-Type': 'application/json' };

  http.get(`${BASE_URL}/`, { tags: { name: 'homepage' } });
  sleep(randomIntBetween(2, 5));

  http.get(`${BASE_URL}/api/items/1`, {
    headers,
    tags: { name: 'item_detail' },
  });
  sleep(randomIntBetween(1, 3));
}

export function checkoutFlow(data) {
  const headers = { 'Content-Type': 'application/json' };

  const res = http.post(`${BASE_URL}/api/checkout`, JSON.stringify({
    items: [{ id: 1, quantity: 1 }],
  }), {
    headers,
    tags: { name: 'checkout' },
  });

  check(res, {
    'checkout success': (r) => r.status === 200 || r.status === 201,
  });

  checkoutLatency.add(res.timings.duration);
  sleep(randomIntBetween(1, 2));
}

// ---------------------------------------------------------------------------
// Teardown: runs once after all VUs finish
// ---------------------------------------------------------------------------

export function teardown(data) {
  // Clean up test data if needed
  // http.del(`${BASE_URL}/api/test-data`, { headers: { Authorization: `Bearer ${data.token}` } });
}
