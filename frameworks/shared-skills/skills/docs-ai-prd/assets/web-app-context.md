# Web Application CLAUDE.md Template

Template for frontend web applications (React, Vue, Angular, Svelte).

---

```markdown
# [Project Name]

[One-line description of the web application]

## Tech Stack

- **Framework**: [Next.js 16 / React 19 / Vue 3 / Angular 17 / Svelte 5]
- **Language**: TypeScript [version]
- **Styling**: [Tailwind CSS / CSS Modules / styled-components / Emotion]
- **UI Library**: [shadcn/ui / Material UI / Chakra / Radix / None]
- **State Management**: [Zustand / Redux / Recoil / Pinia / None]
- **Data Fetching**: [TanStack Query / SWR / Apollo Client / tRPC]
- **Form Handling**: [React Hook Form / Formik / Zod]
- **Testing**: [Vitest / Jest / Playwright / Cypress]

## Architecture

[2-3 sentences describing the frontend architecture approach]

### Directory Structure

```
src/
├── app/                  # Next.js App Router / Pages
│   ├── (auth)/           # Auth-related routes
│   ├── (dashboard)/      # Dashboard routes
│   └── api/              # API routes (if applicable)
├── components/
│   ├── ui/               # Reusable UI components
│   ├── forms/            # Form components
│   └── layouts/          # Layout components
├── lib/                  # Utilities, helpers
│   ├── api/              # API client
│   ├── hooks/            # Custom hooks
│   └── utils/            # Helper functions
├── stores/               # State management
├── types/                # TypeScript types
└── styles/               # Global styles
```

### Rendering Strategy

- **SSR Pages**: [List pages with server-side rendering]
- **SSG Pages**: [List statically generated pages]
- **CSR Pages**: [List client-side only pages]
- **ISR Config**: [Revalidation intervals]

### Data Flow

```
User Action → Event Handler → API Call / State Update
                                      ↓
                              Server Response
                                      ↓
                           State Update → Re-render
```

## Conventions

### Component Structure

```typescript
// Standard component structure
export function ComponentName({ prop1, prop2 }: ComponentProps) {
  // 1. Hooks
  const [state, setState] = useState();
  const { data } = useQuery();

  // 2. Derived state / computations
  const computed = useMemo(() => {}, []);

  // 3. Effects
  useEffect(() => {}, []);

  // 4. Event handlers
  const handleClick = () => {};

  // 5. Render
  return <div>...</div>;
}
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Hooks | camelCase with `use` | `useAuth.ts` |
| Utilities | camelCase | `formatDate.ts` |
| Types | PascalCase | `UserProfile.ts` |
| Constants | SCREAMING_SNAKE | `API_ENDPOINTS.ts` |
| CSS Modules | camelCase | `styles.module.css` |

### File Organization

- One component per file
- Co-locate tests: `Component.test.tsx`
- Co-locate styles: `Component.module.css`
- Barrel exports via `index.ts`

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| App entry | `src/app/layout.tsx` | Root layout |
| Global styles | `src/styles/globals.css` | Tailwind + custom |
| API client | `src/lib/api/client.ts` | Axios/fetch wrapper |
| Auth config | `src/lib/auth/index.ts` | Auth provider |
| Theme | `src/lib/theme/index.ts` | Theme configuration |
| Routes | `src/app/` | File-based routing |

## State Management

### Global State (Zustand)

```typescript
// src/stores/user.ts
export const useUserStore = create<UserState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
```

### Server State (TanStack Query)

```typescript
// src/lib/hooks/useUsers.ts
export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => api.get('/users'),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

## Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Production build
npm run start            # Start production server

# Testing
npm run test             # Run unit tests
npm run test:e2e         # Run E2E tests
npm run test:coverage    # Coverage report

# Quality
npm run lint             # ESLint
npm run typecheck        # TypeScript check
npm run format           # Prettier
```

## Important Context

### Performance Considerations

- Images: Use `next/image` with proper sizing
- Fonts: Use `next/font` for optimization
- Bundle: Check bundle size with `npm run analyze`
- Hydration: Avoid hydration mismatches

### Known Gotchas

- **[Component]**: [Non-obvious behavior]
- **[Hook]**: [Edge case to handle]
- **[API]**: [Rate limit or quirk]

### Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## For AI Assistants

### When modifying this codebase:

- Use existing UI components from `src/components/ui/`
- Follow the component structure pattern above
- Add types for all props and state
- Run `npm run typecheck` before committing

### Patterns to follow:

- Server Components by default, Client Components when needed
- Optimistic updates for mutations
- Error boundaries for error handling
- Suspense for loading states

### Avoid:

- Direct DOM manipulation
- Inline styles (use Tailwind classes)
- `any` types
- Console.log in production
```

---

## Quick Start Commands

```bash
# Project structure
tree -L 3 -I 'node_modules|.next|dist|.git'

# Check framework
cat package.json | jq '.dependencies' | grep -E "next|react|vue|angular|svelte"

# Find components
find src -name "*.tsx" | head -30

# Check routing
ls -la src/app/ 2>/dev/null || ls -la src/pages/
```
