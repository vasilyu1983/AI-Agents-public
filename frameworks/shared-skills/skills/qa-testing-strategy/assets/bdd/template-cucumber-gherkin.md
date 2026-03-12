# BDD Testing Template: Cucumber & Gherkin

Use this template for behavior-driven development (BDD) with Cucumber and Gherkin syntax to create executable specifications.

## Why BDD (2024 Best Practices)

**Benefits**:
- Living documentation (scenarios are always up-to-date)
- Collaboration between technical and non-technical stakeholders
- Clear acceptance criteria before development
- Executable specifications
- Shared understanding of requirements

**When to use**: Acceptance tests, E2E critical paths, stakeholder-facing features

**When NOT to use**: Unit tests (use code directly), implementation details

## Basic Gherkin Syntax

```gherkin
# features/user-login.feature
Feature: User Login
  As a registered user
  I want to log in to my account
  So that I can access my personalized dashboard

  Background:
    Given the application is running
    And I am on the login page

  Scenario: Successful login with valid credentials
    When I enter email "user@example.com"
    And I enter password "SecurePass123"
    And I click the "Login" button
    Then I should see my dashboard
    And I should see "Welcome back, John"

  Scenario: Failed login with invalid password
    When I enter email "user@example.com"
    And I enter password "WrongPassword"
    And I click the "Login" button
    Then I should see an error "Invalid credentials"
    And I should remain on the login page

  Scenario: Account lockout after multiple failed attempts
    When I enter email "user@example.com"
    And I enter password "WrongPassword"
    And I click the "Login" button 3 times
    Then I should see an error "Account temporarily locked"
    And I should not be able to log in for 15 minutes
```

## Step Definitions (TypeScript)

```typescript
// step-definitions/login.steps.ts
import { Given, When, Then, Before, After } from '@cucumber/cucumber'
import { expect } from '@playwright/test'
import { LoginPage } from '../pages/login.page'

let page: Page
let loginPage: LoginPage

Before(async function () {
  page = await this.browser.newPage()
  loginPage = new LoginPage(page)
})

After(async function () {
  await page.close()
})

Given('the application is running', async function () {
  // Verify app health endpoint
  const response = await page.request.get('https://api.example.com/health')
  expect(response.status()).toBe(200)
})

Given('I am on the login page', async function () {
  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible()
})

When('I enter email {string}', async function (email: string) {
  await page.getByLabel('Email').fill(email)
})

When('I enter password {string}', async function (password: string) {
  await page.getByLabel('Password').fill(password)
})

When('I click the {string} button', async function (buttonText: string) {
  await page.getByRole('button', { name: buttonText }).click()
})

When('I click the {string} button {int} times', async function (buttonText: string, times: number) {
  for (let i = 0; i < times; i++) {
    await page.getByRole('button', { name: buttonText }).click()
    await page.waitForTimeout(1000)
  }
})

Then('I should see my dashboard', async function () {
  await expect(page).toHaveURL('/dashboard')
  await expect(page.getByTestId('dashboard')).toBeVisible()
})

Then('I should see {string}', async function (text: string) {
  await expect(page.getByText(text)).toBeVisible()
})

Then('I should see an error {string}', async function (errorMessage: string) {
  await expect(page.getByRole('alert')).toContainText(errorMessage)
})

Then('I should remain on the login page', async function () {
  await expect(page).toHaveURL('/login')
})

Then('I should not be able to log in for {int} minutes', async function (minutes: number) {
  // Store context for future validation
  this.lockoutDuration = minutes
  const lockoutMessage = await page.getByTestId('lockout-message').textContent()
  expect(lockoutMessage).toContain(`${minutes} minutes`)
})
```

## Scenario Outlines (Data-Driven Tests)

```gherkin
Feature: Shopping Cart

  Scenario Outline: Apply discount codes
    Given I have "<item>" in my cart with price <price>
    When I apply discount code "<code>"
    Then the total should be <total>
    And I should see discount message "<message>"

    Examples:
      | item      | price | code     | total | message                |
      | Laptop    | 1000  | SAVE10   | 900   | 10% discount applied   |
      | Mouse     | 50    | SAVE10   | 45    | 10% discount applied   |
      | Laptop    | 1000  | SAVE50   | 500   | 50% discount applied   |
      | Mouse     | 50    | INVALID  | 50    | Invalid discount code  |
      | Keyboard  | 100   |          | 100   | No discount applied    |

  Scenario Outline: Validate product search
    Given I am on the products page
    When I search for "<query>"
    Then I should see <result_count> results
    And the first result should be "<first_result>"

    Examples:
      | query     | result_count | first_result       |
      | laptop    | 15           | MacBook Pro        |
      | mouse     | 42           | Logitech MX Master |
      | keyboard  | 28           | Mechanical Keyboard|
      | monitor   | 31           | Dell UltraSharp    |
      | invalid   | 0            |                    |
```

## Tags for Organization

```gherkin
@smoke @critical
Feature: User Authentication

  @happy-path
  Scenario: Successful login
    # ...

  @error-handling
  Scenario: Invalid credentials
    # ...

  @security @slow
  Scenario: Account lockout
    # ...

  @wip
  Scenario: Two-factor authentication
    # Work in progress
```

```bash
# Run specific tags
npm run test:cucumber -- --tags "@smoke"
npm run test:cucumber -- --tags "@critical and not @slow"
npm run test:cucumber -- --tags "@smoke or @regression"
```

## Best Practices: Writing Good Gherkin

### GOOD: Declarative (Focus on WHAT, not HOW)

```gherkin
# Good - Describes behavior from user perspective
Scenario: User completes checkout
  Given I have items in my cart
  When I complete the checkout process
  Then my order should be confirmed

# Bad - Implementation details (HOW)
Scenario: User completes checkout
  Given I click the cart icon
  And I see the cart page
  When I click the "Checkout" button
  And I fill in field "address" with "123 Main St"
  And I fill in field "city" with "San Francisco"
  And I click the "Submit" button
  Then I should see element with id "confirmation"
```

### GOOD: Independent Scenarios

```gherkin
# Good - Self-contained
Scenario: Delete user account
  Given I have a user account
  When I request account deletion
  Then my account should be deleted

# Bad - Depends on previous scenario
Scenario: Delete user account
  # Assumes account was created in previous scenario
  When I request account deletion
  Then my account should be deleted
```

### GOOD: Use Background for Common Setup

```gherkin
Feature: Product Management

  Background:
    Given I am logged in as an admin
    And I am on the products page

  Scenario: Add new product
    When I create a product with name "Laptop"
    Then I should see "Laptop" in the product list

  Scenario: Edit product
    Given I have a product "Mouse"
    When I edit the product name to "Wireless Mouse"
    Then I should see "Wireless Mouse" in the product list
```

## Data Tables

```gherkin
Scenario: Create user with complete profile
  When I create a user with the following details:
    | field      | value                |
    | name       | John Doe             |
    | email      | john@example.com     |
    | age        | 30                   |
    | country    | USA                  |
    | role       | admin                |
  Then the user should be created successfully

Scenario: Bulk create users
  When I create the following users:
    | name       | email                | role   |
    | Alice      | alice@example.com    | user   |
    | Bob        | bob@example.com      | admin  |
    | Charlie    | charlie@example.com  | user   |
  Then all users should be created successfully
```

```typescript
// Step definition for data tables
When('I create a user with the following details:', async function (dataTable) {
  const userData = dataTable.rowsHash()
  await this.api.post('/users', userData)
})

When('I create the following users:', async function (dataTable) {
  const users = dataTable.hashes()
  for (const user of users) {
    await this.api.post('/users', user)
  }
})
```

## Hooks for Setup/Teardown

```typescript
// support/hooks.ts
import { Before, After, BeforeAll, AfterAll, Status } from '@cucumber/cucumber'

BeforeAll(async function () {
  // Global setup (runs once before all scenarios)
  console.log('Starting test suite')
})

AfterAll(async function () {
  // Global teardown (runs once after all scenarios)
  console.log('Test suite completed')
})

Before(async function () {
  // Setup before each scenario
  this.startTime = Date.now()
})

After(async function (scenario) {
  // Teardown after each scenario
  const duration = Date.now() - this.startTime
  console.log(`Scenario "${scenario.pickle.name}" took ${duration}ms`)

  // Take screenshot on failure
  if (scenario.result?.status === Status.FAILED) {
    const screenshot = await this.page.screenshot()
    this.attach(screenshot, 'image/png')
  }
})

// Tagged hooks
Before({ tags: '@database' }, async function () {
  await this.db.clear()
})

After({ tags: '@database' }, async function () {
  await this.db.close()
})
```

## Custom World (Shared Context)

```typescript
// support/world.ts
import { setWorldConstructor, World, IWorldOptions } from '@cucumber/cucumber'
import { chromium, Browser, Page } from '@playwright/test'

export class CustomWorld extends World {
  browser?: Browser
  page?: Page
  apiResponse?: any
  testData: Map<string, any>

  constructor(options: IWorldOptions) {
    super(options)
    this.testData = new Map()
  }

  async init() {
    this.browser = await chromium.launch()
    const context = await this.browser.newContext()
    this.page = await context.newPage()
  }

  async cleanup() {
    await this.page?.close()
    await this.browser?.close()
  }

  // Helper methods
  async login(email: string, password: string) {
    await this.page!.goto('/login')
    await this.page!.getByLabel('Email').fill(email)
    await this.page!.getByLabel('Password').fill(password)
    await this.page!.getByRole('button', { name: 'Login' }).click()
  }

  storeData(key: string, value: any) {
    this.testData.set(key, value)
  }

  getData(key: string) {
    return this.testData.get(key)
  }
}

setWorldConstructor(CustomWorld)
```

## Configuration

```typescript
// cucumber.config.ts
export default {
  require: ['step-definitions/**/*.ts'],
  requireModule: ['ts-node/register'],
  format: [
    'progress-bar',
    'html:test-results/cucumber-report.html',
    'json:test-results/cucumber-report.json',
    'junit:test-results/cucumber-report.xml'
  ],
  formatOptions: {
    snippetInterface: 'async-await'
  },
  parallel: 2,
  retry: 1,
  retryTagFilter: '@flaky'
}
```

## Integration with CI/CD

```yaml
# .github/workflows/bdd-tests.yml
name: BDD Tests

on: [push, pull_request]

jobs:
  cucumber-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run Cucumber tests
        run: npm run test:cucumber

      - name: Publish test results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: test-results/cucumber-report.xml

      - name: Upload HTML report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: cucumber-report
          path: test-results/cucumber-report.html
```

## Common Patterns Checklist

- [ ] Write scenarios from user perspective (declarative)
- [ ] Keep scenarios independent (no dependencies)
- [ ] Use Background for common setup
- [ ] Use Scenario Outline for data-driven tests
- [ ] Use tags for organization (@smoke, @regression, @wip)
- [ ] Implement reusable step definitions
- [ ] Use Custom World for shared context
- [ ] Add screenshots on failure
- [ ] Write one assertion per Then step
- [ ] Avoid brittle implementation details

## Anti-Patterns to Avoid

[FAIL] **Overly specific scenarios**:
```gherkin
# Too detailed
When I click the button with id "submit-btn-123"
And I wait 2 seconds
Then I should see element with class "success-message"
```

[OK] **User-focused scenarios**:
```gherkin
# Better
When I submit the form
Then I should see a success message
```

[FAIL] **Reusing steps inappropriately**:
```gherkin
# Confusing reuse
Given I am on the login page
And I am on the products page  # Which page am I on?
```

[FAIL] **Testing too much in one scenario**:
```gherkin
# Too much in one scenario (split into 3 scenarios)
Scenario: Complete user journey
  Given I register a new account
  And I log in
  And I add products to cart
  And I checkout
  And I view order history
  And I update my profile
  # ... 20 more steps
```

## Related Resources

See [../../references/shift-left-testing.md](../../references/shift-left-testing.md) for writing scenarios in requirements phase, and [../e2e/template-playwright.md](../e2e/template-playwright.md) for implementing step definitions with Playwright.
