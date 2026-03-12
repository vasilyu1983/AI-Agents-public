# Payment Testing Patterns

E2E testing patterns for Stripe checkout flows, webhook testing, and subscription state management.

---

## Stripe CLI for Local Webhook Testing

```bash
# Forward events to local webhook endpoint
stripe listen --forward-to localhost:3001/api/stripe/webhook

# Trigger specific events for testing
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_failed
```

---

## Test Card Numbers

| Card | Scenario |
|------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Declined |
| `4000 0000 0000 3220` | 3D Secure required |
| `4000 0025 0000 3155` | Requires authentication |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0000 0000 0077` | Charge succeeds, dispute created |
| `4000 0000 0000 0341` | Attaching card to customer fails |
| `4000 0000 0000 3063` | 3D Secure 2 authentication required |

---

## Playwright E2E for Checkout Flows

When testing Stripe Checkout with dynamic payment methods enabled, Card may not be the default view. Use multiple strategies:

```typescript
async function fillStripeCheckout(page: Page) {
  await page.waitForURL(/checkout\.stripe\.com/, { timeout: 30000 });
  await page.waitForTimeout(3000);

  // With dynamic payment methods, Card might not be pre-selected
  // Use evaluate() to click the Card radio — Stripe's custom components
  // may not respond to standard Playwright clicks
  await page.evaluate(() => {
    const radios = document.querySelectorAll('[role="radio"]');
    for (const radio of radios) {
      if (radio.textContent?.includes('Card')) {
        (radio as HTMLElement).click();
        return;
      }
    }
  });
  await page.waitForTimeout(2000);

  await page.locator('input[name="cardNumber"]').fill('4242424242424242');
  await page.locator('input[name="cardExpiry"]').fill('1234');
  await page.locator('input[name="cardCvc"]').fill('123');

  const nameInput = page.locator('input[name="billingName"]');
  if (await nameInput.isVisible({ timeout: 2000 }).catch(() => false)) {
    await nameInput.fill('Test User');
  }

  await page.locator('button:has-text("Start trial"), button:has-text("Subscribe")').first().click();
  await page.waitForURL(/localhost/, { timeout: 60000 });
}
```

---

## Subscription State Sync for Tests

```typescript
// When Stripe CLI isn't forwarding webhooks, sync state manually
async function syncSubscriptionState(email: string) {
  const customers = await stripe.customers.list({ email, limit: 1 });
  const customerId = customers.data[0]?.id;
  if (!customerId) return;

  const subscriptions = await stripe.subscriptions.list({
    customer: customerId,
    status: 'all',
    limit: 10,
  });

  const active = subscriptions.data.find(
    s => s.status === 'active' || s.status === 'trialing'
  );

  // Upsert to local DB with current Stripe state
  await db.subscriptions.upsert({
    stripe_customer_id: customerId,
    stripe_subscription_id: active?.id,
    tier: active ? getTierFromPriceId(active.items.data[0].price.id) : 'free',
    status: active ? mapStripeStatus(active.status) : 'active',
  });
}
```

---

## Test Environment Setup Checklist

- [ ] Stripe test mode API keys in `.env.local`
- [ ] Stripe CLI installed and authenticated (`stripe login`)
- [ ] Webhook endpoint configured for local forwarding
- [ ] Test customer created in Stripe Dashboard (test mode)
- [ ] Test price IDs configured in environment variables
- [ ] Playwright configured with extended timeouts for Stripe redirects (30s+)
- [ ] Database seeded with test user matching Stripe test customer
