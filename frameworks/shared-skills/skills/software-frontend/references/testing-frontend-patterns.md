# Frontend Testing Patterns

Comprehensive testing patterns for modern frontend applications: testing pyramid, Vitest, Testing Library, component testing, visual regression, E2E with Playwright, and CI integration. Covers React/Next.js, Vue, and framework-agnostic patterns.

---

## Table of Contents

1. [Testing Pyramid for Frontend](#testing-pyramid-for-frontend)
2. [Vitest Patterns](#vitest-patterns)
3. [Testing Library Patterns](#testing-library-patterns)
4. [Component Testing](#component-testing)
5. [Visual Regression Testing](#visual-regression-testing)
6. [E2E with Playwright](#e2e-with-playwright)
7. [Testing Server Components and RSC](#testing-server-components-and-rsc)
8. [CI Integration and Performance](#ci-integration-and-performance)
9. [Anti-Patterns](#anti-patterns)

---

## Testing Pyramid for Frontend

### Recommended Distribution

```text
                    /\
                   /  \       E2E (Playwright)
                  / 5% \      Critical user flows only
                 /------\
                /        \    Integration (Component + API)
               /   15%    \   Feature-level tests with MSW
              /------------\
             /              \  Component (Testing Library)
            /     30%        \ Isolated components with props/events
           /------------------\
          /                    \ Unit (Vitest)
         /        50%           \ Pure functions, hooks, utilities
        /________________________\
```

### What to Test at Each Level

| Level | What to Test | Tools | Speed |
|-------|-------------|-------|-------|
| Unit | Utilities, formatters, validators, hooks | Vitest | < 1ms each |
| Component | Rendered output, user interactions, accessibility | Testing Library + Vitest | < 100ms each |
| Integration | Feature workflows, API integration (mocked) | Testing Library + MSW | < 500ms each |
| E2E | Critical user paths, cross-page flows | Playwright | 2-10s each |
| Visual | UI appearance, layout, responsive design | Chromatic / Playwright screenshots | 5-30s each |

---

## Vitest Patterns

### Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: 'jsdom',        // or 'happy-dom' (faster)
    globals: true,               // describe, it, expect globally available
    setupFiles: ['./tests/setup.ts'],
    css: true,                   // Process CSS imports
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
});
```

### Test Setup File

```typescript
// tests/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';
import { server } from './mocks/server';

// MSW server setup
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => {
  server.resetHandlers();
  cleanup();
});
afterAll(() => server.close());

// Mock IntersectionObserver
const IntersectionObserverMock = vi.fn(() => ({
  disconnect: vi.fn(),
  observe: vi.fn(),
  unobserve: vi.fn(),
}));
vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

### Mocking

```typescript
// Mock modules
vi.mock('@/lib/api', () => ({
  fetchUsers: vi.fn(),
  createUser: vi.fn(),
}));

// Mock with implementation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    refresh: vi.fn(),
    back: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/test',
}));

// Spy on module functions
import { fetchUsers } from '@/lib/api';
const fetchUsersMock = vi.mocked(fetchUsers);
fetchUsersMock.mockResolvedValue([{ id: '1', name: 'Test User' }]);
```

### Snapshot Testing

```typescript
// Use sparingly -- snapshots are brittle for UI components
// Good for: serializable data structures, error messages

it('should generate correct config', () => {
  const config = generateConfig({ env: 'production' });
  expect(config).toMatchInlineSnapshot(`
    {
      "apiUrl": "https://api.example.com",
      "debug": false,
    }
  `);
});

// BAD: Snapshot of entire component tree (breaks on any change)
// GOOD: Snapshot of specific computed values
```

### Testing Hooks

```typescript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from '@/hooks/useCounter';

it('should increment counter', () => {
  const { result } = renderHook(() => useCounter(0));

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});

// Testing hooks with providers
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

it('should fetch user data', async () => {
  const { result } = renderHook(() => useUser('1'), {
    wrapper: createWrapper(),
  });

  await waitFor(() => {
    expect(result.current.data).toBeDefined();
  });
});
```

---

## Testing Library Patterns

### Query Priority

Use queries in this order of priority (most accessible first):

| Priority | Query | When to Use |
|----------|-------|-------------|
| 1 | `getByRole` | Interactive elements (button, link, textbox) |
| 2 | `getByLabelText` | Form fields with labels |
| 3 | `getByPlaceholderText` | When label is absent (avoid this pattern) |
| 4 | `getByText` | Static text content |
| 5 | `getByDisplayValue` | Current value of form elements |
| 6 | `getByAltText` | Images |
| 7 | `getByTestId` | Last resort only |

```typescript
// GOOD: Query by accessible role
screen.getByRole('button', { name: 'Submit' });
screen.getByRole('heading', { level: 1 });
screen.getByRole('textbox', { name: 'Email' });
screen.getByRole('link', { name: 'Learn more' });

// AVOID: Query by test ID (not accessible, breaks if refactored)
screen.getByTestId('submit-button');
```

### User Events (Preferred over fireEvent)

```typescript
import userEvent from '@testing-library/user-event';

it('should submit the form', async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();

  render(<LoginForm onSubmit={onSubmit} />);

  // Type into fields (simulates real keyboard input)
  await user.type(
    screen.getByRole('textbox', { name: 'Email' }),
    'test@example.com'
  );
  await user.type(
    screen.getByLabelText('Password'),
    'password123'
  );

  // Click submit
  await user.click(screen.getByRole('button', { name: 'Log in' }));

  expect(onSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123',
  });
});
```

### Async Patterns

```typescript
// waitFor: poll until assertion passes
await waitFor(() => {
  expect(screen.getByText('User loaded')).toBeInTheDocument();
});

// findBy: shorthand for waitFor + getBy
const element = await screen.findByText('User loaded');

// waitForElementToBeRemoved
await waitForElementToBeRemoved(() =>
  screen.queryByText('Loading...')
);
```

### Accessibility Assertions

```typescript
import { axe } from 'jest-axe';

it('should have no accessibility violations', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});

// Specific a11y checks
it('should have proper ARIA attributes', () => {
  render(<Modal isOpen title="Confirm">Content</Modal>);

  const dialog = screen.getByRole('dialog');
  expect(dialog).toHaveAttribute('aria-label', 'Confirm');
  expect(dialog).toHaveAttribute('aria-modal', 'true');
});
```

---

## Component Testing

### Isolated Component Testing

```typescript
// Test component in isolation with controlled props
import { render, screen } from '@testing-library/react';
import { UserCard } from '@/components/UserCard';

const mockUser = {
  id: '1',
  name: 'Jane Doe',
  email: 'jane@example.com',
  role: 'admin' as const,
};

describe('UserCard', () => {
  it('renders user information', () => {
    render(<UserCard user={mockUser} />);

    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
  });

  it('shows edit button for admin users', () => {
    render(<UserCard user={mockUser} canEdit />);

    expect(screen.getByRole('button', { name: 'Edit' })).toBeInTheDocument();
  });

  it('hides edit button for non-admin', () => {
    render(<UserCard user={{ ...mockUser, role: 'user' }} canEdit={false} />);

    expect(screen.queryByRole('button', { name: 'Edit' })).not.toBeInTheDocument();
  });
});
```

### Provider Wrappers

```typescript
// Create a reusable wrapper for tests that need providers
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/components/theme-provider';

function createTestWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });

  return function TestWrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <ThemeProvider defaultTheme="light">
          {children}
        </ThemeProvider>
      </QueryClientProvider>
    );
  };
}

// Usage
render(<MyComponent />, { wrapper: createTestWrapper() });
```

### MSW for API Mocking

```typescript
// tests/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'Alice' },
      { id: '2', name: 'Bob' },
    ]);
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { id: '3', ...body },
      { status: 201 }
    );
  }),

  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'Test User',
    });
  }),
];

// tests/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// Override handlers in specific tests
it('handles server error', async () => {
  server.use(
    http.get('/api/users', () => {
      return HttpResponse.json(
        { error: 'Internal Server Error' },
        { status: 500 }
      );
    })
  );

  render(<UserList />);

  await screen.findByText('Error loading users');
});
```

---

## Visual Regression Testing

### Chromatic (Storybook-based)

```typescript
// Component story for visual testing
// components/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  component: Button,
};
export default meta;

type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: { variant: 'primary', children: 'Click me' },
};

export const Disabled: Story = {
  args: { variant: 'primary', children: 'Disabled', disabled: true },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '8px' }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
    </div>
  ),
};
```

```bash
# Run Chromatic visual tests
npx chromatic --project-token=<TOKEN>
```

### Playwright Screenshots

```typescript
// Visual regression with Playwright
import { test, expect } from '@playwright/test';

test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100,    // Allow minor differences
    threshold: 0.2,         // Per-pixel threshold
  });
});

test('responsive layout', async ({ page }) => {
  await page.goto('/');

  // Desktop
  await page.setViewportSize({ width: 1280, height: 720 });
  await expect(page).toHaveScreenshot('homepage-desktop.png');

  // Tablet
  await page.setViewportSize({ width: 768, height: 1024 });
  await expect(page).toHaveScreenshot('homepage-tablet.png');

  // Mobile
  await page.setViewportSize({ width: 375, height: 667 });
  await expect(page).toHaveScreenshot('homepage-mobile.png');
});
```

---

## E2E with Playwright

### Page Objects Pattern

```typescript
// tests/pages/LoginPage.ts
import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByRole('textbox', { name: 'Email' });
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Log in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

### Fixtures

```typescript
// tests/fixtures.ts
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';

type Fixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  authenticatedPage: Page;
};

export const test = base.extend<Fixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  authenticatedPage: async ({ page }, use) => {
    // Pre-authenticate
    await page.goto('/login');
    await page.getByRole('textbox', { name: 'Email' }).fill('test@test.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Log in' }).click();
    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

### Network Interception

```typescript
test('handles API errors gracefully', async ({ page }) => {
  // Intercept API and return error
  await page.route('/api/users', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' }),
    })
  );

  await page.goto('/users');
  await expect(page.getByText('Error loading users')).toBeVisible();
});

test('displays loading state', async ({ page }) => {
  // Delay API response
  await page.route('/api/users', async (route) => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify([{ id: '1', name: 'User' }]),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Loading...')).toBeVisible();
  await expect(page.getByText('User')).toBeVisible();
});
```

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Testing Server Components and RSC

### Server Component Testing

```typescript
// Server components run on the server -- test them as async functions
import { render, screen } from '@testing-library/react';
import UserProfile from '@/app/users/[id]/page';

// Mock the data fetching
vi.mock('@/lib/db/users', () => ({
  getUser: vi.fn().mockResolvedValue({
    id: '1',
    name: 'Test User',
    email: 'test@test.com',
  }),
}));

it('renders server component with data', async () => {
  // Server components are async -- await the render
  const component = await UserProfile({
    params: { id: '1' },
  });

  render(component);

  expect(screen.getByText('Test User')).toBeInTheDocument();
  expect(screen.getByText('test@test.com')).toBeInTheDocument();
});
```

### Testing Server Actions

```typescript
// Test server actions as regular async functions
import { createPost } from '@/app/actions/posts';

vi.mock('@/lib/db', () => ({
  prisma: {
    post: {
      create: vi.fn().mockResolvedValue({
        id: '1',
        title: 'Test Post',
      }),
    },
  },
}));

vi.mock('next/cache', () => ({
  revalidatePath: vi.fn(),
}));

vi.mock('next/navigation', () => ({
  redirect: vi.fn(),
}));

it('creates a post and redirects', async () => {
  const formData = new FormData();
  formData.set('title', 'Test Post');
  formData.set('content', 'Test content');

  await createPost(formData);

  expect(prisma.post.create).toHaveBeenCalledWith({
    data: expect.objectContaining({
      title: 'Test Post',
      content: 'Test content',
    }),
  });
});
```

---

## CI Integration and Performance

### GitHub Actions Pipeline

```yaml
# .github/workflows/test.yml
name: Test

on: [pull_request]

jobs:
  unit-and-component:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npx vitest run --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage/lcov.info

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

### Test Performance Tips

| Technique | Impact | How |
|-----------|--------|-----|
| Use `happy-dom` over `jsdom` | 2-3x faster | `environment: 'happy-dom'` in vitest config |
| Parallelize tests | Linear speedup | `vitest run --pool=threads` (default) |
| Mock heavy dependencies | 10-100x faster per test | Mock date-fns, lodash, image processing |
| Avoid full page renders | 5-10x faster | Test components in isolation |
| Use `vi.useFakeTimers()` | Eliminate `setTimeout` waits | Control time in tests |
| Split E2E into shards | Linear speedup | `npx playwright test --shard=1/4` |

---

## Anti-Patterns

### 1. Testing Implementation Details

**Problem**: Testing internal state, private methods, or specific DOM structure.

**Fix**: Test user-visible behavior. If the component shows "Hello, Jane" after loading, assert on that text, not on the state variable.

### 2. Snapshot Everything

**Problem**: Snapshot tests for complex components break on every CSS or text change, providing noise rather than signal.

**Fix**: Use snapshots for data structures. Use assertion-based tests for UI.

### 3. Mocking Everything

**Problem**: So many mocks that the test verifies the mocks, not the code.

**Fix**: Use MSW to mock at the network level. Let components, hooks, and utilities run with real logic.

### 4. No Test Isolation

**Problem**: Tests depend on each other or share mutable state.

**Fix**: Each test should set up its own state. Use `beforeEach` for cleanup, `afterEach` for teardown.

### 5. E2E for Everything

**Problem**: Running hundreds of E2E tests for every PR. Slow, flaky, expensive.

**Fix**: Reserve E2E for critical user flows (5-10 tests). Use component and integration tests for coverage.

---

## Cross-References

- [state-management-patterns.md](state-management-patterns.md) -- State management patterns to test
- [fullstack-patterns.md](fullstack-patterns.md) -- Server components and server actions
- [performance-optimization.md](performance-optimization.md) -- Performance testing strategies
- [../../software-clean-code-standard/utilities/testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) -- Shared testing utilities (MSW, factories)
- [../../software-code-review/SKILL.md](../../software-code-review/SKILL.md) -- Test review checklist
