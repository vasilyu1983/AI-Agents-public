# Primitive: Loss Aversion

## Definition

Loss aversion describes greater fitted subjective weight for losses than equivalent gains in some reference-dependent choice tasks. Its magnitude depends on task, model, elicitation and population; reported means do not bound individual estimates. The canonical estimate from Kahneman & Tversky (1992) is a loss aversion coefficient (λ) of approximately **2.25**, a historical task-specific estimate, not an upper bound: Brown et al. (JEL 2024, 607 estimates) place the cross-domain mean at λ ≈ 1.955, and a 2025 re-meta-analysis (JEP 107) finds λ ≈ 1.07 (non-significant) for symmetric unordered gain-loss designs. The effect is robust when experimental design induces ordinal asymmetry, but is not a universal constant.

Implications:
- "Don't lose X" and "Get X" are candidate frames; a utility coefficient does not establish copy superiority. Compare truthful variants locally.
- A fitted loss-weight parameter describes the modeled choice task, not a direct measurement of pain or copy response.
- Endowment effect: people demand more to give up something they own than they would pay to acquire it.
- Status quo bias is partly driven by loss aversion — changing from the current state is framed as a loss.

Loss aversion is a component of prospect theory (#1) but deserves its own primitive because the direct application — loss-frame vs gain-frame — appears in almost every conversion, retention, and upsell context.

## When to Use

- **Churn prevention**: the user is about to lose something they have built (data, streaks, integrations, team access).
- **Trial expiry**: the user will lose trial access; what they currently enjoy will be taken away.
- **Feature removal or downgrade warnings**: plan changes that remove access to features already in use.
- **Subscription upsell**: the user risks losing something currently available on a trial or lower tier.
- **Any scenario where the baseline is "keep what you have" vs "gain something new"**.

## Misuse Boundary

**Ethical use**: Deploy loss framing when the user genuinely possesses or currently benefits from something they will lose if they don't act. The loss must be real, specific, and relevant to this user.

**Manipulation**: Manufacturing a loss that doesn't exist ("You're about to lose your spot!" when spots are unlimited), exaggerating the magnitude of loss, or triggering loss aversion on trivial stakes to create chronic anxiety.

**Required condition**: (1) The loss is real — the user actually has the thing at risk. (2) The loss is specific — name what is lost, not a vague threat. (3) The loss is proportionate — the emotional weight of the framing should match the actual stakes.

## Inputs

- Identification of what the user currently has or is currently experiencing.
- A specific action the user needs to take to preserve it.
- The timeline (if any) before loss occurs.

## Outputs

- Loss-framed copy that names the specific thing at risk.
- A clear, low-friction action that prevents the loss.
- Optional: a reminder of what they have built / invested (endowment reinforcement).

Validate candidates through [local outcome testing](../../../references/local-validation.md), including comprehension, pressure and cancellation completion alongside retention. Never multiply conversion or save rate by λ.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Loss framing produces anxiety but no action | No clear path to prevention | Pair every loss frame with one specific, immediate action |
| Loss framing destroys trust | Manufactured loss (not real) discovered by user | Only frame as loss what is objectively, verifiably at risk |
| Loss framing is ineffective | User doesn't feel ownership of the asset being threatened | Establish the endowment first (show usage data, streaks, content created) before invoking loss |
| Overuse creates learned helplessness | Every email threatens a loss | Reserve loss framing for genuine high-stakes moments; don't use it for routine communications |

## Worked Example

**Scenario**: SaaS product, 14-day trial ending in 3 days.

Neutral candidate: "Upgrade now to keep access."

Truthful loss-frame candidate (not guaranteed superior):
- First, establish the endowment: "You've set up 3 integrations and analyzed 127 contacts in your trial."
- Then invoke the loss: "In 3 days, those integrations will pause and your data will become read-only."
- Then provide the action: "Upgrade in 2 minutes to keep everything running."

**Ethical check**: The loss is real — integrations do pause at trial end. The endowment data is the user's actual usage. The action is specific and low-friction. Loss framing is proportionate to a genuine service interruption.

**Contrast with manipulation**: "You're about to lose your competitive edge forever!" — vague, not a real specific loss, manufactured stakes, fails harm test.

## Sources

- Tversky, A. & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. _Journal of Risk and Uncertainty_, 5(4), 297–323. — canonical loss aversion coefficient (λ ≈ 2.25); a historical task-specific estimate, not an upper bound or message-response multiplier. [Brown et al. (2024)](https://www.aeaweb.org/articles?id=10.1257/jel.20221698) reports a cross-study mean of 1.955 across 607 estimates; this does not establish local copy efficacy.
- Kahneman, D., Knetsch, J. L. & Thaler, R. H. (1990). Experimental tests of the endowment effect and the Coase theorem. _Journal of Political Economy_, 98(6), 1325–1348. — endowment effect.
- Kahneman, D. (2011). _Thinking, Fast and Slow_, ch. 26. — loss aversion in everyday choices.
