# React 19 + Next.js 16 Production Gotchas

Seven patterns learned from real production sessions. Each pattern shows a common failure mode and the correct approach.

---

## Table of Contents

1. [Hydration Safety Pattern](#1-hydration-safety-pattern)
2. [Safe Storage Access (String Discriminator)](#2-safe-storage-access-string-discriminator-pattern)
3. [React Three Fiber Prop Spreading](#3-react-three-fiber-r3f-prop-spreading)
4. [Defensive Response Parsing](#4-defensive-response-parsing)
5. [The Truthy `||` Fallback Trap](#5-the-truthy--fallback-trap)
6. [Turbopack + macOS File Descriptor Limit](#6-turbopack--macos-file-descriptor-limit)
7. [Procedural Generation over External Assets (WebGL)](#7-procedural-generation-over-external-assets-webgl)
8. [SEO-Safe UI and Copy Refresh Runbook](#seo-safe-ui-and-copy-refresh-runbook)

---

## 1. Hydration Safety Pattern

In Next.js 16 + React 19 SSR, server components run in Node.js (UTC, no `window`) while client components hydrate in the browser. Every `new Date()`, `localStorage`, and browser API call is a potential mismatch.

```typescript
// PASS: useState(null) + useEffect — server renders skeleton, client fills real value
const [moonPhase, setMoonPhase] = useState<string | null>(null);
useEffect(() => {
  setMoonPhase(calculateMoonPhase(new Date()));
}, []);
if (!moonPhase) return <Skeleton />;

// FAIL: useMemo with Date() — server (UTC midnight) !== client (user timezone)
const moonPhase = useMemo(() => calculateMoonPhase(new Date()), []);
// Causes React Error #418 (hydration mismatch), 53 occurrences in production
```

**Rule**: Use `useState(null) + useEffect` for ANY computation depending on:
- `new Date()` (timezone-dependent)
- `localStorage` / `sessionStorage` (not available on server)
- `window.*` properties (navigator, screen, location)
- Any browser-only API

---

## 2. Safe Storage Access (String Discriminator Pattern)

JavaScript evaluates function arguments BEFORE the function body executes. Passing `localStorage` to a safe wrapper defeats the try/catch:

```typescript
// FAIL: localStorage is evaluated at the CALL SITE, before try/catch
function safeGet(storage: Storage, key: string) {
  try { return storage.getItem(key); } // too late — already threw
  catch { return null; }
}
safeGet(localStorage, 'theme'); // SecurityError in Firefox (cookies disabled)

// PASS: String discriminator — storage access inside try/catch
function safeGet(type: 'local' | 'session', key: string) {
  try {
    const storage = type === 'local' ? window.localStorage : window.sessionStorage;
    return storage.getItem(key);
  } catch { return null; }
}
safeGet('local', 'theme'); // Safe — never throws
```

---

## 3. React Three Fiber (R3F) Prop Spreading

Never rest-spread props onto R3F/Three.js elements. Unknown props corrupt Three.js internal state silently:

```typescript
// FAIL: Spreads isHovered, color, etc. onto <mesh> — breaks click handlers
<mesh {...handlers} position={pos}>

// PASS: Destructure and pass only known R3F event props
const { onClick, onPointerOver, onPointerOut } = handlers;
<mesh onClick={onClick} onPointerOver={onPointerOver} onPointerOut={onPointerOut} position={pos}>
```

---

## 4. Defensive Response Parsing

Dev servers, CDNs, and proxies can return HTML error pages. Never call `.json()` without guards:

```typescript
// FAIL: Throws SyntaxError when server returns HTML error page
const data = await response.json();

// PASS: Check response.ok + try/catch json()
if (!response.ok) {
  throw new Error(`API error: ${response.status}`);
}
let data;
try {
  data = await response.json();
} catch {
  throw new Error('Invalid JSON response — server may have returned an error page');
}
```

---

## 5. The Truthy `||` Fallback Trap

`data.field || []` does NOT protect against truthy non-array objects:

```typescript
// FAIL: { __gated: true, teaser: "..." } is truthy — passes through as "the array"
const items = data.transits || [];
items.sort(); // TypeError: items.sort is not a function

// PASS: Array.isArray() at system boundaries
const items = Array.isArray(data.transits) ? data.transits : [];
```

---

## 6. Turbopack + macOS File Descriptor Limit

macOS default ulimit (~256) is too low for Turbopack in large Next.js projects. Causes:
- `EMFILE: too many open files` errors
- `build-manifest.json` ENOENT panics
- Stale chunk loading failures in browser

Fix:
```bash
# Add to ~/.zshrc or ~/.bashrc
ulimit -n 10240

# Emergency recovery when .next is corrupted
# 1. Kill dev server
# 2. rm -rf .next
# 3. npm run dev
```

---

## 7. Procedural Generation over External Assets (WebGL)

For WebGL/Three.js visuals, procedural generation (GLSL shaders) is more robust than external texture files:
- No 404 errors from missing textures
- No sandbox/CORS issues
- No loading states or error cascades
- Zero external file dependencies
- Often more visually striking (simplex noise patterns)

---

## SEO-Safe UI and Copy Refresh Runbook

Use this for redesigns, pricing-copy updates, and landing refreshes that must not break indexed routes.

### Command Checklist

```bash
# 1) Verify route/link impact
rg -n "href=|router\.push\(|redirect\(" src app

# 2) Verify metadata/sitemap/robots touchpoints
rg -n "metadata|sitemap|robots|canonical|hreflang|alternates" src app

# 3) Sweep for stale phrases (pricing/trial/campaign copy)
rg -n "free trial|7-day|old-price|legacy-plan-name" src/messages src/components

# 4) Build to catch route/import regressions
npm run build
```

### No-Regressions Rules

- Do not remove or rename indexed routes without explicit redirect mapping.
- Keep locale routes and metadata aligned; no mixed-language metadata.
- Update copy and analytics labels together when pricing language changes.
- Run link audit after deleting/renaming components used by navigation cards.
