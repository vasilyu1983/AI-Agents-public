# AI & Automation UX Patterns (2025-2026)

Comprehensive guide to designing user experiences for AI-powered products: agent interfaces, conversational UI, generative content, human-AI collaboration, and regulatory compliance. Covers trust calibration, transparency, loading states, handoff patterns, and agentic UI. Applies to chatbots, copilots, autonomous agents, recommendation engines, and any product where AI generates, suggests, or acts on behalf of users.

**Last Updated**: August 2026

---
## Table of Contents

- [AI Agent UX Patterns](#ai-agent-ux-patterns)
- [Trust Indicators](#trust-indicators)
- [Explainability Patterns](#explainability-patterns)
- [User Control Hierarchy](#user-control-hierarchy)
- [Progressive Autonomy](#progressive-autonomy)
- [Conversational UI](#conversational-ui)
- [Chatbot Design Patterns](#chatbot-design-patterns)
- [Multi-Turn State Management](#multi-turn-state-management)
- [Streaming Response UX](#streaming-response-ux)
- [Error Recovery in Conversations](#error-recovery-in-conversations)
- [AI-Generated Content UX](#ai-generated-content-ux)
- [Confidence Indicators](#confidence-indicators)
- [Edit Affordances for AI Output](#edit-affordances-for-ai-output)
- [Attribution Patterns](#attribution-patterns)
- [Hallucination Prevention in UI](#hallucination-prevention-in-ui)
- [Human-AI Handoff](#human-ai-handoff)
- [Escalation Patterns](#escalation-patterns)
- [Context Preservation During Handoff](#context-preservation-during-handoff)
- [Graceful Degradation](#graceful-degradation)
- [AI Loading States](#ai-loading-states)
- [State Taxonomy](#state-taxonomy)
- [Skeleton Screens for AI Content](#skeleton-screens-for-ai-content)
- [Progress Indicators for Long-Running AI Tasks](#progress-indicators-for-long-running-ai-tasks)
- [AI Transparency & Ethics](#ai-transparency-&-ethics)
- [Disclosure Requirements](#disclosure-requirements)
- [When and How to Disclose AI Involvement](#when-and-how-to-disclose-ai-involvement)
- [Watermarking and Provenance](#watermarking-and-provenance)
- [Consent Patterns for AI Features](#consent-patterns-for-ai-features)
- [Agentic UI Patterns](#agentic-ui-patterns)
- [Multi-Step Task Interfaces](#multi-step-task-interfaces)
- [Agent Status Dashboard](#agent-status-dashboard)
- [Tool Use Visibility](#tool-use-visibility)
- [Approval Gates](#approval-gates)
- [Reversibility Tiering](#reversibility-tiering)
- [Interruption and Steering](#interruption-and-steering)
- [Cost and Consumption Visibility](#cost-and-consumption-visibility)
- [Agent Memory as an Editable Surface](#agent-memory-as-an-editable-surface)
- [Human-Agent Interaction Principles](#human-agent-interaction-principles)
- [Agent-Computer Interface (ACI)](#agent-computer-interface-aci)
- [Generative UI and the Agent-to-UI Contract](#generative-ui-and-the-agent-to-ui-contract)
- [Anti-Patterns](#anti-patterns)
- [Common AI UX Mistakes](#common-ai-ux-mistakes)
- [Anthropomorphism Scale](#anthropomorphism-scale)
- [Implementation Checklists](#implementation-checklists)
- [AI Feature Launch Checklist](#ai-feature-launch-checklist)
- [Conversational UI Checklist](#conversational-ui-checklist)
- [Agentic Task Checklist](#agentic-task-checklist)
- [References](#references)
- [Cross-References](#cross-references)


## AI Agent UX Patterns

### Trust Indicators

Users must calibrate trust accurately -- neither over-trusting nor under-trusting AI output. The goal is appropriate reliance, not maximum trust.

| Indicator | Implementation | When to Use |
|-----------|---------------|-------------|
| **Confidence score** | Visual meter or label (High / Medium / Low) | Classification, diagnosis, risk scoring |
| **Source citation** | Inline footnotes linking to source material | AI-generated summaries, research answers |
| **Model identity** | Label the model or system version | Multi-model products, versioned outputs |
| **Hedging language** | "This appears to be..." / "Based on available data..." | All generated text with uncertainty |
| **Track record** | "This model is correct ~92% of the time for this task" | Repeated classification tasks |
| **Peer comparison** | "3 of 4 models agree on this answer" | Ensemble or multi-agent outputs |

### Explainability Patterns

| Pattern | Description | Best For |
|---------|------------|----------|
| **Feature attribution** | Highlight which inputs influenced the output | Tabular data, credit scoring, medical |
| **Counterfactual** | "If X were different, the result would be Y" | Decision support, rejections |
| **Example-based** | "This is similar to these past cases" | Legal, medical, support triage |
| **Chain-of-thought** | Show reasoning steps the model followed | Agentic tasks, complex analysis |
| **Attention highlight** | Visually mark text or image regions the model focused on | Document analysis, image classification |
| **Plain-language summary** | One-sentence explanation of why | Any user-facing AI decision |

### User Control Hierarchy

Every AI feature needs an appropriate level of user control. Map each AI capability to this hierarchy.

```text
AUTONOMY LEVELS (ascending):

  Level 0: Manual
    User does everything. AI is off.

  Level 1: Suggestion
    AI suggests, user decides and acts.
    Example: autocomplete, spell check, "Did you mean..."

  Level 2: Approve-then-act
    AI proposes an action, user approves before execution.
    Example: "Schedule this meeting?" [Approve] [Edit] [Dismiss]

  Level 3: Act-then-review
    AI acts automatically, user can review and undo.
    Example: email categorization, spam filtering

  Level 4: Autonomous with alerts
    AI acts independently, alerts user on exceptions.
    Example: fraud detection, automated scaling

  Level 5: Fully autonomous
    AI acts without notification.
    Example: CDN routing, load balancing (invisible to end user)
```

### Progressive Autonomy

Start users at lower autonomy levels and let them graduate upward as trust builds.

| Phase | Behavior | UI Pattern |
|-------|----------|------------|
| **Onboarding** | AI suggests only, user acts | Inline suggestions with accept/dismiss |
| **Building trust** | AI pre-fills, user confirms | Pre-populated fields with edit affordance |
| **Established trust** | AI acts, user reviews batch | Activity log with undo per item |
| **Full trust** | AI acts autonomously, user sets policy | Dashboard with policy controls and exception alerts |

```jsx
// Progressive autonomy toggle
function AutonomyControl({ feature, currentLevel, onLevelChange }) {
  const levels = [
    { value: 'suggest', label: 'Suggest only' },
    { value: 'ask-first', label: 'Ask before acting' },
    { value: 'act-notify', label: 'Act and notify me' },
    { value: 'autonomous', label: 'Handle automatically' },
  ];

  return (
    <fieldset>
      <legend>How should AI handle {feature}?</legend>
      {levels.map((level) => (
        <label key={level.value}>
          <input
            type="radio"
            name={`autonomy-${feature}`}
            value={level.value}
            checked={currentLevel === level.value}
            onChange={() => onLevelChange(level.value)}
          />
          {level.label}
        </label>
      ))}
    </fieldset>
  );
}
```

---

## Conversational UI

### Chatbot Design Patterns

| Pattern | Description | When to Use |
|---------|------------|-------------|
| **Command palette** | Slash commands for structured input (`/summarize`, `/translate`) | Power users, productivity tools |
| **Suggested prompts** | Clickable prompt chips below the input | Onboarding, empty states, low-confidence moments |
| **Context panel** | Side panel showing referenced documents, data, or tools | Complex research, multi-document tasks |
| **Thread branching** | Fork a conversation to explore alternatives | Creative writing, brainstorming, code generation |
| **System message** | Visible system/role context the user can edit | Developer tools, customizable assistants |
| **Pinned context** | User pins important messages to keep them in context | Long conversations, project-based work |

### Multi-Turn State Management

```text
CONVERSATION STATE MODEL:

  ┌─────────────┐
  │   Idle       │  Input field active, no pending request
  └──────┬──────┘
         │ User sends message
         v
  ┌─────────────┐
  │  Processing  │  Input disabled, typing indicator shown
  └──────┬──────┘
         │ First token received
         v
  ┌─────────────┐
  │  Streaming   │  Text appearing progressively, cancel available
  └──────┬──────┘
         │ Stream complete
         v
  ┌─────────────┐
  │  Complete    │  Actions shown (copy, regenerate, edit, feedback)
  └──────┬──────┘
         │ User sends follow-up
         v
  ┌─────────────┐
  │  Processing  │  Previous context preserved, new request pending
  └─────────────┘

ERROR STATES (can occur at Processing or Streaming):
  - Network error → Retry button, preserve user message
  - Rate limit → Queue position indicator, estimated wait
  - Context overflow → Summarize option, start new thread
  - Model error → Apologize, offer regenerate or fallback model
```

### Streaming Response UX

| Requirement | Implementation |
|-------------|---------------|
| **Cursor indicator** | Blinking block or line cursor at insertion point |
| **Smooth scrolling** | Auto-scroll to bottom only if user is already at bottom |
| **Scroll lock** | If user scrolls up during streaming, stop auto-scroll; show "Jump to bottom" button |
| **Cancel button** | Visible during streaming, stops generation immediately |
| **Partial utility** | Partially streamed text remains visible and usable after cancel |
| **Code block detection** | Detect code fences early, render with syntax highlighting as tokens arrive |
| **Markdown rendering** | Parse markdown incrementally; avoid layout reflow on block completion |

```css
/* Streaming cursor animation */
.streaming-cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background-color: currentColor;
  margin-left: 1px;
  vertical-align: text-bottom;
  animation: blink 0.8s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

/* Scroll anchor for auto-scroll behavior */
.chat-container {
  overflow-y: auto;
  overflow-anchor: auto;
}
.chat-anchor {
  overflow-anchor: auto;
  height: 1px;
}
```

### Error Recovery in Conversations

| Error Type | User-Facing Message | Recovery Action |
|-----------|-------------------|----------------|
| Network failure | "Connection lost. Your message has been saved." | Auto-retry with exponential backoff; manual retry button |
| Rate limit | "High demand right now. Your request is queued (position 3)." | Queue with progress; option to cancel |
| Context too long | "This conversation is getting long. Want me to summarize and continue?" | Auto-summarize; start new thread with summary |
| Model refusal | "I can't help with that specific request. Here's what I can do instead." | Suggest alternative framing; link to guidelines |
| Timeout | "This is taking longer than expected." | Cancel and retry; option to switch to lighter model |
| Malformed output | "Something went wrong with my response." | Regenerate button; auto-retry once silently |

---

## AI-Generated Content UX

### Confidence Indicators

| Confidence Level | Visual Treatment | Interaction |
|-----------------|-----------------|-------------|
| **High** | Standard text styling, no special marking | Direct use encouraged |
| **Medium** | Subtle background tint or left border | "Verify this" prompt, edit affordance |
| **Low** | Dashed underline or muted text with warning icon | Explicit "Unverified" label, require user confirmation |
| **Unknown** | Italic or quoted style | "AI-generated, not fact-checked" disclaimer |

```jsx
// Confidence-aware content block
function AIContent({ text, confidence, sources }) {
  const confidenceStyles = {
    high: 'ai-content--high',
    medium: 'ai-content--medium',
    low: 'ai-content--low',
  };

  return (
    <div className={`ai-content ${confidenceStyles[confidence]}`}>
      <div className="ai-content__body">{text}</div>
      {confidence !== 'high' && (
        <p className="ai-content__disclaimer">
          AI-generated content -- verify before use
        </p>
      )}
      {sources?.length > 0 && (
        <details className="ai-content__sources">
          <summary>Sources ({sources.length})</summary>
          <ol>
            {sources.map((s, i) => (
              <li key={i}><a href={s.url}>{s.title}</a></li>
            ))}
          </ol>
        </details>
      )}
    </div>
  );
}
```

### Edit Affordances for AI Output

| Affordance | Description | Implementation |
|-----------|------------|---------------|
| **Inline edit** | Click any part of AI output to edit directly | `contentEditable` region or click-to-edit fields |
| **Accept/reject chunks** | Diff-style accept/reject for each paragraph or section | Side-by-side diff view with per-block controls |
| **Regenerate section** | Regenerate a specific section without regenerating the whole response | Section-level regenerate button on hover |
| **Tone/length sliders** | Adjust output characteristics post-generation | Controls that re-generate with modified parameters |
| **Version history** | Browse previous generations and revert | Numbered version tabs or timeline |
| **Copy as...** | Copy as plain text, markdown, HTML, or formatted | Dropdown copy button with format options |

### Attribution Patterns

```text
INLINE ATTRIBUTION:
  "The population of Tokyo is approximately 14 million [1]
   as of the 2023 census [2]."

  [1] Statistics Bureau of Japan, 2023
  [2] Tokyo Metropolitan Government Census Report

BLOCK ATTRIBUTION:
  ┌────────────────────────────────────────────┐
  │ AI-generated summary                       │
  │                                            │
  │ Content here...                            │
  │                                            │
  │ Sources:                                   │
  │   - source-document-1.pdf (pages 3-7)     │
  │   - internal-wiki/topic-page              │
  │   - https://example.com/article           │
  │                                            │
  │ Generated by: ModelName v2.1               │
  │ Confidence: High | Last updated: Mar 2026  │
  └────────────────────────────────────────────┘
```

### Hallucination Prevention in UI

| Strategy | Implementation |
|----------|---------------|
| **Grounded generation** | Display only claims the model can attribute to provided sources |
| **Citation required mode** | Every factual claim must have an inline citation; unsupported claims are flagged |
| **Fact-check toggle** | Let users enable a mode that cross-references claims against a knowledge base |
| **Confidence thresholds** | Suppress or flag content below a confidence threshold rather than displaying it |
| **User verification prompts** | For high-stakes content, require explicit user confirmation before publishing |
| **Diff against source** | Show what was in the source vs. what the AI generated, highlighting additions |

---

## Human-AI Handoff

### Escalation Patterns

| Pattern | Trigger | UX Treatment |
|---------|---------|-------------|
| **Confidence-based** | AI confidence drops below threshold | "I'm not sure about this. Would you like to connect with a human?" |
| **Complexity-based** | Task requires capabilities beyond AI scope | "This requires [specific expertise]. Routing to a specialist." |
| **User-initiated** | User explicitly requests human help | Always-visible "Talk to a person" option |
| **Sentiment-based** | User frustration detected (repeated rephrasing, negative language) | Proactive offer: "Would you prefer to speak with someone?" |
| **Regulatory** | Decision has legal or financial consequences | Mandatory human review before execution |
| **Time-based** | Conversation exceeds duration or turn threshold without resolution | "Let me connect you with someone who can help directly." |

### Context Preservation During Handoff

```text
HANDOFF CONTEXT PACKAGE (what transfers to the human agent):

  1. Conversation summary (AI-generated, editable by human)
  2. User intent classification
  3. Steps already attempted and their outcomes
  4. Relevant user account data (pre-fetched)
  5. AI confidence assessment for each attempted answer
  6. User sentiment trajectory
  7. Suggested next steps for the human agent

UI FOR THE USER DURING HANDOFF:
  ┌────────────────────────────────────────────┐
  │ Connecting you with a specialist...        │
  │                                            │
  │ Wait time: ~2 minutes                      │
  │ Your conversation history will be shared   │
  │ so you won't need to repeat yourself.      │
  │                                            │
  │ [Cancel and return to AI]                  │
  └────────────────────────────────────────────┘
```

### Graceful Degradation

When AI services are unavailable or degraded, the product must remain functional.

| Degradation Level | User Experience | Implementation |
|------------------|----------------|---------------|
| **Full outage** | AI features hidden or replaced with manual alternatives | Feature flags disable AI UI; show traditional workflows |
| **High latency** | Longer loading states with accurate time estimates | Timeout thresholds; queue position; option to cancel |
| **Reduced quality** | Simpler model or cached responses with disclosure | "Using a simpler model -- results may be less detailed" |
| **Partial failure** | Some AI features work, others do not | Per-feature health checks; degrade individually |

```jsx
// Graceful degradation wrapper
function AIFeature({ children, fallback, featureId }) {
  const { status } = useAIServiceHealth(featureId);

  if (status === 'unavailable') {
    return (
      <div className="ai-degraded">
        <p>AI assistance is temporarily unavailable.</p>
        {fallback}
      </div>
    );
  }

  if (status === 'degraded') {
    return (
      <div className="ai-degraded-notice">
        <p>AI features may be slower or less accurate right now.</p>
        {children}
      </div>
    );
  }

  return children;
}
```

---

## AI Loading States

### State Taxonomy

| State | Visual Treatment | Duration | User Action |
|-------|-----------------|----------|-------------|
| **Queued** | "Your request is in the queue (position N)" | 0-30s | Cancel |
| **Initiating** | Pulsing dot or "Thinking..." label | < 2s | Wait |
| **Streaming** | Progressive text reveal with cursor | 2-60s | Read, cancel, scroll |
| **Tool use** | "Searching the web..." / "Reading document..." | 2-15s per tool | Watch progress, cancel |
| **Multi-step** | Step indicator: "Step 2 of 5: Analyzing data" | 10s-5min | Monitor, cancel, skip step |
| **Complete** | Cursor removed, action buttons appear | Instant | Copy, edit, regenerate, rate |
| **Error** | Error message with recovery action | Until dismissed | Retry, edit prompt, escalate |

### Skeleton Screens for AI Content

```text
BEFORE AI RESPONSE (skeleton):
┌────────────────────────────────────────────┐
│ AI Assistant                               │
│                                            │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░        │
│                                            │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│ ░░░░░░░░░░░░░░░                           │
│                                            │
│ [Generating...]                            │
└────────────────────────────────────────────┘

DURING STREAMING (partial content):
┌────────────────────────────────────────────┐
│ AI Assistant                               │
│                                            │
│ Based on the documents you provided,       │
│ there are three main findings:             │
│                                            │
│ 1. Revenue increased by 12% year over      │
│    year, driven primarily by|              │
│                                            │
│ [Stop generating]                          │
└────────────────────────────────────────────┘

COMPLETE:
┌────────────────────────────────────────────┐
│ AI Assistant                               │
│                                            │
│ Based on the documents you provided,       │
│ there are three main findings:             │
│                                            │
│ 1. Revenue increased by 12%...             │
│ 2. Customer acquisition cost decreased...  │
│ 3. Retention rates improved by...          │
│                                            │
│ [Copy] [Regenerate] [Edit]    [Good] [Bad] │
└────────────────────────────────────────────┘
```

### Progress Indicators for Long-Running AI Tasks

| Task Duration | Pattern | Example |
|--------------|---------|---------|
| < 2 seconds | Inline spinner or pulse | Single query, autocomplete |
| 2-10 seconds | Animated status label with elapsed time | Document summary, image generation |
| 10-60 seconds | Step-by-step progress with labels | Multi-document analysis, code review |
| 1-5 minutes | Progress bar with percentage and ETA | Dataset processing, batch operations |
| 5+ minutes | Background task with notification on completion | Training, large export, full repo analysis |

```jsx
// Multi-step AI progress indicator
function AIProgress({ steps, currentStep, elapsed }) {
  return (
    <div className="ai-progress" role="status" aria-live="polite">
      <ol className="ai-progress__steps">
        {steps.map((step, i) => (
          <li
            key={i}
            className={
              i < currentStep ? 'complete' :
              i === currentStep ? 'active' : 'pending'
            }
          >
            {i < currentStep && <span aria-hidden="true">Done: </span>}
            {step.label}
            {i === currentStep && (
              <span className="ai-progress__elapsed">
                ({elapsed}s)
              </span>
            )}
          </li>
        ))}
      </ol>
      <button className="ai-progress__cancel">Cancel</button>
    </div>
  );
}
```

---

## AI Transparency & Ethics

### Disclosure Requirements

| Regulation / Framework | Requirement | UI Implication |
|-----------------------|-------------|---------------|
| **EU AI Act (2025)** | High-risk AI systems must inform users they are interacting with AI | Persistent label on AI-generated content; chatbots must identify as non-human |
| **EU AI Act -- GPAI** | General-purpose AI outputs must be machine-readable as AI-generated | Embed C2PA metadata or equivalent watermark |
| **FTC (US)** | AI-generated content must not deceive consumers | Clear "AI-generated" labels on marketing, reviews, testimonials |
| **NIST AI RMF** | AI systems should be explainable and accountable | Provide explanations on request; log AI decisions for audit |
| **California AB 2655** | AI-generated election content must be labeled | Watermark and visible label on political content |
| **China AI Regulations** | AI-generated content must be labeled; deep synthesis requires watermarking | Mandatory watermark on generated images, audio, video |

### When and How to Disclose AI Involvement

| Scenario | Disclosure Level | Implementation |
|----------|-----------------|---------------|
| AI chatbot or assistant | Explicit identification | "I'm an AI assistant" in first message or persistent header |
| AI-generated text content | Visible label | "AI-generated" badge near content |
| AI-assisted suggestions | Subtle indicator | Small icon or label: "AI suggestion" |
| AI-powered search ranking | Transparent on request | Explanation available in settings or info panel |
| Fully automated decision | Full explanation + appeal | Decision rationale shown; human review option available |
| AI-edited user content | Inline markup | Track-changes view showing AI modifications |

### Watermarking and Provenance

| Medium | Watermarking Approach | Standard |
|--------|----------------------|----------|
| **Text** | Statistical watermarking (token distribution shifts) | No universal standard yet; research active |
| **Images** | Invisible pixel-level watermark + C2PA metadata | C2PA / Content Credentials |
| **Audio** | Spectral watermarking | C2PA |
| **Video** | Per-frame invisible watermark | C2PA |
| **All media** | Cryptographic provenance chain (who created, with what tool) | C2PA Content Credentials |

### Consent Patterns for AI Features

| Scenario | Consent Pattern |
|----------|----------------|
| Data used for AI training | Explicit opt-in with clear explanation; easy opt-out |
| AI processes personal data | Informed consent per GDPR; purpose limitation |
| AI makes automated decisions | Right to explanation and human review (GDPR Art. 22) |
| AI features enabled by default | Clear notice on first use; settings to disable |
| Voice/face data collection | Explicit consent with biometric data warnings |

```html
<!-- AI feature consent banner -->
<div role="dialog" aria-labelledby="ai-consent-title" class="ai-consent">
  <h2 id="ai-consent-title">AI-Powered Features</h2>
  <p>
    This product uses AI to provide suggestions and automate tasks.
    Your data is processed to generate personalized results.
  </p>
  <ul>
    <li>AI suggestions are based on your usage patterns</li>
    <li>Your data is not used to train AI models</li>
    <li>You can disable AI features at any time in Settings</li>
  </ul>
  <div class="ai-consent__actions">
    <button class="btn-primary">Enable AI Features</button>
    <button class="btn-secondary">Keep AI Off</button>
    <a href="/privacy/ai">Learn more</a>
  </div>
</div>
```

---

## Agentic UI Patterns

### Multi-Step Task Interfaces

When an AI agent performs a sequence of actions to complete a task, users need visibility into what is happening, what has been done, and what comes next.

| Component | Purpose | Implementation |
|-----------|---------|---------------|
| **Task plan** | Show the steps the agent will take before starting | Numbered list with descriptions; user can reorder or remove steps |
| **Live step tracker** | Show current progress through the plan | Stepper with active/complete/pending states |
| **Action log** | Timestamped record of every action taken | Scrollable log with expandable details |
| **Rollback** | Undo a specific step or revert to a checkpoint | Per-step undo buttons; full rollback to any checkpoint |
| **Pause/resume** | Let user halt the agent mid-task | Pause button pauses after current step completes |

```text
AGENTIC TASK UI:
┌────────────────────────────────────────────────────────┐
│ Task: "Update all pricing pages to reflect new tiers"  │
│ Status: In Progress (Step 3 of 5)                      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [Done]  1. Identify all pricing page files            │
│          Found 4 files                                 │
│                                                        │
│  [Done]  2. Read current pricing data                  │
│          Extracted 3 pricing tiers from each file       │
│                                                        │
│  [>>>>]  3. Generate updated pricing content           │
│          Processing pricing-enterprise.html...          │
│                                                        │
│  [    ]  4. Apply changes to files                     │
│  [    ]  5. Run tests and validate links               │
│                                                        │
├────────────────────────────────────────────────────────┤
│ [Pause]  [Cancel Task]  [View Full Log]                │
└────────────────────────────────────────────────────────┘
```

### Agent Status Dashboard

For systems with multiple agents or long-running background agents, provide a dashboard view.

| Element | Description |
|---------|------------|
| **Agent list** | Named agents with current status (idle, running, paused, error) |
| **Active task** | Current task name, progress, elapsed time |
| **Resource usage** | API calls made, tokens consumed, cost estimate |
| **Recent activity** | Last N actions with timestamps |
| **Controls** | Start, pause, stop, configure per agent |

### Tool Use Visibility

When agents call external tools (search, file read, API calls, code execution), show users what is happening.

| Tool Action | Display Pattern |
|------------|----------------|
| Web search | "Searching for: [query]" with results preview |
| File read | "Reading: filename.ext" with file icon |
| Code execution | Collapsible code block with output |
| API call | "Calling [service name]..." with response summary |
| Database query | "Querying [table/collection]..." with result count |
| Calculation | "Computing..." with formula and result |

```jsx
// Tool use indicator component
function ToolUseIndicator({ tool, query, status, result }) {
  return (
    <div className="tool-use" aria-live="polite">
      <div className="tool-use__header">
        <span className="tool-use__icon">{toolIcons[tool]}</span>
        <span className="tool-use__label">
          {status === 'running' ? `Using ${tool}: ${query}` : `Used ${tool}: ${query}`}
        </span>
        {status === 'running' && <span className="tool-use__spinner" />}
      </div>
      {status === 'complete' && result && (
        <details className="tool-use__result">
          <summary>View result</summary>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </details>
      )}
    </div>
  );
}
```

### Approval Gates

For high-stakes actions, require explicit user approval before the agent proceeds.

| Gate Type | Trigger | UI Pattern |
|----------|---------|-----------|
| **Destructive action** | Delete, overwrite, send externally | Confirmation dialog with action summary |
| **Cost threshold** | Action exceeds dollar or token budget | Cost estimate with approve/deny |
| **Scope expansion** | Agent needs access to new resources | Permission request with justification |
| **External communication** | Agent will send email, post message, call API | Preview of outbound content with edit option |
| **Batch operation** | Agent will modify N items (N > threshold) | Preview list with select-all/deselect, item-level review |

```text
APPROVAL GATE UI:
┌────────────────────────────────────────────────────────┐
│ Approval Required                                      │
│                                                        │
│ The agent wants to send an email to 47 customers       │
│ notifying them of the pricing change.                  │
│                                                        │
│ Preview:                                               │
│ ┌────────────────────────────────────────────────┐     │
│ │ Subject: Important update to your plan pricing │     │
│ │ Dear {name}, We're writing to inform you...    │     │
│ └────────────────────────────────────────────────┘     │
│                                                        │
│ [Preview All 47 Emails]                                │
│                                                        │
│ [Deny]  [Edit Template]  [Approve and Send]            │
└────────────────────────────────────────────────────────┘
```

### Reversibility Tiering

The Approval Gates table above selects the *UI pattern* once you've decided to gate. This decides *whether* to gate at all — and the deciding variable is reversibility, not importance. The two compose: tier first, then pick the gate UI by trigger type.

| Tier | Action class | Behavior | User recourse |
|------|--------------|----------|---------------|
| **Auto-approve** | Safe and reversible (read a file, draft text, run a query) | Agent proceeds silently; action appears in the activity log | Undo from log |
| **Notify-gate** | Impactful but recoverable (edit a document, move a file, update a record) | Agent proceeds *and* surfaces a dismissible notice with an inline undo | Undo without restarting the task |
| **Block-gate** | Irreversible or externally visible (send email, delete, publish, spend money) | Agent halts and waits for explicit approval before proceeding | Approve, edit, or deny before anything happens |

Two design consequences most implementations get wrong:

- **A notify-gate without a working undo is just a block-gate with extra steps** — or worse, an unrecoverable action wearing a recoverable-looking UI. If you can't build the undo, promote the action to block-gate.
- **Tier by what the action does in the world, not by how confident the model is.** High confidence on an irreversible action is still irreversible. Confidence belongs in the display (see Confidence Indicators), never in the gating decision.

Framework-level support now exists for this: LangGraph exposes interrupt/resume as a first-class runtime construct, meaning the pause point is part of the agent's execution graph rather than a UI-layer afterthought. Design the tiers against that runtime capability rather than trying to bolt approval onto a streaming response.

> **Evidence note**: the three-tier shape is widely repeated across 2026 pattern catalogs whose wording is near-identical, so treat the *blog* corroboration as weak — possible circular reposting. The load-bearing evidence is that agent frameworks now ship interrupt/resume primitives, not the number of posts describing the pattern.

### Interruption and Steering

Users change their mind mid-task. Most agent UIs treat this as an error path — offering only "stop" — when it is a normal, expected interaction that deserves first-class support.

Zou et al. (2026) formalize three interruption types and show that all six LLM backbones they tested struggle to handle them gracefully in long-horizon web navigation. Design for all three:

| Type | User intent | Required agent behavior | UI affordance |
|------|-------------|-------------------------|---------------|
| **Addition** | "Also do X" | Absorb the new requirement without discarding completed work | Append-to-task input that stays live during execution |
| **Revision** | "Actually, make it Y instead" | Update the goal, re-plan from current state, keep valid prior steps | Editable plan/goal surface, not a read-only progress log |
| **Retraction** | "Never mind the X part" | Drop the requirement and unwind only its dependent steps | Per-step or per-requirement removal, not all-or-nothing cancel |

Design rules that follow:

- **The composer stays enabled while the agent works.** Disabling input during execution forces users to either wait or hard-stop — the two worst options.
- **Distinguish stop / pause / redirect.** A single "Stop" button collapses three different intents into the most destructive one.
- **Show what survives an interruption.** After a revision, state which completed steps were kept and which are being redone; otherwise users can't tell whether interrupting cost them the whole run.
- **Test interruption explicitly.** It is a distinct failure surface from the happy path — see [../software-ux-research/references/agentic-evaluation-methods.md](../../software-ux-research/references/agentic-evaluation-methods.md).

*Source: [arXiv:2604.00892](https://arxiv.org/abs/2604.00892), Zou et al., "When Users Change Their Mind: Evaluating Interruptible Agents in Long-Horizon Web Navigation" (2026-04-01). InterruptBench, derived from WebArena-Lite; code and dataset public.*

### Cost and Consumption Visibility

Agent token cost compounds in ways users cannot predict from the interface: retries, growing context windows, and multi-step tool chains all multiply usage invisibly. Datadog's production telemetry reports that token usage per request "more than doubled for median customers year over year and quadrupled for 90th-percentile power users" — which makes consumption a UX surface, not a billing afterthought.

| Surface | What to show | Where |
|---------|--------------|-------|
| **Pre-flight estimate** | Expected cost/tokens before a long-running task starts | Task confirmation, alongside the plan |
| **Live accrual** | Running total while the agent works | Status area, updating with each step |
| **Post-task receipt** | Actual vs. estimated, with the steps that dominated | Activity log entry |
| **Budget ceiling** | User-set limit that triggers a block-gate when approached | Settings, surfaced again at the gate |

Rules:

- **Express cost in the user's unit, not yours.** "About 3 minutes and £0.40" beats "~48,000 tokens" for anyone who isn't an engineer. Show tokens as secondary detail.
- **Retries are the surprise.** A task that silently retried four times and cost 5× the estimate reads as a billing bug. Attribute retry cost explicitly.
- **A budget ceiling only works if crossing it stops the agent.** A warning the agent blows through is worse than no ceiling, because it trains users to ignore the signal.

### Agent Memory as an Editable Surface

Once an agent persists preferences and facts across sessions, memory stops being infrastructure and becomes a thing users have opinions about. Treat it as a first-class surface:

- **Viewable** — users can see what the agent believes about them, in plain language, not as a JSON dump.
- **Attributable** — each memory shows when and from which interaction it was learned. "Why does it think that?" is the first question every user asks.
- **Editable and deletable** — per-item correction and removal, not just a global wipe. A wrong memory that can only be fixed by erasing everything will simply stay wrong.
- **Scoped** — users can tell which memories affect current behavior versus which are dormant history. This is the distinction between a memory *log* and a memory *state*.

The deletion path carries a legal dimension for EU-facing products: persisted user facts are personal data, and GDPR erasure rights apply to what the agent remembers, not only to what the database row says.

---

## Human-Agent Interaction Principles

Zhu et al. (2026) argue agents should be evaluated on interaction quality rather than autonomous task performance alone, and organize design guidance across **four interaction stages**. The stage frame is more useful than the individual principles for design review, because it surfaces the two stages teams routinely skip.

| Stage | Design question | Commonly skipped because |
|-------|-----------------|--------------------------|
| **Initially** | How does the user establish intent, scope, and constraints before the agent acts? | Teams optimize the demo path, where intent is assumed |
| **During interaction** | Can the user observe, interrupt, steer, and understand what's happening? | Progress is treated as something to display, not something to act on |
| **Over time** | Does the relationship improve — does it learn preferences, and can the user shape that? | Requires longitudinal thinking; invisible in a single-session usability test |
| **When things go wrong** | Can the user diagnose the failure, recover, and decide whether to trust the next run? | The failure surface is large and unglamorous |

This maps cleanly onto the design skill's existing state-coverage rule. Where a conventional UI needs loading / empty / error / offline / happy states, an agent surface needs those *plus* the four stages above — "when things go wrong" is not the same as an error state, because it includes partial success, wrong-but-plausible output, and recoverable mid-task failure.

**Applying it as a review**: for any agent surface, ask the four stage questions in order. A surface that answers only "during interaction" is a demo, not a product.

*Source: [arXiv:2606.20630](https://arxiv.org/abs/2606.20630), Zhu, Wang, Xiao, Shen, "Design Principles for Human-Agent Interaction" (2026-05-28). 14 principles across 4 stages, applied to evaluate nine agent systems. Position paper — the principles are argued and applied, not empirically validated in a controlled study.*

### Agent-Computer Interface (ACI)

A design discipline symmetric to human-computer interface design: the *agent's* interface to its tools deserves the same care as the user's interface to the product. Anthropic's position is blunt — "We spent more time optimizing our tools than the overall prompt."

This belongs in a UI/UX reference because tool design is where most agent UX failures originate. An agent that picks the wrong tool, or calls the right tool with malformed arguments, produces a user-visible failure that no amount of interface polish repairs.

| Principle | Applied to tool design |
|-----------|------------------------|
| **Write for a competent stranger** | Tool descriptions should read like a docstring written for a new engineer with no context — not a terse schema label |
| **Poka-yoke the arguments** | Design parameters so malformed calls are hard to express: absolute paths over relative, enums over free strings, required fields over optional-with-defaults |
| **Test empirically** | Run realistic tasks and read the actual tool calls. Mispicks and malformed arguments are observable, and they cluster |
| **Match format to failure cost** | Formats the model can produce reliably beat formats that are elegant but easy to get subtly wrong |

*Source: [Anthropic, "Building Effective AI Agents"](https://www.anthropic.com/engineering/building-effective-agents) (2024-12-19). Pre-dates this scan's window but remains canonical and widely cited 18 months on.*

### Generative UI and the Agent-to-UI Contract

When an agent selects or generates interface at runtime rather than the developer pre-building every view, the boundary between agent and UI needs an explicit contract. An emerging spec layer addresses this — AG-UI (CopilotKit), A2UI, Open-JSON-UI, and MCP Apps.

The design-relevant idea is the **event contract shape**, independent of which spec wins: the agent emits typed events (tool call started/finished, generative UI component requested, human-in-the-loop interrupt raised, state delta) and the UI layer owns how each is rendered. That separation is what makes approval gates, tool-use visibility, and streaming coexist without the agent hardcoding presentation.

Design constraints that survive whichever spec you adopt:

- **The agent proposes UI; the design system disposes.** Runtime-generated interface must resolve to your existing components and tokens, or the product's visual coherence degrades one generation at a time.
- **Constrain the component vocabulary.** An agent that can emit arbitrary layout will eventually emit bad layout. A bounded set of composable, pre-designed components is the accessible and on-brand option.
- **Generated UI is still UI.** Focus order, target size, contrast, and reduced-motion apply identically. It is not exempt because a model produced it.

Reference implementations worth reading for pattern (not vendoring): [CopilotKit/AG-UI](https://github.com/CopilotKit/CopilotKit) (MIT), [Vercel AI Elements](https://github.com/vercel/ai), [assistant-ui](https://github.com/assistant-ui/assistant-ui) (MIT) — all actively maintained as of 2026-08-10.

> **Maturity caveat**: the GenUI spec layer is unsettled and vendor-authored. Adopt the *contract shape*; treat any specific spec as a bet, not a standard.

---

## Anti-Patterns

### Common AI UX Mistakes

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| **Anthropomorphizing** | Creates false expectations of understanding, empathy, or memory | Describe capabilities accurately; avoid first-person emotional language |
| **"AI says so" authority** | Removes human accountability for decisions | Human reviews AI recommendations; AI provides supporting evidence |
| **False certainty** | Overconfidence in uncertain outputs erodes trust when wrong | Communicate uncertainty with confidence indicators and hedging language |
| **Hidden AI** | User unaware AI is involved; feels deceived when discovered | Disclose AI involvement at point of interaction |
| **Uncanny valley chatbot** | Avatar or persona that is almost-human but clearly not | Use abstract avatars or clearly non-human design; or go fully realistic |
| **Magic wand syndrome** | Single "AI" button with no explanation of what it does | Label AI actions specifically: "Summarize", "Translate", "Fix grammar" |
| **No undo for AI actions** | AI makes changes with no way to revert | Every AI action must have undo, at minimum for the last action |
| **Infinite generation loop** | User regenerates endlessly hoping for a perfect answer | Offer edit affordances and parameter controls instead of only regenerate |
| **Context amnesia** | AI forgets previous conversation context without explanation | Show context window limits; offer summarization; persist key context |
| **One-size-fits-all responses** | Same verbosity and style regardless of user expertise | Detect or let users set expertise level; adjust output accordingly |
| **Dark patterns with AI** | Using AI to manipulate (urgency, fake personalization) | Transparent AI use; genuine user benefit |
| **Feature-dumping AI** | Adding AI to every feature without clear value | Each AI feature must solve a specific user problem measurably |

### AI-Generated Design Antipatterns

Visual quality problems that emerge when AI generates or assists UI design. Detect and correct before shipping.

| Antipattern | Symptom | Fix |
|-------------|---------|-----|
| **Generic typography** | Inter/Roboto used without intention | Choose fonts matching brand and context |
| **Unmotivated color** | Purple gradients, blue glow with no brand rationale | Derive palette from brand, content, or context |
| **Card-on-card nesting** | Cards inside cards with redundant borders and shadows | Flatten hierarchy; use spacing and type instead |
| **Bounce/elastic easing** | Playful spring animations in professional contexts | Match easing to product tone; default to ease-out |
| **Gray text on color** | Low-contrast gray labels on colored backgrounds | Tint text with background hue; verify contrast |
| **Pure black/gray** | Flat #000 or untinted grays | Tint darks toward warm or cool hue |
| **Frankenstein layouts** | Disjointed sections with no visual rhythm | Establish grid and vertical rhythm first |
| **Repeated elements** | Same component pattern copy-pasted without variation | Vary density, hierarchy, and content structure |
| **Mismatched hierarchy** | Visual weight doesn't match content importance | Define heading hierarchy before generation |
| **Design system drift** | Generated components ignore existing design system | Constrain to schema-defined tokens and components |

Sources: [Impeccable.style](https://impeccable.style/), [NNGroup](https://www.nngroup.com/articles/vague-prototyping/), [AI Slop vs Constrained UI](https://dev.to/puckeditor/ai-slop-vs-constrained-ui-why-most-generative-interfaces-fail-pm9)

### Anthropomorphism Scale

| Level | Example | Risk | Recommendation |
|-------|---------|------|----------------|
| **None** | "Results generated" | No emotional connection | Good for tools and utilities |
| **Minimal** | "AI Assistant" with abstract icon | Low risk | Recommended default for most products |
| **Moderate** | Named assistant with personality traits | Medium: users may over-trust | Use for brand differentiation with clear AI disclosure |
| **High** | Human-like avatar with emotional responses | High: users may confuse for human | Generally avoid; if used, add persistent "AI" label |

---

## Implementation Checklists

### AI Feature Launch Checklist

- [ ] AI involvement is disclosed at the point of interaction
- [ ] User can disable or opt out of AI features
- [ ] Every AI action has an undo or revert mechanism
- [ ] Loading states cover all phases (queued, processing, streaming, complete, error)
- [ ] Error states provide recovery actions (retry, edit, escalate)
- [ ] Confidence is communicated where outputs are uncertain
- [ ] AI-generated content is labeled as such
- [ ] Human escalation path exists for critical tasks
- [ ] Graceful degradation works when AI services are unavailable
- [ ] Accessibility: AI content works with screen readers and keyboard navigation
- [ ] Regulatory compliance: disclosure labels meet applicable jurisdiction requirements
- [ ] Performance: response times are within acceptable thresholds for the use case
- [ ] Feedback mechanism: users can rate AI quality (thumbs up/down, detailed report)
- [ ] Audit trail: AI decisions and actions are logged for review

### Conversational UI Checklist

- [ ] First message identifies the system as AI
- [ ] Suggested prompts shown on empty state
- [ ] Streaming responses with visible progress
- [ ] Cancel button available during generation
- [ ] Copy, regenerate, and edit actions on completed responses
- [ ] Error messages are specific and offer recovery
- [ ] Context limits are communicated before they are hit
- [ ] Conversation history is preserved across sessions
- [ ] Input supports multiline, paste, and file attachment where relevant
- [ ] Keyboard shortcuts documented and accessible

### Agentic Task Checklist

- [ ] Task plan shown before execution begins
- [ ] Each step has visible status (pending, running, complete, error)
- [ ] Tool use is visible with query and result
- [ ] Approval gates protect destructive or high-cost actions
- [ ] User can pause, resume, or cancel at any step
- [ ] Per-step undo or full rollback is available
- [ ] Cost/resource tracking is visible during execution
- [ ] Completion summary shows what was done, what changed, and any issues

---

## References

- [Google PAIR Guidebook](https://pair.withgoogle.com/guidebook/) -- People + AI Research
- [Microsoft HAX Toolkit](https://www.microsoft.com/en-us/haxtoolkit/) -- Human-AI Experience guidelines
- [Apple HIG -- Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Nielsen Norman Group -- AI UX](https://www.nngroup.com/topic/ai/) -- Research on AI user experience
- [EU AI Act](https://artificialintelligenceact.eu/) -- Regulatory requirements for AI systems
- [NIST AI Risk Management Framework](https://www.nist.gov/artificial-intelligence/ai-risk-management-framework)
- [C2PA Content Credentials](https://c2pa.org/) -- Content provenance standard
- [Anthropic Responsible Disclosure Policy](https://www.anthropic.com/responsible-disclosure-policy)
- [IBM Design for AI](https://www.ibm.com/design/ai/) -- Enterprise AI design patterns
- [Impeccable.style](https://impeccable.style/) -- AI design antipattern toolkit
- [The Shape of AI](https://www.shapeof.ai/) -- 58 UX patterns for AI interfaces
- [AI UX Patterns](https://www.aiuxpatterns.com/) -- AI UX pattern catalog
- [Smashing Magazine -- AI Interface Patterns](https://www.smashingmagazine.com/2025/07/design-patterns-ai-interfaces/)

---

## Cross-References

- [SKILL.md](../SKILL.md) -- Parent skill overview and platform constraints
- [wcag-accessibility.md](wcag-accessibility.md) -- Accessibility requirements for AI interfaces
- [nielsen-heuristics.md](nielsen-heuristics.md) -- Heuristic evaluation applicable to AI UX
- [modern-ux-patterns.md](modern-ux-patterns.md) -- Broader UX patterns including AI-adjacent trends
- [form-design-patterns.md](form-design-patterns.md) -- Form patterns relevant to AI input interfaces
- [design-systems.md](design-systems.md) -- Component architecture for AI UI components
- [ai-design-tools.md](ai-design-tools.md) -- AI tools for the design process itself
