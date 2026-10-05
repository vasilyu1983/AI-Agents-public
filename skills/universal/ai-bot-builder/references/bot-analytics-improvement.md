# Bot Analytics and Improvement

Use this reference when measuring bot performance, running conversation reviews, A/B testing bot changes, and building improvement loops.

## Table of Contents

- [Core Metrics Taxonomy](#core-metrics-taxonomy)
- [Conversation Review Workflow](#conversation-review-workflow)
- [A/B Testing Bot Variants](#ab-testing-bot-variants)
- [Improvement Loop](#improvement-loop)
- [Dashboard Template](#dashboard-template)
- [Common Failure Patterns](#common-failure-patterns)

## Core Metrics Taxonomy

### Resolution metrics

| Metric | Formula | Target | Why it matters |
|--------|---------|--------|---------------|
| Containment rate | Resolved without human / Total conversations | 60-80% | Primary measure of bot value |
| Resolution rate | Issue actually resolved (confirmed) / Total conversations | > 70% | Containment without resolution is meaningless |
| Escalation rate | Escalated to human / Total conversations | < 25% | High escalation = bot scope or quality problem |
| Abandonment rate | User left without resolution / Total conversations | < 15% | High abandonment = friction or trust problem |

### Quality metrics

| Metric | Formula | Target | Why it matters |
|--------|---------|--------|---------------|
| CSAT | Average satisfaction score (1-5) | > 4.0 | Direct user perception |
| NPS | Promoters - Detractors (scale -100 to 100) | > 30 | Willingness to recommend |
| First-contact resolution | Resolved in first conversation / Resolved total | > 85% | Repeat contacts signal incomplete resolution |
| Correct resolution rate | Spot-checked correct / Spot-checked total | > 95% | Bot may "resolve" with wrong information |

### Efficiency metrics

| Metric | Formula | Target | Why it matters |
|--------|---------|--------|---------------|
| Average turns to resolution | Sum of turns for resolved / Resolved count | < 6 | More turns = more friction |
| First-response time | Time from user message to first bot response | < 2s | Responsiveness drives satisfaction |
| Cost per conversation | (LLM tokens + tool calls + infra) / Conversations | Track trend | Unit economics matter at scale |
| Conversations per hour | Total conversations / Hours | Track trend | Capacity planning |

### Tracking implementation

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ConversationMetrics:
    session_id: str
    started_at: datetime
    ended_at: datetime | None = None
    channel: str = ""
    intent: str = ""

    # Resolution
    resolution: str = ""            # resolved_by_bot, escalated, abandoned
    resolution_confirmed: bool = False

    # Efficiency
    turn_count: int = 0
    first_response_ms: int = 0
    total_duration_seconds: int = 0

    # Quality
    csat_score: int | None = None
    csat_feedback: str | None = None

    # Cost
    prompt_tokens: int = 0
    completion_tokens: int = 0
    tool_calls: int = 0
    tool_call_details: list[dict] = field(default_factory=list)

    def cost_estimate_usd(self, rates: dict) -> float:
        """Cost from rates you supply: {"input_per_1m", "output_per_1m", "per_tool_call"}.

        Take the model rates from the provider's pricing page and the tool rate
        from your API vendors; no default rate, so a missing key raises.
        """
        input_cost = self.prompt_tokens * rates["input_per_1m"] / 1_000_000
        output_cost = self.completion_tokens * rates["output_per_1m"] / 1_000_000
        tool_cost = self.tool_calls * rates["per_tool_call"]
        return input_cost + output_cost + tool_cost
```

**Rules:**
- Track containment rate AND resolution rate. A bot that "contains" by confusing users until they leave is not working.
- Cost per conversation should include LLM costs, tool/API call costs, and amortized infrastructure.
- Segment every metric by intent, channel, and customer tier. Aggregates hide problems.

## Conversation Review Workflow

Automated metrics tell you what's happening. Conversation review tells you why.

**Sampling strategy:**

| Sample type | How to select | Volume | Frequency |
|-------------|--------------|--------|-----------|
| Random | Uniform random across all conversations | 50/week | Weekly |
| Escalated | All conversations that escalated to human | All (or 50 if high volume) | Weekly |
| Low CSAT | Conversations with CSAT 1-2 | All | Weekly |
| Abandoned | Conversations where user dropped mid-flow | 20/week | Weekly |
| Long conversations | Conversations > 10 turns | 20/week | Weekly |
| New intent | Conversations where intent was "other" / "unknown" | 20/week | Weekly |

**Review scorecard:**

```python
@dataclass
class ConversationReview:
    session_id: str
    reviewer: str
    reviewed_at: str

    # Correctness (1-5)
    factual_accuracy: int           # Was the information correct?
    action_accuracy: int            # Were the right actions taken?

    # Quality (1-5)
    tone_consistency: int           # Did the bot maintain persona?
    response_clarity: int           # Were responses clear and concise?
    conversation_flow: int          # Did the flow feel natural?

    # Outcome
    was_resolution_correct: bool    # Did the bot reach the right outcome?
    could_have_been_contained: bool # If escalated — could the bot have handled it?
    missed_intent: str | None       # Intent the bot should have caught but didn't

    # Action items
    notes: str
    action_items: list[str]         # Specific improvements to make
```

**Review cadence:**
- Weekly: one team member reviews 50+ conversations using the scorecard.
- Monthly: aggregate review findings into improvement themes.
- Quarterly: calibrate reviewers (2+ people review the same 20 conversations, compare scores).

## A/B Testing Bot Variants

Test one change at a time. Measure impact before rolling out.

**Testable dimensions:**

| Dimension | What to change | Primary metric |
|-----------|---------------|---------------|
| System prompt | Tone, instructions, persona | CSAT, resolution rate |
| Flow design | State transitions, fallback hierarchy | Containment rate, turns to resolution |
| Tool usage | Add/remove tools, change tool parameters | Resolution rate, escalation rate |
| Model | Model A vs model B (same prompt, same eval set) | Cost, latency, accuracy |
| Temperature | 0.0 vs 0.3 vs 0.7 | Response consistency, CSAT |
| Few-shot examples | Add/remove/change examples in prompt | Accuracy, tone consistency |

**A/B test implementation:**

```python
import hashlib

@dataclass
class BotVariant:
    name: str                       # "control", "variant_a", "variant_b"
    system_prompt: str
    model: str
    temperature: float
    tools: list[str]

class ABTestRouter:
    def __init__(self, experiment_id: str, variants: list[BotVariant], weights: list[float]):
        self.experiment_id = experiment_id
        self.variants = variants
        self.weights = weights          # e.g., [0.5, 0.5] for 50/50 split

    def assign(self, session_id: str) -> BotVariant:
        """Deterministic assignment — same session always gets the same variant."""
        hash_input = f"{self.experiment_id}:{session_id}"
        bucket = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16) % 1000
        cumulative = 0
        for variant, weight in zip(self.variants, self.weights):
            cumulative += int(weight * 1000)
            if bucket < cumulative:
                return variant
        return self.variants[-1]

# Usage
experiment = ABTestRouter(
    experiment_id="prompt_tone_test_2026_03",
    variants=[control_variant, warm_tone_variant],
    weights=[0.5, 0.5],
)
```

**Statistical rigor:**

```python
from scipy import stats

def is_significant(
    control_metric: float,
    variant_metric: float,
    control_n: int,
    variant_n: int,
    alpha: float = 0.05,
) -> bool:
    """Check if the difference is statistically significant (two-proportion z-test)."""
    p_pool = (control_metric * control_n + variant_metric * variant_n) / (control_n + variant_n)
    se = (p_pool * (1 - p_pool) * (1/control_n + 1/variant_n)) ** 0.5
    if se == 0:
        return False
    z = (variant_metric - control_metric) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    return p_value < alpha
```

**Rules:**
- Minimum 1,000 conversations per variant before evaluating.
- Run for at least 2 weeks to account for weekday/weekend variation.
- Test one dimension at a time. If you change the prompt AND the model, you can't attribute the effect.
- Always include the current production setup as the control.
- Kill tests early if a variant causes harm (escalation rate spikes, CSAT drops below threshold).

## Improvement Loop

A structured cycle from observation to measurement.

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│   Review     │──▶│   Identify   │──▶│    Update       │──▶│   Measure    │
│   Convos     │   │   Patterns   │   │    Bot          │   │   Impact     │
└──────┬───────┘   └──────────────┘   └────────────────┘   └──────┬───────┘
       │                                                          │
       └──────────────────────────────────────────────────────────┘
```

**Step 1: Review conversations**
- Use the sampling strategy and scorecard from the review workflow above.
- Focus on failures: escalated, abandoned, low CSAT, long conversations.

**Step 2: Identify patterns**
- Group failures by root cause, not by symptom.

| Root cause | Example symptoms |
|-----------|-----------------|
| Missing knowledge | Bot says "I don't have information on that" for a documented topic |
| Wrong tool usage | Bot looks up wrong order, queries wrong system |
| Poor conversation flow | User goes in circles, bot asks the same question twice |
| Tone mismatch | User is frustrated, bot is too cheerful |
| Scope gap | Users ask for something reasonable the bot can't do |
| Hallucination | Bot invents policies, order numbers, or deadlines |

**Step 3: Update the bot**
- For each identified pattern, make a targeted fix:

| Root cause | Fix |
|-----------|-----|
| Missing knowledge | Add articles to KB, re-index |
| Wrong tool usage | Fix tool descriptions, add input validation |
| Poor conversation flow | Redesign state transitions, add slot validation |
| Tone mismatch | Update persona spec, add situation-specific tone modifiers |
| Scope gap | Add new tool or intent handler, or add to out-of-scope messaging |
| Hallucination | Strengthen grounding rules, lower temperature, add citation requirements |

**Step 4: Measure impact**
- Deploy the fix as an A/B test (or canary) if the change is significant.
- For small fixes (KB update, typo), deploy directly and monitor for regression.
- Compare the specific metric the fix targets, plus overall metrics.

**Cadence:**
- Weekly: review + identify (1-2 hours).
- Bi-weekly: deploy updates.
- Monthly: measure cumulative improvement across all metrics.

## Dashboard Template

**Top-level view (daily):**

| Section | Metrics | Visualization |
|---------|---------|---------------|
| Volume | Conversations today, vs 7-day avg | Sparkline |
| Containment | Containment rate, resolution rate | Gauge (target zone: green) |
| Quality | CSAT average, NPS | Trend line (7-day rolling) |
| Efficiency | Avg turns to resolution, first-response time | Bar chart |
| Cost | Cost per conversation, total daily cost | Trend line |

**Drill-down views:**

| View | Dimensions | Purpose |
|------|-----------|---------|
| By intent | Containment, CSAT, escalation per intent | Find which intents need work |
| By channel | All metrics per channel | Channel-specific issues |
| By time | Hourly volume and escalation | Staffing and capacity planning |
| By customer tier | All metrics per tier | VIP experience tracking |

**Alert thresholds:**

```python
ALERT_THRESHOLDS = {
    "containment_rate": {"warn": 0.55, "critical": 0.45, "direction": "below"},
    "escalation_rate": {"warn": 0.30, "critical": 0.40, "direction": "above"},
    "csat_average": {"warn": 3.5, "critical": 3.0, "direction": "below"},
    "abandonment_rate": {"warn": 0.20, "critical": 0.30, "direction": "above"},
    "avg_first_response_ms": {"warn": 3000, "critical": 5000, "direction": "above"},
    "error_rate": {"warn": 0.05, "critical": 0.10, "direction": "above"},
}

async def check_alerts(current_metrics: dict):
    for metric, thresholds in ALERT_THRESHOLDS.items():
        value = current_metrics.get(metric)
        if value is None:
            continue

        if thresholds["direction"] == "below":
            if value < thresholds["critical"]:
                await send_alert(metric, value, "critical")
            elif value < thresholds["warn"]:
                await send_alert(metric, value, "warn")
        else:
            if value > thresholds["critical"]:
                await send_alert(metric, value, "critical")
            elif value > thresholds["warn"]:
                await send_alert(metric, value, "warn")
```

## Common Failure Patterns

### Loops

**Symptom:** Bot asks the same question 3+ times or cycles between two states.

**Detection:**

```python
def detect_loop(messages: list[dict], window: int = 6) -> bool:
    """Check if the bot repeated the same message in the last N messages."""
    bot_messages = [m["text"] for m in messages[-window:] if m["sender"] == "bot"]
    from collections import Counter
    counts = Counter(bot_messages)
    return any(count >= 3 for count in counts.values())
```

**Root cause:** Missing or incorrect state transitions. The bot doesn't know how to advance.
**Fix:** Add a `turns_in_current_state` counter with a hard limit. After 3 turns in the same state with no progress, advance or escalate.

### Dead ends

**Symptom:** Bot delivers a final-sounding message but the user isn't done.

**Detection:** User sends another message after a "closing" bot message.
**Root cause:** Bot assumed resolution without confirming.
**Fix:** Always ask "Is there anything else I can help with?" before closing. Track the "reopen after close" rate.

### Topic drift

**Symptom:** Conversation wanders from the original intent without resolution.

**Detection:**

```python
def detect_topic_drift(messages: list[dict]) -> bool:
    """Check if the conversation has drifted from the original intent."""
    first_intent = classify_intent(messages[0]["text"])
    latest_intent = classify_intent(messages[-1]["text"])
    return first_intent != latest_intent and not is_resolved(messages)
```

**Root cause:** Bot follows the user's tangents instead of steering back.
**Fix:** Track the primary intent. If the user introduces a new topic, acknowledge it but steer back: "I'll note that — let me first finish helping with your [original intent]."

### Hallucination

**Symptom:** Bot states made-up policies, prices, dates, or order details.

**Detection:**
- Cross-reference bot claims against tool results and KB articles.
- Flag responses that contain numbers, dates, or policies not found in any source.

```python
async def check_hallucination(bot_response: str, sources: list[str]) -> bool:
    """Check if the bot's response contains claims not supported by sources."""
    result = await llm.classify(
        prompt=f"""Does this response contain any factual claims not supported by the sources?

Response: {bot_response}
Sources: {sources}

Answer YES or NO."""
    )
    return "YES" in result.upper()
```

**Root cause:** LLM generating plausible-sounding but invented details. Weak grounding instructions.
**Fix:** Strengthen grounding rules in the system prompt. Add "cite your source" requirements. Lower temperature. Add a post-generation verification step for high-stakes responses.

For eval harnesses and red-team testing, see [`../qa-agent-testing/SKILL.md`](../../qa-agent-testing/SKILL.md).
