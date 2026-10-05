# Metabase API Authentication

Goal: programmatic access to Metabase with the right auth method for the right surface.

## Inputs

- `METABASE_URL`: Base URL, e.g. `https://metabase.example.com` (no trailing `/` preferred)
- Preferred: `METABASE_API_KEY`
- Optional reuse: `METABASE_SESSION`
- Fallback: `METABASE_USERNAME` + `METABASE_PASSWORD`

## Auth Modes

| Surface | Preferred auth | Notes |
|---------|----------------|-------|
| Classic Metabase REST API | `METABASE_API_KEY` | Best for cards, dashboards, collections, admin automation |
| Classic REST API fallback | Session token | Use only when API keys are unavailable |
| Agent API | API key (`X-API-Key`), session, or JWT | JWT is Pro/Enterprise only; see `agent-api.md` |
| Internal admin notify endpoints | `MB_API_KEY` | Server-side internal key, not the same as `METABASE_API_KEY` |

## Strategy: confirm auth by calling a cheap endpoint

Use an endpoint that requires auth and returns the current principal:

- `GET /api/user/current`

If the request returns HTTP 200, your auth method is accepted.

## API key authentication

Metabase API keys go in the `x-api-key` header (header names are case-insensitive):

- `X-API-KEY: <key>`

Do not send API keys as `Authorization: Bearer <key>`; that is not a documented API-key header. Confirm with `GET /api/user/current` (HTTP 200).

If it fails with 401/403:

- Confirm API keys are enabled in your Metabase instance.
- Check the Metabase admin UI for an "API keys" page and regenerate a key.
- Fall back to session auth if allowed (below).

## Session authentication (fallback)

If your environment permits a service username/password (not recommended for long-lived automation), create a session:

- `POST /api/session` with JSON body:
  - `{"username":"...","password":"..."}`

Use the response `id` as the session token in subsequent requests:

- `X-Metabase-Session: <id>`

### Session lifetime and caching

- Sessions are valid for a limited period and should be treated as short-lived
- Cache the session token and reuse it until it expires
- Logins are rate-limited; avoid creating new sessions per request

### Handling 401 errors (auto-retry pattern)

When the API returns 401, the current session may have expired or the runtime may have switched auth modes. Retry once after re-selecting auth:

```python
def request_with_retry(method, path, headers, body=None):
    status, payload, raw = _request(method, path, headers, body)
    if status == 401:
        # Refresh auth and retry once
        _, new_headers = _pick_auth_headers()
        status, payload, raw = _request(method, path, new_headers, body)
    return status, payload, raw
```

This pattern handles:

- Expired sessions
- Rotated API keys
- Temporary auth failures

## Agent API note

The Agent API docs list three accepted methods: an API key (`X-API-Key`; permissions come from the key's group), a session token (`X-Metabase-Session`), or JWT (Pro/Enterprise only). Pick by product boundary: API key for a service account, session for a logged-in user, JWT for per-user scoping in an embedded app. Details: `agent-api.md`. Re-check the plan and header requirements against your running version.

## Internal admin notify endpoints

Metabase documents some internal admin endpoints for notifying schema and metadata changes. These use server-side `MB_API_KEY`, not normal Metabase API keys. Treat them as instance-admin only and do not expose them in regular automation scripts.

## Safety notes

- Never commit `METABASE_API_KEY`, passwords, or session tokens to the repository.
- Prefer a least-privileged service user and a dedicated collection for automation-managed assets.
