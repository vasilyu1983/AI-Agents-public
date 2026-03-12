# Micro-interactions Design Template

Micro-interactions are small, functional animations that enhance user experience by providing feedback, guiding users, and making interfaces feel alive and responsive. In 2024-2025, micro-interactions are considered essential for modern UX design across both mobile and desktop platforms.

---

## What Are Micro-interactions?

**Definition**: Small, subtle animations or visual responses triggered by user actions that communicate system status, provide feedback, or guide users through tasks.

**Four Components** (Dan Saffer Framework):
1. **Trigger** — What initiates the interaction (user action or system event)
2. **Rules** — What happens during the interaction (logic and constraints)
3. **Feedback** — How users perceive the interaction (visual, audio, haptic)
4. **Loops & Modes** — Ongoing behavior or state changes (repeat, duration, modes)

**Purpose**:
- Acknowledge user actions instantly
- Prevent errors through visual guidance
- Communicate system status (loading, processing, success/error)
- Delight users with polished, responsive UI
- Guide attention to important elements

---

## Core Principles (2024 Best Practices)

### 1. Keep Them Simple and Purposeful
Every micro-interaction must serve a clear function—avoid decorative animations that distract or slow down task completion.

GOOD: Button changes color on hover to indicate interactivity
BAD: Button rotates 360° with confetti animation just for hover

### 2. Provide Instant Feedback
Users expect immediate response (<100ms feels instant). Delayed feedback makes interfaces feel broken or unresponsive.

```
Response time perception:
- <100ms: Instant, feels like direct manipulation
- 100-300ms: Perceptible but still feels fast
- 300-1000ms: Noticeable delay, requires loading indicator
- >1000ms: User loses focus, needs progress indicator
```

### 3. Design with Consistency
Use uniform timing, easing curves, and animation styles across the UI to create predictability and build user trust.

### 4. Use Timing Effectively
Animation duration affects perceived performance and polish:
- **Too fast** (<150ms): Jarring, hard to perceive
- **Just right** (200-400ms): Smooth, professional
- **Too slow** (>600ms): Sluggish, annoying

---

## Common Micro-interaction Patterns

### 1. Button Interactions

#### Hover State
```css
.button {
  background-color: #007bff;
  transition: all 0.2s ease-in-out;
}

.button:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}
```

#### Active/Click State
```css
.button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.1s ease-out;
}
```

#### Loading State
```tsx
// React example with loading button
function LoadingButton({ loading, children, ...props }) {
  return (
    <button {...props} disabled={loading}>
      {loading ? (
        <>
          <Spinner className="animate-spin" />
          <span className="ml-2">Processing...</span>
        </>
      ) : (
        children
      )}
    </button>
  )
}
```

#### Success Animation
```tsx
function SuccessButton() {
  const [success, setSuccess] = useState(false)

  const handleClick = async () => {
    await submitForm()
    setSuccess(true)
    setTimeout(() => setSuccess(false), 2000)
  }

  return (
    <button
      onClick={handleClick}
      className={success ? 'bg-green-500' : 'bg-blue-500'}
    >
      {success ? (
        <>
          <CheckIcon className="animate-check" />
          <span>Success!</span>
        </>
      ) : (
        'Submit'
      )}
    </button>
  )
}
```

---

### 2. Form Input Interactions

#### Focus State with Label Animation
```tsx
// Floating label pattern
import { useState } from 'react'

export function FloatingLabelInput({ label, ...props }) {
  const [isFocused, setIsFocused] = useState(false)
  const [hasValue, setHasValue] = useState(false)

  return (
    <div className="relative">
      <input
        {...props}
        onFocus={() => setIsFocused(true)}
        onBlur={(e) => {
          setIsFocused(false)
          setHasValue(e.target.value !== '')
        }}
        className="w-full px-4 pt-6 pb-2 border rounded-md"
      />
      <label
        className={`
          absolute left-4 transition-all duration-200
          ${isFocused || hasValue
            ? 'top-2 text-xs text-blue-600'
            : 'top-4 text-base text-gray-500'
          }
        `}
      >
        {label}
      </label>
    </div>
  )
}
```

#### Real-time Validation Feedback
```tsx
export function EmailInput() {
  const [email, setEmail] = useState('')
  const [isValid, setIsValid] = useState(null)

  const validateEmail = (value) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return regex.test(value)
  }

  const handleChange = (e) => {
    const value = e.target.value
    setEmail(value)

    if (value.length > 0) {
      setIsValid(validateEmail(value))
    } else {
      setIsValid(null)
    }
  }

  return (
    <div className="relative">
      <input
        type="email"
        value={email}
        onChange={handleChange}
        className={`
          w-full px-4 py-2 border-2 rounded-md transition-all duration-200
          ${isValid === true ? 'border-green-500' : ''}
          ${isValid === false ? 'border-red-500' : ''}
        `}
      />
      {isValid === true && (
        <CheckIcon className="absolute right-3 top-3 text-green-500 animate-scale-in" />
      )}
      {isValid === false && (
        <XIcon className="absolute right-3 top-3 text-red-500 animate-shake" />
      )}
    </div>
  )
}
```

#### Password Strength Indicator
```tsx
export function PasswordInput() {
  const [password, setPassword] = useState('')
  const [strength, setStrength] = useState(0)

  const calculateStrength = (pwd) => {
    let score = 0
    if (pwd.length >= 8) score += 25
    if (pwd.length >= 12) score += 25
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score += 25
    if (/\d/.test(pwd)) score += 15
    if (/[^a-zA-Z0-9]/.test(pwd)) score += 10
    return Math.min(score, 100)
  }

  const handleChange = (e) => {
    const value = e.target.value
    setPassword(value)
    setStrength(calculateStrength(value))
  }

  const getStrengthColor = () => {
    if (strength < 40) return 'bg-red-500'
    if (strength < 70) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getStrengthLabel = () => {
    if (strength < 40) return 'Weak'
    if (strength < 70) return 'Medium'
    return 'Strong'
  }

  return (
    <div>
      <input
        type="password"
        value={password}
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded-md"
      />
      {password && (
        <div className="mt-2">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${getStrengthColor()}`}
              style={{ width: `${strength}%` }}
            />
          </div>
          <p className="text-sm mt-1">{getStrengthLabel()}</p>
        </div>
      )}
    </div>
  )
}
```

---

### 3. Toggle & Switch Interactions

```tsx
export function AnimatedToggle({ checked, onChange }) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`
        relative w-14 h-8 rounded-full transition-colors duration-300
        ${checked ? 'bg-blue-500' : 'bg-gray-300'}
      `}
    >
      <span
        className={`
          absolute top-1 left-1 w-6 h-6 bg-white rounded-full
          transition-transform duration-300 ease-in-out
          ${checked ? 'transform translate-x-6' : ''}
        `}
      />
    </button>
  )
}
```

---

### 4. Loading States

#### Skeleton Screens
```tsx
export function SkeletonCard() {
  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-full" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6" />
      <div className="h-8 bg-gray-200 rounded animate-pulse w-1/3 mt-4" />
    </div>
  )
}
```

#### Progress Indicators
```tsx
export function ProgressBar({ progress }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className="bg-blue-500 h-2 rounded-full transition-all duration-300 ease-out"
        style={{ width: `${progress}%` }}
      />
    </div>
  )
}

// Circular progress
export function CircularProgress({ progress }) {
  const radius = 40
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (progress / 100) * circumference

  return (
    <svg width="100" height="100">
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="#e5e7eb"
        strokeWidth="8"
      />
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        stroke="#3b82f6"
        strokeWidth="8"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform="rotate(-90 50 50)"
        style={{ transition: 'stroke-dashoffset 0.3s ease' }}
      />
    </svg>
  )
}
```

---

### 5. Feedback Notifications

#### Toast Notifications
```tsx
import { useState, useEffect } from 'react'

export function Toast({ message, type = 'success', duration = 3000, onClose }) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(onClose, 300) // Wait for fade-out animation
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  const bgColor = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500',
  }[type]

  return (
    <div
      className={`
        fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white
        transition-all duration-300 ${bgColor}
        ${isVisible ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform -translate-y-2'}
      `}
    >
      {message}
    </div>
  )
}
```

#### Snackbar with Action
```tsx
export function Snackbar({ message, action, onAction, onClose }) {
  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-4 animate-slide-up">
      <span>{message}</span>
      {action && (
        <button
          onClick={onAction}
          className="text-blue-400 hover:text-blue-300 font-medium"
        >
          {action}
        </button>
      )}
      <button onClick={onClose} className="ml-2 hover:text-gray-300">
        ×
      </button>
    </div>
  )
}
```

---

### 6. Drag and Drop Interactions

```tsx
import { useState } from 'react'

export function DraggableItem({ id, children }) {
  const [isDragging, setIsDragging] = useState(false)

  return (
    <div
      draggable
      onDragStart={(e) => {
        setIsDragging(true)
        e.dataTransfer.effectAllowed = 'move'
        e.dataTransfer.setData('text/html', e.target.parentNode.innerHTML)
      }}
      onDragEnd={() => setIsDragging(false)}
      className={`
        p-4 border rounded-lg cursor-move transition-all duration-200
        ${isDragging
          ? 'opacity-50 scale-95 rotate-2'
          : 'opacity-100 scale-100 hover:shadow-md'
        }
      `}
    >
      {children}
    </div>
  )
}

export function DropZone({ onDrop, children }) {
  const [isOver, setIsOver] = useState(false)

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setIsOver(true)
      }}
      onDragLeave={() => setIsOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setIsOver(false)
        onDrop(e)
      }}
      className={`
        min-h-[200px] border-2 border-dashed rounded-lg p-4
        transition-all duration-200
        ${isOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
      `}
    >
      {children}
    </div>
  )
}
```

---

### 7. Like/Favorite Animations

```tsx
export function LikeButton() {
  const [isLiked, setIsLiked] = useState(false)

  return (
    <button
      onClick={() => setIsLiked(!isLiked)}
      className="relative p-2 rounded-full hover:bg-gray-100 transition-colors"
    >
      <svg
        className={`
          w-6 h-6 transition-all duration-300
          ${isLiked ? 'scale-110 fill-red-500 stroke-red-500' : 'fill-none stroke-gray-400'}
        `}
        viewBox="0 0 24 24"
        strokeWidth="2"
      >
        <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" />
      </svg>
      {isLiked && (
        <span className="absolute inset-0 rounded-full bg-red-500 opacity-0 animate-ping-once" />
      )}
    </button>
  )
}
```

---

## Animation Easing Curves

```css
/* Timing functions for different effects */

/* Default (smooth acceleration/deceleration) */
transition: all 0.3s ease;

/* Start slow, accelerate (entering elements) */
transition: all 0.3s ease-out;

/* Start fast, decelerate (exiting elements) */
transition: all 0.3s ease-in;

/* Sharp acceleration (material design) */
transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);

/* Bounce effect */
transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);

/* Spring effect */
transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
```

---

## Accessibility Considerations

### 1. Respect User Preferences
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 2. Provide Alternative Feedback
Never rely solely on motion—provide additional visual or text feedback for users with reduced motion preferences.

### 3. Keyboard Interaction
Ensure all micro-interactions triggered by mouse also work with keyboard (focus states, Enter/Space keys).

```tsx
// Good: Works with both mouse and keyboard
<button
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick()
    }
  }}
  className="hover:bg-blue-600 focus:ring-2 focus:ring-blue-500"
>
  Click me
</button>
```

---

## Common Mistakes to Avoid

AVOID: Over-animation (too many simultaneous animations distract users)
AVOID: Slow animations (>600ms feels sluggish)
AVOID: Meaningless animation (decorative effects without functional purpose)
AVOID: Missing feedback (no response to user actions)
AVOID: Inconsistent timing (different durations for similar interactions)
AVOID: Ignoring reduced motion (forcing animations on users with motion sensitivities)

---

## Testing Micro-interactions

**Checklist:**
- [ ] Animations feel smooth at 60fps
- [ ] Timing is appropriate (200-400ms for most transitions)
- [ ] Feedback is instant (<100ms for critical interactions)
- [ ] Works on low-end devices without janking
- [ ] Respects prefers-reduced-motion
- [ ] All states are visually distinct (hover, active, focus, disabled)
- [ ] Keyboard users get equivalent feedback
- [ ] Animations don't block interaction (no forced waiting)

---

## Resources

- **Framer Motion**: [framer.com/motion](https://www.framer.com/motion/) (React animation library)
- **GSAP**: [greensock.com/gsap](https://greensock.com/gsap/) (Professional animation platform)
- **Lottie**: [airbnb.design/lottie](https://airbnb.design/lottie/) (JSON-based animations)
- **Interaction Design Foundation**: [interaction-design.org](https://www.interaction-design.org/literature/article/micro-interactions-ux) (Micro-interactions UX)
- **Material Design 3 Motion**: [m3.material.io/styles/motion](https://m3.material.io/styles/motion/overview) (M3 easing, duration, transitions)

---

## Related Templates

- `template-state-machines.md` — Managing complex interaction states
- `template-animation-library.md` — Using Framer Motion and GSAP
- [template-wcag-testing.md](../accessibility/template-wcag-testing.md) — Accessibility testing (includes reduced motion)
