# Performance Testing Template: k6

Use this template for load and performance testing with k6, a modern developer-centric load testing tool.

## Why k6 (2024-2025)

**Advantages over JMeter/Gatling**:
- JavaScript DSL (familiar syntax)
- CLI-first approach (no GUI overhead)
- Built-in Grafana Cloud integration
- Excellent CI/CD integration
- Real-time metrics and thresholds
- Protocol Buffers and gRPC support

## Basic Load Test

```javascript
// load-test.js
import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate } from 'k6/metrics'

// Custom metrics
const errorRate = new Rate('errors')

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users over 2 minutes
    { duration: '5m', target: 100 },   // Stay at 100 users for 5 minutes
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% under 500ms, 99% under 1s
    http_req_failed: ['rate<0.01'],                   // Error rate under 1%
    errors: ['rate<0.1'],                             // Custom error rate under 10%
  }
}

export default function () {
  // GET request
  const response = http.get('https://api.example.com/products')

  // Validate response
  const checkResult = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'body contains products': (r) => r.json('products') !== undefined
  })

  // Track errors
  errorRate.add(!checkResult)

  // Think time (simulate user behavior)
  sleep(1)
}
```

## API Testing with Authentication

```javascript
import http from 'k6/http'
import { check } from 'k6'

export const options = {
  vus: 50, // 50 virtual users
  duration: '5m'
}

// Setup: Authenticate once per VU
export function setup() {
  const loginRes = http.post('https://api.example.com/auth/login', {
    email: 'test@example.com',
    password: 'password123'
  })

  const token = loginRes.json('token')
  return { token }
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json'
  }

  // Authenticated requests
  const productsRes = http.get('https://api.example.com/products', { headers })
  check(productsRes, {
    'products loaded': (r) => r.status === 200
  })

  const ordersRes = http.get('https://api.example.com/orders', { headers })
  check(ordersRes, {
    'orders loaded': (r) => r.status === 200
  })
}
```

## User Scenarios (Realistic Workflows)

```javascript
import http from 'k6/http'
import { check, sleep, group } from 'k6'
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js'

export const options = {
  scenarios: {
    // 80% of users browse products
    browsers: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 80 },
        { duration: '10m', target: 80 },
        { duration: '2m', target: 0 }
      ],
      exec: 'browseProducts'
    },
    // 20% of users make purchases
    buyers: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 20 },
        { duration: '10m', target: 20 },
        { duration: '2m', target: 0 }
      ],
      exec: 'purchaseFlow'
    }
  },
  thresholds: {
    'group_duration{group:::Browse Products}': ['p(95)<2000'],
    'group_duration{group:::Purchase Flow}': ['p(95)<5000']
  }
}

export function browseProducts() {
  group('Browse Products', () => {
    // Homepage
    http.get('https://api.example.com/')
    sleep(2)

    // Category page
    const categories = ['laptops', 'phones', 'tablets']
    http.get(`https://api.example.com/products?category=${randomItem(categories)}`)
    sleep(3)

    // Product detail
    const productId = Math.floor(Math.random() * 100) + 1
    http.get(`https://api.example.com/products/${productId}`)
    sleep(2)
  })
}

export function purchaseFlow() {
  group('Purchase Flow', () => {
    // Login
    const loginRes = http.post('https://api.example.com/auth/login', {
      email: 'buyer@example.com',
      password: 'password'
    })
    const token = loginRes.json('token')
    const headers = { 'Authorization': `Bearer ${token}` }

    sleep(1)

    // Add to cart
    http.post('https://api.example.com/cart', {
      productId: 42,
      quantity: 1
    }, { headers })

    sleep(2)

    // Checkout
    http.post('https://api.example.com/orders', {
      cartId: '123',
      paymentMethod: 'card'
    }, { headers })

    sleep(1)
  })
}
```

## Spike Testing

```javascript
export const options = {
  stages: [
    { duration: '10s', target: 100 },   // Normal load
    { duration: '1m', target: 100 },    // Sustain normal load
    { duration: '10s', target: 1000 },  // SPIKE to 10x load
    { duration: '3m', target: 1000 },   // Sustain spike
    { duration: '10s', target: 100 },   // Drop back to normal
    { duration: '3m', target: 100 },    // Recovery period
    { duration: '10s', target: 0 }      // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<3000'],  // Allow higher latency during spike
    http_req_failed: ['rate<0.05']      // Allow 5% errors during spike
  }
}
```

## Stress Testing (Find Breaking Point)

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },
    { duration: '5m', target: 300 },
    { duration: '2m', target: 400 },  // Continue increasing until system breaks
    { duration: '5m', target: 400 },
    { duration: '10m', target: 0 }
  ]
}
```

## Soak Testing (Endurance)

```javascript
export const options = {
  stages: [
    { duration: '5m', target: 100 },   // Ramp up
    { duration: '8h', target: 100 },   // Sustained load for 8 hours
    { duration: '5m', target: 0 }      // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<1000'],
    http_req_failed: ['rate<0.001']    // Very low error rate for sustained test
  }
}
```

## Custom Metrics and Trends

```javascript
import { Trend, Counter, Gauge } from 'k6/metrics'

// Custom metrics
const productLoadTime = new Trend('product_load_time')
const cartItemsCount = new Gauge('cart_items')
const ordersPlaced = new Counter('orders_placed')

export default function () {
  const start = Date.now()
  const res = http.get('https://api.example.com/products/42')
  const duration = Date.now() - start

  productLoadTime.add(duration)

  if (res.status === 200) {
    const product = res.json()
    // Track cart items
    cartItemsCount.add(product.quantity || 0)
  }

  // Simulate order placement
  if (Math.random() < 0.1) {  // 10% of users place order
    http.post('https://api.example.com/orders', {})
    ordersPlaced.add(1)
  }
}
```

## Thresholds and SLOs

```javascript
export const options = {
  thresholds: {
    // HTTP metrics
    http_req_duration: [
      'p(50)<200',    // 50% under 200ms
      'p(90)<400',    // 90% under 400ms
      'p(95)<500',    // 95% under 500ms
      'p(99)<1000'    // 99% under 1s
    ],
    'http_req_duration{name:ProductPage}': ['p(95)<300'],
    'http_req_duration{name:Checkout}': ['p(95)<1000'],

    // Error rates
    http_req_failed: ['rate<0.01'],  // Total error rate < 1%
    'http_req_failed{name:Checkout}': ['rate<0.001'],  // Checkout errors < 0.1%

    // Custom metrics
    'product_load_time': ['p(95)<500'],
    'orders_placed': ['count>100']  // At least 100 orders during test
  }
}
```

## Data-Driven Testing

```javascript
import { SharedArray } from 'k6/data'
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js'

// Load test data once (shared across VUs)
const testData = new SharedArray('users', function () {
  return papaparse.parse(open('./test-users.csv'), { header: true }).data
})

export default function () {
  // Each VU gets a different user
  const user = testData[__VU % testData.length]

  const loginRes = http.post('https://api.example.com/auth/login', {
    email: user.email,
    password: user.password
  })

  check(loginRes, {
    'login successful': (r) => r.status === 200
  })
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Run nightly
  workflow_dispatch:

jobs:
  k6-load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run k6 load test
        uses: grafana/k6-action@v0.3.0
        with:
          filename: load-test.js
          cloud: true
          token: ${{ secrets.K6_CLOUD_TOKEN }}

      - name: Check thresholds
        if: failure()
        run: |
          echo "Load test thresholds failed!"
          exit 1
```

### Docker

```bash
# Run k6 in Docker
docker run --rm -i grafana/k6 run - <load-test.js

# With output to InfluxDB
docker run --rm \
  -e K6_OUT=influxdb=http://influxdb:8086/k6 \
  grafana/k6 run /scripts/load-test.js
```

## Running Tests

```bash
# Basic run
k6 run load-test.js

# With custom VUs and duration
k6 run --vus 100 --duration 30s load-test.js

# Output to file
k6 run --out json=results.json load-test.js

# Cloud execution
k6 cloud load-test.js

# With environment variables
k6 run -e BASE_URL=https://staging.example.com load-test.js
```

## Analyzing Results

```javascript
// Example summary output
data_received..................: 148 MB  2.5 MB/s
data_sent......................: 13 MB   219 kB/s
http_req_blocked...............: avg=1.46ms   min=1µs    med=5µs     max=1.03s   p(90)=11µs   p(95)=15µs
http_req_connecting............: avg=700µs    min=0s     med=0s      max=608ms   p(90)=0s     p(95)=0s
http_req_duration..............: avg=145.12ms min=100ms  med=124ms   max=2.35s   p(90)=203ms  p(95)=232ms
http_req_failed................: 0.52%   [check] 52    [x] 9948
http_req_receiving.............: avg=332µs    min=22µs   med=108µs   max=117ms   p(90)=214µs  p(95)=278µs
http_req_sending...............: avg=88µs     min=7µs    med=29µs    max=5.12ms  p(90)=149µs  p(95)=186µs
http_req_tls_handshaking.......: avg=0s       min=0s     med=0s      max=0s      p(90)=0s     p(95)=0s
http_req_waiting...............: avg=144.7ms  min=100ms  med=124ms   max=2.35s   p(90)=202ms  p(95)=232ms
http_reqs......................: 10000   166.666667/s
iteration_duration.............: avg=1.14s    min=1s     med=1.12s   max=3.37s   p(90)=1.2s   p(95)=1.23s
iterations.....................: 10000   166.666667/s
vus............................: 100     min=100 max=100
vus_max........................: 100     min=100 max=100
```

## Best Practices Checklist

- [ ] Define realistic load scenarios (not just max load)
- [ ] Use stages for gradual ramp-up
- [ ] Set meaningful thresholds (based on SLOs)
- [ ] Include think time to simulate real users
- [ ] Test authentication flows separately
- [ ] Monitor backend metrics during tests (CPU, memory, DB connections)
- [ ] Run tests from multiple geographic regions
- [ ] Test during expected peak hours
- [ ] Gradually increase load to find breaking point
- [ ] Include soak tests for long-running stability

## Common Patterns

```javascript
// Pattern: Weighted scenarios
export const options = {
  scenarios: {
    light_load: {
      executor: 'constant-vus',
      vus: 50,
      duration: '10m',
      exec: 'browsing'
    },
    heavy_load: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 100,
      stages: [
        { duration: '5m', target: 50 },
        { duration: '10m', target: 50 }
      ],
      exec: 'checkout'
    }
  }
}

// Pattern: Smoke test (quick validation)
export const options = {
  vus: 1,
  duration: '1m',
  thresholds: {
    http_req_failed: ['rate<0.01']
  }
}

// Pattern: Breakpoint test (find max capacity)
export const options = {
  executor: 'ramping-arrival-rate',
  startRate: 1,
  timeUnit: '1s',
  preAllocatedVUs: 500,
  maxVUs: 1000,
  stages: [
    { duration: '2h', target: 100 }  // Slowly ramp up until system breaks
  ]
}
```

## Related Resources

See [../../references/comprehensive-testing-guide.md](../../references/comprehensive-testing-guide.md) for performance testing strategies and [../../references/shift-left-testing.md](../../references/shift-left-testing.md) for early performance validation.
