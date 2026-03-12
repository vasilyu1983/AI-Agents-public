# Article Templates

Copy-paste templates for all help center article types.

## Contents

- How-To article template
- Troubleshooting article template
- Conceptual article template
- FAQ article template
- Reference article template
- Video tutorial script template
- Production checklist
- Visual content guidelines

## How-To Article Template

```markdown
# How to [Action Verb] [Object]

[1-2 sentence intro explaining what this guide covers and the outcome]

## Prerequisites

- [Requirement 1 - e.g., Admin access required]
- [Requirement 2 - e.g., Feature enabled in Settings]
- [Requirement 3 - optional, link to setup guide]

## Steps

### Step 1: [Action verb + specific action]

[2-3 sentences explaining what to do]

![Screenshot description](path/to/screenshot.png)
*Caption: What the user should see*

### Step 2: [Action verb + specific action]

[Instructions]

> **Note**: [Important callout if needed]

### Step 3: [Action verb + specific action]

[Instructions]

```
Code block if relevant
```

## Result

[Describe what success looks like - what the user should see/experience]

![Success state screenshot](path/to/success.png)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| [Common problem 1] | [Quick fix] |
| [Common problem 2] | [Quick fix or link] |

## Next Steps

- [Related task 1](link)
- [Related task 2](link)
- [Advanced guide](link)

---

**Was this helpful?** [Yes] [No]

*Last updated: YYYY-MM-DD*
```

### How-To Writing Guidelines

| Element | Rule |
|---------|------|
| Title | Start with "How to" + action verb |
| Steps | 3-7 steps ideal, max 10 |
| Screenshots | One per major step |
| Prerequisites | List all blockers upfront |
| Result | Always show success state |

## Troubleshooting Article Template

```markdown
# Fix: [Error Message or Problem Description]

[Brief description of the issue and its impact]

## Symptoms

- [What the user sees - exact error text]
- [Related behavior]
- [When it typically occurs]

**Error Message:**
```
[Exact error text user sees]
```

## Quick Fixes

Try these solutions in order:

### 1. [Most common solution]

**Why this works**: [Brief explanation]

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected result**: [What should happen]

---

### 2. [Second most common solution]

**Why this works**: [Brief explanation]

**Steps:**
1. [Step 1]
2. [Step 2]

---

### 3. [Edge case solution]

**When to try**: [Specific condition]

**Steps:**
1. [Step 1]
2. [Step 2]

## Root Causes

| Cause | Likelihood | Solution |
|-------|------------|----------|
| [Cause 1] | Common | Solution 1 above |
| [Cause 2] | Occasional | Solution 2 above |
| [Cause 3] | Rare | Contact support |

## Prevention

- [How to avoid this in the future]
- [Best practice recommendation]

## Still Not Working?

If none of the solutions above resolved your issue:

1. **Gather this information:**
   - Browser/app version
   - Steps to reproduce
   - Screenshot of error

2. **Contact support:**
   [Contact Support](link) — Average response: [X hours]

---

**Was this helpful?** [Yes] [No]

*Last updated: YYYY-MM-DD*
```

### Troubleshooting Writing Guidelines

| Element | Rule |
|---------|------|
| Title | "Fix:" prefix or exact error message |
| Solutions | Most common first (80/20 rule) |
| Error text | Include exact message for search |
| Escalation | Always provide escape path |

## Conceptual Article Template

```markdown
# [Concept Name]: [Brief Description]

[2-3 sentence overview explaining what this is and why it matters]

## What is [Concept]?

[Clear definition in plain language, 2-4 sentences]

### Key Points

- [Essential point 1]
- [Essential point 2]
- [Essential point 3]

## How [Concept] Works

[Explanation with diagram or visual if helpful]

```
[Simple diagram using ASCII or embedded image]
```

### Components

| Component | Purpose | Example |
|-----------|---------|---------|
| [Part 1] | [What it does] | [Concrete example] |
| [Part 2] | [What it does] | [Concrete example] |
| [Part 3] | [What it does] | [Concrete example] |

## When to Use [Concept]

**Use when:**
- [Scenario 1]
- [Scenario 2]

**Don't use when:**
- [Anti-pattern 1]
- [Alternative approach]

## Examples

### Example 1: [Common use case]

[Concrete example with before/after or input/output]

### Example 2: [Advanced use case]

[Second example showing more complex application]

## Related Concepts

- **[Related concept 1]**: [How it relates](link)
- **[Related concept 2]**: [How it relates](link)

## Learn More

- [How-to guide using this concept](link)
- [Advanced documentation](link)
- [Video tutorial](link)

---

**Was this helpful?** [Yes] [No]

*Last updated: YYYY-MM-DD*
```

## FAQ Article Template

```markdown
# [Topic] FAQs

Frequently asked questions about [topic].

---

## Getting Started

<details>
<summary><strong>Q: [Question in natural language]?</strong></summary>

[Answer in 2-4 sentences]

[Link to detailed guide if needed](link)

</details>

<details>
<summary><strong>Q: [Question 2]?</strong></summary>

[Answer]

</details>

---

## [Category 2]

<details>
<summary><strong>Q: [Question]?</strong></summary>

[Answer]

| Option | Result |
|--------|--------|
| [A] | [What happens] |
| [B] | [What happens] |

</details>

<details>
<summary><strong>Q: [Question]?</strong></summary>

[Answer]

> **Tip**: [Helpful additional info]

</details>

---

## Billing & Account

<details>
<summary><strong>Q: [Billing question]?</strong></summary>

[Answer]

**Related**: [Billing settings](link)

</details>

---

## Troubleshooting

<details>
<summary><strong>Q: Why am I seeing [error]?</strong></summary>

This usually happens when [cause].

**Quick fix:**
1. [Step 1]
2. [Step 2]

**Still not working?** [Contact support](link)

</details>

---

**Can't find your answer?**

- [Search help center](link)
- [Contact support](link)
- [Community forum](link)

*Last updated: YYYY-MM-DD*
```

### FAQ Writing Guidelines

| Element | Rule |
|---------|------|
| Questions | Natural language (how users actually ask) |
| Answers | 2-4 sentences max, link to detail |
| Grouping | By topic, 5-8 questions per group |
| Format | Collapsible for scannability |

## Reference Article Template

```markdown
# [Feature/API] Reference

Complete reference for [feature/API name].

## Overview

| Property | Value |
|----------|-------|
| **Availability** | [Plan tier] |
| **API Endpoint** | `[endpoint]` |
| **Rate Limit** | [X requests/minute] |
| **Last Updated** | [Date] |

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `param1` | string | [Description] |
| `param2` | integer | [Description] |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `option1` | boolean | `false` | [Description] |
| `option2` | string | `null` | [Description] |

## Examples

### Basic Usage

```json
{
  "param1": "value",
  "param2": 123
}
```

**Response:**

```json
{
  "status": "success",
  "data": { ... }
}
```

### Advanced Usage

```json
{
  "param1": "value",
  "param2": 123,
  "option1": true
}
```

## Error Codes

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| 400 | Invalid parameter | [Cause] | [Fix] |
| 401 | Unauthorized | [Cause] | [Fix] |
| 429 | Rate limited | [Cause] | [Fix] |

## Limits & Quotas

| Limit | Free | Pro | Enterprise |
|-------|------|-----|------------|
| [Limit 1] | [Value] | [Value] | [Value] |
| [Limit 2] | [Value] | [Value] | Unlimited |

## Changelog

| Date | Change |
|------|--------|
| YYYY-MM-DD | [Change description] |
| YYYY-MM-DD | [Change description] |

## Related

- [API Authentication](link)
- [Webhooks Reference](link)
- [SDK Documentation](link)

---

*Last updated: YYYY-MM-DD*
```

## Video Tutorial Script Template

```markdown
# Video: How to [Action]

**Duration**: [X:XX]
**Skill Level**: [Beginner/Intermediate/Advanced]

## Script

### Intro (0:00-0:15)

"In this video, you'll learn how to [outcome]. By the end, you'll be able to [specific skill]."

### Section 1: [Topic] (0:15-1:00)

**Visuals**: [Screen recording of X]

"First, let's [action]. Navigate to [location]..."

**Key Points to Show**:
- [ ] [Visual element 1]
- [ ] [Visual element 2]

### Section 2: [Topic] (1:00-2:00)

**Visuals**: [Screen recording of Y]

"Now that we've [previous action], let's [next action]..."

### Section 3: [Topic] (2:00-3:00)

**Visuals**: [Result/confirmation screen]

"You've successfully [outcome]. Here's what you should see..."

### Outro (3:00-3:30)

"That's how you [action]. For more help, check the links in the description. If you found this helpful, [CTA]."

## Production Checklist

- [ ] Script approved
- [ ] Screen recording captured
- [ ] Voiceover recorded
- [ ] Captions added
- [ ] Thumbnail created
- [ ] Chapter markers set
- [ ] Description with links
- [ ] Published to: [platforms]

## Metadata

**Title**: How to [Action] | [Product Name]
**Description**: Learn how to [action] in [time]. This tutorial covers [topics]. Timestamps: [chapters]
**Tags**: [tag1], [tag2], [tag3]
**Thumbnail**: [Description]
```

## Content Quality Checklist

### Before Publishing

```markdown
QUALITY GATES

[ ] Title matches search intent
[ ] Intro answers "what will I learn?"
[ ] Steps are numbered and actionable
[ ] Screenshots are current (check version)
[ ] Links work (test all)
[ ] Mobile-friendly formatting
[ ] Accessibility: alt text, captions
[ ] Related articles linked
[ ] Feedback mechanism present
[ ] Last updated date set

AI-FRIENDLY CHECKS

[ ] Clear headings with keywords
[ ] No ambiguous pronouns
[ ] Error messages exact (for search)
[ ] No duplicate content elsewhere
[ ] Structured data (tables, lists)
```

### Content Review Schedule

| Content Type | Review Frequency | Trigger |
|--------------|------------------|---------|
| How-To | Quarterly | Feature update |
| Troubleshooting | Monthly | New errors reported |
| FAQ | Monthly | Ticket trends |
| Reference | On release | API/feature change |
| Conceptual | Bi-annually | Architecture change |

## Visual Content Guidelines

### Screenshots

```
SCREENSHOT REQUIREMENTS

Size: 1200x800px minimum (2x for retina)
Format: PNG for UI, GIF for sequences
Annotations:
  - Red boxes for emphasis
  - Numbered callouts for steps
  - Blur sensitive data
File naming: [article-slug]-step-[N].png
```

### GIF Recordings

```
GIF GUIDELINES

Duration: 5-15 seconds
Frame rate: 10-15 fps
Size: Under 5MB
Tools: CleanShot, Kap, LICEcap
Use for: Multi-step actions, hover states
```

### Diagrams

```
DIAGRAM TYPES

Flowcharts: Decision processes
Architecture: System overviews
Timelines: Sequences, processes
Comparison: Feature matrices

Tools: Excalidraw, Mermaid, Whimsical
Style: Consistent colors, minimal text
```
