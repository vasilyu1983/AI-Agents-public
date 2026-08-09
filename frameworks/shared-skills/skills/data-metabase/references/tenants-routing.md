# Metabase Tenants, Routing, and Embedded Access

> Purpose: Operational guide for multi-tenant Metabase deployments in customer-facing apps. Freshness anchor: June 2026.

## When to Use Tenants

Use tenants when one embedded application must serve multiple customers, workspaces, or organizations with isolated views of data and models.

## Core Model

- a tenant represents an isolated logical Metabase experience
- routing decides which tenant, database connection, or semantic model a request should use
- embedding permissions decide what each end user can see inside that tenant

## Decision Rule

| Scenario | Preferred pattern |
|----------|-------------------|
| One internal team using a single Metabase instance | Standard groups and collections |
| Customer portal with strict tenant isolation | Tenants + embedding permissions |
| App-side AI analytics per customer | Tenants + Agent API |
| Simple row-level filtering only | Groups, sandboxing, or locked embed params |

## Recommended Workflow

1. Define the tenant boundary first: customer, workspace, org, or region.
2. Decide whether data isolation is done by tenant routing, database routing, sandboxing, or a mix.
3. Configure embedding permissions for each tenant path.
4. Test the same dashboard or query under multiple tenant identities before shipping.
5. If AI workflows are involved, keep the tenant context explicit in every Agent API request.

## Guardrails

- Do not rely on dashboard filters alone for isolation.
- Keep tenancy and end-user permissions explicit in architecture docs and code.
- If native SQL bypasses sandboxing in your setup, disable native query access for tenant-scoped users.
- Export and diff representative dashboards after tenant-related edits to ensure filters and mappings survived.
