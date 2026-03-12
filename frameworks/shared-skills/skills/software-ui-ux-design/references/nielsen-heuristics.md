# Nielsen's 10 Usability Heuristics — Detailed Guide

Jakob Nielsen's 10 usability heuristics are general principles for interaction design. They were developed in 1990 (with Rolf Molich) and refined in 1994 based on factor analysis of 249 usability problems. These heuristics have remained relevant and unchanged since 1994.

---

## 1. Visibility of System Status

**Principle**: The design should always keep users informed about what is going on, through appropriate feedback within a reasonable amount of time.

### Why It Matters
When users know the current system status, they learn the outcome of their prior interactions and determine next steps. Predictable interactions create trust in the product and the brand.

### Implementation Guidelines
- Provide immediate feedback for user actions
- Show loading states for async operations
- Display progress indicators for multi-step processes
- Confirm successful actions (visual feedback, messages)
- Update UI state to reflect system changes

### Good Examples
- Progress bar showing file upload percentage
- "Saving..." indicator when auto-saving documents
- Typing indicator in messaging apps ("John is typing...")
- Shopping cart icon updating with item count
- Read receipts in email and messaging

### Bad Examples
- Button click with no visual response
- Long process with no progress indication
- Form submission with no confirmation
- Background sync with no status update

### Code Example (React)
```jsx
function UploadButton() {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  return (
    <div>
      <button disabled={isUploading}>
        {isUploading ? `Uploading... ${progress}%` : 'Upload File'}
      </button>
      {isUploading && <ProgressBar value={progress} />}
    </div>
  );
}
```

---

## 2. Match Between System and the Real World

**Principle**: The design should speak the users' language. Use words, phrases, and concepts familiar to the user, rather than internal jargon. Follow real-world conventions, making information appear in a natural and logical order.

### Why It Matters
The way you should design depends very much on your specific users. Terms, concepts, icons, and images that seem perfectly clear to you might be unfamiliar or confusing to your users.

### Implementation Guidelines
- Use user-centric language, not technical jargon
- Follow familiar mental models and metaphors
- Respect cultural conventions (dates, names, numbers)
- Order information logically based on user tasks
- Use recognizable icons and symbols

### Good Examples
- Trash/recycle bin icon for delete
- Shopping cart metaphor for e-commerce
- Folder structure for file organization
- Calendar interface resembling physical calendars
- "Archive" instead of "soft delete"

### Bad Examples
- Technical error codes shown to users ("Error 500")
- Industry jargon ("optimize your CTR")
- Unfamiliar icons without labels
- Form fields in database order, not logical order
- American date format (MM/DD/YYYY) for European users

### Checklist
- [ ] Terminology matches user vocabulary (not developers')
- [ ] Icons are universally recognized or have labels
- [ ] Date/time formats match user locale
- [ ] Information grouped by user mental models
- [ ] Metaphors align with user experience

---

## 3. User Control and Freedom

**Principle**: Users often perform actions by mistake. They need a clearly marked "emergency exit" to leave the unwanted action without having to go through an extended process.

### Why It Matters
Supporting undo and redo helps users recover from errors and encourages exploration of unfamiliar options.

### Implementation Guidelines
- Provide undo/redo functionality
- Allow users to cancel ongoing operations
- Enable easy navigation backward
- Support exiting from multi-step flows
- Avoid forced paths without escape

### Good Examples
- Undo/redo in text editors
- "Restore from trash" for deleted items
- Cancel button on all modal dialogs
- Back button always available
- Gmail's "Undo send" feature
- Browser back button navigation

### Bad Examples
- Irreversible destructive actions without confirmation
- Modal dialogs without close button
- Multi-step forms without back navigation
- Forced linear flows without exit
- Auto-save without version history

### Pattern: Confirmation Before Destructive Actions
```jsx
function DeleteButton({ onDelete }) {
  const [confirmOpen, setConfirmOpen] = useState(false);

  return (
    <>
      <button onClick={() => setConfirmOpen(true)}>
        Delete
      </button>

      {confirmOpen && (
        <ConfirmDialog
          title="Delete this item?"
          message="This action cannot be undone."
          onConfirm={() => {
            onDelete();
            setConfirmOpen(false);
          }}
          onCancel={() => setConfirmOpen(false)}
        />
      )}
    </>
  );
}
```

---

## 4. Consistency and Standards

**Principle**: Users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform and industry conventions.

### Why It Matters
Jakob's Law states that users spend most of their time on other sites, so they prefer your site to work the same way as all the other sites they already know.

### Types of Consistency

**1. Internal Consistency**
- Consistent terminology throughout the app
- Same components behave the same way
- Uniform visual style (colors, typography, spacing)

**2. External Consistency**
- Follow platform conventions (iOS HIG, Material Design)
- Respect browser defaults (link colors, button styles)
- Use common patterns (shopping cart, search icon)

**3. Consistency Standards**
- Logo in top-left links to homepage
- Search bar in top-right or center header
- Primary action button on the right
- Confirmation dialogs: Cancel left, Confirm right

### Implementation Guidelines
- Use a design system for consistent components
- Follow platform-specific patterns
- Maintain consistent terminology
- Apply consistent spacing and alignment
- Standardize interaction patterns

### Good Examples
- Blue underlined text for links (web convention)
- Swipe actions consistent across all list items
- Save icon always uses same symbol
- Error messages formatted consistently
- Submit buttons always labeled "Submit" (not varied)

### Bad Examples
- "Submit" on one form, "Send" on another (same action)
- Delete icon different in various parts of app
- Inconsistent button placement
- Mixed design patterns (iOS + Material Design)
- Different interaction methods for same action

### Checklist
- [ ] Design system in use
- [ ] Platform guidelines followed
- [ ] Terminology consistent throughout
- [ ] Component behaviors standardized
- [ ] Visual styles unified

---

## 5. Error Prevention

**Principle**: Good error messages are important, but the best designs carefully prevent problems from occurring in the first place. Either eliminate error-prone conditions or check for them and present users with a confirmation option before they commit to the action.

### Types of Errors

**1. Slips** — Unconscious errors caused by inattention
- User knows correct action but executes it incorrectly
- Prevention: Constraints, helpful defaults, good affordances

**2. Mistakes** — Conscious errors based on mismatch between user's mental model and design
- User has wrong goal or mental model
- Prevention: Clear labels, helpful hints, better onboarding

### Implementation Guidelines
- Use constraints to prevent invalid input
- Provide helpful defaults
- Disable invalid actions rather than showing errors
- Show inline validation as users type
- Use confirmation for destructive actions
- Offer suggestions and autocomplete

### Good Examples
- Date picker instead of free text date entry
- Disabled "Submit" button until form is valid
- Email autocomplete from contacts
- Spell check in text editors
- File type restrictions on upload
- Confirmation before deleting account

### Bad Examples
- Free-form text for structured data (phone, credit card)
- Allowing submission of invalid forms (then showing errors)
- No confirmation for destructive actions
- Cryptic validation rules
- Silent failures

### Pattern: Inline Validation
```jsx
function EmailInput() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');

  const validateEmail = (value) => {
    if (!value.includes('@')) {
      setError('Please enter a valid email address');
    } else {
      setError('');
    }
  };

  return (
    <div>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        onBlur={(e) => validateEmail(e.target.value)}
        aria-invalid={!!error}
        aria-describedby="email-error"
      />
      {error && <span id="email-error" role="alert">{error}</span>}
    </div>
  );
}
```

### Pattern: Smart Defaults
```jsx
// Default to user's timezone
const defaultDate = new Date();

// Default country from user's locale
const defaultCountry = getUserCountry();

// Prefill known information
const defaultEmail = user.email;
```

---

## 6. Recognition Rather Than Recall

**Principle**: Minimize the user's memory load by making elements, actions, and options visible. The user should not have to remember information from one part of the interface to another. Information required to use the design should be visible or easily retrievable when needed.

### Why It Matters
Humans have limited short-term memory. Recognition (seeing and choosing) is easier than recall (remembering from memory).

### Implementation Guidelines
- Make options visible (don't hide in menus)
- Show recent/frequent actions
- Display context and progress in multi-step flows
- Use breadcrumbs for navigation
- Persist search history
- Show keyboard shortcuts in menus

### Good Examples
- Autocomplete in search boxes
- Recently used items/documents
- Breadcrumb navigation showing location
- Step indicators in multi-page forms
- Command palettes showing shortcuts
- Visible toolbar vs hidden gestures

### Bad Examples
- Gesture-only controls with no visual cues
- Complex keyboard shortcuts with no hints
- Multi-step forms without progress indicator
- No indication of current page in navigation
- Hidden features without discoverability

### Pattern: Breadcrumbs
```jsx
function Breadcrumbs({ path }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol>
        {path.map((crumb, index) => (
          <li key={index}>
            {index < path.length - 1 ? (
              <a href={crumb.url}>{crumb.label}</a>
            ) : (
              <span aria-current="page">{crumb.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
```

### Pattern: Recent Items
```jsx
function FileMenu() {
  const recentFiles = getRecentFiles(); // From localStorage or state

  return (
    <menu>
      <section>
        <h3>Recent Files</h3>
        {recentFiles.map(file => (
          <button onClick={() => openFile(file)}>{file.name}</button>
        ))}
      </section>
    </menu>
  );
}
```

---

## 7. Flexibility and Efficiency of Use

**Principle**: Shortcuts — hidden from novice users — may speed up the interaction for the expert user such that the design can cater to both inexperienced and experienced users. Allow users to tailor frequent actions.

### Implementation Guidelines
- Provide keyboard shortcuts for power users
- Allow customization and personalization
- Support both mouse and keyboard navigation
- Offer batch operations for repeated tasks
- Enable templates and saved preferences
- Progressive disclosure of advanced features

### Good Examples
- Keyboard shortcuts (Ctrl+C, Ctrl+V, Ctrl+S)
- Command palette (Cmd+K in many apps)
- Customizable dashboards
- Saved filters and searches
- Bulk actions (select multiple, apply action)
- Accelerators (autocomplete, smart suggestions)

### Bad Examples
- Keyboard shortcuts that conflict with browser/OS
- No way to customize frequent workflows
- Forcing expert users through novice flows
- Hiding all advanced features with no access path

### Pattern: Command Palette
```jsx
function CommandPalette({ commands }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filtered = commands.filter(cmd =>
    cmd.name.toLowerCase().includes(search.toLowerCase())
  );

  return open ? (
    <dialog open>
      <input
        placeholder="Type a command..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <ul>
        {filtered.map(cmd => (
          <li onClick={cmd.action}>
            {cmd.name} <kbd>{cmd.shortcut}</kbd>
          </li>
        ))}
      </ul>
    </dialog>
  ) : null;
}
```

### Accelerator Patterns
- Jump lists (recent/frequent items)
- Smart defaults based on user behavior
- Templates for common tasks
- Saved filters and views
- Drag-and-drop for efficiency
- Inline editing (not separate edit page)

---

## 8. Aesthetic and Minimalist Design

**Principle**: Interfaces should not contain information which is irrelevant or rarely needed. Every extra unit of information in an interface competes with the relevant units of information and diminishes their relative visibility.

### Why It Matters
Attention is a scarce resource, and users have a limited cognitive capacity. Every additional element reduces the percentage of attention that users can allocate to the truly important information.

### Implementation Guidelines
- Remove unnecessary elements
- Prioritize content over chrome
- Use progressive disclosure for advanced features
- Focus on essential functionality
- Keep visual design clean and uncluttered
- Write concise copy

### Good Examples
- Google homepage (single search box)
- Medium reading experience (distraction-free)
- Progressive disclosure (show more/less)
- Collapsible sections for optional information
- Clean dashboards showing key metrics only

### Bad Examples
- Cluttered dashboards with every possible metric
- Multiple CTAs competing for attention
- Decorative elements that don't serve a purpose
- Verbose copy when concise would work
- Too many features on one screen

### Pattern: Progressive Disclosure
```jsx
function ProductDetails({ product }) {
  const [showTechnical, setShowTechnical] = useState(false);

  return (
    <div>
      {/* Always visible: essential info */}
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <button>Buy Now</button>

      {/* Hidden by default: additional details */}
      <button onClick={() => setShowTechnical(!showTechnical)}>
        {showTechnical ? 'Hide' : 'Show'} Technical Specifications
      </button>
      {showTechnical && (
        <dl>
          {product.specs.map(spec => (
            <>
              <dt>{spec.name}</dt>
              <dd>{spec.value}</dd>
            </>
          ))}
        </dl>
      )}
    </div>
  );
}
```

### Visual Hierarchy
- Size — Larger = more important
- Color — High contrast for primary actions
- Position — Top and left get noticed first
- White space — Creates emphasis
- Typography — Weight and style for hierarchy

---

## 9. Help Users Recognize, Diagnose, and Recover from Errors

**Principle**: Error messages should be expressed in plain language (no error codes), precisely indicate the problem, and constructively suggest a solution.

### Implementation Guidelines
- Use plain language, not technical jargon
- Explain what went wrong and why
- Suggest specific actions to fix the problem
- Make error messages visible and noticeable
- Preserve user input when showing errors
- Use appropriate tone (not blaming user)

### Error Message Structure
1. **What happened** — Describe the error clearly
2. **Why it happened** — Explain the cause (if helpful)
3. **How to fix it** — Provide actionable next steps

### Good Examples
```
BAD: "Email address is already registered"
GOOD: "This email address is already registered.
   Try logging in instead, or use a different email."

BAD: "Invalid input"
GOOD: "Password must be at least 8 characters and include
   a number and special character"

BAD: "Error 404"
GOOD: "We couldn't find that page. It may have been moved
   or deleted. Try searching or return to the homepage."
```

### Bad Examples
- Generic error messages ("Something went wrong")
- Error codes with no explanation ("Error 500")
- Blaming the user ("You entered an invalid email")
- No recovery path suggested
- Errors that clear user's form input

### Pattern: Helpful Error Messages
```jsx
function LoginForm() {
  const [error, setError] = useState(null);

  const handleSubmit = async (credentials) => {
    try {
      await login(credentials);
    } catch (err) {
      if (err.code === 'INVALID_CREDENTIALS') {
        setError({
          message: 'Email or password is incorrect',
          action: 'Please try again or reset your password',
          actionLink: '/reset-password'
        });
      } else if (err.code === 'ACCOUNT_LOCKED') {
        setError({
          message: 'Your account has been locked for security',
          action: 'Contact support to unlock your account',
          actionLink: '/support'
        });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div role="alert" className="error">
          <p>{error.message}</p>
          <p>
            {error.action}
            {error.actionLink && (
              <a href={error.actionLink}>Click here</a>
            )}
          </p>
        </div>
      )}
      {/* form fields */}
    </form>
  );
}
```

### Error Message Tone
- AVOID: "You failed to enter a valid email"
- USE: "Please enter a valid email address"
- AVOID: "Your password is too weak"
- USE: "Password must be at least 8 characters"

---

## 10. Help and Documentation

**Principle**: It's best if the system doesn't need any additional explanation. However, it may be necessary to provide documentation to help users understand how to complete their tasks.

### Why It Matters
Even though it's better if the system can be used without documentation, it may be necessary to provide help. When required, documentation should be easy to search, focused on the user's task, list concrete steps, and not be too large.

### Implementation Guidelines
- Design for zero documentation (intuitive UI)
- Provide contextual help when needed
- Make help content searchable
- Focus on user tasks, not features
- Use concrete examples and steps
- Keep documentation concise and scannable

### Types of Help

**1. Contextual Help**
- Tooltips for icons and buttons
- Inline hints for form fields
- "?" icons near complex features
- Placeholder text with examples

**2. Documentation**
- Getting started guides
- FAQs for common questions
- Video tutorials for complex workflows
- API reference for developers

**3. Interactive Help**
- Onboarding tours for new users
- Interactive tutorials
- Chatbots for common questions
- In-app search for help articles

### Good Examples
- Tooltips on hover for icon-only buttons
- Placeholder text: "e.g., john@example.com"
- Contextual help: "?" icon opening relevant docs
- Onboarding checklist for new users
- Search within help documentation
- Video tutorials for complex features

### Bad Examples
- Only help available is a PDF manual
- Help content not searchable
- Documentation describes features, not tasks
- No contextual help (user must leave app)
- Outdated documentation

### Pattern: Contextual Tooltips
```jsx
function TooltipButton({ label, tooltip, onClick }) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="tooltip-container">
      <button
        onClick={onClick}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        aria-label={label}
        aria-describedby="tooltip"
      >
        {label}
      </button>
      {showTooltip && (
        <div role="tooltip" id="tooltip">
          {tooltip}
        </div>
      )}
    </div>
  );
}
```

### Pattern: Onboarding Tour
```jsx
function OnboardingTour({ steps }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || !steps[currentStep]) return null;

  return (
    <div className="tour-overlay">
      <div className="tour-step">
        <h3>{steps[currentStep].title}</h3>
        <p>{steps[currentStep].description}</p>
        <div className="tour-actions">
          <button onClick={() => setDismissed(true)}>
            Skip Tour
          </button>
          <button onClick={() => setCurrentStep(currentStep + 1)}>
            {currentStep < steps.length - 1 ? 'Next' : 'Finish'}
          </button>
        </div>
        <span>{currentStep + 1} of {steps.length}</span>
      </div>
    </div>
  );
}
```

---

## Using Heuristics for Evaluation

### Heuristic Evaluation Process

1. **Preparation**
   - Recruit 3-5 evaluators (experts or informed users)
   - Provide task scenarios
   - Review the 10 heuristics

2. **Evaluation** (Individual)
   - Each evaluator inspects UI independently
   - Note usability issues and violated heuristics
   - Rate severity (1-4 scale)

3. **Debriefing** (Group)
   - Compile all findings
   - Discuss and prioritize issues
   - Create action plan

### Severity Rating Scale

- **0 — Not a usability problem**
- **1 — Cosmetic** — Fix if time allows
- **2 — Minor** — Low priority fix
- **3 — Major** — High priority fix
- **4 — Catastrophic** — Must fix before release

### Example Findings Format

```
Issue: No confirmation before deleting account
Heuristic: #3 (User control and freedom)
Severity: 4 (Catastrophic)
Recommendation: Add confirmation dialog with warning
```

---

## Quick Reference Summary

1. **Visibility** — Show system status
2. **Match Real World** — Use user language
3. **User Control** — Provide undo/exit
4. **Consistency** — Follow conventions
5. **Error Prevention** — Prevent before correct
6. **Recognition** — Make options visible
7. **Flexibility** — Support novice and expert
8. **Minimalism** — Remove unnecessary elements
9. **Error Recovery** — Clear, helpful error messages
10. **Help** — Provide when needed, make searchable

---

## References

- **Original Article**: [10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- **Heuristic Evaluation**: [How to Conduct](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/)
- **Jakob's Law**: [Users spend most time on other sites](https://www.nngroup.com/videos/jakobs-law-internet-ux/)
