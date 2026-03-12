# shadcn/ui Component Library Template

shadcn/ui is a collection of beautifully designed, accessible, and customizable React components built with Radix UI and Tailwind CSS. Unlike traditional UI libraries, shadcn/ui is not installed as a dependency—components are copied directly into your project for full ownership and customization.

---

## Key Characteristics

**Architecture**: Copy-paste component system (not an NPM package)
**Styling**: Tailwind CSS with CSS variables for theming
**Primitives**: Built on Radix UI (accessible, unstyled components)
**TypeScript**: Full TypeScript support with type safety
**Customization**: Full component ownership—modify as needed
**Accessibility**: Strong a11y defaults; verify WCAG 2.2 AA at the app level

**Best for**:
- Projects requiring design flexibility
- Teams that want component ownership
- Tailwind CSS users
- Modern React applications with Next.js/Vite

---

## Installation & Setup

### Prerequisites
```bash
# Ensure you have a React project with Tailwind CSS
npm install tailwindcss
npx tailwindcss init -p
```

### Initialize shadcn/ui
```bash
npx shadcn-ui@latest init
```

**Configuration prompts:**
- Would you like to use TypeScript? **Yes**
- Which style would you like to use? **Default / New York**
- Which color would you like to use as base color? **Slate / Zinc / Neutral**
- Where is your global CSS file? **src/app/globals.css**
- Would you like to use CSS variables for colors? **Yes** (recommended)
- Where is your tailwind.config.js? **tailwind.config.ts**
- Configure the import alias for components? **@/components**
- Configure the import alias for utils? **@/lib/utils**

### Add Components
```bash
# Add individual components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card

# Add multiple components at once
npx shadcn-ui@latest add button input card dialog
```

---

## Project Structure

```
src/
├── components/
│   └── ui/              # shadcn/ui components (copied)
│       ├── button.tsx
│       ├── input.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       └── ...
├── lib/
│   └── utils.ts         # cn() utility for class merging
├── app/
│   ├── globals.css      # Tailwind + CSS variables
│   └── layout.tsx
└── tailwind.config.ts   # Tailwind configuration
```

---

## Core Components Usage

### Button Component

```tsx
import { Button } from "@/components/ui/button"

export function ButtonDemo() {
  return (
    <div className="space-x-2">
      {/* Variants */}
      <Button variant="default">Default</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>

      {/* Sizes */}
      <Button size="sm">Small</Button>
      <Button size="default">Default</Button>
      <Button size="lg">Large</Button>
      <Button size="icon">
        <Icons.plus className="h-4 w-4" />
      </Button>

      {/* States */}
      <Button disabled>Disabled</Button>
      <Button loading>Loading</Button>
    </div>
  )
}
```

### Form Components

```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

export function FormDemo() {
  return (
    <form className="space-y-4">
      {/* Text Input */}
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="you@example.com"
        />
      </div>

      {/* Select Dropdown */}
      <div className="space-y-2">
        <Label htmlFor="country">Country</Label>
        <Select>
          <SelectTrigger id="country">
            <SelectValue placeholder="Select a country" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="us">United States</SelectItem>
            <SelectItem value="uk">United Kingdom</SelectItem>
            <SelectItem value="ca">Canada</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Checkbox */}
      <div className="flex items-center space-x-2">
        <Checkbox id="terms" />
        <Label htmlFor="terms">Accept terms and conditions</Label>
      </div>

      {/* Radio Group */}
      <RadioGroup defaultValue="option-1">
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="option-1" id="option-1" />
          <Label htmlFor="option-1">Option 1</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="option-2" id="option-2" />
          <Label htmlFor="option-2">Option 2</Label>
        </div>
      </RadioGroup>

      <Button type="submit">Submit</Button>
    </form>
  )
}
```

### Card Component

```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export function CardDemo() {
  return (
    <Card className="w-[380px]">
      <CardHeader>
        <CardTitle>Create Project</CardTitle>
        <CardDescription>Deploy your new project in one-click.</CardDescription>
      </CardHeader>
      <CardContent>
        <form>
          <div className="grid w-full items-center gap-4">
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="name">Name</Label>
              <Input id="name" placeholder="Name of your project" />
            </div>
          </div>
        </form>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline">Cancel</Button>
        <Button>Deploy</Button>
      </CardFooter>
    </Card>
  )
}
```

### Dialog (Modal) Component

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function DialogDemo() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Edit Profile</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit profile</DialogTitle>
          <DialogDescription>
            Make changes to your profile here. Click save when you're done.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input id="name" value="Pedro Duarte" className="col-span-3" />
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Save changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
```

---

## Theming & Customization

### CSS Variables (globals.css)

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    /* ... other dark mode variables */
  }
}
```

### Customizing Components

Since components are copied into your project, you can modify them directly:

```tsx
// components/ui/button.tsx

// Add custom variants
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md...",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground...",
        // Add your custom variant
        custom: "bg-gradient-to-r from-purple-500 to-pink-500 text-white...",
      },
    },
  }
)

// Usage
<Button variant="custom">Custom Button</Button>
```

---

## Form Handling with React Hook Form + Zod

```tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
  email: z.string().email({
    message: "Please enter a valid email address.",
  }),
})

export function ProfileForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      email: "",
    },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="shadcn" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

---

## Accessibility Features

shadcn/ui components are built on Radix UI, which provides:

- **Keyboard navigation** — Full keyboard support (Tab, Enter, Escape, Arrow keys)
- **ARIA attributes** — Proper aria-* attributes automatically applied
- **Focus management** — Focus trapping in modals, proper focus indicators
- **Screen reader support** — Descriptive labels and live regions
- **Touch targets** — Minimum 44x44px touch targets on mobile

### Example: Dialog Accessibility
```tsx
// Radix UI Dialog handles:
// - Focus trap (can't Tab outside modal)
// - Escape key to close
// - Click outside to close
// - aria-describedby for description
// - Focus restoration after close
// - Scroll locking
```

---

## Dark Mode Support

shadcn/ui uses CSS variables for easy dark mode:

```tsx
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}

// Theme toggle component
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { setTheme, theme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```

---

## Best Practices

### 1. Component Composition
```tsx
// GOOD: Compose with smaller components
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>

// BAD: Monolithic component
<Card title="Title" content="Content" />
```

### 2. Use the cn() Utility
```tsx
import { cn } from "@/lib/utils"

// Merge classes conditionally
<Button className={cn(
  "base-classes",
  isActive && "active-classes",
  isPrimary && "primary-classes"
)} />
```

### 3. Extend Components
```tsx
// Create wrapper components for project-specific variants
import { Button } from "@/components/ui/button"

export function SubmitButton({ children, ...props }: ButtonProps) {
  return (
    <Button
      type="submit"
      className="w-full"
      {...props}
    >
      {children}
    </Button>
  )
}
```

### 4. Form Validation Pattern
```tsx
// Always use Zod + React Hook Form for complex forms
// Built-in validation + type safety + accessibility
```

---

## Component Checklist

Essential shadcn/ui components to add:

**Layout & Structure:**
- [ ] Card
- [ ] Separator
- [ ] Aspect Ratio
- [ ] Scroll Area

**Forms:**
- [ ] Input
- [ ] Textarea
- [ ] Select
- [ ] Checkbox
- [ ] Radio Group
- [ ] Switch
- [ ] Slider
- [ ] Label
- [ ] Form

**Feedback:**
- [ ] Alert
- [ ] Alert Dialog
- [ ] Toast
- [ ] Progress
- [ ] Badge

**Navigation:**
- [ ] Command (Command palette)
- [ ] Menu (Dropdown menu)
- [ ] Navigation Menu
- [ ] Tabs
- [ ] Breadcrumb

**Overlays:**
- [ ] Dialog
- [ ] Sheet (Slide-over)
- [ ] Popover
- [ ] Tooltip
- [ ] Hover Card

**Data Display:**
- [ ] Table
- [ ] Avatar
- [ ] Calendar
- [ ] Accordion

---

## Resources

- **Official Docs**: https://ui.shadcn.com/
- **GitHub**: https://github.com/shadcn-ui/ui
- **Component Examples**: https://ui.shadcn.com/examples
- **Figma Kit**: Available in community files
- **Theme Generator**: https://ui.shadcn.com/themes

---

## Related Templates

- `template-radix-ui.md` — Unstyled primitives (shadcn/ui's foundation)
- [template-design-system.md](../design-systems/template-design-system.md) — Design system template
- [template-wcag-testing.md](../accessibility/template-wcag-testing.md) — Accessibility testing
