# Code Commenting and Docstring Guide

Comprehensive guide for writing effective code comments, docstrings, and inline documentation that improves code maintainability.

## Core Commenting Principles

### 1. Comment WHY, Not WHAT

**The code already shows WHAT it does. Comments explain WHY.**

**BAD: Bad (Explains WHAT)**:
```javascript
// Increment counter by 1
counter++;

// Loop through users array
for (const user of users) {
  // Print user name
  console.log(user.name);
}
```

**GOOD: Good (Explains WHY)**:
```javascript
// Retry counter incremented to track failed connection attempts.
// We allow up to 3 retries due to transient network issues.
counter++;

// Process each user to send welcome emails. Must be synchronous
// to comply with GDPR "right to erasure" - if user requests deletion
// mid-batch, we need to stop immediately.
for (const user of users) {
  await sendWelcomeEmail(user);
}
```

### 2. Avoid Obvious Comments

**Self-explanatory code doesn't need comments.**

**BAD: Bad (Obvious)**:
```python
# Get user by ID
user = get_user(user_id)

# Check if user exists
if user is not None:
    # Return user email
    return user.email
```

**GOOD: Good (No comments needed - code is clear)**:
```python
user = get_user(user_id)
if user is not None:
    return user.email
```

**When code is complex, refactor first, comment second**:

**BAD: Bad (Complex code with comment)**:
```javascript
// Calculate discount based on user tier
const d = u.t === 'gold' ? p * 0.2 : u.t === 'silver' ? p * 0.1 : 0;
```

**GOOD: Good (Self-documenting code)**:
```javascript
function calculateDiscount(user, price) {
  const TIER_DISCOUNTS = {
    gold: 0.20,
    silver: 0.10,
    bronze: 0.05
  };

  return price * (TIER_DISCOUNTS[user.tier] || 0);
}

const discount = calculateDiscount(user, price);
```

### 3. Keep Comments Updated

**Outdated comments are worse than no comments.**

**BAD: Bad (Outdated comment)**:
```javascript
// Connect to MongoDB database
const pool = new Pool({
  host: 'localhost',
  port: 5432,  // PostgreSQL, not MongoDB!
  database: 'myapp'
});
```

**GOOD: Good (Updated comment or removed)**:
```javascript
// Connect to PostgreSQL database for user data
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'myapp'
});
```

**Better: Make code self-documenting**:
```javascript
const postgresPool = new Pool(DATABASE_CONFIG);
```

### 4. Use Comments for Complex Logic

**When logic is unavoidably complex, explain the reasoning.**

**GOOD: Good (Explains complex algorithm)**:
```python
def calculate_shipping_cost(weight, distance, priority):
    """
    Calculate shipping cost using complex tiered pricing.

    We use exponential pricing for priority shipping because:
    1. Courier partners charge us exponentially for faster delivery
    2. Higher prices discourage abuse of priority option
    3. Revenue from priority offsets losses on free standard shipping
    """
    base_cost = weight * 0.5 + distance * 0.1

    if priority == 'express':
        # Exponential multiplier: express costs 4x standard
        # This matches our courier's pricing model
        return base_cost * 4
    elif priority == 'priority':
        # Priority is 2x - sweet spot for customer value vs cost
        return base_cost * 2
    else:
        return base_cost
```

## Docstrings for Functions/Methods

### JavaScript (JSDoc)

**Format**:
```javascript
/**
 * Brief description of what function does.
 *
 * Detailed explanation if needed. Explain parameters, behavior,
 * edge cases, or important context.
 *
 * @param {string} userId - User unique identifier
 * @param {Object} options - Optional configuration
 * @param {boolean} [options.includeDeleted=false] - Include soft-deleted users
 * @param {number} [options.timeout=5000] - Request timeout in milliseconds
 * @returns {Promise<User>} User object with profile data
 * @throws {NotFoundError} If user doesn't exist
 * @throws {TimeoutError} If request exceeds timeout
 *
 * @example
 * const user = await getUser('user-123', { includeDeleted: true });
 * console.log(user.email);
 *
 * @example
 * // With timeout
 * const user = await getUser('user-123', { timeout: 3000 });
 */
async function getUser(userId, options = {}) {
  const { includeDeleted = false, timeout = 5000 } = options;

  // Implementation...
}
```

**JSDoc tags**:

| Tag | Purpose | Example |
|-----|---------|---------|
| `@param` | Parameter description | `@param {string} name - User's full name` |
| `@returns` | Return value | `@returns {Promise<User>} User object` |
| `@throws` | Exceptions thrown | `@throws {NotFoundError} If user not found` |
| `@example` | Usage example | `@example const user = await getUser('123')` |
| `@deprecated` | Mark as deprecated | `@deprecated Use fetchUser() instead` |
| `@see` | Related functions | `@see updateUser` |
| `@private` | Private function | `@private Internal use only` |
| `@async` | Async function | `@async` |

### Python (Google Style)

**Format**:
```python
def calculate_total(base_price: float, tax_rate: float, discount_percent: float = 0) -> float:
    """Calculate total price with tax and discount.

    Calculates the final price by applying discount to base price,
    then adding tax. Tax is calculated after discount to comply with
    local tax regulations.

    Args:
        base_price: Base price before tax and discount (must be positive)
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
        discount_percent: Discount percentage from 0 to 100 (default: 0)

    Returns:
        Final price after discount and tax, rounded to 2 decimal places

    Raises:
        ValueError: If base_price is negative
        ValueError: If tax_rate is negative or exceeds 1.0
        ValueError: If discount_percent is negative or exceeds 100

    Examples:
        >>> calculate_total(100, 0.08)
        108.0

        >>> calculate_total(100, 0.08, discount_percent=10)
        97.2

        >>> calculate_total(-10, 0.08)
        Traceback (most recent call last):
            ...
        ValueError: Base price must be positive

    Note:
        Tax is calculated AFTER applying discount, as required by
        California tax law (CA Revenue and Taxation Code §6011).
    """
    if base_price < 0:
        raise ValueError("Base price must be positive")
    if tax_rate < 0 or tax_rate > 1.0:
        raise ValueError("Tax rate must be between 0 and 1.0")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")

    discounted_price = base_price * (1 - discount_percent / 100)
    total = discounted_price * (1 + tax_rate)
    return round(total, 2)
```

**Python docstring sections**:

| Section | Purpose |
|---------|---------|
| **Summary** | One-line description |
| **Args** | Parameter descriptions |
| **Returns** | Return value description |
| **Raises** | Exceptions that can be raised |
| **Examples** | Usage examples (doctest format) |
| **Note** | Additional context or warnings |
| **See Also** | Related functions |

### TypeScript (TSDoc)

**Format**:
```typescript
/**
 * Fetch user data from the API.
 *
 * @remarks
 * This function implements retry logic with exponential backoff.
 * It will retry up to 3 times on network errors.
 *
 * @param userId - The user's unique identifier (UUID v4)
 * @param options - Optional fetch configuration
 * @returns A promise that resolves to the user object
 * @throws {@link NotFoundError} When user doesn't exist
 * @throws {@link NetworkError} After 3 failed retry attempts
 *
 * @example
 * ```typescript
 * const user = await fetchUser('550e8400-e29b-41d4-a716-446655440000');
 * console.log(user.email);
 * ```
 *
 * @see {@link updateUser} for updating user data
 * @see {@link deleteUser} for deleting users
 */
async function fetchUser(
  userId: string,
  options?: FetchOptions
): Promise<User> {
  // Implementation...
}
```

### Go (Godoc)

**Format**:
```go
// GetUser retrieves a user by ID from the database.
//
// This function queries the users table and returns a User struct.
// It returns an error if the user is not found or if there's a
// database connection issue.
//
// Parameters:
//   - id: User's unique identifier (UUID)
//
// Returns:
//   - *User: Pointer to User struct with user data
//   - error: ErrNotFound if user doesn't exist, or database error
//
// Example:
//
//	user, err := GetUser("user-123")
//	if err != nil {
//	    if errors.Is(err, ErrNotFound) {
//	        // Handle not found
//	    }
//	    return err
//	}
//	fmt.Println(user.Email)
func GetUser(id string) (*User, error) {
    // Implementation...
}
```

## Inline Comments

### When to Use Inline Comments

**Use inline comments for**:
- Complex algorithms
- Non-obvious optimizations
- Workarounds for bugs
- Business logic context
- Regulatory requirements
- Performance considerations

### Comment Placement

**BAD: Bad (Comment after code)**:
```javascript
const result = data.filter(x => x.status === 'active'); // Filter active items
```

**GOOD: Good (Comment before code)**:
```javascript
// Filter to only active items to exclude soft-deleted records
const result = data.filter(x => x.status === 'active');
```

### Temporary Comments (TODOs, FIXMEs)

**Standard tags**:

```javascript
// TODO: Add input validation for email format
// FIXME: Race condition when multiple users update simultaneously
// HACK: Workaround for IE11 bug - remove when dropping IE11 support
// NOTE: This must run synchronously due to GDPR compliance
// OPTIMIZE: Consider caching results - current O(n²) complexity
```

**Best practices**:
- Include issue number: `// TODO(#123): Add pagination`
- Add date: `// FIXME(2025-11-22): Memory leak in WebSocket`
- Assign owner: `// TODO(@john): Implement retry logic`

## Comment Anti-Patterns

### BAD: Commented-Out Code

**Don't commit commented-out code. Use version control instead.**

**BAD: Bad**:
```javascript
function processOrder(order) {
  // const discount = calculateDiscount(order);
  // order.total -= discount;

  const total = order.total;
  return total;
}
```

**GOOD: Good**:
```javascript
function processOrder(order) {
  const total = order.total;
  return total;
}

// If you need old code, check Git history
```

### BAD: Redundant Comments

**BAD: Bad**:
```python
# Initialize counter to zero
counter = 0

# Loop from 1 to 10
for i in range(1, 11):
    # Add i to counter
    counter += i
```

**GOOD: Good**:
```python
# Calculate sum of numbers 1-10 using arithmetic series formula
counter = 0
for i in range(1, 11):
    counter += i
```

### BAD: Changelog Comments

**Don't use comments as changelog. Use Git.**

**BAD: Bad**:
```javascript
// 2025-11-22: Added validation - John
// 2025-11-15: Fixed bug - Sarah
// 2025-11-10: Initial version - Mike
function validateEmail(email) {
  // Implementation
}
```

**GOOD: Good**:
```javascript
function validateEmail(email) {
  // Implementation
}

// Check Git history for changes:
// git log --follow -- path/to/file.js
```

### BAD: Divider Comments

**Don't use comment dividers. Use file structure instead.**

**BAD: Bad**:
```javascript
// ============================================
// USER FUNCTIONS
// ============================================

function getUser() { }
function updateUser() { }

// ============================================
// ORDER FUNCTIONS
// ============================================

function getOrder() { }
```

**GOOD: Good**:
```
src/
├── users/
│   ├── getUser.js
│   └── updateUser.js
└── orders/
    └── getOrder.js
```

## Comments for Complex Business Logic

**Use comments to explain business rules**:

```javascript
function calculateShippingCost(order, user) {
  let baseCost = order.weight * COST_PER_KG;

  // Free shipping for orders over $100 (marketing campaign requirement)
  // Campaign runs until 2025-12-31 - see marketing doc: /docs/campaigns/free-shipping.md
  if (order.total >= 100) {
    return 0;
  }

  // Premium members get 20% discount on shipping (loyalty program)
  // Approved by CFO on 2025-11-01 - see email thread #12345
  if (user.tier === 'premium') {
    baseCost *= 0.8;
  }

  // Express shipping costs 3x standard (courier contract requirement)
  // Rates locked until 2026-01-01 per DHL contract clause 4.2
  if (order.shippingSpeed === 'express') {
    baseCost *= 3;
  }

  return baseCost;
}
```

## Documentation Comments vs Implementation Comments

**Documentation comments** (docstrings):
- Describe what function does
- Document public API
- Extracted by documentation tools
- Written for users of the function

**Implementation comments** (inline):
- Explain how function works
- Clarify complex logic
- Note edge cases
- Written for maintainers of the code

**Example**:

```python
def calculate_fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number.

    This is a DOCUMENTATION COMMENT for users of the function.

    Args:
        n: Position in Fibonacci sequence (0-indexed)

    Returns:
        The nth Fibonacci number

    Examples:
        >>> calculate_fibonacci(0)
        0
        >>> calculate_fibonacci(5)
        5
    """
    # IMPLEMENTATION COMMENT for maintainers:
    # Use iterative approach instead of recursion to avoid
    # stack overflow for large n (n > 1000).
    # Time: O(n), Space: O(1)

    if n <= 1:
        return n

    # Track previous two numbers in sequence
    prev, curr = 0, 1

    for _ in range(2, n + 1):
        # Calculate next Fibonacci number
        prev, curr = curr, prev + curr

    return curr
```

## Comment Linting

**Tools**:
- **ESLint** (JavaScript): `eslint-plugin-jsdoc`
- **Pydocstyle** (Python): Check docstring conventions
- **golint** (Go): Check Godoc comments
- **TSLint** (TypeScript): Check TSDoc comments

**Example ESLint config**:

```json
{
  "plugins": ["jsdoc"],
  "rules": {
    "jsdoc/check-param-names": "error",
    "jsdoc/check-tag-names": "error",
    "jsdoc/require-param": "error",
    "jsdoc/require-returns": "error"
  }
}
```

## Accessibility Comments (HTML/JSX)

**Use ARIA labels and comments for screen readers**:

```jsx
// This icon button has no visible text, so we need aria-label
// for screen reader users
<button
  onClick={handleDelete}
  aria-label="Delete user profile"
>
  <TrashIcon />
</button>

{/*
  Skip navigation link for keyboard users
  Allows skipping header and jumping straight to main content
  WCAG 2.1 Level A requirement
*/}
<a href="#main-content" className="sr-only">
  Skip to main content
</a>
```

## Comment Maintenance Checklist

**When reviewing code**:

- [ ] Comments explain WHY, not WHAT
- [ ] No obvious/redundant comments
- [ ] Comments are up-to-date with code
- [ ] Complex logic has explanatory comments
- [ ] Public functions have docstrings
- [ ] No commented-out code
- [ ] TODOs have issue numbers or dates
- [ ] Business rules have context/references
- [ ] No divider comments (use file structure)
- [ ] Inline comments placed above code, not after

## Comment Quality Metrics

**Good commenting practices lead to**:

1. [OK] Faster onboarding (new developers understand code quickly)
2. [OK] Fewer bugs (complex logic is explained clearly)
3. [OK] Easier maintenance (context is preserved)
4. [OK] Better documentation (docstrings auto-generate API docs)
5. [OK] Reduced support questions (API usage is clear)

**Warning signs**:
- 🚩 Too many comments (code may be too complex)
- 🚩 No comments (code may be under-documented)
- 🚩 Outdated comments (maintenance issue)
- 🚩 Commented-out code (version control issue)
