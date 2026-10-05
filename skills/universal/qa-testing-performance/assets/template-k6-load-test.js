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
  // Option A (default): open-loop constant-arrival-rate. The generator fires
  // requests at a fixed rate regardless of how slow responses are, so a
  // stall shows up as p99 blowing out — not as the generator quietly
  // slowing down with it (see load-testing-patterns.md, "closed-loop
  // generators under-report tail latency"). preAllocatedVUs / maxVUs are
  // estimated from iteration rate * full iteration duration (including
  // journey think time); Little's law uses averages, then add measured margin,
  // with headroom for maxVUs so k6 can borrow extra VUs under a stall
  // instead of dropping iterations.
  scenarios: {
    default: {
      executor: 'constant-arrival-rate',
      rate: 50,                // iterations per timeUnit
      timeUnit: '1s',          // 50 iterations/sec
      duration: '5m',
      preAllocatedVUs: 100,    // illustrative start; measure full journey duration before sizing
      maxVUs: 300,             // ceiling if latency degrades — tune per target
    },
  },

  // Option B: closed-loop staged VU ramp-up. Use only for soak/leak-hunting
  // runs where tail latency is secondary (see the load-testing-patterns.md
  // "Which Model to Use" table) — not for SLO/gate tests.
  // stages: [
  //   { duration: '1m', target: 20 },   // ramp up
  //   { duration: '3m', target: 20 },   // hold at target
  //   { duration: '1m', target: 50 },   // ramp to peak
  //   { duration: '3m', target: 50 },   // hold at peak
  //   { duration: '1m', target: 0 },    // ramp down
  // ],

  // Option C: named scenarios with independent open-loop profiles (uncomment to use)
  // scenarios: {
  //   browse: {
  //     executor: 'ramping-arrival-rate',
  //     startRate: 0,
  //     timeUnit: '1s',
  //     preAllocatedVUs: 60,
  //     maxVUs: 150,
  //     stages: [
  //       { duration: '2m', target: 30 },
  //       { duration: '5m', target: 30 },
  //       { duration: '1m', target: 0 },
  //     ],
  //     exec: 'browseFlow',
  //     tags: { scenario: 'browse' },
  //   },
  //   checkout: {
  //     executor: 'ramping-arrival-rate',
  //     startRate: 0,
  //     timeUnit: '1s',
  //     preAllocatedVUs: 10,
  //     maxVUs: 30,
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

    // Generator-health gate: if k6 could not allocate a VU in time for an
    // iteration under constant-arrival-rate, it drops that iteration
    // instead of running it late. Dropped iterations mean the generator
    // (not just the target) was under-provisioned, and they silently
    // shrink your sample — any non-zero count invalidates the run.
    dropped_iterations: ['count==0'],

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

  const homeOk = check(homeRes, {
    'homepage 200': (r) => r.status === 200,
  });
  // errorRate is a k6 Rate metric: "% of added values that are non-zero".
  // add(1) only on failure means the metric never sees a 0 sample, so it
  // reads 100% the moment any failure occurs. Always add a value: true on
  // failure and false on success, so the rate is computed correctly.
  errorRate.add(!homeOk);

  sleep(randomIntBetween(1, 3));

  // --- Step 2: Search ---
  const searchTerms = ['widget', 'gadget', 'service', 'premium', 'starter'];
  const query = searchTerms[Math.floor(Math.random() * searchTerms.length)];

  const searchRes = http.get(`${BASE_URL}/api/search?q=${query}&limit=20`, {
    headers,
    tags: { name: 'search' },
  });

  const searchOk = check(searchRes, {
    'search 200': (r) => r.status === 200,
    'search has results': (r) => {
      try { return r.json('results').length > 0; }
      catch { return false; }
    },
  });
  errorRate.add(!searchOk);

  searchLatency.add(searchRes.timings.duration);
  sleep(randomIntBetween(2, 5));

  // --- Step 3: View item detail ---
  const itemRes = http.get(`${BASE_URL}/api/items/1`, {
    headers,
    tags: { name: 'item_detail' },
  });

  const itemOk = check(itemRes, {
    'item detail 200': (r) => r.status === 200,
  });
  errorRate.add(!itemOk);

  sleep(randomIntBetween(1, 3));

  // --- Step 4: Checkout (10% of users) ---
  if (Math.random() < 0.1) {
    const checkoutRes = http.post(`${BASE_URL}/api/checkout`, JSON.stringify({
      items: [{ id: 1, quantity: 1 }],
    }), {
      headers,
      tags: { name: 'checkout' },
    });

    const checkoutOk = check(checkoutRes, {
      'checkout 200/201': (r) => r.status === 200 || r.status === 201,
    });
    errorRate.add(!checkoutOk);

    checkoutLatency.add(checkoutRes.timings.duration);
  }

  // Arrival-rate executor already paces iteration starts.
}

// ---------------------------------------------------------------------------
// Named scenario functions (used with scenarios config above)
// ---------------------------------------------------------------------------

export function browseFlow(data) {
  const headers = { 'Content-Type': 'application/json' };

  const home = http.get(`${BASE_URL}/`, { tags: { name: 'homepage' } });
  errorRate.add(!check(home, { 'homepage 200': (r) => r.status === 200 }));
  sleep(randomIntBetween(2, 5));

  const item = http.get(`${BASE_URL}/api/items/1`, {
    headers,
    tags: { name: 'item_detail' },
  });
  errorRate.add(!check(item, { 'item detail 200': (r) => r.status === 200 }));
}

export function checkoutFlow(data) {
  const headers = { 'Content-Type': 'application/json' };

  const res = http.post(`${BASE_URL}/api/checkout`, JSON.stringify({
    items: [{ id: 1, quantity: 1 }],
  }), {
    headers,
    tags: { name: 'checkout' },
  });

  const ok = check(res, {
    'checkout success': (r) => r.status === 200 || r.status === 201,
  });
  errorRate.add(!ok);

  checkoutLatency.add(res.timings.duration);
  // Arrival-rate executor already paces iteration starts.
}

// ---------------------------------------------------------------------------
// Teardown: runs once after all VUs finish
// ---------------------------------------------------------------------------

export function teardown(data) {
  // Clean up test data if needed
  // http.del(`${BASE_URL}/api/test-data`, { headers: { Authorization: `Bearer ${data.token}` } });
}
