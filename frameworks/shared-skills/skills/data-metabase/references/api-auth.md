# Metabase API Authentication

Goal: programmatic access to Metabase with an API key (preferred) and safe fallbacks.

## Inputs

- `METABASE_URL`: Base URL, e.g. `https://metabase.example.com` (no trailing `/` preferred)
- Preferred: `METABASE_API_KEY`
- Fallback: `METABASE_USERNAME` + `METABASE_PASSWORD`

## Strategy: confirm auth by calling a cheap endpoint

Use an endpoint that requires auth and returns the current principal:

- `GET /api/user/current` (commonly available)

If the request returns HTTP 200, your auth method is accepted.

## API key authentication

Metabase API key auth has multiple variants across versions/editions. If you are not sure which header your instance expects, try these in order (and keep the one that returns 200 from `GET /api/user/current`):

1. `X-API-KEY: <key>`
2. `Authorization: Bearer <key>`

If both fail with 401/403:

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

- Sessions are valid for **14 days** by default
- Configure via env var: `MAX_SESSION_AGE` (value in minutes)
- **Cache the session token** and reuse until it expires
- Logins are rate-limited; avoid creating new sessions per request

### Handling 401 errors (auto-retry pattern)

When the API returns 401 (Unauthorized), your session may have expired. Implement auto-retry:

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

## Safety notes

- Never commit `METABASE_API_KEY`, passwords, or session tokens to the repository.
- Prefer a least-privileged service user and a dedicated collection for automation-managed assets.
