# Metabase Embedding and Integration

> Purpose: Operational guide for embedding Metabase dashboards and questions into external applications — public links, signed embedding (JWT), modular embedding SDK, theming, security, and troubleshooting. Freshness anchor: June 2026 (v0.62.x).

For multi-tenant isolation and routing, see [tenants-routing.md](tenants-routing.md). For AI-driven in-app analytics workflows, see [agent-api.md](agent-api.md).

---
## Table of Contents

- [Decision Tree: Choosing an Embedding Approach](#decision-tree-choosing-an-embedding-approach)
- [Quick Reference: Embedding Comparison (2026)](#quick-reference-embedding-comparison-2026)
- [Public Sharing Links](#public-sharing-links)
- [Setup](#setup)
- [Usage](#usage)
- [Security Checklist](#security-checklist)
- [Signed Embedding (JWT)](#signed-embedding-jwt)
- [How It Works](#how-it-works)
- [Backend Setup](#backend-setup)
- [Python — JWT token generation](#python-—-jwt-token-generation)
- [Example: embed dashboard 42 locked to customer_id=123](#example-embed-dashboard-42-locked-to-customerid=123)
- [Frontend Integration](#frontend-integration)
- [Parameter Control](#parameter-control)
- [JWT Payload Examples](#jwt-payload-examples)
- [Interactive Embedding (SDK)](#interactive-embedding-sdk)
- [Prerequisites](#prerequisites)
- [React SDK Setup](#react-sdk-setup)
- [Key SDK Components](#key-sdk-components)
- [Auth Endpoint Pattern](#auth-endpoint-pattern)
- [Theme and Appearance Customization](#theme-and-appearance-customization)
- [CSS Variables (Signed Embedding)](#css-variables-signed-embedding)
- [URL Parameters for Appearance](#url-parameters-for-appearance)
- [Example: dark mode, no title, no borders](#example-dark-mode-no-title-no-borders)
- [SSO Integration for Embedded Analytics](#sso-integration-for-embedded-analytics)
- [SSO Flow for Interactive Embedding](#sso-flow-for-interactive-embedding)
- [Metabase JWT SSO Configuration](#metabase-jwt-sso-configuration)
- [Group Mapping](#group-mapping)
- [Troubleshooting Common Embedding Issues](#troubleshooting-common-embedding-issues)
- [Debug Checklist](#debug-checklist)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Decision Tree: Choosing an Embedding Approach

```
START: How will users access the embedded content?
│
├─ Public / no authentication needed
│   └─ Public sharing links
│       - Zero setup, URL-based
│       - No parameter filtering
│       - WARNING: anyone with URL can access
│
├─ Authenticated users, read-only dashboards
│   └─ Signed embedding (JWT)
│       - Server-side token generation
│       - Parameter locking for row-level security
│       - Iframe-based, limited interactivity
│
├─ Authenticated users, full interactivity
│   └─ Interactive embedding (SDK)
│       - Full Metabase experience in your app
│       - Drill-down, filtering, custom questions
│       - Requires Metabase Pro/Enterprise
│
└─ Programmatic data access (no UI)
    └─ Metabase API
        - REST API for query results
        - JSON responses for custom rendering
```

---

## Quick Reference: Embedding Comparison (2026)

| Feature | Public Link | Signed (JWT) | Interactive (SDK) | API |
|---------|------------|--------------|-------------------|-----|
| Authentication | None | Server-side JWT | SSO integration | API key/session |
| Parameters | URL params only | Locked or editable | Full filter UI | Request body |
| Interactivity | View only | View + locked filters | Full (drill, filter, explore) | Programmatic |
| Theming | No | Basic (CSS) | Full (SDK theme API) | N/A |
| License | Free | Free | Pro/Enterprise | Free |
| Security | Low | Medium | High | High |
| Implementation | Minutes | Hours | Days | Hours |
| Best for | Public data | Customer portals | SaaS analytics | Custom UIs |

---

## Public Sharing Links

### Setup

```
Admin → Settings → Public Sharing → Enable
```

### Usage

- **Use when**: Data is truly public, no sensitivity
- **URL pattern**: `https://metabase.company.com/public/dashboard/{uuid}`
- **Parameters**: Append `?param_name=value` to URL

### Security Checklist

- [ ] Only enable for genuinely public dashboards
- [ ] Review shared items regularly (Admin → Sharing)
- [ ] Disable public sharing globally if not needed
- [ ] No PII or sensitive data in public dashboards
- [ ] Consider rate limiting via reverse proxy

---

## Signed Embedding (JWT)

### How It Works

```
1. User visits your app
2. Your server generates JWT with:
   - Dashboard/question ID
   - Locked parameters (e.g., customer_id)
   - Expiration time
3. Frontend loads iframe with signed URL
4. Metabase validates JWT and renders content
```

### Backend Setup

```python
# Python — JWT token generation
import jwt
import time

METABASE_SECRET_KEY = "your-embedding-secret-key"  # from Admin → Embedding

def generate_embed_url(dashboard_id: int, params: dict) -> str:
    """Generate signed embedding URL for a dashboard."""
    payload = {
        "resource": {"dashboard": dashboard_id},
        "params": params,
        "exp": int(time.time()) + (10 * 60)  # 10 minute expiration
    }

    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
    return f"https://metabase.company.com/embed/dashboard/{token}"


# Example: embed dashboard 42 locked to customer_id=123
url = generate_embed_url(
    dashboard_id=42,
    params={"customer_id": 123}
)
```

```javascript
// Node.js — JWT token generation
const jwt = require("jsonwebtoken");

const METABASE_SECRET_KEY = process.env.METABASE_EMBED_SECRET;

function generateEmbedUrl(dashboardId, params) {
  const payload = {
    resource: { dashboard: dashboardId },
    params: params,
    exp: Math.round(Date.now() / 1000) + 10 * 60, // 10 min
  };

  const token = jwt.sign(payload, METABASE_SECRET_KEY);
  return `https://metabase.company.com/embed/dashboard/${token}`;
}

// Example
const url = generateEmbedUrl(42, { customer_id: 123 });
```

### Frontend Integration

```html
<!-- Iframe embedding -->
<iframe
  src="{{ embed_url }}"
  frameborder="0"
  width="100%"
  height="800"
  allowtransparency="true"
  loading="lazy"
></iframe>
```

### Parameter Control

| Parameter Mode | In JWT `params` | User Can Change | Use When |
|---------------|----------------|-----------------|----------|
| **Locked** | `{"customer_id": 123}` | No | Row-level security |
| **Editable** | `{"date_range": null}` | Yes | User-controlled filters |
| **Disabled** | Not included | No (hidden) | Irrelevant parameters |

### JWT Payload Examples

```json
// Locked customer_id, editable date range
{
  "resource": {"dashboard": 42},
  "params": {
    "customer_id": 123,
    "date_range": null
  },
  "exp": 1707580800
}

// Multiple locked parameters
{
  "resource": {"dashboard": 42},
  "params": {
    "customer_id": 123,
    "region": "US",
    "plan_type": "enterprise"
  },
  "exp": 1707580800
}

// Question (not dashboard) embedding
{
  "resource": {"question": 99},
  "params": {},
  "exp": 1707580800
}
```

---

## Modular Embedding SDK

Metabase's official name is now "Modular embedding SDK" (previously "Interactive embedding SDK"). Functionality is unchanged.

### Prerequisites

- Metabase Pro or Enterprise license
- SSO configured (SAML, JWT, or OIDC)
- React 18 or 19; Node.js 20.x or higher; Metabase v1.52 or higher

### React SDK Setup

```bash
npm install @metabase/embedding-sdk-react
```

```jsx
// MetabaseProvider.jsx
import { MetabaseProvider } from "@metabase/embedding-sdk-react";

const config = {
  metabaseInstanceUrl: "https://metabase.company.com",
  authProviderUri: "/api/metabase/auth", // your auth endpoint
};

const theme = {
  colors: {
    brand: "#4C51BF",
    "text-primary": "#1A202C",
    "text-secondary": "#718096",
    background: "#FFFFFF",
    "background-hover": "#F7FAFC",
  },
  fontSize: "14px",
  fontFamily: "Inter, sans-serif",
};

function App() {
  return (
    <MetabaseProvider config={config} theme={theme}>
      <YourApp />
    </MetabaseProvider>
  );
}
```

### Key SDK Components

- `InteractiveDashboard` — Full dashboard with filters, drill-down
- `StaticQuestion` — Single chart/visualization (read-only)
- Props: `dashboardId`, `initialParameterValues`, `withDownloads`, `hiddenParameters`

### Auth Endpoint Pattern

- Your server verifies app authentication
- Creates JWT with `email`, `first_name`, `last_name`, `groups` (maps to Metabase groups)
- Returns `{ id: token }` to SDK
- SDK uses token to authenticate with Metabase instance

### SDK version matrix (49 → 51+)

| SDK version | Key change | Auth endpoint pattern |
|-------------|------------|-----------------------|
| 49 | Initial public SDK release | `/api/metabase/auth` returns `{ id: token }` |
| 50 | `MetabaseProvider` config shape stabilized; `authProviderUri` is the canonical field | Same pattern; `authClientId` deprecated |
| 51+ | `InteractiveDashboard` prop API updated; `withDownloads` and `hiddenParameters` moved to top-level props | `/sso/metabase` endpoint preferred for SSO-backed auth; `/api/session/sso` deprecated path removed |

_This matrix reflects SDK state at time of authoring; verify current SDK changelog._

**Version-pinning advice**: pin `@metabase/embedding-sdk-react` to a minor version in `package.json` and test SDK upgrades in a staging environment before rolling to production. The SDK follows Metabase's release cadence; patch versions may include breaking changes when the underlying Metabase version changes. Check the official Metabase changelog at `metabase.com/changelog` and the SDK release notes on GitHub before each upgrade.

---

## Theme and Appearance Customization

### CSS Variables (Signed Embedding)

```css
/* Custom styles for iframe embedding */
:root {
  --mb-color-brand: #4C51BF;
  --mb-color-brand-light: #EBF4FF;
  --mb-color-text-primary: #1A202C;
  --mb-color-text-secondary: #718096;
  --mb-color-bg-white: #FFFFFF;
  --mb-color-bg-light: #F7FAFC;
  --mb-font-family: "Inter", sans-serif;
}
```

### URL Parameters for Appearance

| Parameter | Values | Effect |
|-----------|--------|--------|
| `bordered` | `true/false` | Card borders |
| `titled` | `true/false` | Dashboard/question title |
| `theme` | `night` | Dark mode |
| `hide_parameters` | `param1,param2` | Hide specific filters |
| `hide_download_button` | `true` | Remove download option |

```
# Example: dark mode, no title, no borders
/embed/dashboard/{token}#theme=night&titled=false&bordered=false
```

---

## SSO Integration for Embedded Analytics

### SSO Flow for Interactive Embedding

```
1. User logs into your app (your SSO)
2. Your app calls your auth endpoint
3. Auth endpoint creates Metabase JWT with user info + groups
4. SDK uses JWT to authenticate with Metabase
5. Metabase maps JWT groups to Metabase permission groups
6. User sees only data their group permits
```

### Metabase JWT SSO Configuration

```
Admin → Settings → Authentication → JWT
├─ JWT Identity Provider URI: https://yourapp.com/api/metabase/auth
├─ String used by the JWT signing key: [shared secret]
├─ User attribute → Email: email
├─ User attribute → First Name: first_name
├─ User attribute → Last Name: last_name
└─ User attribute → Groups: groups
```

### Group Mapping

| Your App Role | Metabase Group | Permissions |
|--------------|---------------|-------------|
| `admin` | Administrators | Full access |
| `analyst` | Data Analysts | All dashboards, SQL access |
| `customer:acme` | ACME Corp | Sandboxed to ACME data |
| `viewer` | Viewers | Curated dashboards only |

---

## Troubleshooting Common Embedding Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Iframe shows "Embedding is not enabled" | Embedding not toggled on | Admin → Settings → Embedding → Enable |
| JWT error "Token is expired" | Clock skew or short TTL | Increase expiration; sync server clocks |
| Dashboard shows no data | Parameters not matching filter values | Verify parameter names match dashboard filter slugs |
| CORS errors in browser console | Metabase not allowing your domain | Admin → Settings → Embedding → Authorized origins |
| Iframe blocked by CSP | Content Security Policy too restrictive | Add `frame-src https://metabase.company.com` to CSP |
| Blank iframe on Safari | Third-party cookie blocking | Use SDK instead of iframe; or SameSite=None cookies |
| Slow initial load | No caching, cold warehouse | Configure Metabase caching; use saved questions |
| "No permission" error in embed | JWT groups not mapping to Metabase groups | Verify group names in JWT match Metabase group names exactly |
| Parameters ignored in embed | Wrong parameter key name | Use dashboard filter slug, not display name |
| Dark mode not applying | Theme parameter syntax error | Use `#theme=night` as URL hash, not query param |

### Debug Checklist

- [ ] Verify embedding secret matches between app and Metabase
- [ ] Check JWT payload with jwt.io (do NOT paste production secrets)
- [ ] Confirm parameter names match filter slugs in dashboard URL
- [ ] Test in incognito mode (rule out cached auth issues)
- [ ] Check browser console for CORS/CSP errors
- [ ] Verify authorized origins include your domain
- [ ] Test with a simple dashboard first before complex ones

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Public sharing for sensitive data | Data exposure to anyone with URL | Use signed or interactive embedding |
| Long-lived JWT tokens (>1 hour) | Security risk if token leaked | Keep TTL to 10-15 minutes |
| Hardcoding embedding secret in frontend | Secret exposed in browser | Generate JWT server-side only |
| Not locking customer_id parameter | Users can see other customers' data | Always lock tenant identifiers in JWT params |
| Embedding without CSP headers | Clickjacking vulnerability | Set `Content-Security-Policy: frame-ancestors` |
| Using iframe when SDK is available | Missing interactivity, worse UX | Use SDK for Pro/Enterprise |
| No caching on embedded dashboards | Slow load, poor user experience | Enable Metabase caching for embedded questions |
| Embedding full Metabase URL | Exposes Metabase instance to end users | Use `/embed/` routes, not regular dashboard URLs |

---

## Cross-References

- `permissions-collections.md` — Permission model that governs embedded content
- `native-query-patterns.md` — SQL patterns used in embedded questions
- [software-security-appsec skill](../../software-security-appsec/SKILL.md) — Security layers for data underlying embedded dashboards

---

*Last updated: 2026-06-09*
