# Component Testing Template: Vitest Browser Mode

Use this template when you want real-browser component coverage without paying full E2E cost.

## Typical use cases

- Form validation and state transitions
- Keyboard navigation and focus behavior
- Loading, empty, and error states
- Stable visual regression for design-system components

## Example

```typescript
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from 'vitest-browser-react'
import userEvent from '@testing-library/user-event'
import { SignupForm } from './SignupForm'

describe('SignupForm', () => {
  it('shows validation and submits valid input', async () => {
    const onSubmit = vi.fn()
    const user = userEvent.setup()

    render(<SignupForm onSubmit={onSubmit} />)

    await user.click(screen.getByRole('button', { name: 'Create account' }))
    await expect.element(screen.getByText('Email is required')).toBeVisible()

    await user.type(screen.getByLabelText('Email'), 'user@example.com')
    await user.type(screen.getByLabelText('Password'), 'correct horse battery staple')
    await user.click(screen.getByRole('button', { name: 'Create account' }))

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'correct horse battery staple'
    })
  })
})
```

## Accessibility smoke

- Add an accessibility pass in the same browser harness you use for the component.
- Prefer role, label, and keyboard-flow assertions alongside automated axe checks.
- Keep the automation narrow and repeatable; manual review is still required for WCAG 2.2 coverage.

## Defaults

- Prefer role, label, and text queries over CSS selectors
- Keep mocks at the component boundary
- Use screenshot diffs only for stable states
- Escalate to E2E only when the risk crosses page boundaries
