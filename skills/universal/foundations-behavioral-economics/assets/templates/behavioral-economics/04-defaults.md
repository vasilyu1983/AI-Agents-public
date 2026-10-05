# Primitive: Defaults

## Definition

Default bias (or status quo bias in its broader form) is the strong tendency for people to accept pre-set options rather than actively choosing alternatives. The default is what happens when the user does nothing. Because inertia and loss aversion both favor the status quo, defaults exert disproportionate influence on outcomes.

Key properties:
- Opt-out rates are substantially lower than opt-in rates for the same outcome. Thaler & Sunstein's canonical examples: organ donation rates in opt-out countries (Austria ~99%) vs opt-in countries (Germany ~12%).
- Defaults signal social norms ("this is what most people do").
- Defaults reduce cognitive load — they substitute for a decision.
- The default is not neutral: whoever sets the default shapes the distribution of outcomes.

Types of defaults:
- **Opt-in**: user must take action to receive the feature/service. Low uptake.
- **Opt-out**: user must take action to not receive the feature/service. High uptake.
- **Active choice**: user is required to make an explicit choice (no default). Used when the best option is genuinely user-specific.
- **Prompted choice**: user is required to choose but is shown a recommended option.

## When to Use

- **Onboarding flows**: pre-select the configuration that most users benefit from.
- **Notification settings**: default to useful notification types; require opt-out for less important ones.
- **Plan pre-selection**: highlight a recommended tier as pre-selected.
- **Annual vs monthly billing**: if annual is better for the user, pre-select it.
- **Consent and privacy flows**: critical — default must be the user's best option, not the operator's.

## Misuse Boundary

**Ethical use**: The default must be the option that is genuinely best for the user — not what generates the most revenue for the operator at the user's expense. Defaults are appropriate when most users in this context benefit from the pre-selected option, and when opting out is equally easy to opting in.

**Manipulation**: Setting a default that benefits the operator while harming the user (e.g., defaulting to data sharing the user would not consent to; pre-selecting the most expensive plan when cheaper plans meet the user's need; hiding the opt-out path behind multiple screens).

**Required conditions**:
1. The default is the user's best option for the typical case in this context.
2. The default is transparent — users see what was pre-selected and why.
3. The opt-out path is equally prominent and low-friction as the default path.
4. For consent (GDPR/ICO context): no default consent — explicit affirmative action is required. Defaults cannot be used to obtain consent.

## Inputs

- The population of users who will encounter this choice.
- What outcome is best for the typical user in this population.
- The friction cost of opting out vs the cost of accepting the default.

## Outputs

- A pre-selected option with a brief explanation of why it was pre-selected.
- A visible, equally accessible opt-out path.
- For active-choice scenarios: a recommended option with no pre-selection.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Default is never changed even by users who should change it | Default is too sticky; friction to opt-out is too high | Audit opt-out path; reduce its friction; consider active-choice for high-variance user populations |
| Default adoption rate is used to claim user preference | Defaults drive adoption, not preference | Distinguish revealed preference (with opt-out available) from inertia; don't cite default-rate as demand evidence |
| Regulatory action | Default used to obtain consent or enroll users in paid service without explicit choice | Use active choice for consent and billing; consult ICO/CMA guidance |
| Wrong default for a segment | Default is correct for median user but wrong for a significant minority | Personalize defaults where signal is available; always surface the default clearly |

## Worked Example

**Scenario**: New user onboarding for a project management tool.

Without defaults: User sees an empty "Notification preferences" screen and skips it.

With ethical defaults:
- Pre-select: "Email me when a task is assigned to me" (clearly beneficial to the user).
- Do not pre-select: "Email me marketing updates from [Product]" (operator benefit, not user benefit).
- Show a brief note: "We've enabled notifications that help you stay on top of your work. You can change these anytime."
- Opt-out path: one click on the same screen.

**Ethical check**: The pre-selected option benefits the user (task notifications). The marketing email is opt-in only. Opt-out is equally easy.

**Contrast with manipulation**: Pre-selecting "Allow [Product] to share your usage data with third parties for advertising" — operator benefit, user harm, dark pattern, fails ICO consent requirements.

## Sources

- Thaler, R. H. & Sunstein, C. R. (2008). _Nudge_, ch. 1, 3. — canonical defaults framework and organ donation example.
- Johnson, E. J. & Goldstein, D. (2003). Do defaults save lives? _Science_, 302(5649), 1338–1339. — opt-in vs opt-out organ donation rates.
- Samuelson, W. & Zeckhauser, R. (1988). Status quo bias in decision making. _Journal of Risk and Uncertainty_, 1(1), 7–59. — status quo bias.
- ICO (UK). Guidance on consent under GDPR — explicit prohibition on default consent.
