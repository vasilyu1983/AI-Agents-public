# E2E Testing Template: Playwright

Use this template for end-to-end testing with Playwright for cross-browser automation.

## Why Playwright (2024-2025)

**Advantages**:
- Cross-browser support (Chromium, Firefox, WebKit)
- Auto-wait and retry mechanisms
- Parallel execution by default
- Network interception and mocking
- Multiple contexts (auth, sessions)
- Mobile device emulation
- Video/screenshot/trace recording

## Basic Test Structure

```typescript
// tests/checkout.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Navigate and authenticate
    await page.goto('/')
    await page.getByRole('button', { name: 'Sign In' }).click()
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByLabel('Password').fill('password123')
    await page.getByRole('button', { name: 'Login' }).click()
    await expect(page.getByText('Welcome back')).toBeVisible()
  })

  test('user can complete purchase', async ({ page }) => {
    // Add item to cart
    await page.goto('/products/laptop')
    await page.getByRole('button', { name: 'Add to Cart' }).click()
    await expect(page.getByTestId('cart-count')).toHaveText('1')

    // Go to checkout
    await page.getByRole('link', { name: 'Cart' }).click()
    await page.getByRole('button', { name: 'Proceed to Checkout' }).click()

    // Fill shipping info
    await page.getByLabel('Address').fill('123 Main St')
    await page.getByLabel('City').fill('San Francisco')
    await page.getByLabel('ZIP Code').fill('94102')
    await page.getByRole('button', { name: 'Continue' }).click()

    // Fill payment info
    await page.getByLabel('Card Number').fill('4242424242424242')
    await page.getByLabel('Expiry').fill('12/25')
    await page.getByLabel('CVV').fill('123')

    // Submit order
    await page.getByRole('button', { name: 'Place Order' }).click()

    // Verify success
    await expect(page.getByRole('heading', { name: 'Order Confirmed' })).toBeVisible()
    await expect(page.getByTestId('order-number')).toContainText('ORDER-')
  })

  test('should validate required fields', async ({ page }) => {
    await page.goto('/checkout')

    // Try to proceed without filling fields
    await page.getByRole('button', { name: 'Continue' }).click()

    // Expect validation errors
    await expect(page.getByText('Address is required')).toBeVisible()
    await expect(page.getByText('City is required')).toBeVisible()
  })
})
```

## Page Object Model (POM)

```typescript
// pages/checkout.page.ts
import { Page, Locator } from '@playwright/test'

export class CheckoutPage {
  readonly page: Page
  readonly addressInput: Locator
  readonly cityInput: Locator
  readonly zipInput: Locator
  readonly continueButton: Locator
  readonly cardNumberInput: Locator
  readonly expiryInput: Locator
  readonly cvvInput: Locator
  readonly placeOrderButton: Locator
  readonly orderConfirmation: Locator

  constructor(page: Page) {
    this.page = page
    this.addressInput = page.getByLabel('Address')
    this.cityInput = page.getByLabel('City')
    this.zipInput = page.getByLabel('ZIP Code')
    this.continueButton = page.getByRole('button', { name: 'Continue' })
    this.cardNumberInput = page.getByLabel('Card Number')
    this.expiryInput = page.getByLabel('Expiry')
    this.cvvInput = page.getByLabel('CVV')
    this.placeOrderButton = page.getByRole('button', { name: 'Place Order' })
    this.orderConfirmation = page.getByRole('heading', { name: 'Order Confirmed' })
  }

  async fillShippingInfo(address: string, city: string, zip: string) {
    await this.addressInput.fill(address)
    await this.cityInput.fill(city)
    await this.zipInput.fill(zip)
    await this.continueButton.click()
  }

  async fillPaymentInfo(cardNumber: string, expiry: string, cvv: string) {
    await this.cardNumberInput.fill(cardNumber)
    await this.expiryInput.fill(expiry)
    await this.cvvInput.fill(cvv)
  }

  async placeOrder() {
    await this.placeOrderButton.click()
    await this.orderConfirmation.waitFor()
  }
}

// Usage in tests
import { CheckoutPage } from './pages/checkout.page'

test('checkout with POM', async ({ page }) => {
  const checkoutPage = new CheckoutPage(page)
  await page.goto('/checkout')

  await checkoutPage.fillShippingInfo('123 Main St', 'San Francisco', '94102')
  await checkoutPage.fillPaymentInfo('4242424242424242', '12/25', '123')
  await checkoutPage.placeOrder()

  await expect(checkoutPage.orderConfirmation).toBeVisible()
})
```

## Authentication State Reuse

```typescript
// auth.setup.ts
import { test as setup } from '@playwright/test'

const authFile = 'playwright/.auth/user.json'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill('test@example.com')
  await page.getByLabel('Password').fill('password123')
  await page.getByRole('button', { name: 'Sign In' }).click()
  await page.waitForURL('/dashboard')

  // Save storage state
  await page.context().storageState({ path: authFile })
})

// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: authFile
      },
      dependencies: ['setup']
    }
  ]
})

// Now all tests run with authenticated state
test('access protected page', async ({ page }) => {
  await page.goto('/dashboard') // Already authenticated
  await expect(page.getByText('Welcome back')).toBeVisible()
})
```

## API Mocking

```typescript
test('mock API responses', async ({ page }) => {
  // Mock API call
  await page.route('**/api/products', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Laptop', price: 999 },
        { id: 2, name: 'Mouse', price: 29 }
      ])
    })
  })

  await page.goto('/products')
  await expect(page.getByText('Laptop')).toBeVisible()
  await expect(page.getByText('$999')).toBeVisible()
})

test('simulate API error', async ({ page }) => {
  await page.route('**/api/products', route => {
    route.fulfill({ status: 500, body: 'Internal Server Error' })
  })

  await page.goto('/products')
  await expect(page.getByText('Failed to load products')).toBeVisible()
})
```

## Mobile Testing

```typescript
import { devices } from '@playwright/test'

test.use({ ...devices['iPhone 13 Pro'] })

test('mobile navigation', async ({ page }) => {
  await page.goto('/')

  // Mobile menu
  await page.getByRole('button', { name: 'Menu' }).click()
  await expect(page.getByRole('navigation')).toBeVisible()

  // Test mobile-specific features
  await page.getByRole('link', { name: 'Products' }).click()
  await expect(page).toHaveURL(/.*products/)
})
```

## Visual Testing

```typescript
test('visual regression', async ({ page }) => {
  await page.goto('/products')

  // Full page screenshot
  await expect(page).toHaveScreenshot('products-page.png')

  // Element screenshot
  const product = page.getByTestId('product-1')
  await expect(product).toHaveScreenshot('product-card.png')
})
```

## Parallel Execution

```typescript
// playwright.config.ts
export default defineConfig({
  workers: process.env.CI ? 2 : undefined, // 2 workers in CI, all CPU cores locally
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0
})

// Shard tests across machines
// Machine 1:
// npx playwright test --shard=1/3

// Machine 2:
// npx playwright test --shard=2/3

// Machine 3:
// npx playwright test --shard=3/3
```

## Tracing and Debugging

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    trace: 'on-first-retry', // or 'on', 'off', 'retain-on-failure'
    video: 'retain-on-failure',
    screenshot: 'only-on-failure'
  }
})

// View trace
// npx playwright show-trace trace.zip

// Debug mode
// npx playwright test --debug

// Headed mode
// npx playwright test --headed
```

## Accessibility Testing

```typescript
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('homepage should be accessible', async ({ page }) => {
  await page.goto('/')

  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze()

  expect(accessibilityScanResults.violations).toEqual([])
})
```

## Network Interception

```typescript
test('track network requests', async ({ page }) => {
  const requests: string[] = []

  page.on('request', request => {
    if (request.url().includes('/api/')) {
      requests.push(request.url())
    }
  })

  await page.goto('/dashboard')

  expect(requests).toContain('https://api.example.com/api/user')
  expect(requests).toContain('https://api.example.com/api/products')
})

test('wait for specific API call', async ({ page }) => {
  await page.goto('/products')

  // Wait for API response
  const responsePromise = page.waitForResponse(
    response => response.url().includes('/api/products') && response.status() === 200
  )

  await page.getByRole('button', { name: 'Load More' }).click()
  await responsePromise // Wait for API call to complete
})
```

## Best Practices

```typescript
// GOOD: Use data-testid for stable selectors
await page.getByTestId('submit-button').click()

// GOOD: Use role and accessible name
await page.getByRole('button', { name: 'Submit' }).click()

// BAD: Avoid CSS selectors (brittle)
await page.locator('.btn.btn-primary').click()

// GOOD: Use auto-waiting (built-in retries)
await page.getByText('Loading...').waitFor({ state: 'hidden' })
await page.getByText('Content loaded').waitFor()

// GOOD: Test user journeys, not implementation
test('user can purchase product', async ({ page }) => {
  // Focus on user actions and outcomes
})

// BAD: Don't test internal state
test('cart state updated', async ({ page }) => {
  // Avoid testing Redux store or internal state
})
```

## Configuration Template

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit.xml' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure'
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup']
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup']
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup']
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup']
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI
  }
})
```

## Common Patterns Checklist

- [ ] Use Page Object Model for reusable page interactions
- [ ] Reuse authentication state across tests
- [ ] Mock external APIs for reliability
- [ ] Test critical user journeys only (not every page)
- [ ] Use data-testid or ARIA roles for selectors
- [ ] Enable trace/video for debugging failures
- [ ] Run tests in parallel
- [ ] Test across multiple browsers
- [ ] Include mobile device testing
- [ ] Set up retry logic for flaky tests

## Related Resources

See [../../references/comprehensive-testing-guide.md](../../references/comprehensive-testing-guide.md) for E2E testing strategies and [../bdd/template-cucumber-gherkin.md](../bdd/template-cucumber-gherkin.md) for BDD integration.
