# AI Coding Tools Adoption Survey

**Last Updated**: {{DATE}}
**Owner**: {{NAME}}
**Version**: {{VERSION}}

---

Purpose: measure developer adoption, satisfaction, and friction with AI coding tools. Use as a copy-paste template for your survey platform (Google Forms, Typeform, SurveyMonkey, etc.).

## Administration Instructions

- **Cadence**: run quarterly, at minimum. Run an additional pulse after major tool changes.
- **Response rate target**: >70% of licensed developers. Below 50% makes results unreliable.
- **Anonymity**: responses must be anonymous. Collect only team/role demographics, never names.
- **Distribution**: send via engineering-wide channel. Send 2 reminders (day 3, day 6 of a 10-day window).
- **Time to complete**: target under 8 minutes. Pre-test with 3 developers and adjust.
- **Results sharing**: publish summary to all respondents within 2 weeks of close.

---

## Section 1: Usage (Q1-Q3)

### Q1. How often do you use AI coding tools in your work?

- Response type: **Single choice**
- Options:
  - Multiple times per day
  - About once per day
  - A few times per week
  - Rarely (less than once per week)
  - Never
- Benchmark: healthy adoption = >60% daily users after 3 months

### Q2. Which AI coding tools do you actively use? (Select all that apply)

- Response type: **Multiple choice**
- Options:
  - {{TOOL_1}} (e.g., GitHub Copilot)
  - {{TOOL_2}} (e.g., Cursor)
  - {{TOOL_3}} (e.g., Claude Code)
  - {{TOOL_4}} (e.g., ChatGPT)
  - Other: {{FREE_TEXT}}
  - None
- Benchmark: track tool distribution shifts quarter over quarter

### Q3. What are your primary use cases? (Select top 3)

- Response type: **Multiple choice (max 3)**
- Options:
  - Code completion / autocomplete
  - Writing new functions or modules
  - Writing tests
  - Debugging / fixing errors
  - Code review assistance
  - Refactoring existing code
  - Documentation and comments
  - Learning new APIs or languages
  - Explaining unfamiliar code
  - Other: {{FREE_TEXT}}
- Benchmark: track shifts in use-case mix over time

---

## Section 2: Effectiveness (Q4-Q7)

### Q4. How has AI tooling affected your personal productivity?

- Response type: **Single choice**
- Options:
  - Significantly more productive (>20% time savings)
  - Somewhat more productive (5-20% time savings)
  - No noticeable change
  - Somewhat less productive (net time lost on corrections)
  - Significantly less productive
- Benchmark: >70% reporting "somewhat" or "significantly" more productive

### Q5. How has AI tooling affected the quality of code you produce?

- Response type: **Single choice**
- Options:
  - Noticeably higher quality
  - Slightly higher quality
  - No change
  - Slightly lower quality
  - Noticeably lower quality
- Benchmark: <10% reporting lower quality

### Q6. Estimate hours saved per week due to AI coding tools.

- Response type: **Single choice**
- Options:
  - 0 hours (no savings)
  - 1-2 hours
  - 3-4 hours
  - 5-6 hours
  - 7-8 hours
  - More than 8 hours
- Benchmark: median of 3-5 hours at mature adoption

### Q7. For which tasks do AI tools help most vs least?

- Response type: **Two free-text fields**
  - "AI tools help most with:" {{FREE_TEXT}}
  - "AI tools help least with:" {{FREE_TEXT}}
- Benchmark: qualitative; code for recurring themes

---

## Section 3: Experience (Q8-Q11)

### Q8. Overall, how satisfied are you with the AI coding tools provided?

- Response type: **Likert scale (1-5)**
  - 1 = Very dissatisfied
  - 2 = Dissatisfied
  - 3 = Neutral
  - 4 = Satisfied
  - 5 = Very satisfied
- Benchmark: target mean >= 3.8

### Q9. How much do you trust the output of AI coding tools?

- Response type: **Likert scale (1-5)**
  - 1 = Do not trust at all; review everything line by line
  - 2 = Low trust; accept only trivial suggestions
  - 3 = Moderate trust; accept after a quick scan
  - 4 = High trust; accept most suggestions for familiar code
  - 5 = Very high trust; rarely need to modify
- Benchmark: healthy range is 3-4; scores of 5 may indicate under-review risk

### Q10. What frustrates you most about AI coding tools? (Select top 2)

- Response type: **Multiple choice (max 2)**
- Options:
  - Irrelevant or wrong suggestions
  - Slow response time
  - Breaks my flow / context switching
  - Security / IP concerns
  - Inconsistent quality across languages
  - Hard to customize or configure
  - Nothing; no frustrations
  - Other: {{FREE_TEXT}}
- Benchmark: track top frustration shifts quarter over quarter

### Q11. Does using AI coding tools increase or decrease your cognitive load?

- Response type: **Single choice**
- Options:
  - Significantly decreases cognitive load
  - Somewhat decreases cognitive load
  - No change
  - Somewhat increases cognitive load (evaluating suggestions is tiring)
  - Significantly increases cognitive load
- Benchmark: <15% reporting increased cognitive load

---

## Section 4: Barriers (Q12-Q14)

### Q12. What prevents you from using AI coding tools more? (Select all that apply)

- Response type: **Multiple choice**
- Options:
  - Nothing; I use them as much as I want
  - Doesn't work well with my language/framework
  - Concerns about code quality/correctness
  - Security or compliance restrictions
  - Lack of training or onboarding
  - Tool is too slow or unreliable
  - My workflow doesn't benefit from it
  - Team norms discourage use
  - Other: {{FREE_TEXT}}
- Benchmark: identify top 3 barriers; track removal progress

### Q13. What would help you get more value from AI coding tools?

- Response type: **Multiple choice (select top 2)**
- Options:
  - Better onboarding / training
  - Prompt engineering tips and examples
  - More context-aware suggestions (repo-level)
  - Integration with our specific tools/frameworks
  - Faster response times
  - Clearer security/compliance guidelines
  - Team sharing of effective patterns
  - Other: {{FREE_TEXT}}
- Benchmark: feed into training and enablement roadmap

### Q14. Have you received adequate training on AI coding tools?

- Response type: **Single choice**
- Options:
  - Yes, comprehensive training
  - Yes, basic training (enough to get started)
  - Self-taught only
  - No training received
- Benchmark: >80% should have at least basic training

---

## Section 5: Open-Ended (Q15)

### Q15. Any other feedback, suggestions, or concerns about AI coding tools?

- Response type: **Free text (optional)**
- {{FREE_TEXT}}
- Analysis: code responses into themes; report top 5 themes with representative quotes

---

## Scoring Methodology

### Aggregate Adoption Score (0-100)

Calculate a weighted composite:

| Component | Weight | Calculation |
|-----------|--------|-------------|
| Usage frequency (Q1) | 30% | Map to 0-100: Never=0, Rarely=25, Few/week=50, Daily=75, Multi-daily=100 |
| Productivity impact (Q4) | 25% | Map to 0-100: Sig. less=0, Somewhat less=25, No change=50, Somewhat more=75, Sig. more=100 |
| Satisfaction (Q8) | 25% | Likert 1-5 mapped to 0-100 |
| Trust (Q9) | 20% | Likert 1-5 mapped to 0-100 |

**Aggregate Score** = (Q1_score x 0.30) + (Q4_score x 0.25) + (Q8_score x 0.25) + (Q9_score x 0.20)

### Interpretation

| Score Range | Label | Action |
|-------------|-------|--------|
| 80-100 | Strong adoption | Maintain; share best practices |
| 60-79 | Healthy adoption | Minor improvements; address top barrier |
| 40-59 | Developing | Targeted training; investigate friction |
| 20-39 | Struggling | Intervention needed; exec sponsorship |
| 0-19 | Not adopted | Reassess tool fit and rollout strategy |

---

## Quarter-over-Quarter Tracking

| Metric | Q{{N-2}} | Q{{N-1}} | Q{{N}} | Trend |
|--------|----------|----------|--------|-------|
| Response Rate (%) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{TREND}} |
| Aggregate Adoption Score | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{TREND}} |
| Mean Satisfaction (Q8) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{TREND}} |
| Median Hours Saved (Q6) | {{VALUE}} | {{VALUE}} | {{VALUE}} | {{TREND}} |
| Top Barrier (Q12) | {{VALUE}} | {{VALUE}} | {{VALUE}} | — |
