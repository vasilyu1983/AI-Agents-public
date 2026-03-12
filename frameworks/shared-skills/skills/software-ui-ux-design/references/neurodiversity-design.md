# Neurodiversity-Inclusive Design

Design patterns for users with ADHD, autism spectrum, dyslexia, dyscalculia, and other cognitive differences.

**Last Updated**: January 2026
**References**: [W3C Cognitive Accessibility](https://www.w3.org/WAI/cognitive/), [British Dyslexia Association](https://www.bdadyslexia.org.uk/advice/employers/creating-a-dyslexia-friendly-workplace/dyslexia-friendly-style-guide), [ADHD Foundation](https://www.adhdfoundation.org.uk/)

---

## Quick Reference: Pattern Matrix

| Condition | Key Need | Primary Pattern | Avoid |
|-----------|----------|-----------------|-------|
| ADHD | Focus & structure | External organization | Wall of text |
| Autism | Predictability | Explicit expectations | Ambiguity |
| Dyslexia | Readability | Typography optimization | Dense text |
| Dyscalculia | Visual numbers | Charts over tables | Raw number grids |

---

## ADHD-Inclusive Design

**Prevalence**: ~5% of adults globally

### Core Challenges

| Challenge | Design Response |
|-----------|-----------------|
| Sustained attention | Chunked content, progress indicators |
| Working memory | External structure, visible state |
| Time blindness | Time estimates, deadlines visible |
| Task initiation | Clear starting points, quick wins |
| Hyperfocus risk | Session breaks, save reminders |

### Patterns

**External Structure**
```
PROVIDE:
- Clear task lists with checkboxes
- Progress bars for multi-step processes
- "What's next" prompts
- Visible deadlines and due dates
- Automatic state saving

IMPLEMENTATION:
- Persist form state every 30 seconds
- Show step X of Y always visible
- Time estimates for tasks ("~5 min")
- "Continue where you left off" prompts
```

**Focus Support**
```css
/* Focus mode styling */
.focus-mode {
  /* Reduce visual noise */
  --sidebar-width: 0;
  --secondary-nav: hidden;

  /* Emphasize current task */
  --current-task-highlight: var(--color-primary-light);

  /* Minimize distractions */
  --notification-frequency: batched;
  --animation-duration: 0;
}
```

**Content Chunking**
| Content Type | Chunk Size | Break Pattern |
|--------------|------------|---------------|
| Text | 2-3 sentences/paragraph | Visual divider |
| Lists | 5-7 items max | Categorize longer |
| Forms | 3-5 fields/section | Progress save point |
| Videos | 5-10 min segments | Chapter markers |

**Task Management Components**
```typescript
interface ADHDFriendlyTask {
  title: string;
  timeEstimate: string;        // "~5 min"
  steps: string[];             // Broken down
  currentStep: number;         // Visual progress
  deadline?: Date;             // If applicable
  quickWin: boolean;           // Flag easy tasks
  savedState: TaskState;       // Auto-persist
}
```

### Anti-Patterns to Avoid

```
AVOID:
- Auto-playing videos
- Infinite scroll without progress
- Time-limited sessions (or warn clearly)
- Mandatory fields without clear indication
- Long unstructured forms
- Hidden navigation (forces memory)
- Interrupting notifications
```

---

## Autism Spectrum-Inclusive Design

**Prevalence**: ~1-2% of population

### Core Challenges

| Challenge | Design Response |
|-----------|-----------------|
| Sensory sensitivity | Calm colors, no autoplay, motion control |
| Need for predictability | Consistent patterns, clear expectations |
| Literal interpretation | Explicit language, no idioms |
| Social cues | Clear feedback, explicit status |
| Change sensitivity | Warn before changes, gradual updates |

### Patterns

**Predictable Interactions**
```
EVERY action should have:
1. Clear affordance (looks interactive)
2. Immediate feedback (visual/haptic)
3. Predictable outcome (same input = same output)
4. Undo option (reduces anxiety)
```

**Explicit Communication**
| Instead Of | Use |
|------------|-----|
| "Hang tight!" | "Loading, please wait" |
| "Oops!" | "Error: [specific issue]" |
| "We'll be in touch" | "Email response within 24 hours" |
| "Submit" (vague) | "Create Account" (specific) |

**Sensory Considerations**
```css
/* Sensory-friendly defaults */
.sensory-safe {
  /* Calm color palette */
  --color-primary: #4A90A4; /* Muted blue */
  --color-background: #F5F5F0; /* Warm off-white */

  /* Reduced motion */
  --animation-duration: 0;
  --transition-duration: 0.1s; /* Instant feels jarring */

  /* No autoplay anything */
  --video-autoplay: paused;
  --audio-autoplay: muted;

  /* Consistent spacing */
  --spacing-unit: 8px;
}
```

**Change Management**
```
BEFORE any UI change:
1. Announce changes in advance (banner, email)
2. Provide changelog accessible in-app
3. Allow reverting to previous version (if possible)
4. Highlight what changed (visual diff)
5. Keep core navigation unchanged when possible
```

**Pattern Consistency Checklist**
- [ ] Buttons same style throughout
- [ ] Links same color and behavior
- [ ] Icons consistent meaning
- [ ] Error messages same location
- [ ] Success messages same pattern
- [ ] Navigation in same position
- [ ] Form fields same styling

### Component Patterns

**Clear Status States**
```typescript
// Explicit status, never ambiguous
type TaskStatus =
  | 'Not Started'      // Clear, not "Pending"
  | 'In Progress'      // Active state
  | 'Waiting for You'  // Action needed
  | 'Waiting for Others' // No action needed
  | 'Completed'        // Done
  | 'Cancelled';       // Explicitly ended

// Display with icon + text always
```

---

## Dyslexia-Inclusive Design

**Prevalence**: ~10% of population

### Core Challenges

| Challenge | Design Response |
|-----------|-----------------|
| Letter/word recognition | Optimized typography |
| Reading speed | Shorter content, scannable |
| Tracking lines | Adequate line spacing |
| Working memory | Chunked information |
| Spelling | Autocomplete, spell-check |

### Typography Optimization

**Font Selection**
```
RECOMMENDED FONTS (tested for dyslexia):
- Lexie Readable
- OpenDyslexic
- Comic Sans (seriously - irregular shapes help)
- Verdana
- Arial
- Tahoma

AVOID:
- Serif fonts (Times New Roman)
- Thin/light weights
- Italics for body text
- ALL CAPS for sentences
- Justified text alignment
```

**CSS Implementation**
```css
.dyslexia-friendly {
  /* Font settings */
  font-family: 'Lexie Readable', Verdana, sans-serif;
  font-size: 16px; /* minimum */
  font-weight: 400; /* regular, not light */

  /* Spacing */
  line-height: 1.5; /* minimum */
  letter-spacing: 0.12em;
  word-spacing: 0.16em;

  /* Layout */
  max-width: 70ch; /* characters per line */
  text-align: left; /* never justify */

  /* Background */
  background-color: #FFFBF0; /* cream, not pure white */
}
```

**Line Length & Spacing**
| Property | Minimum | Recommended | Maximum |
|----------|---------|-------------|---------|
| Font size | 16px | 18px | User choice |
| Line height | 1.5 | 1.8 | 2.0 |
| Line length | - | 60-70 chars | 80 chars |
| Paragraph spacing | 1.5em | 2em | - |

### Content Patterns

**Text Structure**
```
DO:
- Short sentences (15-20 words max)
- One idea per paragraph
- Bulleted lists for multiple points
- Bold for emphasis (not italics)
- Left-aligned text
- Clear headings hierarchy

AVOID:
- Long paragraphs
- Complex sentence structures
- Walls of unbroken text
- Light gray text on white
- Patterned backgrounds
- Moving or flashing text
```

**Alternative Content**
| Text Content | Alternative |
|--------------|-------------|
| Long instructions | Step-by-step with numbers |
| Dense paragraphs | Bullet points |
| Data tables | Simple charts |
| Error messages | Icon + short text |
| Help documentation | Video tutorials |

### Reading Aids

**Dyslexia Support Features**
```typescript
interface DyslexiaSettings {
  // Font
  fontFamily: 'system' | 'dyslexic' | 'custom';
  fontSize: number; // 100-200% of base
  letterSpacing: number; // 0-0.3em

  // Display
  lineHeight: number; // 1.5-2.5
  lineHighlight: boolean; // Highlight current line
  rulerMode: boolean; // Reading ruler overlay
  backgroundTint: 'white' | 'cream' | 'yellow' | 'blue';

  // Assistance
  textToSpeech: boolean;
  syllableBreaks: boolean; // word-hy-phen-a-tion
}
```

---

## Dyscalculia-Inclusive Design

**Prevalence**: ~5-7% of population

### Core Challenges

| Challenge | Design Response |
|-----------|-----------------|
| Number processing | Visual representations |
| Arithmetic | Calculators, auto-compute |
| Number sequences | Color coding, grouping |
| Estimation | Concrete examples |
| Time/money concepts | Visual aids |

### Patterns

**Number Presentation**
```
INSTEAD OF:
- Raw number grids
- Tables with many columns
- Percentages without context

USE:
- Progress bars (visual %)
- Charts and graphs
- Color-coded ranges
- Relative comparisons ("2x more than average")
- Concrete examples ("enough for 3 cups of coffee")
```

**Visual Alternatives**
| Data Type | Alternative Display |
|-----------|---------------------|
| Percentages | Progress bar + label |
| Prices | Size comparison, icons |
| Quantities | Visual counter, grouping |
| Time durations | Timeline, calendar |
| Comparisons | Side-by-side visual |

**Financial UI**
```typescript
// Dyscalculia-friendly price display
interface PriceDisplay {
  amount: number;
  // Show both
  formatted: string;      // "$49.99"
  visual: 'bar' | 'icon'; // Progress toward budget

  // Context
  comparison?: string;    // "Most popular" or "Best value"
  perUnit?: string;       // "$4.17/month"
  savings?: string;       // "Save $60/year"
}
```

**Calculator Integration**
```
ALWAYS provide:
- Built-in calculator for quantity fields
- Running total visible
- Tax/tip calculated automatically
- "Split evenly" options for shared costs
- Visual confirmation of math
```

### Date & Time Patterns

**Time Display**
| Instead Of | Use |
|------------|-----|
| "3 days ago" | "Tuesday, Jan 7" + "3 days ago" |
| "15:30" | "3:30 PM" (12-hour with AM/PM) |
| "In 2 weeks" | "January 23" + calendar icon |
| Duration: "90 min" | "1 hour 30 minutes" |

**Calendar Support**
- Visual calendars over date pickers
- Highlight weekends differently
- Show "today" marker clearly
- Countdown to events with visual progress

---

## Universal Implementation

### Settings Panel

```typescript
// Combined neurodiversity settings
interface AccessibilitySettings {
  // Visual
  motion: 'full' | 'reduced' | 'none';
  contrast: 'standard' | 'high' | 'custom';
  fontSize: number;
  colorTheme: 'default' | 'calm' | 'high-contrast';

  // Reading
  fontFamily: 'system' | 'dyslexic';
  lineSpacing: 'standard' | 'relaxed' | 'spacious';
  textWidth: 'narrow' | 'standard' | 'wide';

  // Focus
  focusMode: boolean;
  notificationBatching: boolean;
  autoSave: boolean;

  // Numbers
  visualNumbers: boolean;
  calculatorEnabled: boolean;

  // Predictability
  changeNotifications: boolean;
  confirmDialogs: 'minimal' | 'standard' | 'all';
}
```

### Testing Protocol

**Cognitive Accessibility Audit**
- [ ] Content readable at 200% zoom
- [ ] All animations can be disabled
- [ ] No time-limited actions (or extensions available)
- [ ] Error messages specific and actionable
- [ ] Forms save state automatically
- [ ] Navigation consistent throughout
- [ ] Complex actions have undo
- [ ] Numbers have visual alternatives
- [ ] Instructions available in multiple formats

**User Testing Recruitment**
| Condition | Testing Adaptation |
|-----------|-------------------|
| ADHD | Shorter sessions (30 min max), breaks |
| Autism | Familiar environment, script shared ahead |
| Dyslexia | Tasks read aloud option, extra time |
| Dyscalculia | Avoid number-heavy tasks in isolation |

---

## Related Resources

- [Demographic-Inclusive Design](demographic-inclusive-design.md) - Age-specific patterns
- [WCAG Accessibility](wcag-accessibility.md) - Technical standards
- [Modern UX Patterns](modern-ux-patterns-2025.md) - Progressive disclosure, skeleton screens
