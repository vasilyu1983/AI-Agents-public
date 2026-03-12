# Playwright Web App Testing — Helper Pattern

## When to Use
- E2E coverage for locally served apps (frontend-only or full-stack).
- Need reliable startup/shutdown of one or more dev servers.
- Reconnaissance-driven selector discovery before writing assertions.

## Decision Tree
- Static HTML? → Open file://, identify selectors, write a short Playwright script.  
- Dynamic app and server not running? → Start your app server (`npm run dev`, `docker compose up`, etc.), wait for the port/health endpoint, then run Playwright.  
- Dynamic app and server running? → Navigate, wait for `networkidle`, inspect DOM/screenshot, then script actions.

## Server Lifecycle Helper
- Prefer a deterministic server lifecycle in CI and local runs:
  - Start the server(s)
  - Wait for readiness (port open or `/healthz`)
  - Run tests
  - Always stop the server(s) (even on failure)

Example (bash skeleton):

```bash
PORT=5173
npm run dev -- --port "$PORT" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT
until nc -z 127.0.0.1 "$PORT"; do sleep 0.2; done
npx playwright test
```

## Recon-Then-Action Pattern
1) Load page and `page.wait_for_load_state('networkidle')`.  
2) Capture `page.screenshot(...)` or `page.content()` to discover selectors.  
3) Prefer stable locators (roles/labels/test IDs) over brittle CSS.  
4) Add waits (`wait_for_selector`, timeouts) around async UI updates.

## Common Pitfalls
- Do not inspect DOM before network idle on dynamic apps.  
- Close browsers to avoid leaks.  
- Keep scripts focused on Playwright; leverage helper scripts as black boxes instead of inlining them.

## Example Skeleton
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")
    # discover selectors, then act
    browser.close()
```
