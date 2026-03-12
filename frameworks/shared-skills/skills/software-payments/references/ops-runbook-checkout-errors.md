# Ops Runbook: Checkout 500 + Authorization or RLS Denials

Use this when checkout endpoints return 500 and DB writes fail due to auth policy (for example PostgreSQL RLS, tenant predicates, or missing role grants).

---

## 5-Step Incident Loop

```bash
# 1) Trace checkout call path fast
rg -n "checkout|purchase|subscription|webhook" src app lib

# 2) Reproduce with minimal request (capture full response)
curl -i -X POST http://localhost:3000/api/purchases/checkout \
  -H 'content-type: application/json' \
  -d '{"productKey":"example"}'

# 3) Inspect auth and policy checks in code
rg -n "auth\.|user_id|tenant_id|policy|row level|RLS|canPurchase" src app lib

# 4) Verify DB policies (PostgreSQL)
psql "$DATABASE_URL" -c "select schemaname, tablename, policyname, permissive, cmd, qual, with_check from pg_policies where tablename in ('purchases','subscriptions','orders') order by tablename, policyname;"

# 5) Verify constrained insert path under app role
psql "$DATABASE_URL" -c "begin; set local role app_user; -- run minimal insert/select test here; rollback;"
```

---

## Required Logging for Fast Triage

- `request_id`, `user_id`, `tenant_id`, `product_key`, `price_id`, `policy_branch`
- database error code + message + table name
- payment provider request id (`stripe_request_id` or equivalent)

---

## Guardrails

- Keep checkout create calls idempotent (idempotency key per user + product + window).
- Validate authorization before payment intent/session creation.
- In webhook handlers, never trust client state; reconcile from provider event + DB.
- Fail closed on entitlement write errors; do not grant access on partial checkout success.
