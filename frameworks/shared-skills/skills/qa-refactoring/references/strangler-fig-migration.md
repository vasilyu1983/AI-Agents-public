# Strangler Fig Migration

Incremental migration patterns for replacing legacy systems without big-bang rewrites. Based on Martin Fowler's Strangler Fig Application pattern.

## Contents

- [Strangler Fig Theory](#strangler-fig-theory)
- [Implementation Strategies](#implementation-strategies)
- [Proxy Layer Patterns](#proxy-layer-patterns)
- [Dual-Write Strategies](#dual-write-strategies)
- [Data Migration Approaches](#data-migration-approaches)
- [Feature Toggle Integration](#feature-toggle-integration)
- [Rollback Strategies](#rollback-strategies)
- [Progress Tracking](#progress-tracking)
- [Risk Assessment per Phase](#risk-assessment-per-phase)
- [Timeline Expectations](#timeline-expectations)
- [Common Pitfalls](#common-pitfalls)
- [Related Resources](#related-resources)

---

## Strangler Fig Theory

The strangler fig is a tropical plant that grows around a host tree, eventually replacing it entirely. The metaphor applies directly to software migration: build the new system around the old one, gradually routing traffic to the new system, until the old system can be decommissioned.

### Why Strangler Fig Over Big-Bang Rewrite

| Approach | Risk | Delivery | Rollback | Team Impact |
|----------|------|----------|----------|-------------|
| **Big-bang rewrite** | Very high | Nothing until done | All or nothing | Full team blocked |
| **Strangler fig** | Low per step | Incremental value | Per-feature rollback | Parallel work possible |

### Core Principles

1. **Never stop delivering value** -- the old system stays live while the new one grows
2. **Route, don't rewrite everything** -- migrate one feature or route at a time
3. **Prove equivalence** -- characterization tests ensure the new system matches the old
4. **Rollback at any point** -- each step is independently reversible
5. **Measure progress** -- track what percentage of traffic hits old vs new

### The Three Phases

```
Phase 1: WRAP
  Build a proxy layer in front of the legacy system.
  All traffic still goes to legacy, but through your proxy.

Phase 2: STRANGLE
  One by one, implement features in the new system.
  Route traffic to new system feature by feature.
  Old and new run in parallel.

Phase 3: DECOMMISSION
  When all traffic routes to the new system,
  remove the proxy, shut down the legacy system.
```

---

## Implementation Strategies

### Route-Based Strangling

Migrate one API endpoint (or URL path) at a time.

```
Before:
  Client → Legacy System (all routes)

During:
  Client → Proxy → /api/users → New System
                  → /api/orders → Legacy System
                  → /api/payments → Legacy System

After:
  Client → New System (all routes)
```

**Best for:** REST APIs, microservice extraction, web application rewrites.

### Feature-Based Strangling

Migrate one business feature at a time, regardless of how many endpoints it touches.

```
Feature: "Order Management"
  Endpoints: POST /orders, GET /orders/:id, PUT /orders/:id/status
  Database tables: orders, order_items, order_events
  Background jobs: order_confirmation_email, inventory_update

All migrated together as a single unit.
```

**Best for:** Complex features that span multiple endpoints and data stores.

### Data-Based Strangling

Migrate based on data segments (by customer, region, or cohort).

```
Phase 1: New customers → New System, Existing → Legacy
Phase 2: Small accounts → New System, Enterprise → Legacy
Phase 3: All customers → New System
```

**Best for:** Multi-tenant systems, when data isolation is feasible.

### Strategy Selection Guide

| Factor | Route-Based | Feature-Based | Data-Based |
|--------|:-----------:|:-------------:|:----------:|
| API-heavy system | Best | Good | Possible |
| Tightly coupled features | Poor | Best | Possible |
| Multi-tenant SaaS | Possible | Possible | Best |
| Independent endpoints | Best | Good | Possible |
| Shared database | Possible | Possible | Best |
| Speed of migration | Fastest per step | Medium | Slowest to start |

---

## Proxy Layer Patterns

The proxy layer is the critical infrastructure that enables gradual migration.

### NGINX Routing Proxy

```nginx
# nginx.conf: Route-based strangler proxy

upstream legacy {
    server legacy-app:8080;
}

upstream new_system {
    server new-app:8080;
}

server {
    listen 80;

    # Migrated routes → new system
    location /api/v2/users {
        proxy_pass http://new_system;
        proxy_set_header X-Migrated "true";
        proxy_set_header X-Original-Host $host;
    }

    location /api/v2/products {
        proxy_pass http://new_system;
        proxy_set_header X-Migrated "true";
    }

    # Everything else → legacy
    location / {
        proxy_pass http://legacy;
        proxy_set_header X-Migrated "false";
    }
}
```

### Application-Level Proxy (Node.js)

```javascript
const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const LaunchDarkly = require("launchdarkly-node-server-sdk");

const app = express();
const ldClient = LaunchDarkly.init(process.env.LD_SDK_KEY);

// Feature flag-driven routing
app.use("/api/orders", async (req, res, next) => {
  const user = { key: req.headers["x-user-id"] || "anonymous" };
  const useNewSystem = await ldClient.variation("orders-new-system", user, false);

  if (useNewSystem) {
    // Route to new system
    return createProxyMiddleware({
      target: "http://new-order-service:8080",
      changeOrigin: true,
      on: {
        proxyReq: (proxyReq) => {
          proxyReq.setHeader("X-Routed-By", "strangler-proxy");
        },
      },
    })(req, res, next);
  }

  // Route to legacy
  return createProxyMiddleware({
    target: "http://legacy-monolith:8080",
    changeOrigin: true,
  })(req, res, next);
});

app.listen(3000);
```

### Proxy Monitoring

```python
"""
Track routing decisions for migration progress monitoring.
Emit metrics for every request showing old vs new routing.
"""
from prometheus_client import Counter

route_counter = Counter(
    "strangler_proxy_requests_total",
    "Requests routed by the strangler proxy",
    ["path", "target", "result"]
)

# In proxy middleware:
def track_routing(path: str, target: str, status_code: int):
    result = "success" if status_code < 500 else "error"
    route_counter.labels(
        path=parameterize_path(path),
        target=target,  # "legacy" or "new"
        result=result
    ).inc()
```

---

## Dual-Write Strategies

During migration, both systems may need to stay in sync. Dual-write patterns handle this.

### Dual-Write Approaches

| Approach | How It Works | Consistency | Complexity |
|----------|-------------|-------------|------------|
| **Synchronous dual-write** | Write to both in same transaction | Strong | High (distributed TX) |
| **Async replication** | Write to primary, replicate to secondary | Eventual | Medium |
| **Change Data Capture (CDC)** | Stream DB changes to secondary | Eventual | Medium |
| **Event sourcing** | Publish events, both systems consume | Eventual | Low |

### CDC with Debezium

```yaml
# docker-compose.yml (Debezium CDC setup)
services:
  debezium:
    image: debezium/connect:2.5
    environment:
      BOOTSTRAP_SERVERS: kafka:9092
      GROUP_ID: strangler-cdc
      CONFIG_STORAGE_TOPIC: debezium-configs
      OFFSET_STORAGE_TOPIC: debezium-offsets

# Register CDC connector
# POST http://debezium:8083/connectors
{
  "name": "legacy-db-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "legacy-db",
    "database.port": "5432",
    "database.user": "cdc_user",
    "database.password": "${CDC_PASSWORD}",
    "database.dbname": "legacy",
    "table.include.list": "public.orders,public.order_items",
    "topic.prefix": "legacy",
    "slot.name": "strangler_cdc"
  }
}
```

### Verification: Comparing Dual-Write Outputs

```python
"""
Compare outputs from legacy and new system to verify equivalence.
Run as a background job during the dual-write phase.
"""
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("dual-write-verifier")

def verify_dual_write_consistency(
    legacy_db,
    new_db,
    table: str,
    time_window_minutes: int = 5,
    sample_size: int = 100,
):
    """Compare records between legacy and new databases."""
    cutoff = datetime.utcnow() - timedelta(minutes=time_window_minutes)

    # Sample recent records from both systems
    legacy_records = legacy_db.query(
        f"SELECT * FROM {table} WHERE updated_at > %s ORDER BY RANDOM() LIMIT %s",
        (cutoff, sample_size)
    )

    mismatches = []
    missing_in_new = []

    for legacy_record in legacy_records:
        new_record = new_db.query(
            f"SELECT * FROM {table} WHERE id = %s",
            (legacy_record["id"],)
        )

        if not new_record:
            missing_in_new.append(legacy_record["id"])
            continue

        # Compare field by field
        for field in legacy_record:
            if field in ("updated_at", "created_at"):
                continue  # Timestamps may differ slightly
            if legacy_record[field] != new_record[0].get(field):
                mismatches.append({
                    "id": legacy_record["id"],
                    "field": field,
                    "legacy": legacy_record[field],
                    "new": new_record[0].get(field),
                })

    # Report results
    total = len(legacy_records)
    match_rate = (total - len(mismatches) - len(missing_in_new)) / max(total, 1) * 100

    logger.info(
        "dual_write_verification",
        table=table,
        total_checked=total,
        mismatches=len(mismatches),
        missing_in_new=len(missing_in_new),
        match_rate=f"{match_rate:.1f}%",
    )

    return {
        "match_rate": match_rate,
        "mismatches": mismatches,
        "missing": missing_in_new,
    }
```

---

## Data Migration Approaches

### Online Migration (Zero Downtime)

```
Step 1: Dual-write new records to both old and new DB
Step 2: Backfill historical data from old DB to new DB
Step 3: Verify consistency (comparison job)
Step 4: Switch reads to new DB
Step 5: Stop writes to old DB
Step 6: Decommission old DB after verification period
```

### Backfill Script

```python
"""
Backfill historical data from legacy to new database.
Designed for zero-downtime migration with idempotent operations.
"""
import time
import logging

logger = logging.getLogger("backfill")

def backfill_table(
    legacy_db,
    new_db,
    table: str,
    batch_size: int = 1000,
    sleep_between_batches: float = 0.5,
):
    """Backfill data in batches with progress tracking."""
    total = legacy_db.query(f"SELECT COUNT(*) FROM {table}")[0][0]
    migrated = 0
    last_id = 0

    logger.info(f"Starting backfill of {table}: {total} records")

    while True:
        batch = legacy_db.query(
            f"SELECT * FROM {table} WHERE id > %s ORDER BY id LIMIT %s",
            (last_id, batch_size)
        )

        if not batch:
            break

        # Upsert to handle re-runs (idempotent)
        for record in batch:
            new_db.upsert(table, record)

        last_id = batch[-1]["id"]
        migrated += len(batch)

        logger.info(
            "backfill_progress",
            table=table,
            migrated=migrated,
            total=total,
            pct=f"{migrated / total * 100:.1f}%",
            last_id=last_id,
        )

        # Throttle to avoid overwhelming the databases
        time.sleep(sleep_between_batches)

    logger.info(f"Backfill complete: {table} ({migrated} records)")
    return migrated
```

---

## Feature Toggle Integration

Feature toggles are the control mechanism for strangler fig migrations.

### Toggle Configuration

```python
"""
Feature toggle-driven routing for strangler fig migration.
"""
import launchdarkly_server_sdk as ld

MIGRATION_FLAGS = {
    "orders-new-system": {
        "description": "Route order endpoints to new system",
        "phase": "canary",
        "rollout_pct": 10,
        "fallback": False,
    },
    "users-new-system": {
        "description": "Route user endpoints to new system",
        "phase": "complete",
        "rollout_pct": 100,
        "fallback": False,
    },
    "payments-new-system": {
        "description": "Route payment endpoints to new system",
        "phase": "not_started",
        "rollout_pct": 0,
        "fallback": False,
    },
}

class MigrationRouter:
    def __init__(self, ld_client):
        self.client = ld_client

    def should_use_new_system(self, feature: str, user_context: dict) -> bool:
        """Check if request should route to new system."""
        flag_key = f"{feature}-new-system"
        user = ld.Context.builder(user_context.get("user_id", "anonymous")).build()
        return self.client.variation(flag_key, user, False)

    def get_migration_status(self) -> dict:
        """Get current migration status for all features."""
        return {
            flag: {
                "phase": config["phase"],
                "rollout_pct": config["rollout_pct"],
            }
            for flag, config in MIGRATION_FLAGS.items()
        }
```

### Rollout Stages

| Stage | Rollout % | Duration | Validation |
|-------|-----------|----------|------------|
| **Off** | 0% | -- | Development and testing |
| **Shadow** | 0% (dual-run) | 1-2 weeks | Run both, compare outputs, route to legacy |
| **Canary** | 1-5% | 1 week | Monitor errors, latency, correctness |
| **Partial** | 10-50% | 1-2 weeks | Expand if metrics are green |
| **Majority** | 50-95% | 1 week | Final validation |
| **Complete** | 100% | 2 weeks | Monitoring period before decommission |
| **Decommission** | 100% + remove flag | -- | Remove legacy code and toggle |

---

## Rollback Strategies

Every migration step must be reversible.

### Rollback by Phase

| Phase | Rollback Action | Recovery Time | Data Impact |
|-------|----------------|---------------|-------------|
| **Proxy setup** | Remove proxy, point DNS to legacy | Minutes | None |
| **Canary routing** | Set feature flag to 0% | Seconds | None (stateless) |
| **Dual-write** | Stop writes to new DB, keep legacy as source of truth | Minutes | Discard new DB data |
| **Read migration** | Switch reads back to legacy DB | Seconds (flag) | None |
| **Write migration** | Switch writes back to legacy DB | Minutes | Reconcile any new-DB-only writes |
| **Decommission** | Restore legacy from backup (last resort) | Hours | Potential data loss |

### Rollback Automation

```bash
#!/bin/bash
# rollback-migration.sh: Emergency rollback for strangler fig migration

FEATURE="$1"
PHASE="$2"

if [ -z "$FEATURE" ]; then
    echo "Usage: rollback-migration.sh <feature> [phase]"
    echo "Features: orders, users, payments"
    exit 1
fi

echo "=== Rolling back migration for: $FEATURE ==="

# Step 1: Disable feature flag (route all traffic to legacy)
echo "Setting feature flag to 0%..."
curl -X PATCH "https://app.launchdarkly.com/api/v2/flags/default/${FEATURE}-new-system" \
  -H "Authorization: $LD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"op": "replace", "path": "/environments/production/on", "value": false}]'

# Step 2: Verify legacy is serving traffic
echo "Waiting 30 seconds for traffic to drain..."
sleep 30

echo "Checking legacy health..."
HEALTH=$(curl -sf "http://legacy-app:8080/health" | jq -r '.status')
if [ "$HEALTH" != "ok" ]; then
    echo "WARNING: Legacy health check failed!"
    exit 1
fi

# Step 3: Notify team
echo "Sending rollback notification..."
curl -X POST "$SLACK_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Migration rollback: ${FEATURE} routed back to legacy. Investigating.\"}"

echo "Rollback complete. All traffic for $FEATURE now routes to legacy."
```

---

## Progress Tracking

### Migration Dashboard

```
+-----------------------------------------------------------+
| Strangler Fig Migration Progress                           |
+-----------------------------------------------------------+
| Feature      | Phase     | New % | Legacy % | Errors     |
|-------------|-----------|-------|----------|------------|
| Users        | Complete  | 100%  | 0%       | 0.01%      |
| Products     | Majority  | 80%   | 20%      | 0.02%      |
| Orders       | Canary    | 5%    | 95%      | 0.05%      |
| Payments     | Shadow    | 0%*   | 100%     | N/A        |
| Reports      | Not started| 0%   | 100%     | N/A        |
+-----------------------------------------------------------+
| Overall: 37% migrated | Estimated completion: Q3 2026     |
+-----------------------------------------------------------+
```

### Prometheus Metrics

```promql
# Migration progress: percentage of traffic to new system
sum(rate(strangler_proxy_requests_total{target="new"}[5m]))
/
sum(rate(strangler_proxy_requests_total[5m]))

# Error rate comparison: new vs legacy
sum(rate(strangler_proxy_requests_total{target="new", result="error"}[5m]))
/
sum(rate(strangler_proxy_requests_total{target="new"}[5m]))

# Latency comparison
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{system="new"}[5m])) by (le)
)
```

---

## Risk Assessment per Phase

| Phase | Risk Level | Key Risks | Mitigations |
|-------|-----------|-----------|-------------|
| **Proxy setup** | Low | Latency overhead, proxy becomes SPOF | Load test proxy, deploy HA |
| **Shadow mode** | Low | Resource cost of dual-running | Monitor resource usage |
| **Canary** | Medium | New system bugs affect real users | Small %, immediate rollback |
| **Partial rollout** | Medium | Data consistency between systems | Dual-write verification |
| **Majority** | Medium-High | Edge cases at scale | Comprehensive monitoring |
| **Complete** | Low | Legacy decommission leaves orphans | Audit dependencies first |
| **Decommission** | Medium | Hidden dependencies on legacy | Keep legacy available for 30 days |

---

## Timeline Expectations

### Realistic Timelines

| System Complexity | Feature Count | Expected Duration | Team Size |
|-------------------|---------------|-------------------|-----------|
| Small monolith | 5-10 features | 3-6 months | 2-3 engineers |
| Medium monolith | 10-30 features | 6-12 months | 3-5 engineers |
| Large monolith | 30-100 features | 12-24 months | 5-10 engineers |
| Enterprise legacy | 100+ features | 2-5 years | Dedicated team |

### Phase Duration Guidelines

```
Proxy Setup:          1-2 weeks
Per Feature Migration:
  Shadow mode:        1-2 weeks
  Canary (1-5%):      1 week
  Partial (10-50%):   1-2 weeks
  Majority (50-95%):  1 week
  Complete (100%):    1 week
  Monitoring period:  2 weeks
  Decommission:       1 week
  ---
  Total per feature:  6-10 weeks

With 10 features in parallel (2-3 at a time): ~6-9 months
```

---

## Common Pitfalls

### Pitfall 1: Big Bang Temptation

**Problem:** Team decides "we've migrated 80%, let's just do the rest at once."

**Why it fails:** The remaining 20% is usually the hardest (legacy edge cases, complex integrations, undocumented behavior).

**Prevention:** Maintain the same per-feature cadence for every feature. No shortcuts.

### Pitfall 2: Incomplete State Migration

**Problem:** New system handles requests but doesn't have all the historical state. Users see missing data.

**Prevention:**
- Backfill all historical data before routing reads
- Verify data completeness with automated comparison jobs
- Test with real user accounts in staging

### Pitfall 3: Proxy Becoming a Monolith

**Problem:** Business logic creeps into the proxy layer (data transformation, validation, authorization).

**Prevention:**
- Proxy should ONLY route. No business logic.
- Code review proxy changes strictly
- If you need transformation, do it in the destination service

### Pitfall 4: Neglecting Legacy Maintenance

**Problem:** Team focuses only on new system. Legacy gets zero maintenance and starts breaking.

**Prevention:**
- Legacy still serves production traffic. Keep it stable.
- Budget 20% of time for legacy bug fixes during migration
- Monitor legacy as carefully as the new system

### Pitfall 5: No Equivalence Testing

**Problem:** New system subtly differs from legacy (rounding, encoding, null handling). Users notice.

**Prevention:**
- Shadow mode with output comparison
- Characterization tests from legacy behavior
- Diff every response field during canary

### Summary Checklist

- [ ] Proxy layer is routing-only (no business logic)
- [ ] Feature flags control routing (not code deploys)
- [ ] Dual-write verification running
- [ ] Characterization tests prove equivalence
- [ ] Rollback tested for each phase
- [ ] Progress dashboard visible to stakeholders
- [ ] Legacy system still maintained and monitored
- [ ] Data backfill verified for completeness
- [ ] Decommission plan documented per feature

---

## Related Resources

- [Characterization Testing](./characterization-testing.md) - Proving behavioral equivalence
- [Legacy Code Strategies](./legacy-code-strategies.md) - Working with legacy systems
- [Operational Patterns](./operational-patterns.md) - CI/CD patterns for safe refactoring
- [Tech Debt Management](./tech-debt-management.md) - Prioritizing migration work
- [Automated Refactoring Tools](./automated-refactoring-tools.md) - Tool-assisted code migration
- [SKILL.md](../SKILL.md) - Parent skill overview
