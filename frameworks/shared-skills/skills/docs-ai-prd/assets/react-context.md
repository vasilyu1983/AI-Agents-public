# React / Next.js CLAUDE.md Template

Copy and customize for React or Next.js projects.

---

```markdown
# [Project Name]

[One-line description of what this project does]

## Tech Stack

- **Framework**: [Next.js 16 / React 19 / Remix / Vite + React]
- **Language**: TypeScript [version]
- **Styling**: [Tailwind CSS / CSS Modules / styled-components / Emotion]
- **State**: [Zustand / Redux Toolkit / Jotai / React Query / Context]
- **Data Fetching**: [React Query / SWR / tRPC / Server Actions]
- **Forms**: [React Hook Form / Formik] + [Zod / Yup]
- **UI Components**: [shadcn/ui / Radix / Headless UI / MUI]
- **Testing**: [Vitest / Jest] + [Testing Library / Playwright]

## Architecture

[2-3 sentences describing the overall design approach]

### Directory Structure (Next.js App Router)

```
src/
├── app/                      # App Router pages
│   ├── (auth)/               # Route group: auth pages
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/          # Route group: authenticated
│   │   ├── layout.tsx
│   │   └── settings/
│   ├── api/                  # API routes
│   │   └── users/
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home page
│   └── globals.css
├── components/               # Shared components
│   ├── ui/                   # Base UI components (buttons, inputs)
│   ├── forms/                # Form components
│   ├── layouts/              # Layout components
│   └── features/             # Feature-specific components
├── lib/                      # Utilities and configurations
│   ├── api.ts                # API client
│   ├── auth.ts               # Auth utilities
│   └── utils.ts              # Helper functions
├── hooks/                    # Custom React hooks
├── stores/                   # State management (Zustand)
├── types/                    # TypeScript types
└── styles/                   # Global styles (if not using Tailwind)
```

### Alternative: Pages Router / Vite

```
src/
├── pages/                    # Page components (Pages Router)
├── components/
├── features/                 # Feature-based organization
│   └── users/
│       ├── components/
│       ├── hooks/
│       ├── api.ts
│       └── types.ts
├── lib/
├── hooks/
└── stores/
```

### Key Patterns

- **Server Components**: Default for data fetching, use `'use client'` for interactivity
- **Colocation**: Keep related files together (component + styles + tests)
- **Composition**: Small, composable components over large monolithic ones
- **Custom Hooks**: Extract reusable logic into hooks

### Data Flow

```
Server Component → fetch data → pass to Client Component as props
                                        ↓
Client Component → useState/useStore → UI updates
                                        ↓
User action → Server Action / API call → revalidate → refresh
```

## Conventions

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Hooks | camelCase + use prefix | `useUserData.ts` |
| Utilities | camelCase | `formatDate.ts` |
| Types | PascalCase | `UserProfileProps` |
| Constants | SCREAMING_SNAKE | `MAX_FILE_SIZE` |
| CSS classes | kebab-case (BEM optional) | `user-profile__avatar` |

### Component Structure

```tsx
// 1. Imports (external → internal → relative → types)
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { formatDate } from '@/lib/utils';
import type { User } from '@/types';

// 2. Types
interface UserCardProps {
  user: User;
  onEdit?: () => void;
}

// 3. Component
export function UserCard({ user, onEdit }: UserCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="user-card">
      {/* JSX */}
    </div>
  );
}

// 4. Sub-components (if small and tightly coupled)
function UserAvatar({ src }: { src: string }) {
  return <img src={src} alt="" className="avatar" />;
}
```

### File Organization

- One component per file (except small sub-components)
- Barrel exports via `index.ts` in component directories
- Tests co-located as `ComponentName.test.tsx`
- Styles co-located as `ComponentName.module.css` (if using CSS Modules)

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Root layout | `src/app/layout.tsx` | HTML structure, providers |
| Home page | `src/app/page.tsx` | Landing page |
| API routes | `src/app/api/` | Backend endpoints |
| UI components | `src/components/ui/` | shadcn/ui or custom |
| API client | `src/lib/api.ts` | fetch wrapper |
| Auth | `src/lib/auth.ts` | NextAuth / custom |
| Global styles | `src/app/globals.css` | Tailwind base |
| Tailwind config | `tailwind.config.ts` | Theme, plugins |
| Types | `src/types/index.ts` | Shared type definitions |

## Configuration

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Server-only (no NEXT_PUBLIC_ prefix)
DATABASE_URL=postgresql://...
NEXTAUTH_SECRET=your-secret
NEXTAUTH_URL=http://localhost:3000
```

### Next.js Config

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['cdn.example.com'],
  },
  experimental: {
    serverActions: true,
  },
};
```

## Commands

```bash
# Development
npm run dev              # Start dev server (localhost:3000)
npm run build            # Production build
npm start                # Start production server
npm run lint             # ESLint
npm run lint:fix         # Auto-fix lint issues

# Testing
npm test                 # Run tests
npm run test:watch       # Watch mode
npm run test:coverage    # With coverage
npm run test:e2e         # Playwright E2E tests

# Type checking
npm run typecheck        # tsc --noEmit

# Storybook (if used)
npm run storybook        # Start Storybook
npm run build-storybook  # Build static Storybook
```

## Important Context

### Technical Decisions

#### [Why App Router over Pages Router]
**Context**: Starting new Next.js 16 project
**Decision**: App Router for Server Components and better data fetching
**Trade-off**: Steeper learning curve, some ecosystem packages not updated

#### [Why Zustand over Redux]
**Context**: Need simple global state
**Decision**: Zustand for minimal boilerplate and hooks-based API
**Trade-off**: Less middleware ecosystem than Redux

### Known Gotchas

- **Server vs Client Components**: Default is server; add `'use client'` for hooks/interactivity
- **Hydration errors**: Ensure server and client render the same initial content
- **Image optimization**: Use `next/image` for automatic optimization, configure domains
- **API routes caching**: Next.js caches by default, use `export const dynamic = 'force-dynamic'`
- **Tailwind purge**: Ensure all class names are complete strings (not dynamic)

### Historical Context

- [Any migrations, refactors, or legacy patterns to know about]

## Component Patterns

### Server Component (default)

```tsx
// app/users/page.tsx
async function UsersPage() {
  const users = await fetchUsers(); // Direct async fetch

  return <UserList users={users} />;
}
```

### Client Component

```tsx
// components/UserForm.tsx
'use client';

import { useState } from 'react';

export function UserForm() {
  const [name, setName] = useState('');
  // Interactive logic
}
```

### Server Action

```tsx
// app/actions.ts
'use server';

export async function createUser(formData: FormData) {
  const name = formData.get('name');
  await db.user.create({ data: { name } });
  revalidatePath('/users');
}
```

## Testing

### Component Test

```tsx
// components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('calls onClick when clicked', async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click me</Button>);

    await userEvent.click(screen.getByRole('button'));

    expect(onClick).toHaveBeenCalledOnce();
  });
});
```

## For AI Assistants

### When modifying this codebase:

- Check if component should be Server or Client
- Use existing UI components from `components/ui/`
- Follow Tailwind utility class patterns
- Add types for all props and state
- Run `npm run lint && npm run typecheck` before committing

### Patterns to follow:

- Server Components for data fetching
- Client Components only when needed (hooks, events)
- Composition over prop drilling
- Custom hooks for reusable logic
- Zod schemas for form validation

### Avoid:

- `useEffect` for data fetching (use Server Components or React Query)
- Inline styles (use Tailwind)
- Large monolithic components
- Direct DOM manipulation
- `any` type
```

---

## Quick Start Commands

Run these to gather context for a new React/Next.js project:

```bash
# Basic structure
tree -L 3 -I 'node_modules|.next|.git|coverage|.turbo'

# Package info
cat package.json | jq '{dependencies, devDependencies}'

# Next.js or Vite config
cat next.config.js 2>/dev/null || cat vite.config.ts 2>/dev/null

# Check for App Router vs Pages Router
ls src/app 2>/dev/null && echo "App Router" || ls src/pages 2>/dev/null && echo "Pages Router"

# Find components
find src/components -name "*.tsx" | head -20

# Check styling approach
cat tailwind.config.* 2>/dev/null && echo "Tailwind detected"
find src -name "*.module.css" | head -5 && echo "CSS Modules detected"
```
