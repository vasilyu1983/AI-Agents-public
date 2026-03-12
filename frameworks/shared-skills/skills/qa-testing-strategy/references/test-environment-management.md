# Test Environment Management

Test environment provisioning, configuration, lifecycle management, and cost optimization -- from local dev through pre-production.

## Contents

- Environment Types
- Environment-as-Code
- Database Seeding and Fixtures
- Service Virtualization
- Environment Isolation Strategies
- Shared vs Dedicated Environments
- Environment Drift Detection
- Secrets Management
- Provisioning Automation
- Teardown and Cleanup
- Health Monitoring
- Cost Optimization
- Environment Management Checklist
- Related Resources

---

## Environment Types

| Environment | Purpose | Data | Lifecycle | Who Uses It |
|-------------|---------|------|-----------|-------------|
| **Local** | Developer testing | Synthetic/seeded | Persistent | Individual devs |
| **CI** | Automated tests | Synthetic, ephemeral | Per-pipeline | CI system |
| **Preview/PR** | Feature review | Seeded from template | Per-PR, ephemeral | Devs + reviewers |
| **Staging** | Integration testing | Sanitized prod subset | Long-lived | QA team |
| **Pre-prod** | Release validation | Prod-like volume | Long-lived | QA + Ops |
| **Prod** | Live users | Real data | Permanent | Everyone |

### Environment Maturity Model

```text
Level 1: Manual setup       → "Works on my machine" problems
Level 2: Documented setup   → Wiki/README with manual steps
Level 3: Scripted setup     → Shell scripts, Makefiles
Level 4: Environment-as-code → Docker Compose, Terraform
Level 5: Self-service       → On-demand provisioning, auto-teardown
```

---

## Environment-as-Code

### Docker Compose (Local + CI)

```yaml
# docker-compose.test.yml
version: "3.9"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: test
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://test:test@db:5432/testdb
      - REDIS_URL=redis://cache:6379
      - NODE_ENV=test
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: testdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - ./scripts/seed.sql:/docker-entrypoint-initdb.d/seed.sql
    tmpfs:
      - /var/lib/postgresql/data  # RAM disk for speed

  cache:
    image: redis:7-alpine

  mailhog:
    image: mailhog/mailhog
    ports:
      - "8025:8025"  # Web UI for email testing
```

```bash
# Start environment
docker compose -f docker-compose.test.yml up -d

# Run tests against it
npm run test:e2e

# Tear down
docker compose -f docker-compose.test.yml down -v
```

### Terraform (Cloud Environments)

```hcl
# environments/staging/main.tf
module "staging_env" {
  source = "../../modules/test-environment"

  environment_name = "staging"
  app_version      = var.app_version
  instance_type    = "t3.medium"
  db_instance_class = "db.t3.medium"

  # Smaller resources than prod
  min_instances    = 1
  max_instances    = 2
  db_storage_gb    = 20

  tags = {
    Environment = "staging"
    ManagedBy   = "terraform"
    CostCenter  = "engineering-qa"
  }
}
```

### Pulumi (Infrastructure in Code)

```typescript
// infra/test-environment.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

export function createTestEnvironment(name: string) {
  const db = new aws.rds.Instance(`${name}-db`, {
    engine: "postgres",
    engineVersion: "16",
    instanceClass: "db.t3.micro",
    allocatedStorage: 10,
    dbName: "testdb",
    username: "test",
    password: pulumi.secret("test-password"),
    skipFinalSnapshot: true,
    tags: { Environment: name },
  });

  const app = new aws.ecs.Service(`${name}-app`, {
    desiredCount: 1,
    taskDefinition: createTaskDef(name, db.endpoint),
  });

  return { dbEndpoint: db.endpoint, appUrl: app.id };
}
```

---

## Database Seeding and Fixtures

### Seed Script Pattern

```typescript
// scripts/seed-test-data.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function seed() {
  // Clean existing data (order matters for foreign keys)
  await prisma.orderItem.deleteMany();
  await prisma.order.deleteMany();
  await prisma.product.deleteMany();
  await prisma.user.deleteMany();

  // Seed users
  const admin = await prisma.user.create({
    data: {
      email: 'admin@test.example.com',
      name: 'Test Admin',
      role: 'ADMIN',
      password: '$2b$10$hashedpassword', // pre-hashed
    },
  });

  const user = await prisma.user.create({
    data: {
      email: 'user@test.example.com',
      name: 'Test User',
      role: 'USER',
      password: '$2b$10$hashedpassword',
    },
  });

  // Seed products
  const products = await Promise.all(
    Array.from({ length: 10 }, (_, i) =>
      prisma.product.create({
        data: {
          name: `Test Product ${i + 1}`,
          price: (i + 1) * 9.99,
          stock: 100,
        },
      })
    )
  );

  console.log(`Seeded: ${2} users, ${products.length} products`);
}

seed()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

### Fixture Factory Pattern

```typescript
// test/factories/user.factory.ts
import { faker } from '@faker-js/faker';

export function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    role: 'USER',
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}

export function buildUsers(count: number, overrides: Partial<User> = {}): User[] {
  return Array.from({ length: count }, () => buildUser(overrides));
}

// Usage in tests
const adminUser = buildUser({ role: 'ADMIN' });
const regularUsers = buildUsers(5);
```

### Database Snapshot Pattern

```bash
# Create a snapshot of seeded database
pg_dump -U test -d testdb -F c -f test-snapshot.dump

# Restore before each test suite (fast reset)
pg_restore -U test -d testdb --clean --no-owner test-snapshot.dump
```

---

## Service Virtualization

### WireMock (HTTP API Mocking)

```json
// wiremock/mappings/payment-gateway.json
{
  "request": {
    "method": "POST",
    "urlPattern": "/api/v1/charges",
    "headers": {
      "Authorization": { "matches": "Bearer .*" }
    }
  },
  "response": {
    "status": 200,
    "headers": { "Content-Type": "application/json" },
    "jsonBody": {
      "id": "ch_test_123",
      "status": "succeeded",
      "amount": "{{jsonPath request.body '$.amount'}}",
      "currency": "usd"
    },
    "transformers": ["response-template"]
  }
}
```

```yaml
# docker-compose.test.yml - add WireMock
services:
  wiremock:
    image: wiremock/wiremock:3.3.1
    ports:
      - "8080:8080"
    volumes:
      - ./wiremock:/home/wiremock
    command: --verbose --global-response-templating
```

### MockServer

```typescript
// test/mocks/setup-mockserver.ts
import { MockServerClient } from 'mockserver-client';

const mockServer = new MockServerClient('localhost', 1080);

export async function setupExternalMocks() {
  // Mock email service
  await mockServer.mockSimpleResponse(
    '/api/send-email',
    { success: true, messageId: 'mock-123' },
    200
  );

  // Mock geolocation API
  await mockServer.mockAnyResponse({
    httpRequest: { path: '/api/geoip/.*', method: 'GET' },
    httpResponse: {
      statusCode: 200,
      body: JSON.stringify({ country: 'US', region: 'CA', city: 'San Francisco' }),
    },
  });
}
```

### When to Virtualize

| External Service | Virtualize? | Rationale |
|-----------------|-------------|-----------|
| Payment gateway (Stripe, etc.) | Yes, always | Cost, rate limits, side effects |
| Email service (SendGrid, etc.) | Yes, always | Side effects (spam), delivery delays |
| SMS provider | Yes, always | Cost, side effects |
| Auth provider (Auth0, etc.) | Usually | Rate limits; test mode may suffice |
| Analytics (Segment, etc.) | Yes | Irrelevant to test, slows execution |
| Database | No | Use real instance (Docker) |
| Message queue | Sometimes | Use real for integration, mock for unit |

---

## Environment Isolation Strategies

### Namespace Isolation (Kubernetes)

```yaml
# Per-PR namespace
apiVersion: v1
kind: Namespace
metadata:
  name: pr-${PR_NUMBER}
  labels:
    environment: preview
    pr: "${PR_NUMBER}"
    auto-cleanup: "true"
---
# NetworkPolicy: isolate from other namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: isolate-namespace
  namespace: pr-${PR_NUMBER}
spec:
  podSelector: {}
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: pr-${PR_NUMBER}
```

### Database Isolation

```text
Strategy 1: Separate databases per environment
  + Full isolation, no cross-contamination
  - Higher resource cost

Strategy 2: Schema-per-tenant
  + Lower resource cost, faster provisioning
  - Shared database risks

Strategy 3: Row-level isolation (tenant_id column)
  + Cheapest, simplest
  - Data leaks possible if filter missed

Recommendation: Separate databases for staging/pre-prod;
  schema-per-tenant for ephemeral PR environments.
```

---

## Shared vs Dedicated Environments

| Dimension | Shared | Dedicated |
|-----------|--------|-----------|
| **Cost** | Low (1 env, many teams) | High (1 env per team/feature) |
| **Isolation** | Low (data conflicts possible) | High (full independence) |
| **Stability** | Lower (broken by other teams) | Higher (self-controlled) |
| **Maintenance** | Lower (one set of infra) | Higher (many environments) |
| **Best for** | Manual QA, demo | Automated testing, CI |

### Hybrid Approach

```text
Shared environments:
  - staging: manual QA, demos, exploratory testing
  - pre-prod: release validation, performance testing

Dedicated environments:
  - CI: ephemeral per pipeline, torn down after
  - PR preview: ephemeral per pull request
  - Feature: on-demand for large features (request-based)
```

---

## Environment Drift Detection

### Configuration Comparison Script

```python
#!/usr/bin/env python3
"""Detect configuration drift between environments."""
import json
import subprocess
import sys

def get_env_config(env_name: str) -> dict:
    """Fetch running config from environment."""
    result = subprocess.run(
        ["kubectl", "get", "configmap", "app-config",
         "-n", env_name, "-o", "json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)["data"]

def compare_configs(source: str, target: str) -> list[dict]:
    """Compare two environment configurations."""
    source_config = get_env_config(source)
    target_config = get_env_config(target)

    diffs = []
    all_keys = set(source_config) | set(target_config)

    for key in sorted(all_keys):
        src_val = source_config.get(key, "<MISSING>")
        tgt_val = target_config.get(key, "<MISSING>")
        if src_val != tgt_val:
            diffs.append({
                "key": key,
                source: src_val,
                target: tgt_val,
            })
    return diffs

if __name__ == "__main__":
    drifts = compare_configs("staging", "production")
    if drifts:
        print(f"Found {len(drifts)} config differences:")
        for d in drifts:
            print(f"  {d['key']}: staging={d['staging']} prod={d['production']}")
        sys.exit(1)
    print("No drift detected.")
```

### Infrastructure Drift Check

```bash
# Terraform drift detection
terraform plan -detailed-exitcode -var-file=staging.tfvars
# Exit code 0 = no changes, 1 = error, 2 = changes detected (drift)

# Schedule weekly drift check in CI
# .github/workflows/drift-check.yml
name: Environment Drift Check
on:
  schedule:
    - cron: '0 8 * * 1'  # Monday 8am
jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - run: terraform plan -detailed-exitcode
```

---

## Secrets Management

### Environment Variable Patterns

```bash
# .env.test (checked into git - non-sensitive only)
NODE_ENV=test
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=testdb
LOG_LEVEL=warn

# .env.test.local (git-ignored - sensitive values)
DATABASE_PASSWORD=local-test-password
API_KEY=test-api-key-12345
STRIPE_SECRET_KEY=sk_test_xxxxx
```

### CI Secrets

```yaml
# GitHub Actions: secrets from repository settings
- name: Run tests
  env:
    DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
    API_KEY: ${{ secrets.TEST_API_KEY }}
  run: npm run test:e2e
```

### Vault Integration

```bash
# HashiCorp Vault: dynamic database credentials
vault read database/creds/test-role
# Returns: username=v-test-xxxx, password=yyyy, ttl=1h

# In CI pipeline
export DATABASE_URL=$(vault read -field=connection_url database/creds/test-role)
npm run test:e2e
```

### Secrets Checklist

- [ ] No secrets in source control (git-ignored `.env.local` files)
- [ ] CI secrets stored in platform secrets manager (GitHub/GitLab)
- [ ] Test API keys scoped to test environment only
- [ ] Database passwords rotated regularly
- [ ] Secrets audit log enabled
- [ ] Production secrets never used in test environments

---

## Provisioning Automation

### Makefile Commands

```makefile
# Makefile
.PHONY: env-up env-down env-reset env-seed env-health

env-up:
	docker compose -f docker-compose.test.yml up -d
	@echo "Waiting for services..."
	@sleep 5
	$(MAKE) env-health

env-down:
	docker compose -f docker-compose.test.yml down -v

env-reset: env-down env-up env-seed

env-seed:
	docker compose exec app npx prisma db seed

env-health:
	@curl -sf http://localhost:3000/health > /dev/null && echo "App: OK" || echo "App: DOWN"
	@docker compose exec db pg_isready -U test > /dev/null && echo "DB: OK" || echo "DB: DOWN"
	@docker compose exec cache redis-cli ping > /dev/null && echo "Cache: OK" || echo "Cache: DOWN"
```

### GitHub Actions: Reusable Workflow

```yaml
# .github/workflows/test-env.yml
name: Test with Environment
on:
  workflow_call:
    inputs:
      test-command:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: testdb }
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports: ["5432:5432"]
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx prisma db push && npx prisma db seed
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/testdb
      - run: ${{ inputs.test-command }}
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
```

---

## Teardown and Cleanup

### Automatic Cleanup for Ephemeral Environments

```yaml
# Kubernetes CronJob: clean up old PR environments
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-preview-envs
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: bitnami/kubectl
            command:
            - /bin/sh
            - -c
            - |
              # Delete namespaces older than 48 hours with auto-cleanup label
              kubectl get namespaces -l auto-cleanup=true -o json | \
                jq -r '.items[] | select(
                  (.metadata.creationTimestamp | fromdateiso8601) < (now - 172800)
                ) | .metadata.name' | \
                xargs -r kubectl delete namespace
```

### GitHub Actions: Cleanup on PR Close

```yaml
name: Cleanup Preview Environment
on:
  pull_request:
    types: [closed]

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Delete preview environment
        run: |
          kubectl delete namespace pr-${{ github.event.number }} --ignore-not-found
          echo "Cleaned up preview environment for PR #${{ github.event.number }}"
```

---

## Health Monitoring

### Health Check Endpoint

```typescript
// health.ts - comprehensive health check
app.get('/health', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
    externalApi: await checkExternalApi(),
  };

  const healthy = Object.values(checks).every(c => c.status === 'ok');

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    checks,
  });
});
```

### Environment Health Dashboard

```text
Environment Health - 2026-02-10 09:00 UTC
------------------------------------------
Local dev:     HEALTHY  (all services up)
CI runner 1:   HEALTHY  (pipeline running)
CI runner 2:   HEALTHY  (idle)
Staging:       DEGRADED (redis high memory - 89%)
Pre-prod:      HEALTHY  (all services up)

Alerts:
  - staging/redis: Memory usage 89% (threshold: 85%)
  - Action: Scale redis or flush test data
```

---

## Cost Optimization

| Strategy | Savings | Implementation Effort |
|----------|---------|----------------------|
| Auto-shutdown non-prod at night | 40-60% | Low (cron/lambda) |
| Right-size test instances | 20-40% | Medium (monitoring) |
| Spot/preemptible instances for CI | 60-80% | Medium (retry logic) |
| Share staging across teams | 30-50% | Low (scheduling) |
| Ephemeral PR environments | Variable | High (automation) |
| RAM disk for test databases | Speed, not $ | Low (tmpfs config) |

```bash
# Auto-shutdown staging at 8pm, start at 7am (weekdays)
# AWS Lambda + CloudWatch Events
aws events put-rule --name stop-staging --schedule-expression "cron(0 20 ? * MON-FRI *)"
aws events put-rule --name start-staging --schedule-expression "cron(0 7 ? * MON-FRI *)"
```

---

## Environment Management Checklist

### New Environment Setup

- [ ] Infrastructure defined as code (Docker Compose / Terraform / Pulumi)
- [ ] Database seeding automated
- [ ] Service mocks configured for external dependencies
- [ ] Health check endpoint available
- [ ] Secrets injected from secure source (not hardcoded)
- [ ] Cleanup / teardown automated
- [ ] Cost tracking labels applied
- [ ] Access control configured (who can access what)

### Ongoing Maintenance

- [ ] Weekly drift detection between staging and production
- [ ] Monthly cost review of test environments
- [ ] Quarterly cleanup of orphaned resources
- [ ] Seed data refreshed when schema changes
- [ ] Health monitoring alerts configured

---

## Related Resources

- [synthetic-test-data.md](./synthetic-test-data.md) -- generating test data for seeding
- [operational-playbook.md](./operational-playbook.md) -- CI/CD pipeline patterns using test environments
- [shift-left-testing.md](./shift-left-testing.md) -- preview environments for PR testing
- [SKILL.md](../SKILL.md) -- parent testing strategy skill
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Terraform Testing](https://developer.hashicorp.com/terraform/tutorials/configuration-language/test)
- [WireMock](https://wiremock.org/docs/)
- [MockServer](https://www.mock-server.com/)
