---
name: software-frontend
description: Production-grade frontend development with Next.js 16 App Router, TypeScript 5.9+ strict mode, Tailwind CSS v4, shadcn/ui, React 19.2 Server Components, state management (Zustand/Recoil), performance optimization (Turbopack stable, ISR/SSR/SSG), and accessibility best practices. Includes TanStack Query for server-state, Vitest for testing, and modern React patterns.
---

# Frontend Engineering Skill — Quick Reference

This skill equips frontend engineers with execution-ready patterns for building modern web applications with Next.js, React, TypeScript, and Tailwind CSS. Apply these patterns when you need component design, state management, routing, forms, data fetching, animations, accessibility, or production-grade UI architectures.

**Modern Best Practices (January 2026)**: Next.js 16 with Turbopack (stable, default bundler), **middleware.ts → proxy.ts migration** (clarifies network boundary, runs on Node.js runtime), **DevTools MCP** (AI agent integration), **Cache Components** (`"use cache"` directive for opt-in caching), **React Compiler** (automatic re-render optimization), React 19.2 with Server Components, Actions, Activity component, enhanced ISR/SSR/SSG, partial prerendering (PPR), Zustand/Recoil as Redux alternatives (Redux declining), TanStack Query (React Query) for server-state, TypeScript 5.9+ strict mode (**TypeScript 7 "Corsa" Go-based 10x faster compiler mid-2026**), `satisfies` operator, Tailwind CSS v4 (CSS-first config, 5x faster builds), **Vitest 4.0 Browser Mode** (stable), and progressive enhancement patterns.

**Next.js 16 Breaking Changes**: [Upgrade Guide](https://nextjs.org/docs/app/guides/upgrading/version-16) | **Declining in 2026**: Redux, CSS-in-JS, Create React App

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Next.js App | Next.js 16 + Turbopack | `npx create-next-app@latest` | Full-stack React apps, SEO, SSR/SSG |
| Vue App | Nuxt 4 | `npx nuxi@latest init` | Vue ecosystem, auto-imports, Nitro server |
| Angular App | Angular 21 | `ng new` | Enterprise apps, zoneless change detection, esbuild |
| Svelte App | SvelteKit 2.49+ | `npm create svelte@latest` | Performance-first, minimal JS, Svelte 5 runes |
| React SPA | Vite + React | `npm create vite@latest` | Client-side apps, fast dev server |
| UI Components | shadcn/ui + Radix UI | `npx shadcn@latest init` | Accessible components, Tailwind v4 styling |
| Forms | React Hook Form + Zod | `npm install react-hook-form zod` | Type-safe validation, performance |
| State Management | Zustand/Recoil | `npm install zustand` | Lightweight global state |
| Server State | TanStack Query | `npm install @tanstack/react-query` | API caching, server-state sync |
| Testing | Vitest + Testing Library | `vitest run` | Unit/component tests, fast execution |

# When to Use This Skill

Use this skill when you need:

- Next.js 16 application architecture and setup (Turbopack stable, App Router, React 19)
- React component design and patterns (functional components, hooks, Server Components)
- TypeScript type definitions for UI (strict mode, `satisfies` operator, discriminated unions)
- Tailwind CSS styling and responsive design (utility-first, dark mode variants)
- shadcn/ui component integration (Radix UI + Tailwind)
- Form handling and validation (React Hook Form + Zod, Server Actions)
- State management (Zustand/Recoil for client state, TanStack Query for server state)
- Data fetching (Server Components, TanStack Query/SWR, Server Actions, streaming)
- Authentication flows (NextAuth.js, Clerk, Auth0)
- Route handling and navigation (App Router, parallel routes, intercepting routes)
- Performance optimization (Turbopack, Image optimization, code splitting, ISR/SSR/SSG)
- Accessibility (WCAG 2.2, ARIA, keyboard navigation, screen reader testing) https://www.w3.org/TR/WCAG22/
- Animation and transitions (Framer Motion, Tailwind animations)
- Testing (Vitest for unit tests, Testing Library for components, Playwright for E2E)

## Decision Tree: Frontend Framework Selection

```text
Project needs: [Framework Choice]
    ├─ React ecosystem?
    │   ├─ Full-stack + SEO → Next.js 16 (App Router, React 19.2, Turbopack stable)
    │   ├─ Progressive enhancement → Remix (loaders, actions, nested routes)
    │   └─ Client-side SPA → Vite + React (fast dev, minimal config)
    │
    ├─ Vue ecosystem?
    │   ├─ Full-stack + SSR → Nuxt 4 (auto-imports, Nitro server, file-based routing)
    │   └─ Client-side SPA → Vite + Vue 3.5+ (Composition API, script setup)
    │
    ├─ Angular preferred?
    │   └─ Enterprise app → Angular 21 (zoneless change detection, esbuild, signals)
    │
    ├─ Performance-first?
    │   └─ Minimal JS bundle → SvelteKit 2.49+ (Svelte 5.45 runes, compiler magic)
    │
    ├─ Component library?
    │   ├─ Headless + customizable → shadcn/ui + Radix UI + Tailwind
    │   ├─ Material Design → MUI (Material-UI)
    │   └─ Enterprise UI → Ant Design
    │
    ├─ State management?
    │   ├─ Server data → TanStack Query/SWR (caching, sync)
    │   ├─ Global client state → Zustand (lightweight) or Jotai (atomic)
    │   ├─ Complex state logic → XState (state machines)
    │   ├─ URL-based state → useSearchParams (shareable filters)
    │   └─ ⚠️ DECLINING: Redux (use Zustand instead)
    │
    ├─ Styling approach?
    │   ├─ Utility-first → Tailwind CSS v4 (CSS-first config, 5x faster builds)
    │   ├─ CSS Modules → Built-in CSS Modules
    │   └─ ⚠️ DECLINING: CSS-in-JS (Styled Components, Emotion)
    │
    └─ Testing strategy?
        ├─ Unit/Component → Vitest + Testing Library (fast, modern)
        ├─ E2E → Playwright (cross-browser, reliable)
        └─ Visual regression → Chromatic or Percy
```

**Framework Selection Factors:**

- **Team experience**: Choose what the team knows or can learn quickly
- **SSR/SSG requirements**: Next.js, Nuxt, Remix for server-side rendering
- **Performance constraints**: SvelteKit for minimal JS, Next.js for optimization
- **Ecosystem maturity**: React has largest ecosystem, Vue/Angular are also mature

See [references/](references/) for framework-specific best practices.

---

## Next.js 16 Migration: middleware.ts → proxy.ts

**Breaking Change (Dec 2025)**: The `middleware` convention is renamed to `proxy` in Next.js 16.

### Why the Change?

- **Clarity**: "Proxy" better describes the network boundary behavior (runs in front of the app)
- **Runtime**: `proxy.ts` runs on **Node.js runtime** (not Edge by default)
- **Avoid confusion**: Prevents confusion with Express.js middleware patterns

### Migration Steps

```bash
# 1. Run the codemod (recommended)
npx @next/codemod@canary upgrade latest

# 2. Or manually rename
mv middleware.ts proxy.ts
```

```typescript
// Before (Next.js 15)
export function middleware(request: Request) {
  // ... logic
}

// After (Next.js 16)
export function proxy(request: Request) {
  // ... logic
}
```

```typescript
// next.config.ts - Update config option
const nextConfig: NextConfig = {
  skipProxyUrlNormalize: true, // was: skipMiddlewareUrlNormalize
}
```

### Runtime Considerations

| Feature | proxy.ts (Next.js 16) | middleware.ts (legacy) |
| ------- | --------------------- | ---------------------- |
| Default Runtime | Node.js | Edge |
| Edge Support | Not supported | Supported |
| Use Case | Auth, rewrites, redirects | Edge-first apps |

**⚠️ Keep using `middleware.ts`** if you need Edge Runtime. The `proxy` convention does NOT support Edge.

### Related Changes in Next.js 16

- **Async Request APIs**: `cookies()`, `headers()`, `params`, `searchParams` are now async
- **Turbopack default**: Remove `--turbopack` flags from scripts
- **Parallel routes**: Require explicit `default.js` files
- **Image changes**: `domains` deprecated (use `remotePatterns`), new default cache TTL

---

## Next.js 16 New Features (January 2026)

### DevTools MCP Integration

Next.js 16 introduces DevTools MCP (Model Context Protocol), connecting AI agents directly to your application's runtime context.

| Feature | AI Capability |
|---------|---------------|
| Routing context | AI understands App Router structure automatically |
| Caching semantics | AI knows when/how cache invalidates |
| Rendering behavior | AI explains SSR/SSG/ISR decisions |
| Component hierarchy | AI navigates Server/Client component boundaries |

**Benefit**: Your AI assistant (Copilot, Cursor, Claude) understands Next.js framework concepts without manual explanation.

### Cache Components (`"use cache"`)

Next.js 16 replaces implicit caching with **explicit opt-in caching**. Dynamic code executes at request time by default — no surprise caching.

```typescript
// Cache a page
export default async function Page() {
  "use cache";
  const data = await fetchData();
  return <ProductList data={data} />;
}

// Cache a function
async function getProducts() {
  "use cache";
  return db.query('SELECT * FROM products');
}

// Cache a component
async function ExpensiveComponent() {
  "use cache";
  const result = await heavyComputation();
  return <div>{result}</div>;
}
```

| Caching Approach | Next.js 15 | Next.js 16 |
|------------------|------------|------------|
| Default behavior | Implicit caching | No caching (explicit opt-in) |
| Cache directive | N/A | `"use cache"` |
| Granularity | Route-level | Page, component, or function level |
| Predictability | Surprise caching | Explicit, predictable |

### React Compiler Integration

Next.js 16 includes built-in support for the **React Compiler** (formerly React Forget). It automatically optimizes components by reducing unnecessary re-renders.

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: true, // Enable React Compiler
  },
};
```

**What it does**:
- Automatically memoizes components (no manual `useMemo`/`useCallback`)
- Eliminates re-renders from unchanged props
- Zero config — compiler analyzes and optimizes automatically

**Migration**: Remove manual `useMemo`, `useCallback`, `React.memo` — the compiler handles it.

### Next.js 15 → 16 Migration Checklist

| Step | Action | Command/Change |
|------|--------|----------------|
| 1 | Update Next.js | `npm install next@16` |
| 2 | Update Node.js | Node 20.9+ required |
| 3 | Rename middleware | `mv middleware.ts proxy.ts` |
| 4 | Update export | `export function proxy()` |
| 5 | Make APIs async | `await cookies()`, `await headers()` |
| 6 | Remove Turbopack flag | Delete `--turbopack` from scripts |
| 7 | Add default.js | Required for parallel routes |
| 8 | Update image config | `remotePatterns` instead of `domains` |
| 9 | Run codemod | `npx @next/codemod@canary upgrade latest` |
| 10 | Test thoroughly | Verify caching behavior changed |

---

## TypeScript 7 "Corsa" (Mid-2026)

TypeScript 7, codenamed **Project Corsa**, is a complete rewrite of the compiler in **Go**.

| Feature | TypeScript 5.9 | TypeScript 7 "Corsa" |
|---------|----------------|----------------------|
| Compiler language | JavaScript | Go |
| Build speed | Baseline | **10x faster** |
| Strict mode | Opt-in | **Default** |
| ES5 target | Supported | **Dropped** |
| AMD/UMD/SystemJS | Supported | **Removed** |
| Classic Node resolution | Supported | **Removed** |

### TypeScript 5.9 Features (Current)

```typescript
// Import defer — deferred module evaluation
import defer * as analytics from './analytics';

// Module loads only when accessed
function trackEvent(event: string) {
  analytics.track(event); // Loads analytics module here
}

// Expandable hovers in VS Code
// Click + to expand type details, - to collapse
```

### Migration Path

```text
TypeScript 5.9 (current) → TypeScript 6.0 (bridge) → TypeScript 7.0 (Corsa)
                           Deprecation warnings        Breaking changes
```

**Prepare now**: Enable strict mode, remove ES5 targets, migrate from AMD/UMD.

---

## Vitest 4.0 Browser Mode (Stable)

Vitest Browser Mode is now **stable in Vitest 4.0**, enabling real browser-based component testing.

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: 'playwright', // or 'webdriverio'
      name: 'chromium',
    },
  },
});
```

```typescript
// Button.test.tsx — runs in real browser
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

test('renders button with text', async () => {
  render(<Button>Click me</Button>);
  await expect.element(screen.getByRole('button')).toHaveTextContent('Click me');
});
```

| Testing Layer | Tool | Environment | Speed |
|---------------|------|-------------|-------|
| Unit tests | Vitest | Node/jsdom | Fastest |
| Component tests | Vitest Browser Mode | Real browser | Fast |
| E2E tests | Playwright | Real browser | Slower |

**Best practice**: Use Vitest for unit/component tests, Playwright for E2E. They complement each other.

---

## React 19.2 Patterns (January 2026)

### Security Note (React Server Components)

- Track and patch React Server Components vulnerabilities quickly (RCE/DoS/source exposure advisories in Dec 2025) https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components and https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components

### Partial Prerendering (PPR)

Pre-render static shell, stream dynamic content.

```typescript
// Next.js 16 with PPR enabled
// next.config.js
export default {
  experimental: {
    ppr: true, // Enable Partial Prerendering
  },
};

// Page component
export default async function Page() {
  return (
    <main>
      <Header /> {/* Static: pre-rendered */}
      <Suspense fallback={<Skeleton />}>
        <DynamicContent /> {/* Dynamic: streamed */}
      </Suspense>
      <Footer /> {/* Static: pre-rendered */}
    </main>
  );
}
```

### use() Hook Pattern

Promise resolution in components with Suspense.

```typescript
// Before: useEffect + useState
const [data, setData] = useState(null);
useEffect(() => {
  fetchData().then(setData);
}, []);

// After: use() hook (React 19+)
const data = use(fetchDataPromise);
```

### Error Boundary Patterns

```typescript
'use client';

import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### Performance Budgets

| Metric | Target | Tool | SEO Impact |
|--------|--------|------|------------|
| LCP (Largest Contentful Paint) | <= 2.5s | Lighthouse / web-vitals | Mobile-first indexing threshold |
| INP (Interaction to Next Paint) | <= 200ms | Chrome DevTools / web-vitals https://web.dev/vitals/ | User engagement signals |
| CLS (Cumulative Layout Shift) | <= 0.1 | Lighthouse / web-vitals | Core Web Vitals ranking factor |
| TTFB (Time to First Byte) | < 600ms | Lighthouse | **Crawl rate** — slow servers = fewer pages crawled |
| Bundle size (JS) | Project budget [Inference] | bundle analyzer | Affects LCP and crawlability |

### SSR/SSG and SEO Indexation

| Rendering Strategy | SEO Benefit | When to Use |
|--------------------|-------------|-------------|
| **SSG (Static)** | Pre-rendered HTML, fastest TTFB, best crawlability | Content that rarely changes |
| **SSR (Server)** | Fresh content, good crawlability | Dynamic but SEO-critical pages |
| **ISR (Incremental)** | Static + freshness, balanced crawlability | Frequently updated content |
| **CSR (Client)** | Poor crawlability without workarounds | Non-SEO apps, dashboards |

**Key insight**: Google crawls rendered HTML. Server-rendered content indexes faster and more reliably than client-rendered JavaScript.

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] Run `npm run build` — verify no build errors
- [ ] Run `npm run lint` — zero ESLint errors
- [ ] Run `npm run typecheck` — zero TypeScript errors
- [ ] Run `vitest run` — all tests passing
- [ ] Run `playwright test` — E2E tests passing
- [ ] Check bundle size — within project budget
- [ ] Verify environment variables — all required vars set

### Performance Audit

- [ ] Lighthouse score >= 90 (Performance)
- [ ] LCP <= 2.5s on mobile
- [ ] INP <= 200ms
- [ ] CLS <= 0.1
- [ ] No layout shifts from dynamic content
- [ ] Images optimized (WebP/AVIF, responsive)
- [ ] Fonts preloaded or using `font-display: swap`

### Security Audit

- [ ] CSP headers configured
- [ ] No secrets in client bundle
- [ ] API routes protected (auth checks)
- [ ] HTTPS enforced
- [ ] Rate limiting on API routes
- [ ] Input validation on all forms

### Accessibility Audit

- [ ] axe DevTools — zero critical issues
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Screen reader tested (VoiceOver/NVDA)
- [ ] Color contrast >= 4.5:1
- [ ] Alt text on all images

### SEO Checklist

- [ ] Metadata API configured (title, description)
- [ ] Open Graph images generated
- [ ] sitemap.xml generated
- [ ] robots.txt configured
- [ ] Canonical URLs set
- [ ] Structured data (JSON-LD) where applicable

---

### Optional: AI/Automation Extensions

> **Note**: AI design and development tools. Skip if not using AI tooling.

#### AI Design Tools

| Tool | Use Case |
|------|----------|
| v0.dev | UI generation from prompts |
| Vercel AI SDK | Streaming UI, chat interfaces |
| Figma AI | Design-to-code prototypes |
| Visily | Wireframe generation |

#### AI-Powered Testing

| Tool | Use Case |
|------|----------|
| Playwright AI | Self-healing selectors |
| Testim | AI-generated test maintenance |
| Applitools | Visual AI testing |

#### Optional Related Skills

- [../ai-llm/SKILL.md](../ai-llm/SKILL.md) — Optional: AI-powered features and LLM integration patterns

---

## Navigation

**Resources** (Framework-specific best practices)
- [references/fullstack-patterns.md](references/fullstack-patterns.md) — Universal patterns: Server vs client components, data fetching, TypeScript
- [references/vue-nuxt-patterns.md](references/vue-nuxt-patterns.md) — Vue 3 Composition API, Nuxt 3, Pinia state management
- [references/angular-patterns.md](references/angular-patterns.md) — Angular 18 standalone components, signals, RxJS patterns
- [references/svelte-sveltekit-patterns.md](references/svelte-sveltekit-patterns.md) — Svelte 5 runes, SvelteKit loaders/actions
- [references/remix-react-patterns.md](references/remix-react-patterns.md) — Remix loaders, actions, progressive enhancement
- [references/vite-react-patterns.md](references/vite-react-patterns.md) — Vite setup, React hooks, TanStack Query
- [references/artifacts-builder.md](references/artifacts-builder.md) — React/Tailwind/shadcn artifact workflow and bundling to single HTML
- [README.md](README.md) — Folder overview and usage notes
- [data/sources.json](data/sources.json) — 123 curated resources for all frameworks (Next.js, Vue/Nuxt, Angular, Svelte, Remix, Vite)
- Shared checklist: [../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md](../software-clean-code-standard/assets/checklists/frontend-performance-a11y-checklist.md)

**Shared Utilities** (Centralized patterns — extract, don't duplicate)
- [../software-clean-code-standard/utilities/error-handling.md](../software-clean-code-standard/utilities/error-handling.md) — Effect Result types, correlation IDs
- [../software-clean-code-standard/utilities/config-validation.md](../software-clean-code-standard/utilities/config-validation.md) — Zod 3.24+, Valibot for client validation
- [../software-clean-code-standard/utilities/logging-utilities.md](../software-clean-code-standard/utilities/logging-utilities.md) — Structured logging patterns
- [../software-clean-code-standard/utilities/testing-utilities.md](../software-clean-code-standard/utilities/testing-utilities.md) — Vitest, MSW v2, factories, fixtures
- [../software-clean-code-standard/utilities/observability-utilities.md](../software-clean-code-standard/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) — Canonical clean code rules (`CC-*`) for citation

**Templates** (Production-ready starters by framework)
- **Next.js**: [assets/nextjs/template-nextjs-tailwind-shadcn.md](assets/nextjs/template-nextjs-tailwind-shadcn.md)
- **Vue/Nuxt**: [assets/vue-nuxt/template-nuxt3-tailwind.md](assets/vue-nuxt/template-nuxt3-tailwind.md)
- **Angular**: [assets/angular/template-angular21-standalone.md](assets/angular/template-angular21-standalone.md)
- **Svelte/SvelteKit**: [assets/svelte/template-sveltekit-runes.md](assets/svelte/template-sveltekit-runes.md)
- **Remix**: [assets/remix/template-remix-react.md](assets/remix/template-remix-react.md)
- **Vite + React**: [assets/vite-react/template-vite-react-ts.md](assets/vite-react/template-vite-react-ts.md)

**Related Skills**
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — REST/GraphQL API patterns, OpenAPI, versioning
- [../git-workflow/SKILL.md](../git-workflow/SKILL.md) — Git branching, PR workflow, commit conventions
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — Backend API development, Node.js, Prisma, authentication
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design, scalability, microservices patterns
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Code review best practices, PR workflow
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Deployment, CI/CD, containerization, Kubernetes
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database design, SQL optimization, Prisma/Drizzle

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about frontend development, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best frontend framework for [use case]?"
- "What should I use for [state management/routing/styling]?"
- "What's the latest in React/Next.js/Vue?"
- "Current best practices for [SSR/RSC/hydration]?"
- "Is [framework/library] still relevant in 2026?"
- "[Next.js] vs [Remix] vs [Nuxt]?"
- "Best component library for [framework]?"

### Required Searches

1. Search: `"frontend development best practices 2026"`
2. Search: `"[React/Next.js/Vue] updates January 2026"`
3. Search: `"frontend framework comparison 2026"`
4. Search: `"[specific library] vs alternatives 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What frameworks/libraries are popular NOW
- **Emerging trends**: New patterns or tools gaining traction
- **Deprecated/declining**: Approaches that are losing relevance
- **Recommendation**: Based on fresh data and recent releases

### Example Topics (verify with fresh search)

- React 19 features and adoption
- Next.js 15/16 updates and App Router patterns
- Vue 3 Composition API vs Options API
- Server Components and streaming SSR
- Tailwind CSS v4 and styling trends
- Component libraries (shadcn/ui, Radix, Ark UI)

---

## Operational Playbooks
- [references/operational-playbook.md](references/operational-playbook.md) — Framework-specific architecture patterns, TypeScript guides, and security/performance checklists
