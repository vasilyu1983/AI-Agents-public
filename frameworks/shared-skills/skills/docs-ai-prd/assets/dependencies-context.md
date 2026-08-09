# Dependencies Context Template

Template for documenting external services and integrations in CLAUDE.md.

---

```markdown
## External Dependencies

### Databases

| Service | Purpose | Connection | Notes |
|---------|---------|------------|-------|
| PostgreSQL | Primary data store | `DATABASE_URL` | Managed via Prisma ORM |
| Redis | Cache, sessions | `REDIS_URL` | Used for rate limiting |
| MongoDB | Document storage | `MONGO_URL` | Legacy data |

### Message Queues

| Service | Purpose | Connection | Notes |
|---------|---------|------------|-------|
| RabbitMQ | Async messaging | `RABBITMQ_URL` | Email, notifications |
| SQS | Event processing | AWS credentials | Order processing |
| Kafka | Event streaming | `KAFKA_BROKERS` | Analytics events |

### Third-Party APIs

| Service | Purpose | Auth | Rate Limits | Notes |
|---------|---------|------|-------------|-------|
| Stripe | Payments | `STRIPE_SECRET_KEY` | 100/sec | Webhooks at `/webhooks/stripe` |
| SendGrid | Email | `SENDGRID_API_KEY` | 100/sec | Transactional only |
| Auth0 | Authentication | `AUTH0_*` | 1000/min | SSO enabled |
| S3 | File storage | AWS IAM | N/A | Presigned URLs |
| Twilio | SMS | `TWILIO_*` | 100/sec | 2FA only |

### Internal Services

| Service | Purpose | URL | Auth | Notes |
|---------|---------|-----|------|-------|
| User Service | User management | `USER_SERVICE_URL` | JWT | gRPC |
| Notification Service | Alerts | `NOTIF_SERVICE_URL` | API Key | REST |
| Analytics | Metrics | `ANALYTICS_URL` | None (internal) | Fire-and-forget |

### CI/CD & Infrastructure

| Service | Purpose | Notes |
|---------|---------|-------|
| GitHub Actions | CI/CD | Main branch auto-deploy |
| AWS ECS | Hosting | Production environment |
| Datadog | Monitoring | APM + logs |
| Sentry | Error tracking | All environments |

## Integration Patterns

### API Client Pattern

```typescript
// src/clients/stripe.ts
export const stripeClient = new Stripe(config.stripe.secretKey, {
  apiVersion: '2024-01-01',
  timeout: 10000,
  maxRetries: 3,
});
```

### Retry Configuration

| Service | Retries | Backoff | Timeout |
|---------|---------|---------|---------|
| Stripe | 3 | Exponential | 10s |
| SendGrid | 2 | Linear | 5s |
| Internal APIs | 3 | Exponential | 30s |

### Circuit Breaker Settings

| Service | Failure Threshold | Reset Timeout |
|---------|-------------------|---------------|
| Payment APIs | 5 failures | 30 seconds |
| Email APIs | 10 failures | 60 seconds |
| Non-critical | 20 failures | 120 seconds |

## Environment Variables

```bash
# Databases
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379

# Third-party APIs
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
SENDGRID_API_KEY=SG....
AUTH0_DOMAIN=tenant.auth0.com
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=my-bucket

# Internal services
USER_SERVICE_URL=http://user-service:3001
NOTIFICATION_SERVICE_URL=http://notif-service:3002
```

## Fallback Behavior

| Service | Fallback | Notes |
|---------|----------|-------|
| Redis cache | Skip cache, hit DB | Graceful degradation |
| Email service | Queue for retry | Async, non-blocking |
| Payment service | Fail request | Critical path |
| Analytics | Drop event | Non-critical |
```

---

## Discovery Commands

```bash
# Find external API calls
grep -r "fetch\|axios\|http\." --include="*.ts" | head -30

# Find environment variables
grep -r "process\.env\." --include="*.ts" | sort -u

# Find SDK/client instantiations
grep -r "new.*Client\|createClient\|initialize" --include="*.ts"

# Check package.json for SDK dependencies
cat package.json | jq '.dependencies' | grep -i "aws\|stripe\|sendgrid\|twilio"
```

## Usage

1. Inventory all external services
2. Document connection details (without secrets)
3. Note rate limits and quirks
4. Define fallback behaviors
