---
name: software-frontend
description: "Production-grade frontend for Next.js, Vue, Angular, and Svelte. Use when building UI, fixing hydration errors, or setting up a new web project."
---

# Frontend Engineering

Production-ready patterns for modern web applications.

**Stack (March 2026)**: Next.js 16 + Turbopack, React 19.x + Server Components, TypeScript 5.9+ (strict), Tailwind CSS v4, TanStack Query, Zustand, Vitest (browser mode).

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

## Next.js 16 Key Changes

### proxy.ts replaces middleware.ts

```bash
npx @next/codemod@canary upgrade latest   # recommended
mv middleware.ts proxy.ts                  # or manual rename
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
  experimental: { reactCompiler: true },
};
```

For the full migration checklist (async APIs, image config, parallel routes, caching APIs), see `references/operational-playbook.md` (Next.js 16 Migration Checklist section).

## Performance Budgets

| Metric | Target |
|--------|--------|
| LCP | <= 2.5s |
| INP | <= 200ms |
| CLS | <= 0.1 |
| TTFB | < 600ms |

## Operational Discipline

### Verification Order

1. Lint edited files only.
2. Type-check edited feature surface.
3. Run full project lint/type/build once before handoff.

Avoid repeated full builds while known local lint/type failures remain.

### Watch For

- **Lint pitfalls**: `react-hooks/set-state-in-effect`, `react-hooks/purity`, `react-hooks/rules-of-hooks`, `react/no-unescaped-entities`
- **CLI drift**: Run `npx eslint --help` / `npx vitest --help` before assuming flags from older setups
- **Route deletion**: After deleting/renaming any page, grep for stale imports and `<Link>` hrefs
- **Architecture pre-check**: Before adding new context providers or state stores, search for existing patterns first
- **Hydration mismatches**: Use `useState(null) + useEffect` for browser-only values — see `references/production-gotchas.md`
- **macOS Turbopack**: Set `ulimit -n 10240` to avoid EMFILE errors in large projects

### Handoff Requirements

Include in final output: exact files changed, lint/type/build commands run, whether failures are new or baseline, one prevention note for any repeated class of issue.

## Deployment Checklist

### Pre-Deployment

- [ ] `npm run build` — no errors
- [ ] `npm run lint` — zero ESLint errors
- [ ] `vitest run` — all tests passing
- [ ] Bundle size within budget
- [ ] Environment variables set

### Accessibility

- [ ] axe DevTools — zero critical issues
- [ ] Keyboard navigation works
- [ ] Color contrast >= 4.5:1
- [ ] Screen reader tested

### SEO

- [ ] Metadata configured
- [ ] sitemap.xml generated
- [ ] robots.txt configured

## Reference Routing

Read **only** the reference matching the user's framework or problem — not all of them.

| User's topic | Read this |
|---|---|
| Next.js, RSC, Server Actions, data fetching | `references/fullstack-patterns.md` (see section index below) |
| Next.js migration, upgrade, breaking changes | `references/operational-playbook.md` |
| Hydration bugs, storage access, response parsing | `references/production-gotchas.md` |
| Vue 3, Nuxt 4, Pinia, composables | `references/vue-nuxt-patterns.md` |
| Angular, signals, standalone components | `references/angular-patterns.md` |
| Svelte 5, SvelteKit, runes | `references/svelte-sveltekit-patterns.md` |
| Remix, loaders, actions, progressive enhancement | `references/remix-react-patterns.md` |
| Vite + React SPA (no Next.js / no SSR) | `references/vite-react-patterns.md` |
| State management (Zustand, TanStack Query, Redux) | `references/state-management-patterns.md` |
| Testing (Vitest, Testing Library, Playwright, MSW) | `references/testing-frontend-patterns.md` |
| Lighthouse, bundle size, Core Web Vitals | `references/performance-optimization.md` |
| Quick HTML prototype / artifact | `references/artifacts-builder.md` |

### fullstack-patterns.md Section Index

This file is 2044 lines. Read only the section you need:

| Section | Lines | When to read |
|---|---|---|
| Authentication (JWT, Zustand auth store) | 27–497 | Auth flow, protected routes, login forms |
| Blog Posts CRUD (Prisma, API routes, forms) | 499–1264 | CRUD features, list/detail pages, create forms |
| Real-time data with Server Components | 1266–1355 | Direct DB access in RSC, streaming |
| Server Actions for mutations | 1357–1627 | Form submissions, `"use server"`, revalidation |
| tRPC end-to-end type safety | 1629–2020 | tRPC setup, type-safe API clients |
| Key patterns summary | 1992–2044 | Quick reference for type sharing, validation |

## Templates

| Framework | Template |
|-----------|----------|
| Next.js | [assets/nextjs/template-nextjs-tailwind-shadcn.md](assets/nextjs/template-nextjs-tailwind-shadcn.md) |
| Vue/Nuxt | [assets/vue-nuxt/template-nuxt4-tailwind.md](assets/vue-nuxt/template-nuxt4-tailwind.md) |
| Angular | [assets/angular/template-angular21-standalone.md](assets/angular/template-angular21-standalone.md) |
| Svelte | [assets/svelte/template-sveltekit-runes.md](assets/svelte/template-sveltekit-runes.md) |
| Vite+React | [assets/vite-react/template-vite-react-ts.md](assets/vite-react/template-vite-react-ts.md) |
| Remix | [assets/remix/template-remix-react.md](assets/remix/template-remix-react.md) |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-backend](../software-backend/SKILL.md) | Backend API |
| [dev-api-design](../dev-api-design/SKILL.md) | REST/GraphQL |
| [software-code-review](../software-code-review/SKILL.md) | Code review |
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | CI/CD |

## Fact-Checking

Use web search to verify current external facts, versions, and platform behavior before final answers. Prefer primary sources; report source links and dates for volatile information.
