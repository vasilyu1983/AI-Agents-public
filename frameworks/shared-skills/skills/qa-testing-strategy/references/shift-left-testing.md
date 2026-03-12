# Shift-Left Testing Strategy

Shift-left testing means starting testing early in the development lifecycle—during planning, design, and development phases rather than after code is written.

## Contents

- Why Shift-Left?
- Shift-Left Practices
- Decision
- Test Strategy
- Test Doubles
- Coverage Targets
- Shift-Left Testing Metrics
- Shift-Left Anti-Patterns
- Shift-Left Checklist
- Tools for Shift-Left Testing
- ROI of Shift-Left Testing
- Resources

## Why Shift-Left?

**Traditional approach** (Shift-Right):
```
Requirements → Design → Development → Testing → Deployment
                                         ↑
                                    Testing starts here
                                    (bugs are expensive to fix)
```

**Shift-Left approach**:
```
Requirements → Design → Development → Deployment
    ↓            ↓           ↓
  Testing    Testing     Testing
  (bugs are cheap to fix at every stage)
```

**Benefits**:
- Often much cheaper to fix bugs in design/development than after release
- **Faster feedback** loops (minutes vs days)
- **Better quality** built-in, not inspected-in
- **Reduced rework** and technical debt
- **Higher confidence** in releases

## Shift-Left Practices

### 1. Testing in Requirements Phase

**Behavior-Driven Development (BDD)**:
```gherkin
# Feature file written BEFORE implementation
Feature: User Login
  As a user
  I want to log in to my account
  So that I can access my personalized dashboard

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter email "user@example.com"
    And I enter password "SecurePass123"
    And I click the "Login" button
    Then I should see my dashboard
    And I should see "Welcome, John"

  Scenario: Failed login with invalid password
    Given I am on the login page
    When I enter email "user@example.com"
    And I enter password "WrongPassword"
    And I click the "Login" button
    Then I should see an error "Invalid credentials"
    And I should remain on the login page
```

**Implementation with Cucumber**:
```typescript
// steps/login.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';

Given('I am on the login page', async function () {
  await this.page.goto('/login');
});

When('I enter email {string}', async function (email: string) {
  await this.page.fill('input[name="email"]', email);
});

When('I enter password {string}', async function (password: string) {
  await this.page.fill('input[name="password"]', password);
});

When('I click the {string} button', async function (buttonText: string) {
  await this.page.click(`button:has-text("${buttonText}")`);
});

Then('I should see my dashboard', async function () {
  await expect(this.page.locator('.dashboard')).toBeVisible();
});

Then('I should see {string}', async function (text: string) {
  await expect(this.page.locator('body')).toContainText(text);
});
```

**Acceptance Criteria as Tests**:
```typescript
// Write tests from acceptance criteria BEFORE implementation
describe('Shopping Cart', () => {
  // AC1: Users can add items to cart
  it('should add item to cart when "Add to Cart" clicked', async () => {
    await page.click('[data-testid="add-to-cart"]');
    expect(await getCartCount()).toBe(1);
  });

  // AC2: Cart shows total price
  it('should display correct total price', async () => {
    await addItemToCart({ price: 29.99 });
    await addItemToCart({ price: 19.99 });
    expect(await getCartTotal()).toBe(49.98);
  });

  // AC3: Users can remove items
  it('should remove item when remove button clicked', async () => {
    await addItemToCart({ id: '123' });
    await page.click('[data-testid="remove-item-123"]');
    expect(await getCartCount()).toBe(0);
  });
});
```

### 2. Testing in Design Phase

**API Design Testing (Contract-First)**:
```yaml
# openapi.yml - Written BEFORE implementation
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, name]
              properties:
                email:
                  type: string
                  format: email
                name:
                  type: string
                  minLength: 2
                  maxLength: 100
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid input
```

**Generate tests from OpenAPI**:
```typescript
// Auto-generated test from OpenAPI spec
import { validateAgainstSchema } from 'openapi-validator';

describe('POST /users', () => {
  it('should match OpenAPI schema', async () => {
    const response = await request(app)
      .post('/users')
      .send({ email: 'test@example.com', name: 'Test User' });

    // Validate response against OpenAPI schema
    const validation = validateAgainstSchema(response, openApiSpec, '/users', 'post');
    expect(validation.valid).toBe(true);
  });
});
```

**Architecture Decision Records (ADRs) with Test Implications**:
```markdown
# ADR-005: Use Event-Driven Architecture for Order Processing

## Decision
We will use event-driven architecture with message queues for order processing.

## Test Strategy
- **Unit tests**: Event handlers in isolation
- **Integration tests**: Message queue interactions
- **E2E tests**: Complete order flow with events
- **Idempotency tests**: Duplicate event handling
- **Ordering tests**: Event sequence correctness

## Test Doubles
- Mock message queue for unit tests
- In-memory queue for integration tests
- Real queue (RabbitMQ) for E2E tests

## Coverage Targets
- Event handlers: 100% (critical path)
- Queue integration: 90%
- Retry logic: 100%
```

### 3. Testing During Development (TDD)

**Red-Green-Refactor Cycle**:

**Step 1: Red (Write failing test)**:
```typescript
// Test written FIRST
describe('UserService', () => {
  it('should hash password before saving', async () => {
    const service = new UserService();
    const user = await service.createUser({
      email: 'test@example.com',
      password: 'PlainTextPassword'
    });

    // Password should be hashed, not stored as plaintext
    expect(user.password).not.toBe('PlainTextPassword');
    expect(user.password).toMatch(/^\$2[aby]\$.{56}$/); // bcrypt format
  });
});

// Test FAILS (implementation doesn't exist yet)
```

**Step 2: Green (Make it pass)**:
```typescript
// Minimal implementation to pass test
class UserService {
  async createUser(data: { email: string; password: string }) {
    const hashedPassword = await bcrypt.hash(data.password, 10);

    return {
      email: data.email,
      password: hashedPassword
    };
  }
}

// Test PASSES
```

**Step 3: Refactor (Improve code)**:
```typescript
// Refactored for better design
class UserService {
  constructor(
    private passwordHasher: PasswordHasher,
    private userRepository: UserRepository
  ) {}

  async createUser(data: CreateUserDTO): Promise<User> {
    const hashedPassword = await this.passwordHasher.hash(data.password);

    const user = new User({
      ...data,
      password: hashedPassword
    });

    return this.userRepository.save(user);
  }
}

// Tests still PASS (refactoring didn't break functionality)
```

**TDD Benefits**:
- Forces thinking about interface before implementation
- Ensures testable code (dependency injection, small functions)
- Provides immediate feedback
- Creates regression test suite automatically
- Documents expected behavior

### 4. Preview Environments ( Best Practice)

**Ephemeral environments for every PR**:

```yaml
# .github/workflows/preview.yml
name: Deploy Preview Environment

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to preview
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          scope: preview

      - name: Run E2E tests against preview
        env:
          PREVIEW_URL: ${{ steps.deploy.outputs.preview-url }}
        run: |
          npm run test:e2e -- --url=$PREVIEW_URL

      - name: Comment PR with preview URL
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `Preview deployed: ${{ steps.deploy.outputs.preview-url }}`
            })
```

**Benefits of preview environments**:
- Test changes in production-like environment
- Catch integration issues early
- Enable stakeholder review before merge
- Test database migrations safely
- Verify deployment process

**Example with AWS/Kubernetes**:
```yaml
# deploy-preview.yml
apiVersion: v1
kind: Namespace
metadata:
  name: pr-{{ PR_NUMBER }}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-preview
  namespace: pr-{{ PR_NUMBER }}
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: app
        image: myapp:pr-{{ PR_NUMBER }}
        env:
        - name: DATABASE_URL
          value: postgres://preview-{{ PR_NUMBER }}.db:5432
```

### 5. Continuous Testing in CI/CD

**Pipeline stages**:

```yaml
# Complete testing pipeline
stages:
  - validate
  - unit-test
  - integration-test
  - security-scan
  - e2e-test
  - performance-test
  - deploy

# Stage 1: Validate (seconds)
validate:
  stage: validate
  script:
    - npm run lint
    - npm run type-check
    - npm run format:check

# Stage 2: Unit tests (1-2 minutes)
unit-test:
  stage: unit-test
  script:
    - npm run test:unit -- --coverage
  coverage: '/Lines\s*:\s*(\d+\.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

# Stage 3: Integration tests (2-5 minutes)
integration-test:
  stage: integration-test
  services:
    - postgres:15
    - redis:7
  script:
    - npm run test:integration

# Stage 4: Security scanning (2-3 minutes)
security-scan:
  stage: security-scan
  script:
    - npm audit --audit-level=moderate
    - snyk test --severity-threshold=high

# Stage 5: E2E tests (5-10 minutes)
e2e-test:
  stage: e2e-test
  script:
    - docker-compose up -d
    - npm run test:e2e
  artifacts:
    when: on_failure
    paths:
      - test-results/

# Stage 6: Performance tests (5-10 minutes)
performance-test:
  stage: performance-test
  script:
    - k6 run performance-tests.js
  only:
    - main
    - release/*

# Stage 7: Deploy only if all tests pass
deploy-staging:
  stage: deploy
  script:
    - npm run deploy:staging
  only:
    - main
```

**Fast feedback optimization**:
```yaml
# Parallel test execution
test:
  parallel:
    matrix:
      - TEST_SUITE: [unit, integration, e2e]

  script:
    - npm run test:$TEST_SUITE

# Result: 3x faster (run simultaneously instead of sequentially)
```

### 6. Static Analysis (Pre-Development)

**TypeScript for compile-time safety**:
```typescript
// Catch errors at compile time, not runtime
interface User {
  id: string;
  email: string;
  age: number;
}

function sendEmail(user: User) {
  // TypeScript error if wrong type passed
  mailer.send(user.email);
}

// BAD: Compile error
sendEmail({ id: '123', email: 123 });  // email should be string

// GOOD: Compile success
sendEmail({ id: '123', email: 'test@example.com', age: 30 });
```

**ESLint rules for security**:
```javascript
// .eslintrc.js
module.exports = {
  plugins: ['security'],
  extends: ['plugin:security/recommended'],
  rules: {
    'security/detect-object-injection': 'error',
    'security/detect-non-literal-regexp': 'error',
    'security/detect-unsafe-regex': 'error',
    'no-eval': 'error',
    'no-implied-eval': 'error',
  }
};

// Catches security issues during development
const userInput = getUserInput();
eval(userInput);  // BAD: ESLint error: no-eval
```

**SonarQube quality gates**:
```yaml
# sonar-project.properties
sonar.qualitygate.wait=true

# Block PR if quality gate fails
sonar.qualitygate.coverage=80
sonar.qualitygate.duplications=3
sonar.qualitygate.complexity=10
sonar.qualitygate.maintainability=A
```

## Shift-Left Testing Metrics

### Early Bug Detection Rate

```
Early Bug Detection Rate = (Bugs found in Dev/Design) / (Total Bugs) × 100

Target: >80% (80% of bugs found before QA phase)
```

### Cost of Quality

```
Cost of Quality = Prevention Cost + Appraisal Cost + Failure Cost

Shift-left reduces:
- Failure cost (fewer production bugs)
- Appraisal cost (automated testing cheaper than manual)

Shift-left increases:
- Prevention cost (more upfront testing) - but net savings overall

ROI: often positive when focused on high-risk paths; validate via the metrics above
```

### Lead Time for Changes

```
Lead Time = Time from commit to production

Shift-left reduces lead time by:
- Catching bugs earlier (less rework)
- Faster testing (automated)
- Higher confidence (fewer rollbacks)

Target: <1 day for low-risk changes
```

## Shift-Left Anti-Patterns

### BAD: "We'll add tests later"
```
Problem: Tests never get written, or written as afterthought
Solution: TDD - write tests first
```

### BAD: Manual testing in dev environment
```
Problem: Slow, not repeatable, doesn't scale
Solution: Automated tests in CI/CD
```

### BAD: Testing only happy paths
```
Problem: Edge cases and errors discovered in production
Solution: Test edge cases, errors, boundaries from day 1
```

### BAD: No test ownership
```
Problem: Developers write code, QA writes tests (handoff delay)
Solution: Developers own quality - write tests for own code
```

### BAD: Skipping tests to meet deadlines
```
Problem: Technical debt accumulates, velocity decreases over time
Solution: Tests are non-negotiable part of "done"
```

## Shift-Left Checklist

### Requirements Phase
- [ ] Acceptance criteria defined for all stories
- [ ] BDD scenarios written (Given-When-Then)
- [ ] Test data requirements identified
- [ ] Performance requirements specified
- [ ] Security requirements documented

### Design Phase
- [ ] API contracts defined (OpenAPI/GraphQL schema)
- [ ] Test strategy documented in ADRs
- [ ] Testability considered in architecture
- [ ] Test environment requirements specified
- [ ] Mock/stub strategy defined

### Development Phase
- [ ] TDD practiced (test written before code)
- [ ] Unit tests for all business logic
- [ ] Integration tests for external dependencies
- [ ] Static analysis passing (linter, type-checker)
- [ ] Security scanner passing (no high vulnerabilities)

### Pre-Commit
- [ ] All tests passing locally
- [ ] Code coverage meets threshold
- [ ] No linter errors
- [ ] Git hooks running successfully

### CI/CD Pipeline
- [ ] Automated tests run on every commit
- [ ] Preview environment deployed for PRs
- [ ] E2E tests run against preview
- [ ] Performance tests for critical paths
- [ ] Security scans completed

### Pre-Merge
- [ ] All pipeline checks passing
- [ ] Code review completed (including tests)
- [ ] No failing or flaky tests
- [ ] Documentation updated (if needed)

## Tools for Shift-Left Testing

**Requirements & Design**:
- Cucumber / Gherkin (BDD)
- OpenAPI / Swagger (API contracts)
- Figma / Storybook (UI component testing)

**Development**:
- Jest / Vitest (Unit testing)
- Playwright / Cypress (E2E testing)
- Supertest (API testing)
- Docker Compose (Local integration testing)

**Pre-Commit**:
- Husky (Git hooks)
- lint-staged (Incremental linting)
- commitlint (Commit message validation)

**CI/CD**:
- GitHub Actions / GitLab CI
- Vercel / Netlify (Preview environments)
- SonarQube (Quality gates)
- Snyk / Dependabot (Security scanning)

## ROI of Shift-Left Testing

Shift-left ROI is context-dependent. Treat it as an investment decision:

- Start where risk is highest (auth, payments, data loss, distributed workflows).
- Measure outcomes (defect escape rate, lead time, incident rate, rework time, CI duration).
- Expand what works; prune suites that add cost without catching defects.

## Resources

- "Shift Left Testing" - IBM DevOps
- "Continuous Testing in DevOps" - Atlassian
- "Testing in Production" - Charity Majors
- "Accelerate" - Nicole Forsgren (DORA metrics)
- BDD with Cucumber - official documentation
