---
name: software-frontend
description: Production-grade frontend engineering for Next.js/React, Vue/Nuxt, Angular, Svelte/SvelteKit, Remix, and Vite+React. Use for framework selection, App Router/RSC patterns, TypeScript strict-mode UI code, Tailwind CSS v4 + shadcn/ui, state/data flows (TanStack Query, Zustand), forms validation, testing (Vitest/Testing Library/Playwright), performance (Core Web Vitals), and accessibility (WCAG 2.2).
---

# Frontend Engineering

Production-ready patterns for modern web applications.

**Modern Best Practices (January 2026)**: Next.js 16 + Turbopack, React 19.x + Server Components, TypeScript 5.9+ (strict), Tailwind CSS v4, TanStack Query, Zustand, Vitest (browser mode).

**Breaking Changes**: [Next.js 16 Upgrade Guide](https://nextjs.org/docs/app/guides/upgrading/version-16)

Shared release gates: `../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md`

If you use React Server Components (RSC), treat security advisories as blocking: see `data/sources.json` (React RSC advisories).

## Quick Reference

| Task | Tool | Command |
|------|------|---------|
| Next.js App | Next.js 16 + Turbopack | `npx create-next-app@latest` |
| Vue App | Nuxt 4 | `npx nuxi@latest init` |
| Angular App | Angular 21 | `ng new` |
| Svelte App | SvelteKit 2.49+ | `npm create svelte@latest` |
| React SPA | Vite + React | `npm create vite@latest` |
| UI Components | shadcn/ui | `npx shadcn@latest init` |

## Workflow

1. Pick a framework using the decision tree.
2. Start from a matching template in `assets/`.
3. Implement feature-specific patterns from `references/`.
4. Treat accessibility and performance as release gates (shared checklist above).

## Framework Decision Tree

```text
Project needs:
|-- React ecosystem?
|   |-- Full-stack + SEO -> Next.js 16
|   |-- Progressive enhancement -> Remix
|   `-- Client-side SPA -> Vite + React
|
|-- Vue ecosystem?
|   |-- Full-stack -> Nuxt 4
|   `-- SPA -> Vite + Vue 3.5+
|
|-- State management?
|   |-- Server data -> TanStack Query
|   |-- Global client -> Zustand
|   `-- WARNING: DECLINING: Redux
|
`-- Styling?
    |-- Utility-first -> Tailwind CSS v4
    `-- WARNING: DECLINING: CSS-in-JS
```

## Next.js 16 Changes

### middleware.ts -> proxy.ts

```bash
# Run codemod
npx @next/codemod@canary upgrade latest

# Or manually rename
mv middleware.ts proxy.ts
```

```typescript
// After (Next.js 16)
export function proxy(request: Request) {
  // ... logic
}
```

### Cache Components (`"use cache"`)

```typescript
export default async function Page() {
  "use cache";
  const data = await fetchData();
  return <ProductList data={data} />;
}
```

### React Compiler

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true,
  },
};
```

## Performance Budgets

| Metric | Target |
|--------|--------|
| LCP | <= 2.5s |
| INP | <= 200ms |
| CLS | <= 0.1 |
| TTFB | < 600ms |

## Deployment Checklist

### Pre-Deployment

- [ ] `npm run build` - no errors
- [ ] `npm run lint` - zero ESLint errors
- [ ] `vitest run` - all tests passing
- [ ] Bundle size within budget
- [ ] Environment variables set

### Accessibility

- [ ] axe DevTools - zero critical issues
- [ ] Keyboard navigation works
- [ ] Color contrast >= 4.5:1
- [ ] Screen reader tested

### SEO

- [ ] Metadata configured
- [ ] sitemap.xml generated
- [ ] robots.txt configured

## Resources

| Resource | Purpose |
|----------|---------|
| [references/fullstack-patterns.md](references/fullstack-patterns.md) | Server/client components, data fetching |
| [references/vue-nuxt-patterns.md](references/vue-nuxt-patterns.md) | Vue 3, Nuxt, Pinia |
| [references/angular-patterns.md](references/angular-patterns.md) | Angular 21, signals |
| [references/svelte-sveltekit-patterns.md](references/svelte-sveltekit-patterns.md) | Svelte 5, SvelteKit |
| [references/remix-react-patterns.md](references/remix-react-patterns.md) | Remix loaders, actions |
| [references/operational-playbook.md](references/operational-playbook.md) | Architecture, security |
| [references/state-management-patterns.md](references/state-management-patterns.md) | TanStack Query, Zustand, Jotai, Redux Toolkit |
| [references/testing-frontend-patterns.md](references/testing-frontend-patterns.md) | Vitest, Testing Library, Playwright, MSW |
| [references/performance-optimization.md](references/performance-optimization.md) | Core Web Vitals, code splitting, image/font optimization |

## Templates

| Framework | Template |
|-----------|----------|
| Next.js | [assets/nextjs/template-nextjs-tailwind-shadcn.md](assets/nextjs/template-nextjs-tailwind-shadcn.md) |
| Vue/Nuxt | [assets/vue-nuxt/template-nuxt4-tailwind.md](assets/vue-nuxt/template-nuxt4-tailwind.md) |
| Angular | [assets/angular/template-angular21-standalone.md](assets/angular/template-angular21-standalone.md) |
| Svelte | [assets/svelte/template-sveltekit-runes.md](assets/svelte/template-sveltekit-runes.md) |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-backend](../software-backend/SKILL.md) | Backend API |
| [dev-api-design](../dev-api-design/SKILL.md) | REST/GraphQL |
| [software-code-review](../software-code-review/SKILL.md) | Code review |
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | CI/CD |

---

## React 19 + Frontend Ops Addendum (Feb 2026)

### Frequent Lint/Type Pitfalls (Operational)

Treat these as first-class fix targets during frontend work:
- `react-hooks/set-state-in-effect`
- `react-hooks/purity`
- `react-hooks/rules-of-hooks`
- `react/no-unescaped-entities`

### Frontend Verification Order

1. Lint edited files only.
2. Type-check edited feature surface.
3. Run full project lint/type/build once before handoff.

Avoid repeated full builds while known local lint/type failures remain.

### CLI Drift Guard (ESLint/Vitest)

Do not assume flags from older setups.

Use:
```bash
npx eslint --help
npx vitest --help
```

Then run commands compatible with the detected CLI mode.

### Frontend Handoff Requirements

Include in final output:
- exact files changed,
- lint/type/build commands run,
- whether failures are new or baseline,
- one prevention note for any repeated class of issue.

### Route Deletion Link Audit

After deleting or renaming any page/route/component file:

1. Grep the codebase for the old path/import (e.g., `rg "from.*old-module"`, `rg "href.*old-route"`).
2. Update or remove all references (imports, `<Link>` hrefs, redirects, sitemap entries).
3. Check navigation components, breadcrumbs, and cross-link cards for stale references.

Skipping this creates runtime 404s and broken imports that surface only in production.

### Architecture Pre-Check Before New Infrastructure

Before adding new infrastructure (new context providers, new API routes, new state stores):

1. Search for existing patterns that already solve the problem (`rg "createContext"`, `rg "useQuery"`).
2. Prefer extending existing infrastructure over creating parallel systems.
3. If new infrastructure is truly needed, document why the existing pattern is insufficient.

### Route Migration Checklist

When consolidating or restructuring routes (e.g., many pages → tabbed architecture):

1. Map all existing routes to their new destinations.
2. Add redirects for removed routes (Next.js `redirects` in config or middleware).
3. Update all internal `<Link>` components, `router.push()` calls, and shared navigation configs.
4. Update sitemap, robots.txt, and any SEO metadata referencing old routes.
5. Run a full-app link audit: `rg "href=" --glob "*.tsx"` to verify no stale paths remain.

---

## React 19 + Next.js 16 Production Gotchas (Feb 2026)

Seven patterns learned from real production sessions.

### 1. Hydration Safety Pattern

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

### 2. Safe Storage Access (String Discriminator Pattern)

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

### 3. React Three Fiber (R3F) Prop Spreading

Never rest-spread props onto R3F/Three.js elements. Unknown props corrupt Three.js internal state silently:

```typescript
// FAIL: Spreads isHovered, color, etc. onto <mesh> — breaks click handlers
<mesh {...handlers} position={pos}>

// PASS: Destructure and pass only known R3F event props
const { onClick, onPointerOver, onPointerOut } = handlers;
<mesh onClick={onClick} onPointerOver={onPointerOver} onPointerOut={onPointerOut} position={pos}>
```

### 4. Defensive Response Parsing

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

### 5. The Truthy `||` Fallback Trap

`data.field || []` does NOT protect against truthy non-array objects:

```typescript
// FAIL: { __gated: true, teaser: "..." } is truthy — passes through as "the array"
const items = data.transits || [];
items.sort(); // TypeError: items.sort is not a function

// PASS: Array.isArray() at system boundaries
const items = Array.isArray(data.transits) ? data.transits : [];
```

### 6. Turbopack + macOS File Descriptor Limit

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

### 7. Procedural Generation over External Assets (WebGL)

For WebGL/Three.js visuals, procedural generation (GLSL shaders) is more robust than external texture files:
- No 404 errors from missing textures
- No sandbox/CORS issues
- No loading states or error cascades
- Zero external file dependencies
- Often more visually striking (simplex noise patterns)

## Ops Runbook: SEO-Safe UI and Copy Refresh

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

