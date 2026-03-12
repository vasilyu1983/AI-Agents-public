# Metabase Permissions and Collections

> Purpose: Operational guide for configuring Metabase permissions — group-based access control, collection hierarchy, data sandboxing, database/table permissions, API automation, and multi-team organization. Freshness anchor: Q1 2026.

---

## Decision Tree: Permission Architecture

```
START: How many distinct access levels do you need?
│
├─ 1-2 (e.g., admin + viewer)
│   └─ Simple group model
│       - Administrators group (built-in)
│       - All Users group with curated access
│
├─ 3-5 (e.g., admin, analyst, viewer, per-department)
│   └─ Group-per-role model
│       - One Metabase group per access level
│       - Collection hierarchy mirrors org structure
│
├─ 5-20 (e.g., per-customer or per-team sandboxing)
│   └─ Sandboxed groups model
│       - Data sandbox for row/column filtering
│       - Per-tenant groups with sandboxed permissions
│       - Requires Metabase Pro/Enterprise
│
└─ 20+ or dynamic
    └─ API-managed groups
        - Automated group creation via Metabase API
        - SSO group sync (SAML/JWT attributes)
        - Requires Metabase Pro/Enterprise
```

---

## Quick Reference: Permission Levels

### Data Permissions (Database/Schema/Table)

| Level | Can Query | Can See Native SQL | Can See Raw Data |
|-------|----------|-------------------|------------------|
| **Unrestricted** | Yes (any query) | Yes | Yes |
| **Granular** | Per-table control | Per-table control | Per-table control |
| **No self-service** | Saved questions only | No | Limited |
| **Block** | No access | No | No |

### Collection Permissions

| Level | View | Create | Edit | Delete |
|-------|------|--------|------|--------|
| **Curate** | Yes | Yes | Yes | Yes |
| **View** | Yes | No | No | No |
| **No access** | No | No | No | No |

### Native Query Permissions

| Level | Effect |
|-------|--------|
| **Query builder and native** | Full SQL access |
| **Query builder only** | GUI query builder, no raw SQL |
| **No** | Cannot create questions |

---

## Group-Based Permission Model

### Core Concept

- Every user belongs to one or more **groups**
- Permissions are assigned to **groups**, never to individual users
- The **All Users** group sets the baseline (most restrictive)
- Additional groups add permissions (additive model)

### Recommended Group Structure

| Group | Data Access | Collection Access | Use Case |
|-------|-----------|-------------------|----------|
| All Users | Block all databases | View "Public Dashboards" only | Baseline |
| Data Analysts | Unrestricted on analytics DB | Curate "Analytics" collection | Power users |
| SQL Analysts | Native query on analytics DB | Curate "Analytics" collection | SQL users |
| Marketing Team | Granular: marketing tables only | View "Marketing" collection | Department |
| Finance Team | Granular: finance tables only | Curate "Finance" collection | Department |
| Executive Viewers | No self-service | View "Executive" collection | Read-only |
| External: ACME | Sandboxed (customer_id=ACME) | View "ACME Portal" collection | Customer |

### Setup via Admin UI

```
Admin → People → Groups
1. Create group
2. Add members (or sync from SSO)

Admin → Permissions → Data
1. Select group
2. Set database/schema/table access level

Admin → Permissions → Collections
1. Select collection
2. Set group permission (Curate / View / No access)
```

---

## Collection Hierarchy

### Design Principles

- Collections are like folders — nest for organization
- Permission inheritance flows down (child inherits parent unless overridden)
- Keep hierarchy shallow (max 3-4 levels)
- Use naming conventions for discoverability

### Recommended Structure

```
Our Analytics (root)
├── Public Dashboards/          (All Users: View)
│   ├── Company KPIs
│   └── Product Metrics
│
├── Marketing/                  (Marketing Team: Curate, Others: No access)
│   ├── Campaigns/
│   ├── Attribution/
│   └── [WIP]/                  (Working drafts, same permissions)
│
├── Finance/                    (Finance Team: Curate, Exec: View)
│   ├── Revenue/
│   ├── Forecasting/
│   └── Board Reporting/
│
├── Analytics Team/             (Data Analysts: Curate, Others: No access)
│   ├── Explorations/
│   ├── Data Quality/
│   └── Templates/
│
├── Customer Portals/           (No access for internal; per-customer groups)
│   ├── ACME Corp/              (External:ACME: View)
│   ├── Globex Inc/             (External:Globex: View)
│   └── Initech/                (External:Initech: View)
│
└── Archive/                    (Admins only)
```

### Collection Permission Override

```
Parent collection: "Finance" — Finance Team: Curate
  └── Child collection: "Board Reporting" — Finance Team: View (override)
      Exec group: View

Effect: Finance team can curate most finance content
        but only view (not edit) board reporting dashboards
```

---

## Data Sandboxing

### What It Does

- Filters rows and/or hides columns based on user's group
- User sees full dashboard but data is scoped to their permissions
- Requires Metabase Pro/Enterprise

### Row-Level Sandboxing

```
Admin → Permissions → Data → [Database] → [Table]
Select: "Sandboxed" for the group

Filter type: "Filter by a column in the table"
Column: customer_id
User attribute: customer_id (from SSO attributes)
```

### How It Works

```
User logs in via SSO with attribute: customer_id = "acme-123"
  ↓
Metabase appends WHERE customer_id = 'acme-123' to all queries
  ↓
Dashboard shows only ACME data
  ↓
User cannot override or see the filter
```

### Column-Level Sandboxing

```
Admin → Permissions → Data → [Database] → [Table]
Select: "Sandboxed" for the group

Filter type: "Use a saved question to limit data"
Question: pre-built question that excludes sensitive columns
```

### Sandbox Configuration Checklist

- [ ] SSO configured with user attributes (customer_id, org_id, etc.)
- [ ] Sandbox attribute mapped in Admin → People → Group → Attribute
- [ ] Test with multiple user attributes to verify filtering
- [ ] Verify sandbox applies to native SQL queries (it does NOT by default)
- [ ] For native SQL sandbox, disable native query for sandboxed groups
- [ ] Test drill-down paths — sandbox must persist across drill-throughs

### Sandbox Limitations

| Limitation | Workaround |
|-----------|------------|
| Does not filter native SQL queries | Disable native query for sandboxed groups |
| Attribute must be string type | Convert IDs to strings in SSO claims |
| One sandbox per table per group | Use saved question approach for complex filters |
| Cannot sandbox on joined tables | Create denormalized view, sandbox that |
| Performance impact on large tables | Add index on sandbox filter column |

---

## Database-Level vs Table-Level Permissions

### When to Use Each

| Scenario | Level | Configuration |
|----------|-------|---------------|
| Team needs access to entire analytics DB | Database | Unrestricted on database |
| Team needs specific tables only | Table (Granular) | Unrestricted on specific tables, Block on others |
| Team needs filtered view of a table | Sandbox | Sandboxed on specific tables |
| External users, strict isolation | Database + Sandbox | Block all, sandbox specific tables |

### Granular Table Permissions

```
Admin → Permissions → Data → [Database]
Select "Granular" for group

Table: fct_orders → Unrestricted
Table: fct_payments → Unrestricted
Table: dim_customers → Sandboxed (filter by region)
Table: stg_* → Block (staging tables hidden)
Table: raw_* → Block (raw tables hidden)
```

---

## Admin API for Permission Automation

### List Groups

```bash
# GET all groups
curl -s -H "x-api-key: ${MB_API_KEY}" \
  https://metabase.company.com/api/permissions/group | jq '.'
```

### Create Group

```bash
# POST new group
curl -s -X POST \
  -H "x-api-key: ${MB_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name": "External: NewClient"}' \
  https://metabase.company.com/api/permissions/group
```

### Set Data Permissions

```bash
# PUT data permissions for a group
curl -s -X PUT \
  -H "x-api-key: ${MB_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "groups": {
      "7": {
        "1": {
          "data": {
            "schemas": {
              "analytics": {
                "fct_orders": {"query": "all", "read": "all"},
                "dim_customers": {"query": "none", "read": "none"}
              }
            }
          }
        }
      }
    }
  }' \
  https://metabase.company.com/api/permissions/graph
```

### Set Collection Permissions

```bash
# PUT collection permissions
curl -s -X PUT \
  -H "x-api-key: ${MB_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "groups": {
      "7": {
        "15": "read",
        "16": "none"
      }
    }
  }' \
  https://metabase.company.com/api/collection/graph
```

### Automated Customer Onboarding

- Script flow: create group (`POST /api/permissions/group`), create collection (`POST /api/collection`), set permissions via graph API, set sandbox
- Automate via SSO group sync for scale

---

## Multi-Team Organization Patterns

### Pattern 1: Department-Based

- **Use when**: Teams have distinct data domains
- One group per department
- Collections mirror department structure
- Shared "Public" collection for cross-team dashboards

### Pattern 2: Role-Based

- **Use when**: Access correlates with role, not department
- Groups: Admin, Analyst, Viewer, External
- Collections organized by topic, not team
- Role determines depth of access

### Pattern 3: Hybrid (Department + Role)

- **Use when**: Both department and role matter
- User belongs to department group AND role group
- Department group controls data access (which tables)
- Role group controls capability (SQL vs GUI vs view-only)

---

## Audit Logging

### What Metabase Logs

| Event | Logged | Location |
|-------|--------|----------|
| User login | Yes | `login_history` table |
| Question viewed | Yes | `view_log` table |
| Dashboard viewed | Yes | `view_log` table |
| Query executed | Yes | `query_execution` table |
| Permission changed | Yes | `activity` table |
| Content created/modified | Yes | `activity` table |
| Failed login attempts | Yes | `login_history` table |

### Audit Queries (Application Database)

- **Who accessed what**: JOIN `view_log` with `core_user`, filter by timestamp
- **Most active users**: GROUP BY `core_user.email` on `query_execution`, count queries
- **Failed logins**: `login_history` WHERE `session_id IS NULL` (failed attempts have no session)

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Permissive "All Users" group | Everyone sees everything by default | Set All Users to Block; add access via specific groups |
| Individual user permissions | Unmanageable at scale | Always use groups; never per-user permissions |
| Flat collection structure | Hard to navigate, hard to permission | Nest collections by domain (max 3-4 levels) |
| Sandbox without disabling native SQL | Users can bypass sandbox with raw SQL | Disable native query for sandboxed groups |
| No naming convention for groups | Confusion between roles and clients | Prefix: `Role: Analyst`, `Dept: Marketing`, `External: ACME` |
| Manual group management for customers | Slow onboarding, error-prone | Automate via API or SSO group sync |
| No audit review | Permission drift goes unnoticed | Monthly audit of groups, members, and permissions |
| Shared admin credentials | No accountability | Individual admin accounts; review admin list quarterly |

---

## Cross-References

- `embedding-integration.md` — Permissions model for embedded dashboards
- `native-query-patterns.md` — SQL access governed by permission groups
- `security-access-patterns.md` — Data lake security underlying Metabase permissions

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
