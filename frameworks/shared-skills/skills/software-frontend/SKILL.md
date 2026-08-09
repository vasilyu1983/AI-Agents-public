---
name: software-frontend
description: "Builds frontend applications across major web stacks. Use when implementing UI, fixing hydration or SSR issues, or setting up modern frontend architecture."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Frontend Engineering

Use this skill for production web frontend work across React, Next.js, Vue, Nuxt, Angular, Svelte, and adjacent tooling. It owns framework choice, frontend implementation patterns, hydration and SSR debugging, state and data-fetching patterns, and frontend release discipline.

## Quick Reference

| Task | Use |
|------|-----|
| Full-stack React app | [references/fullstack-patterns.md](references/fullstack-patterns.md), [assets/nextjs/template-nextjs-tailwind-shadcn.md](assets/nextjs/template-nextjs-tailwind-shadcn.md) |
| React SPA | [references/vite-react-patterns.md](references/vite-react-patterns.md), [assets/vite-react/template-vite-react-ts.md](assets/vite-react/template-vite-react-ts.md) |
| React Router or Remix | [references/remix-react-patterns.md](references/remix-react-patterns.md), [assets/remix/template-remix-react.md](assets/remix/template-remix-react.md) |
| Vue or Nuxt | [references/vue-nuxt-patterns.md](references/vue-nuxt-patterns.md), [assets/vue-nuxt/template-nuxt4-tailwind.md](assets/vue-nuxt/template-nuxt4-tailwind.md) |
| Angular | [references/angular-patterns.md](references/angular-patterns.md), [assets/angular/template-angular21-standalone.md](assets/angular/template-angular21-standalone.md) |
| Svelte or SvelteKit | [references/svelte-sveltekit-patterns.md](references/svelte-sveltekit-patterns.md), [assets/svelte/template-sveltekit-runes.md](assets/svelte/template-sveltekit-runes.md) |
| State, tests, performance, and gotchas | [references/state-management-patterns.md](references/state-management-patterns.md), [references/testing-frontend-patterns.md](references/testing-frontend-patterns.md), [references/performance-optimization.md](references/performance-optimization.md), [references/production-gotchas.md](references/production-gotchas.md), [references/operational-playbook.md](references/operational-playbook.md) |

## When to Use This Skill

- Build or scaffold a frontend app.
- Fix hydration, SSR, build, or client-server boundary issues.
- Choose routing, state, data-fetching, and component patterns.
- Set up frontend testing, performance budgets, and release gates.
- Implement UI in a modern framework with production-safe defaults.

## Route Elsewhere

- Backend APIs or service implementation: use [software-backend](../software-backend/SKILL.md).
- API contract design: use [dev-api-design](../dev-api-design/SKILL.md).
- UI or UX design work and accessibility audits: use [software-ui-ux-design](../software-ui-ux-design/SKILL.md) or [software-accessibility](../software-accessibility/SKILL.md).
- Mobile native development: use [software-mobile](../software-mobile/SKILL.md).
- Internationalization setup: use [software-localisation](../software-localisation/SKILL.md).
- E2E test-authoring focus: use [qa-testing-playwright](../qa-testing-playwright/SKILL.md).
- Natural conversational chat surfaces in a web app (Chrome `window.ai` built-in AI, WebLLM / transformers.js in-browser inference, cloud LLM streaming, with deterministic fallback when on-device unavailable): use [ai-context-layer/references/conversational-surfaces-cross-platform.md](../ai-context-layer/references/conversational-surfaces-cross-platform.md).

## Defaults

- Pick the framework that matches routing and rendering needs instead of defaulting blindly to one stack.
- Prefer the boring, already-adopted choice in the repo over the newest framework feature. A new primitive (a rendering mode, a compiler, a routing convention) earns adoption only after it has shipped stable for a while and the team has a concrete reason — not because it is new.
- Reuse an existing template before inventing project structure.
- Search for repo-local frontend patterns before adding new providers, stores, or conventions.
- Treat accessibility and performance as release gates.
- Verify framework-version-sensitive advice against current official docs before giving definitive recommendations — frontend tooling and framework majors move fast enough that any specific version number is provisional the moment it's written down.

## Workflow

1. Clarify rendering model, routing needs, SEO constraints, and deployment shape.
2. Pick the framework and template that fit the problem.
3. Load only the reference that matches the user’s framework or issue.
4. Implement with repo-local patterns for state, data fetching, styling, and testing.
5. Check hydration, accessibility, performance, and handoff requirements before signoff.

## ASCII Flow

```text
Frontend task
  -> Identify surface, framework, state, data, and user flow
  -> Reuse existing components, design tokens, and routing patterns
  -> Implement UI states: loading, empty, error, offline, success
  -> Add accessibility, performance, and localization checks
  -> Test with unit, component, integration, or browser proof
  -> Report changed behavior and remaining risk
```

## Core Decisions

### Framework Selection

| Need | Framework | Notes |
|------|-----------|-------|
| Full-stack React, SEO | Next.js | App Router; RSC for server components; current major is 16.x — re-check before pinning a minor |
| Route-centric progressive enhancement | React Router (v7 framework mode, or v8) | Loader/action data contracts. React Router v8 shipped in 2026 and folded in the Remix brand; Remix v2 and React Router v6 are now EOL (no more security fixes) — migrate legacy Remix v2 apps to React Router framework mode rather than starting new Remix v2 projects |
| Client-only React SPA | Vite + React | No SSR complexity |
| Vue full-stack | Nuxt | Auto-imports, server routes; Vue 3.6's Vapor mode (no virtual DOM) is feature-complete but still stabilizing — treat as opt-in, not default, until the ecosystem (Nuxt/Pinia/VueUse) fully catches up |
| Angular app | Angular 22 (current, released Jun 2026) | Standalone components, signal-first, zoneless stable and default; Angular 21 in LTS. Re-verify the exact current major against angular.dev/reference/releases — Angular ships a new major roughly every 6 months |
| Svelte-first | SvelteKit | Runes-based reactivity (Svelte 5, actively maintained; no Svelte 6 as of this writing) |

Pick the rendering model first (CSR / SSR / SSG / hybrid), then the framework. When two frameworks both fit, default to the one the team already runs in production — introducing a second framework has a real ongoing cost (build tooling, testing setup, hiring, mental context-switching) that rarely pays for itself on a single feature.

### Server vs. Client Rendering Judgment

- Default to server rendering (RSC, SSR, or SSG) for anything that is primarily content, SEO-sensitive, or benefits from a fast first paint without shipping a client-side data-fetch waterfall.
- Reach for client-side rendering deliberately: highly interactive widgets, apps behind auth where SEO doesn't matter, or state that must survive without a round trip (drag-and-drop, canvas/WebGL, real-time collaboration).
- Every client component has a hydration cost: JS shipped, parsed, and executed before the component becomes interactive. Treat `'use client'` (or framework equivalent) as an opt-in cost, not a free escape hatch — push it as far down the tree as the interactivity actually requires, rather than marking whole route trees client-side because one child needs `onClick`.
- A component that only needs interactivity for a small piece (an accordion toggle, a tooltip) can usually stay server-rendered with a small client island around just that piece, instead of promoting the whole page to client-rendered.

### Design System vs. Component Library

- A component library (shadcn/ui, Radix, Angular Material, PrimeNG, Nuxt UI) supplies unopinionated or lightly-opinionated building blocks — buttons, dialogs, form controls — with accessibility and behavior handled, but visual language largely left to the consumer.
- A design system is a product decision: a documented, versioned set of tokens (color, spacing, type scale), usage rules, and often a component API layered on top of one or more component libraries. It exists to keep a product visually and behaviorally consistent across teams and time.
- Don't build a design system when a component library already solves the problem — that's usually over-engineering for a single app or small team. Do insist on a design system (or at least shared tokens) once multiple teams or products need to look and behave consistently, or once the same visual inconsistencies keep recurring across PRs.
- When a repo already has a design system, treat its component API as the source of truth over the underlying library's raw components — don't reach past the design system to Radix/shadcn primitives directly unless the design system has a real gap.

### State and Data Fetching

| Data kind | Default tool | Add this only when… |
|-----------|-------------|----------------------|
| Server state (async, cached) | TanStack Query, SWR, framework loaders | Never — one of these is always the right fit |
| Global client state (shared across routes) | Zustand, Jotai, or Pinia (Vue) | Local state and server-state tools are genuinely insufficient |
| Server-owned state in RSC apps | Server components + React cache | Client store is needed for interactive/optimistic UI only |
| URL-driven state (filters, pagination) | URL search params | Don't duplicate into a store |

Do not create new global state layers when local state or server-driven patterns are enough.

### Hydration and SSR Safety

Watch for:
- browser-only values during SSR
- client hooks in server components
- stale effect dependencies
- route and link drift after refactors

If the bug smells like hydration, start with [references/production-gotchas.md](references/production-gotchas.md).

### Release Discipline

Minimum release gate:

- [ ] Lint the edited files
- [ ] Type-check the changed surface (`tsc --noEmit` or equivalent)
- [ ] Run broader lint, type, and build once before handoff
- [ ] Accessibility gate: no new WCAG 2.2 AA violations (run axe-core or equivalent in CI). WCAG 2.2 is the current published version and is a strict superset of 2.1 AA, so targeting 2.2 also satisfies 2.1. Note for EU-facing products: as of mid-2026 the EAA's harmonized technical standard (EN 301 549) still formally cites WCAG 2.1 AA, not 2.2 — treat 2.1 AA as the legal floor and 2.2 AA as the engineering target
- [ ] Performance budget: LCP < 2.5s, CLS < 0.1, INP < 200ms on the user-facing path (thresholds unchanged as of mid-2026; INP is the hardest of the three to hit in practice and carries equal ranking weight with LCP/CLS)
- [ ] Hydration verified: no console errors in SSR/RSC pages after navigation
- [ ] AI-generated code checked for hook rule violations, semantic div soup, and missing ARIA roles

### AI-Generated Frontend Risk

Common AI-specific frontend failures:
- hooks rule violations
- client/server boundary confusion
- div soup and weak semantics
- stale closures and missing deps
- over-fetching in components
- weak keyboard and screen-reader behavior
- imports that don't exist in the project's actual dependency tree, or that exist but at a different version/API shape than the generated code assumes
- components that reinvent a pattern the repo already has (a second modal implementation, a parallel fetch wrapper) instead of matching the existing one

Treat these as expected defects to check for, not rare edge cases. Before accepting AI-generated frontend code, verify it against the real codebase, not just its own internal plausibility: confirm every import resolves in `package.json`/lockfile, confirm the component/hook API used matches the installed version (not a newer or older one the model was trained on), and confirm styling and data-fetching match repo-local conventions rather than introducing a second competing pattern.

## Output Modes

Default to one of these:

- Frontend implementation plan:
  framework, template, state, testing, and release gates.
- Issue diagnosis:
  likely frontend failure mode, affected layer, and fix path.
- Scaffold recommendation:
  framework choice, template, and rationale.
- Production hardening brief:
  hydration, performance, accessibility, and testing checklist.

## Known Traps

- Crossing server and client boundaries casually in SSR or RSC-capable stacks, then debugging hydration mismatches that were baked into the render model.
- Reading browser-only values during server render and assuming the framework will reconcile the difference safely.
- Introducing a new global store before checking whether local state plus server-state tools already cover the problem.
- Refactoring routes, links, or layout composition without validating SEO, navigation semantics, and preserved URL behavior.
- Accepting AI-generated component output that looks plausible but quietly regresses semantics, keyboard support, or hook correctness.

## Anti-Patterns

- Picking a framework because it is fashionable rather than because it matches the rendering model.
- Adding new state or context layers without checking existing patterns.
- Treating accessibility and performance as post-launch polish.
- Mixing browser-only behavior into SSR paths.
- Trusting AI-generated UI code without checking semantics and hooks discipline.

## Navigation

- Framework references: [references/fullstack-patterns.md](references/fullstack-patterns.md), [references/vite-react-patterns.md](references/vite-react-patterns.md), [references/remix-react-patterns.md](references/remix-react-patterns.md), [references/vue-nuxt-patterns.md](references/vue-nuxt-patterns.md), [references/angular-patterns.md](references/angular-patterns.md), [references/svelte-sveltekit-patterns.md](references/svelte-sveltekit-patterns.md)
- Operational references: [references/production-gotchas.md](references/production-gotchas.md), [references/operational-playbook.md](references/operational-playbook.md), [references/state-management-patterns.md](references/state-management-patterns.md), [references/testing-frontend-patterns.md](references/testing-frontend-patterns.md), [references/performance-optimization.md](references/performance-optimization.md), [references/web-platform-apis.md](references/web-platform-apis.md) (native browser APIs that replace JS libraries — 0 KB bundle cost), [references/artifacts-builder.md](references/artifacts-builder.md)
- Templates: [assets/nextjs/template-nextjs-tailwind-shadcn.md](assets/nextjs/template-nextjs-tailwind-shadcn.md), [assets/vite-react/template-vite-react-ts.md](assets/vite-react/template-vite-react-ts.md), [assets/remix/template-remix-react.md](assets/remix/template-remix-react.md), [assets/vue-nuxt/template-nuxt4-tailwind.md](assets/vue-nuxt/template-nuxt4-tailwind.md), [assets/angular/template-angular21-standalone.md](assets/angular/template-angular21-standalone.md), [assets/svelte/template-sveltekit-runes.md](assets/svelte/template-sveltekit-runes.md)
- Related skills: [software-backend](../software-backend/SKILL.md), [software-ui-ux-design](../software-ui-ux-design/SKILL.md), [software-localisation](../software-localisation/SKILL.md), [qa-testing-playwright](../qa-testing-playwright/SKILL.md), [ops-devops-platform](../ops-devops-platform/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Version-sensitive framework guidance should be checked against current official docs before making definitive claims.
- Source mapping lives in [data/sources.json](data/sources.json).
- When freshness cannot be verified, give durable architectural guidance and mark version-specific recommendations as provisional.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

