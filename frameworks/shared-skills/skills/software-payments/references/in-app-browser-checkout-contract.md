# In-App Browser Checkout Contract Propagation

Use this guide when checkout API contract changes must be rolled out safely across multiple purchase entrypoints.

## Canonical Contract Example

```json
{
  "status": 409,
  "error": "IN_APP_BROWSER_BLOCKED",
  "message": "Open in browser to continue checkout",
  "recovery": {
    "open_url": "https://...",
    "copy_url": "https://..."
  }
}
```

## Mandatory Migration Steps

1. Enumerate all checkout callsites:

```bash
rg -n "api/stripe/checkout|api/purchases/checkout|createCheckout|checkout" app src
```

2. Build an entrypoint map (file + component + user surface).
3. Confirm every entrypoint handles the new contract path (for example `409 IN_APP_BROWSER_BLOCKED`).
4. Route blocked state to one shared recovery component.
5. Ensure analytics event ownership is singular (server or client, not both).

## Verification Matrix

For each entrypoint, verify:
- status-specific handling exists
- user sees deterministic recovery UI
- copy is localized
- telemetry emitted exactly once per action
- regression test covers blocked path

## Release Gate

Block release if any active entrypoint fails one of the checks above.

## Common Failure Modes

- Only one component migrated; others still show generic errors.
- Server and client emit duplicate KPI event.
- Recovery copy hardcoded in one locale only.
- New contract handled in subscription flow but not one-time purchases.
