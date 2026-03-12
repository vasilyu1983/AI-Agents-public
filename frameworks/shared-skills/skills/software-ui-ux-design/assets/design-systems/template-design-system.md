# Design System Template

Use this template for building scalable, consistent design systems with tokens, components, and documentation.

## Design System Architecture

```
design-system/
├── tokens/              # Design tokens (colors, spacing, typography)
│   ├── colors.json
│   ├── spacing.json
│   ├── typography.json
│   └── shadows.json
├── primitives/          # Base components (no business logic)
│   ├── Button/
│   ├── Input/
│   ├── Select/
│   └── Card/
├── patterns/            # Composite components
│   ├── Form/
│   ├── Navigation/
│   └── DataTable/
├── layouts/             # Layout primitives
│   ├── Stack/
│   ├── Grid/
│   └── Container/
├── utils/               # Utility functions
│   ├── classNames.ts
│   └── tokens.ts
└── docs/                # Storybook documentation
    ├── Introduction.stories.mdx
    └── DesignPrinciples.stories.mdx
```

## Design Tokens

### Color Tokens (JSON format)

```json
// tokens/colors.json
{
  "color": {
    "brand": {
      "primary": {
        "50": { "value": "#eff6ff", "type": "color" },
        "100": { "value": "#dbeafe", "type": "color" },
        "200": { "value": "#bfdbfe", "type": "color" },
        "300": { "value": "#93c5fd", "type": "color" },
        "400": { "value": "#60a5fa", "type": "color" },
        "500": { "value": "#3b82f6", "type": "color" },
        "600": { "value": "#2563eb", "type": "color" },
        "700": { "value": "#1d4ed8", "type": "color" },
        "800": { "value": "#1e40af", "type": "color" },
        "900": { "value": "#1e3a8a", "type": "color" }
      }
    },
    "semantic": {
      "success": { "value": "{color.green.600}", "type": "color" },
      "error": { "value": "{color.red.600}", "type": "color" },
      "warning": { "value": "{color.yellow.600}", "type": "color" },
      "info": { "value": "{color.blue.600}", "type": "color" }
    },
    "text": {
      "primary": { "value": "{color.gray.900}", "type": "color" },
      "secondary": { "value": "{color.gray.600}", "type": "color" },
      "disabled": { "value": "{color.gray.400}", "type": "color" },
      "inverse": { "value": "{color.white}", "type": "color" }
    },
    "background": {
      "primary": { "value": "{color.white}", "type": "color" },
      "secondary": { "value": "{color.gray.50}", "type": "color" },
      "tertiary": { "value": "{color.gray.100}", "type": "color" }
    },
    "border": {
      "default": { "value": "{color.gray.300}", "type": "color" },
      "focus": { "value": "{color.brand.primary.500}", "type": "color" },
      "error": { "value": "{color.semantic.error}", "type": "color" }
    }
  }
}
```

### Typography Tokens

```json
// tokens/typography.json
{
  "font": {
    "family": {
      "sans": {
        "value": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "type": "fontFamily"
      },
      "mono": {
        "value": "'Fira Code', 'Courier New', monospace",
        "type": "fontFamily"
      }
    },
    "size": {
      "xs": { "value": "0.75rem", "type": "fontSize" },
      "sm": { "value": "0.875rem", "type": "fontSize" },
      "base": { "value": "1rem", "type": "fontSize" },
      "lg": { "value": "1.125rem", "type": "fontSize" },
      "xl": { "value": "1.25rem", "type": "fontSize" },
      "2xl": { "value": "1.5rem", "type": "fontSize" },
      "3xl": { "value": "1.875rem", "type": "fontSize" },
      "4xl": { "value": "2.25rem", "type": "fontSize" }
    },
    "weight": {
      "normal": { "value": "400", "type": "fontWeight" },
      "medium": { "value": "500", "type": "fontWeight" },
      "semibold": { "value": "600", "type": "fontWeight" },
      "bold": { "value": "700", "type": "fontWeight" }
    },
    "lineHeight": {
      "tight": { "value": "1.25", "type": "lineHeight" },
      "normal": { "value": "1.5", "type": "lineHeight" },
      "relaxed": { "value": "1.75", "type": "lineHeight" }
    }
  }
}
```

### Spacing Tokens

```json
// tokens/spacing.json
{
  "spacing": {
    "0": { "value": "0", "type": "spacing" },
    "1": { "value": "0.25rem", "type": "spacing" },
    "2": { "value": "0.5rem", "type": "spacing" },
    "3": { "value": "0.75rem", "type": "spacing" },
    "4": { "value": "1rem", "type": "spacing" },
    "5": { "value": "1.25rem", "type": "spacing" },
    "6": { "value": "1.5rem", "type": "spacing" },
    "8": { "value": "2rem", "type": "spacing" },
    "10": { "value": "2.5rem", "type": "spacing" },
    "12": { "value": "3rem", "type": "spacing" },
    "16": { "value": "4rem", "type": "spacing" },
    "20": { "value": "5rem", "type": "spacing" }
  }
}
```

### Token Conversion to CSS Variables

```typescript
// utils/tokens.ts
import colors from '../tokens/colors.json'
import spacing from '../tokens/spacing.json'
import typography from '../tokens/typography.json'

export function generateCSSVariables() {
  const cssVars: Record<string, string> = {}

  // Convert color tokens
  function flattenTokens(obj: any, prefix = '') {
    for (const [key, value] of Object.entries(obj)) {
      if (value && typeof value === 'object' && 'value' in value) {
        cssVars[`--${prefix}${key}`] = (value as any).value
      } else if (typeof value === 'object') {
        flattenTokens(value, `${prefix}${key}-`)
      }
    }
  }

  flattenTokens(colors.color, 'color-')
  flattenTokens(spacing.spacing, 'spacing-')
  flattenTokens(typography.font, 'font-')

  return cssVars
}

// Export as CSS string
export function getCSSVariablesString() {
  const vars = generateCSSVariables()
  return Object.entries(vars)
    .map(([key, value]) => `  ${key}: ${value};`)
    .join('\n')
}
```

## Base Component: Button

```typescript
// primitives/Button/Button.tsx
import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../utils/classNames'

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-500',
        secondary: 'bg-secondary-600 text-white hover:bg-secondary-700 focus-visible:ring-secondary-500',
        outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-primary-500',
        ghost: 'text-gray-700 hover:bg-gray-100 focus-visible:ring-primary-500',
        destructive: 'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500'
      },
      size: {
        sm: 'h-9 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-11 px-6 text-lg'
      },
      fullWidth: {
        true: 'w-full'
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md'
    }
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      loading,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size, fullWidth }), className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg
            className="mr-2 h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {!loading && leftIcon && <span className="mr-2">{leftIcon}</span>}
        {children}
        {!loading && rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    )
  }
)

Button.displayName = 'Button'
```

### Button Storybook Documentation

```typescript
// primitives/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'
import { SearchIcon, ArrowRightIcon } from 'lucide-react'

const meta: Meta<typeof Button> = {
  title: 'Primitives/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline', 'ghost', 'destructive'],
      description: 'Button visual style'
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Button size'
    },
    loading: {
      control: 'boolean',
      description: 'Shows loading spinner'
    },
    disabled: {
      control: 'boolean',
      description: 'Disables button interaction'
    }
  }
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: {
    children: 'Button',
    variant: 'primary'
  }
}

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  )
}

export const AllSizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  )
}

export const WithIcons: Story = {
  render: () => (
    <div className="flex gap-4">
      <Button leftIcon={<SearchIcon className="h-4 w-4" />}>
        Search
      </Button>
      <Button rightIcon={<ArrowRightIcon className="h-4 w-4" />}>
        Continue
      </Button>
    </div>
  )
}

export const Loading: Story = {
  args: {
    children: 'Loading',
    loading: true
  }
}

export const Disabled: Story = {
  args: {
    children: 'Disabled',
    disabled: true
  }
}

export const FullWidth: Story = {
  args: {
    children: 'Full Width Button',
    fullWidth: true
  }
}
```

## Composite Pattern: Form

```typescript
// patterns/Form/Form.tsx
import React from 'react'
import { cn } from '../../utils/classNames'

// Form Root
export interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {}

export const Form = React.forwardRef<HTMLFormElement, FormProps>(
  ({ className, ...props }, ref) => {
    return (
      <form
        ref={ref}
        className={cn('space-y-6', className)}
        {...props}
      />
    )
  }
)

Form.displayName = 'Form'

// Form Field
export interface FormFieldProps extends React.HTMLAttributes<HTMLDivElement> {
  error?: string
}

export const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({ className, error, children, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('space-y-2', className)} {...props}>
        {children}
        {error && (
          <p className="text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
      </div>
    )
  }
)

FormField.displayName = 'FormField'

// Form Label
export interface FormLabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean
}

export const FormLabel = React.forwardRef<HTMLLabelElement, FormLabelProps>(
  ({ className, required, children, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn('block text-sm font-medium text-gray-700', className)}
        {...props}
      >
        {children}
        {required && <span className="ml-1 text-red-600" aria-label="required">*</span>}
      </label>
    )
  }
)

FormLabel.displayName = 'FormLabel'

// Form Input
export interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
}

export const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm',
          'focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500',
          'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500',
          error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
          className
        )}
        {...props}
      />
    )
  }
)

FormInput.displayName = 'FormInput'

// Usage Example
export function ContactForm() {
  return (
    <Form>
      <FormField>
        <FormLabel htmlFor="name" required>
          Name
        </FormLabel>
        <FormInput id="name" name="name" placeholder="John Doe" />
      </FormField>

      <FormField error="Invalid email address">
        <FormLabel htmlFor="email" required>
          Email
        </FormLabel>
        <FormInput
          id="email"
          name="email"
          type="email"
          placeholder="john@example.com"
          error
        />
      </FormField>

      <FormField>
        <FormLabel htmlFor="message">Message</FormLabel>
        <textarea
          id="message"
          name="message"
          rows={4}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
      </FormField>

      <Button type="submit">Submit</Button>
    </Form>
  )
}
```

## Layout Primitives: Stack

```typescript
// layouts/Stack/Stack.tsx
import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../utils/classNames'

const stackVariants = cva('flex', {
  variants: {
    direction: {
      horizontal: 'flex-row',
      vertical: 'flex-col'
    },
    spacing: {
      0: 'gap-0',
      1: 'gap-1',
      2: 'gap-2',
      3: 'gap-3',
      4: 'gap-4',
      6: 'gap-6',
      8: 'gap-8'
    },
    align: {
      start: 'items-start',
      center: 'items-center',
      end: 'items-end',
      stretch: 'items-stretch'
    },
    justify: {
      start: 'justify-start',
      center: 'justify-center',
      end: 'justify-end',
      between: 'justify-between',
      around: 'justify-around'
    }
  },
  defaultVariants: {
    direction: 'vertical',
    spacing: 4,
    align: 'stretch',
    justify: 'start'
  }
})

export interface StackProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof stackVariants> {}

export const Stack = React.forwardRef<HTMLDivElement, StackProps>(
  ({ className, direction, spacing, align, justify, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(stackVariants({ direction, spacing, align, justify }), className)}
        {...props}
      />
    )
  }
)

Stack.displayName = 'Stack'
```

## Documentation: Design Principles

```mdx
<!-- docs/DesignPrinciples.stories.mdx -->
import { Meta } from '@storybook/blocks'

<Meta title="Introduction/Design Principles" />

# Design Principles

Our design system is built on four core principles:

## 1. Consistency

Consistent visual language across all products and platforms.

- Use design tokens for colors, spacing, and typography
- Follow established patterns for common interactions
- Maintain consistent naming conventions

## 2. Accessibility

Inclusive design that works for everyone.

- WCAG 2.2 AA compliance minimum
- Keyboard navigation support
- Screen reader compatible
- 4.5:1 contrast ratio for text

## 3. Flexibility

Adaptable components that work in various contexts.

- Composable component API
- Responsive design by default
- Theme customization support
- Dark mode compatibility

## 4. Developer Experience

Easy to use and well-documented.

- TypeScript support
- Comprehensive Storybook documentation
- Clear naming conventions
- Minimal API surface

## Component API Design

### Composition over Configuration

Prefer composition patterns:

```tsx
// Good - Composition
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>

// Avoid - Configuration
<Card title="Title" content="Content" />
```

### Consistent Prop Naming

- `variant` for visual variations (primary, secondary, outline)
- `size` for size variations (sm, md, lg)
- `disabled` for disabled state
- `loading` for loading state
- `error` for error state

### Forwarded Refs

All components should forward refs:

```tsx
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>((props, ref) => {
  return <button ref={ref} {...props} />
})
```
```

## Testing Design System Components

```typescript
// primitives/Button/Button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    await userEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies variant styles', () => {
    const { rerender } = render(<Button variant="primary">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-primary-600')

    rerender(<Button variant="outline">Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('border')
  })

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
    expect(screen.getByRole('button')).toContainHTML('svg') // Spinner
  })

  it('forwards ref', () => {
    const ref = React.createRef<HTMLButtonElement>()
    render(<Button ref={ref}>Button</Button>)
    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
  })
})
```

## Versioning and Changelog

```markdown
# Changelog

## [2.1.0] - 2024-01-15

### Added
- New `Toast` component for notifications
- `fullWidth` prop for `Button` component
- Dark mode support for all components

### Changed
- Updated focus ring styles to improve visibility
- Improved TypeScript types for better IDE support

### Fixed
- Fixed accessibility issue in `Modal` component
- Fixed z-index stacking in `Dropdown` component

### Breaking Changes
- Renamed `color` prop to `variant` in `Button` component
  - Migration: Replace `color="primary"` with `variant="primary"`
```

## Best Practices Checklist

- [ ] Use design tokens for all design decisions
- [ ] Document all components in Storybook
- [ ] Include accessibility tests for all components
- [ ] Provide TypeScript types
- [ ] Forward refs in all components
- [ ] Use composition over configuration
- [ ] Test components in isolation
- [ ] Version design system packages
- [ ] Provide migration guides for breaking changes
- [ ] Support theme customization
- [ ] Include dark mode support
- [ ] Document component API clearly
- [ ] Provide code examples

## Related Resources

- [Building Design Systems (Brad Frost)](https://atomicdesign.bradfrost.com/)
- [Design Tokens (W3C Community Group)](https://design-tokens.github.io/community-group/)
- [Storybook Best Practices](https://storybook.js.org/docs/react/writing-stories/introduction)
