# Example Plan-Contract: Add Per-User Rate Limiting to a Node.js API

> **Purpose**: Teaching artifact. Copy-paste this as a starting point for a real medium-complexity task.
> Complexity: Medium (2–3 engineer-days). Fictional service: `api-gateway` (Express + Redis).

---

## 1. Task Statement

**As a** platform engineer,
**I want** per-user rate limiting on all authenticated API endpoints,
**So that** a single abusive or buggy client cannot degrade service for others.

---

## 2. Definition of Ready (DoR)

All boxes must be checked before work begins.

- [x] Acceptance criteria written and agreed (see §4)
- [x] Redis instance available in staging and production (confirmed with infra team [YYYY-MM-DD])
- [x] Token/user identity reliably present on `req.user.id` after auth middleware
- [x] Load-test harness exists (`k6` scripts in `tests/load/`)
- [x] On-call runbook location agreed: `docs/runbooks/rate-limiting.md`
- [x] Story sized at 5 points (1–2 engineer-days implementation + 0.5 day staging verification)
- [x] Reviewer identified: @backend-lead

---

## 3. Definition of Done (DoD)

Mark complete only when all are green.

**Code**
- [ ] `express-rate-limit` + `rate-limit-redis` installed and pinned in `package.json`
- [ ] Middleware applied globally after auth middleware, before route handlers
- [ ] Config (window, max, key prefix) externalised to environment variables with sane defaults
- [ ] No hardcoded limits in route files

**Tests**
- [ ] Unit tests: limit is enforced after N requests within window
- [ ] Unit tests: counter resets after window expires
- [ ] Unit tests: 429 response body matches error schema (RFC 7807)
- [ ] Integration test: different users get independent counters
- [ ] Existing test suite passes with no regressions (`npm test`)

**Observability**
- [ ] `Retry-After` header present on every 429
- [ ] Metric `rate_limit.rejected_total` emitted (label: `user_tier`)
- [ ] Alert rule added in `infra/alerts/api.yml` for rejection rate > 5% over 5 min

**Documentation**
- [ ] `docs/runbooks/rate-limiting.md` created (see §8)
- [ ] Environment variables documented in `README.md#Configuration`
- [ ] OpenAPI spec updated: 429 response added to all authenticated operations

**Deployment**
- [ ] Feature flag `RATE_LIMIT_ENABLED=true` controls middleware activation (default: false in staging, true in production after sign-off)
- [ ] Deployed to staging; load test run and passed (see §6)
- [ ] Product owner accepted in staging demo

---

## 4. Acceptance Criteria

### AC-1: Limit is enforced
```
Given an authenticated user has sent 100 requests within a 60-second window
When they send request #101
Then the API returns HTTP 429
And the body is {"status":429,"title":"Too Many Requests","detail":"Rate limit exceeded. Retry after N seconds."}
And the Retry-After header is set to the remaining window in seconds
```

### AC-2: Counters are per-user, not per-IP
```
Given User A has exhausted their quota
When User B (different user ID) sends a request
Then User B receives HTTP 200
```

### AC-3: Counter resets after window
```
Given User A has exhausted their 60-second quota
When 61 seconds pass
Then User A can send requests again without a 429
```

### AC-4: Unauthenticated requests use IP-based fallback
```
Given a request arrives without a valid auth token
When the rate-limit middleware processes it
Then the key used is the client IP address (not user ID)
```

### AC-5: Health and internal endpoints are exempt
```
Given a request to GET /health or GET /metrics
Then no rate-limit key is incremented and no 429 can be returned
```

---

## 5. Work-Item Breakdown

| # | Task | Owner | Estimate | Verify |
|---|------|-------|----------|--------|
| T1 | Install deps, wire middleware in `src/middleware/rateLimiter.ts` | @eng-1 | 2h | `npm install` green; middleware present in `app.ts` |
| T2 | Env-var config + defaults; exempt /health /metrics | @eng-1 | 1h | Config keys listed in README |
| T3 | Unit tests (counter, reset, 429 body, independent counters) | @eng-1 | 3h | `npm test` passes |
| T4 | Add `Retry-After` header; emit metric | @eng-1 | 1h | Header present in curl response |
| T5 | OpenAPI spec: add 429 to all authenticated operations | @eng-2 | 1h | Spectral lint passes |
| T6 | Alert rule + runbook | @eng-2 | 1h | Alert fires in Grafana staging |
| T7 | Staging deploy + load test | @eng-1 @eng-2 | 2h | Load test report passes §6 threshold |
| T8 | Production deploy + smoke test | @eng-1 | 1h | First 429 observed in prod logs within 10 min |

---

## 6. Milestone Checkpoints

### M1 — Implementation complete (end of Day 1)
- T1–T4 done
- `npm test` passing locally
- PR open, reviewer assigned

**Gate**: reviewer approves before M2 begins.

### M2 — Staging verified (end of Day 2)
- T5–T7 done
- Load test (`k6 run tests/load/rate-limit.js`) result:
  - p99 latency with limiter < baseline p99 + 10ms
  - 429 rate under normal load < 0.1%
  - Redis connection failure triggers fallback (memory store) without crash

**Gate**: product owner demo sign-off.

### M3 — Production deployed (Day 3 morning)
- T8 done
- Feature flag flipped to `true`
- Metric and alert verified live
- No P1 incidents within 2-hour watch window

---

## 7. Rollback Plan

| Trigger | Action | Owner | Time-to-rollback |
|---------|--------|-------|-----------------|
| Redis unavailable in production | Set `RATE_LIMIT_ENABLED=false` and redeploy (one env-var change, ~3 min) | on-call | < 5 min |
| 429 storm (rejection rate > 20% unexpectedly) | Same as above; raise limit temporarily via `RATE_LIMIT_MAX` env var | on-call | < 5 min |
| Memory leak from in-memory fallback store | Roll back to previous image tag via `kubectl rollout undo` | on-call | < 2 min |
| Critical bug in middleware | Revert PR merge; redeploy previous image | @backend-lead | < 15 min |

Rollback does not require a code change — the feature flag is sufficient for immediate recovery.

---

## 8. Eval / Verification Steps

### Unit (automated, pre-merge)
```bash
npm test -- --testPathPattern=rateLimiter
# Expected: all tests pass, coverage ≥ 90% for the new module
```

### Integration (automated, pre-merge)
```bash
npm run test:integration
# Expected: independent-counter test passes against a local Redis (docker-compose up -d redis)
```

### Load test (manual, M2 gate)
```bash
k6 run tests/load/rate-limit.js \
  --env TARGET_URL=https://staging.api.example.com \
  --env RATE_LIMIT_MAX=100
# Pass criteria:
#   http_req_failed rate < 1% (excluding intentional 429s)
#   http_req_duration p99 < 250ms
#   rate_limit_rejections (custom metric) > 0 (proves limiter fired)
```

### Smoke test (manual, M3 gate)
```bash
# Send 101 requests as the same user; confirm 429 on #101.
for i in $(seq 1 101); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TEST_TOKEN" \
    https://api.example.com/v1/me)
  echo "Request $i: $STATUS"
done | tail -5
# Expected last line: "Request 101: 429"
```

### Observability check (post-deploy)
```bash
# Confirm metric is emitted
curl -s https://api.example.com/metrics | grep rate_limit_rejected_total
# Expected: non-empty line with counter value
```

---

## 9. Out of Scope

- Per-endpoint or per-plan (tiered) limits — tracked as follow-up ticket #4412
- Rate-limit bypass for internal service accounts — handled by separate IP-allowlist middleware (already in place)
- Frontend UX for "you've been rate limited" — tracked with product team

---

## 10. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Redis latency spike adds > 5ms p99 to all requests | Medium | High | Pipeline Redis calls; use `ioredis` with connection pooling; measure in load test |
| Feature flag forgotten in staging (stays false) | Low | Medium | Deployment checklist item at M2 gate |
| Incorrect key prefix causes counter collision across environments | Low | High | Prefix includes environment name: `rl:{env}:{userId}` |
| Clock drift between app pods causes inconsistent windows | Low | Low | Use Redis server-side TTL, not local clock |

---

**Last updated**: [YYYY-MM-DD]
**Template version**: plan-contract v1.0 (medium complexity)
