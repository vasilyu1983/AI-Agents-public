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
