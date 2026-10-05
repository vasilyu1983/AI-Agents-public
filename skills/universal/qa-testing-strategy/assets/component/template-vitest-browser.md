# Component Testing Template: Vitest Browser Mode

Use this template when you want real-browser component coverage without paying full E2E cost.

## Typical use cases

- Form validation and state transitions
- Keyboard navigation and focus behavior
- Loading, empty, and error states
- Stable visual regression for design-system components

## Example

`vitest-browser-react` exports `render`, `renderHook` and `cleanup`; there is no `screen` export. Use the locator object returned by `await render(...)`, and use `userEvent` from `vitest/browser` instead of `@testing-library/user-event`. Check the package README and the Vitest component-testing guide for the Vitest version it requires.

```tsx
import { describe, expect, it, vi } from 'vitest'
import { userEvent } from 'vitest/browser'
import { render } from 'vitest-browser-react'
import { SignupForm } from './SignupForm'

describe('SignupForm', () => {
  it('shows validation and submits valid input', async () => {
    const onSubmit = vi.fn()
    const screen = await render(<SignupForm onSubmit={onSubmit} />)

    await screen.getByRole('button', { name: 'Create account' }).click()
    await expect.element(screen.getByText('Email is required')).toBeVisible()

    await screen.getByLabelText('Email').fill('user@example.com')
    await screen.getByLabelText('Password').fill('correct horse battery staple')
    await userEvent.keyboard('{Tab}') // keyboard flow via vitest/browser userEvent
    await screen.getByRole('button', { name: 'Create account' }).click()

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
