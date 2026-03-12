// k6 Load Testing Template
//
// Use this template for performance testing and capacity planning.
// Run: k6 run load-testing-k6.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ====================
// Configuration
// ====================

// Test configuration
export const options = {
  // Scenario 1: Load Test (ramp up to target load)
  scenarios: {
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },   // Ramp up to 50 users
        { duration: '5m', target: 50 },   // Stay at 50 users
        { duration: '2m', target: 100 },  // Ramp up to 100 users
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 200 },  // Ramp up to 200 users
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '2m', target: 0 },    // Ramp down
      ],
      gracefulRampDown: '30s',
    },

    // Scenario 2: Spike Test (sudden traffic spike)
    // spike_test: {
    //   executor: 'ramping-vus',
    //   startTime: '25m',
    //   stages: [
    //     { duration: '10s', target: 500 },  // Spike to 500 users
    //     { duration: '1m', target: 500 },   // Hold spike
    //     { duration: '10s', target: 0 },    // Drop to 0
    //   ],
    // },

    // Scenario 3: Soak Test (sustained load)
    // soak_test: {
    //   executor: 'constant-vus',
    //   vus: 100,
    //   duration: '1h',
    // },
  },

  // Performance thresholds (test fails if violated)
  thresholds: {
    // HTTP request duration
    'http_req_duration': [
      'p(95)<500',  // 95% of requests < 500ms
      'p(99)<1000', // 99% of requests < 1s
    ],

    // HTTP request failed rate
    'http_req_failed': [
      'rate<0.01',  // Error rate < 1%
    ],

    // Custom metrics
    'order_duration': ['p(95)<1000'],
    'errors': ['rate<0.05'],
  },

  // HTTP configuration
  httpDebug: 'full', // Change to 'full' for debugging

  // Discard response bodies to save memory
  discardResponseBodies: false, // Set to true for high-load tests
};

// ====================
// Custom Metrics
// ====================

const orderDuration = new Trend('order_duration');
const checkoutDuration = new Trend('checkout_duration');
const errorRate = new Rate('errors');
const orderCount = new Counter('orders_created');
const activeOrders = new Gauge('active_orders');

// ====================
// Configuration
// ====================

const BASE_URL = __ENV.BASE_URL || 'https://api.example.com';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'your-test-token';

// Test data
const PRODUCT_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const USER_IDS = Array.from({ length: 100 }, (_, i) => i + 1);

// ====================
// Setup (runs once)
// ====================

export function setup() {
  console.log('Starting load test');
  console.log(`Base URL: ${BASE_URL}`);

  // Health check
  const res = http.get(`${BASE_URL}/health`);
  check(res, {
    'health check passed': (r) => r.status === 200,
  });

  return {
    startTime: Date.now(),
  };
}

// ====================
// Main Test Scenario
// ====================

export default function (data) {
  const userId = randomItem(USER_IDS);

  // Request headers
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${AUTH_TOKEN}`,
    'X-User-ID': userId.toString(),
  };

  // Scenario: Create Order Flow
  group('Create Order Flow', function () {
    // Step 1: Get products
    group('Get Products', function () {
      const res = http.get(`${BASE_URL}/api/products`, { headers });

      check(res, {
        'products: status 200': (r) => r.status === 200,
        'products: has data': (r) => JSON.parse(r.body).data.length > 0,
      }) || errorRate.add(1);
    });

    // Step 2: Create order
    group('Create Order', function () {
      const orderStart = Date.now();

      const payload = JSON.stringify({
        user_id: userId,
        items: [
          {
            product_id: randomItem(PRODUCT_IDS),
            quantity: randomIntBetween(1, 5),
          },
        ],
      });

      const res = http.post(`${BASE_URL}/api/orders`, payload, { headers });

      const duration = Date.now() - orderStart;
      orderDuration.add(duration);

      const success = check(res, {
        'order: status 201': (r) => r.status === 201,
        'order: has order_id': (r) => JSON.parse(r.body).order_id !== undefined,
        'order: response time < 1s': (r) => r.timings.duration < 1000,
      });

      if (success) {
        orderCount.add(1);
        const order = JSON.parse(res.body);
        activeOrders.add(1);

        // Step 3: Process payment
        group('Process Payment', function () {
          const paymentPayload = JSON.stringify({
            order_id: order.order_id,
            payment_method: 'card',
            amount: order.total,
          });

          const paymentRes = http.post(`${BASE_URL}/api/payments`, paymentPayload, { headers });

          check(paymentRes, {
            'payment: status 200': (r) => r.status === 200,
            'payment: success': (r) => JSON.parse(r.body).status === 'success',
          }) || errorRate.add(1);

          sleep(0.5); // User waits for payment confirmation
        });

      } else {
        errorRate.add(1);
      }
    });
  });

  // Scenario: Browse Products (80% of users)
  if (Math.random() < 0.8) {
    group('Browse Products', function () {
      const res = http.get(`${BASE_URL}/api/products?page=1&limit=20`, { headers });

      check(res, {
        'browse: status 200': (r) => r.status === 200,
        'browse: response time < 500ms': (r) => r.timings.duration < 500,
      }) || errorRate.add(1);
    });
  }

  // Scenario: View Order History (20% of users)
  if (Math.random() < 0.2) {
    group('View Order History', function () {
      const res = http.get(`${BASE_URL}/api/orders?user_id=${userId}`, { headers });

      check(res, {
        'history: status 200': (r) => r.status === 200,
      }) || errorRate.add(1);
    });
  }

  // Think time (simulate user reading, clicking)
  sleep(randomIntBetween(1, 3));
}

// ====================
// Teardown (runs once)
// ====================

export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000 / 60;
  console.log(`Load test completed in ${duration.toFixed(2)} minutes`);
}

// ====================
// Advanced: Custom Summary
// ====================

export function handleSummary(data) {
  // Print summary to stdout
  console.log('=======================================');
  console.log('Load Test Summary');
  console.log('=======================================');
  console.log(`Total Requests: ${data.metrics.http_reqs.values.count}`);
  console.log(`Request Rate: ${data.metrics.http_reqs.values.rate.toFixed(2)} req/s`);
  console.log(`Failed Requests: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%`);
  console.log(`P95 Latency: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms`);
  console.log(`P99 Latency: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms`);
  console.log('=======================================');

  // Return JSON summary for CI/CD
  return {
    'summary.json': JSON.stringify(data, null, 2),
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}

// Helper for text summary
function textSummary(data, options) {
  return 'Load test completed';
}

// ====================
// Usage Examples
// ====================

/*
1. Basic load test:
   k6 run load-testing-k6.js

2. Custom target:
   k6 run --vus 100 --duration 10m load-testing-k6.js

3. Custom base URL:
   k6 run -e BASE_URL=https://staging.example.com load-testing-k6.js

4. Cloud execution:
   k6 cloud load-testing-k6.js

5. CI/CD integration:
   k6 run --out json=results.json load-testing-k6.js

6. Thresholds only (no summary):
   k6 run --quiet load-testing-k6.js

7. Different scenarios:
   k6 run --scenario spike_test load-testing-k6.js
*/
