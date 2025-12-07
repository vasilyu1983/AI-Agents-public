---
name: software-frontend
description: Production-grade frontend development with Next.js 16 App Router, TypeScript 5.9+ strict mode, Tailwind CSS v4, shadcn/ui, React 19.2 Server Components, state management (Zustand/Recoil), performance optimization (Turbopack stable, ISR/SSR/SSG), and accessibility best practices. Includes TanStack Query for server-state, Vitest for testing, and modern React patterns.
---

# Frontend Engineering Skill — Quick Reference

This skill equips frontend engineers with execution-ready patterns for building modern web applications with Next.js 16, React 19, TypeScript, and Tailwind CSS. Claude should apply these patterns when users ask for component design, state management, routing, forms, data fetching, animations, accessibility, or production-grade UI architectures.

**Modern Best Practices (December 2025)**: Next.js 16 with Turbopack (stable, default bundler), React 19.2 with Server Components, Actions, Activity component, and useEffectEvent hook, enhanced ISR/SSR/SSG, partial prerendering (PPR), Zustand/Recoil as Redux alternatives, TanStack Query (React Query) for server-state, TypeScript 5.9+ strict mode enforcement (TypeScript 7 "Corsa" Go-based compiler in preview), `satisfies` operator, Tailwind CSS v4 (CSS-first config, 5x faster builds), Vitest for testing, and progressive enhancement patterns.

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

Claude should invoke this skill when a user requests:

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
- Accessibility (WCAG 2.1, ARIA, keyboard navigation, screen reader testing)
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
    │   ├─ Global client state → Zustand (lightweight) or Recoil (React-first)
    │   ├─ Complex state logic → XState (state machines)
    │   └─ URL-based state → useSearchParams (shareable filters)
    │
    ├─ Styling approach?
    │   ├─ Utility-first → Tailwind CSS v4 (CSS-first config, 5x faster builds)
    │   ├─ CSS-in-JS → Styled Components or Emotion
    │   └─ CSS Modules → Built-in CSS Modules
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

See [resources/](resources/) for framework-specific best practices.

---

## Navigation

**Resources** (Framework-specific best practices)
- [resources/fullstack-patterns.md](resources/fullstack-patterns.md) — Universal patterns: Server vs client components, data fetching, TypeScript
- [resources/vue-nuxt-patterns.md](resources/vue-nuxt-patterns.md) — Vue 3 Composition API, Nuxt 3, Pinia state management
- [resources/angular-patterns.md](resources/angular-patterns.md) — Angular 18 standalone components, signals, RxJS patterns
- [resources/svelte-sveltekit-patterns.md](resources/svelte-sveltekit-patterns.md) — Svelte 5 runes, SvelteKit loaders/actions
- [resources/remix-react-patterns.md](resources/remix-react-patterns.md) — Remix loaders, actions, progressive enhancement
- [resources/vite-react-patterns.md](resources/vite-react-patterns.md) — Vite setup, React hooks, TanStack Query
- [resources/artifacts-builder.md](resources/artifacts-builder.md) — React/Tailwind/shadcn artifact workflow and bundling to single HTML
- [README.md](README.md) — Folder overview and usage notes
- [data/sources.json](data/sources.json) — 106 curated resources for all frameworks (Next.js, Vue/Nuxt, Angular, Svelte, Remix, Vite)

**Shared Utilities** (Centralized patterns — extract, don't duplicate)
- [../_shared/utilities/error-handling.md](../_shared/utilities/error-handling.md) — Effect Result types, correlation IDs
- [../_shared/utilities/config-validation.md](../_shared/utilities/config-validation.md) — Zod 3.24+, Valibot for client validation
- [../_shared/utilities/logging-utilities.md](../_shared/utilities/logging-utilities.md) — Structured logging patterns
- [../_shared/utilities/testing-utilities.md](../_shared/utilities/testing-utilities.md) — Vitest, MSW v2, factories, fixtures
- [../_shared/utilities/observability-utilities.md](../_shared/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics
- [../_shared/resources/code-quality-operational-playbook.md](../_shared/resources/code-quality-operational-playbook.md) — Canonical coding rules & review protocols

**Templates** (Production-ready starters by framework)
- **Next.js**: [templates/nextjs/template-nextjs-tailwind-shadcn.md](templates/nextjs/template-nextjs-tailwind-shadcn.md)
- **Vue/Nuxt**: [templates/vue-nuxt/template-nuxt3-tailwind.md](templates/vue-nuxt/template-nuxt3-tailwind.md)
- **Angular**: [templates/angular/template-angular18-standalone.md](templates/angular/template-angular18-standalone.md)
- **Svelte/SvelteKit**: [templates/svelte/template-sveltekit-runes.md](templates/svelte/template-sveltekit-runes.md)
- **Remix**: [templates/remix/template-remix-react.md](templates/remix/template-remix-react.md)
- **Vite + React**: [templates/vite-react/template-vite-react-ts.md](templates/vite-react/template-vite-react-ts.md)

**Related Skills**
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — REST/GraphQL API patterns, OpenAPI, versioning
- [../git-workflow/SKILL.md](../git-workflow/SKILL.md) — Git branching, PR workflow, commit conventions
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — Backend API development, Node.js, Prisma, authentication
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design, scalability, microservices patterns
- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Code review best practices, PR workflow
- [../ai-llm/SKILL.md](../ai-llm/SKILL.md) — AI-powered features, LLM integration patterns
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Deployment, CI/CD, containerization, Kubernetes
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database design, SQL optimization, Prisma/Drizzle

---

## Operational Playbooks
- [resources/operational-playbook.md](resources/operational-playbook.md) — Framework-specific architecture patterns, TypeScript guides, and security/performance checklists
