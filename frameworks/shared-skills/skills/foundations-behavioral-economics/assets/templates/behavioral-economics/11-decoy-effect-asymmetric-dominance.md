# Primitive: Decoy Effect / Asymmetric Dominance

## Definition

The decoy effect (asymmetric dominance effect) is the phenomenon where the introduction of a third, dominated option (the decoy) shifts preference between two existing options, increasing preference for the option that dominates the decoy (Huber, Payne & Puto, 1982; Ariely, 2008).

**Asymmetric dominance**: Option C (decoy) is dominated by Option B on all relevant dimensions, and is dominated by Option B on at least one dimension relative to Option A — but Option A is not dominated by Option C. This asymmetry makes Option B more attractive than it was in the two-option set.

Classic example (Ariely, 2008 — Economist subscription):
- Option A: Web subscription — $59/year.
- Option B: Print + Web — $125/year.
- Option C (decoy): Print only — $125/year.

Option C is clearly inferior to Option B (same price, less value). But its presence makes Option B look like an obvious deal. Without Option C, most people chose Option A (cheap). With Option C, most chose Option B (premium).

Why it works: the decoy provides a **contrast reference** that shifts the relative evaluation of the other options. System 1 pattern-matches "this looks like a better deal" before System 2 calculates whether it actually is.

Key properties:
- The decoy must be asymmetrically dominated — dominated by the target option but not dominated by the competitor.
- Effect is strongest when target and competitor are close substitutes and the decoy makes the comparison easy.
- Three-option sets are the typical application; the effect diminishes with more options.

## When to Use

- **Pricing tier design**: three-tier pricing where the middle tier should be the modal choice.
- **Subscription plan comparison tables**: when two plans are close and you want to drive preference toward one.
- **Feature packaging**: when a lower-tier plan needs a reference point to make the next tier look obviously better.
- **Product selection pages**: when two products are equally attractive to the user and you want to direct preference.

## Misuse Boundary

**Ethical use**: The decoy is ethical when the target option (the one the decoy is designed to boost) is genuinely the best option for the modal user in that context. The decoy makes an already-superior option more obviously superior — it clarifies, it doesn't deceive.

**Manipulation**: Using the decoy to push users to an overpriced or inappropriate tier they don't need — where the target option is not genuinely better for the user, only better for the operator's margin. Creating a decoy that is not a real offering, or a decoy designed to obscure the fact that the cheapest option is perfectly adequate for the user's actual use case.

**Test**: Would you be comfortable explaining to a user that you included the middle tier specifically to make the top tier look better? If the top tier genuinely is better for them, the answer should be yes. If it is not, this is a dark pattern.

**Required conditions**:
1. The target option (the one boosted by the decoy) is the genuinely better option for the modal user at this stage.
2. The decoy is a real option — not a phantom that disappears when selected.
3. The cheapest option is not suppressed or degraded to force an upgrade that doesn't serve the user.

## Inputs

- Two primary options the user is choosing between.
- Knowledge of which option is better for the modal user (or which the operator legitimately wants to promote).
- Design of a decoy that is dominated by the target option on the dimensions the user cares about.

## Outputs

- A three-option set where the decoy shifts preference toward the target.
- A pricing or feature table that makes the target option's dominance visually clear.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Decoy has no effect | User is a sophisticated buyer who evaluates options independently | Pair decoy with explicit feature comparison table that makes the dominance explicit |
| Target option is not dominant on user's primary dimension | Decoy designed for operator's preferred metric, not user's | Identify what the user most cares about; design decoy to make target option dominant on that dimension |
| User selects the decoy | Decoy is not sufficiently dominated; user finds it appropriate for their use case | Ensure the decoy has at least one dimension where it is clearly worse than the target |
| Perceived manipulation damages trust | User explicitly notices and resents the pricing structure | Acknowledge the structure (some companies make their pricing transparent); focus on making the target option genuinely the best deal |
| Cheapest option is made unusable as a manipulation | Starter tier stripped to force upgrades | The cheapest option must be a real, usable offering — not a trap |

## Worked Example

**Scenario**: Email marketing SaaS, targeting teams of 5–20.

Without decoy:
- Starter: $29/month (up to 5 users, 10,000 emails).
- Pro: $79/month (unlimited users, 100,000 emails, analytics).

User uncertainty: both seem plausible; many choose Starter to minimize cost.

With decoy:
- Starter: $29/month (up to 5 users, 10,000 emails).
- Pro: $79/month (unlimited users, 100,000 emails, analytics). ← Target
- Scale: $79/month (up to 10 users, 50,000 emails, no analytics). ← Decoy

Scale and Pro cost the same. But Scale has user limits, lower email cap, and no analytics — dominated by Pro. The comparison makes Pro obviously superior to Scale; and Pro now looks like a much better deal than Starter when evaluated against Scale.

**Ethical check**: Pro genuinely is the better option for teams of 5–20 in this scenario. Scale is a real offering (not a phantom). Starter remains available and functional for solo users. The decoy makes an already-correct choice more obvious.

**Contrast with manipulation**: If the team's true need is met by Starter but the decoy is designed to push them to Pro, the technique is being used to exploit, not clarify.

## Sources

- Huber, J., Payne, J. W. & Puto, C. (1982). Adding asymmetrically dominated alternatives: Violations of regularity and the similarity hypothesis. _Journal of Consumer Research_, 9(1), 90–98. — foundational paper on asymmetric dominance.
- Ariely, D. (2008). _Predictably Irrational_, ch. 1. — Economist subscription example and practical applications.
- Tversky, A. & Simonson, I. (1993). Context-dependent preferences. _Management Science_, 39(10), 1179–1189. — theoretical framework.
- Simonson, I. (1989). Choice based on reasons: The case of attraction and compromise effects. _Journal of Consumer Research_, 16(2), 158–174. — compromise effect (related to decoy).
