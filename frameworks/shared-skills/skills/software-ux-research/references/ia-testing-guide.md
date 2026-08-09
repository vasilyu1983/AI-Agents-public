# IA Testing Guide

Practical operator guide for UX researchers running information-architecture and content-comprehension studies on consumer products. Covers card sorting, tree testing, first-click testing, and 5-second testing.

---

## Table of Contents

- [1. Card Sorting (Open, Closed, Hybrid)](#1-card-sorting-open-closed-hybrid)
- [2. Tree Testing (Reverse Card Sort)](#2-tree-testing-reverse-card-sort)
- [3. First-Click Testing](#3-first-click-testing)
- [4. Five-Second Testing](#4-five-second-testing)
- [Method-Selection Decision Table](#method-selection-decision-table)
- [Common Cross-Method Anti-Pattern](#common-cross-method-anti-pattern)
- [Tool Comparison](#tool-comparison)

---

## 1. Card Sorting (Open, Closed, Hybrid)

### When to Use

| Situation | Recommended variant |
|---|---|
| Building IA from scratch — no existing structure | Open |
| Validating or refining a proposed nav structure | Closed or Hybrid |
| Uncovering how users mentally model a domain | Open |
| Confirming whether your category labels make sense to users | Closed |
| Restructuring an existing nav while keeping some anchors | Hybrid |

Do not use card sorting to validate an IA that already exists in production — use tree testing for that.

### Open vs Closed vs Hybrid — Decision Rule

- **Open**: You do not know the categories yet. Participants create and name groups. Output drives label creation.
- **Closed**: Categories are fixed. You want to know whether users distribute cards into them correctly. Use when labels are already drafted and you need quantitative confidence.
- **Hybrid**: You provide categories but allow participants to create new ones. Use when you have a partial structure and want to surface gaps without starting from scratch.

Default to open when in doubt. Closed results look cleaner but will not surface labeling failures — you will only know whether users can work within your chosen labels, not whether those labels are right.

### Sample Size

| Variant | Minimum | Target | Rationale |
|---|---|---|---|
| Open | 15 | 20–30 | Cluster patterns stabilise around 20; going past 30 adds noise, not signal |
| Closed | 30 | 50–100 | Need statistical spread across category cells; chi-square logic applies |
| Hybrid | 20 | 30–50 | Treat as open for cluster analysis, closed for fixed-category cells |

### Tools

- **Optimal Workshop OptimalSort** — gold standard for dendrograms and similarity matrices; export to spreadsheet for custom analysis
- **Maze** — faster setup, built-in reporting, but limited dendrogram depth; good for teams already on Maze
- **UserZoom IA module** — enterprise; pairs well with existing panel contracts
- **Miro card sort kit** — best for moderated sessions where think-aloud is the primary data; not suitable for unmoderated at scale

### Protocol

1. **Card count**: Keep between 30 and 60. Below 30, participants finish too quickly to form genuine groupings. Above 60, fatigue introduces arbitrary sorting.
2. **Terminology**: Write cards in plain language users already use. Avoid product team jargon, feature names, or internal taxonomy. If a card requires explanation, rewrite it.
3. **"Other" bucket**: Do not provide a pre-built "Other" or "Miscellaneous" group. When offered, participants use it as a dumping ground rather than forcing a placement decision. If participants ask, tell them to put cards wherever feels closest.
4. **Instructions**: Tell participants to group cards in any way that makes sense to them — not the "right" way, their way. Emphasise there are no wrong answers.
5. **Think-aloud variant (moderated only)**: Ask participants to narrate as they move cards. Capture verbatim phrasing — the language participants use for categories is often more valuable than the groupings themselves. Do not prompt or suggest categories.
6. **Session length**: Open sort takes 20–40 minutes for 40 cards. Allow buffer; rushing produces coarse groups.

### Output and How to Read It

| Output | What it shows | How to read it |
|---|---|---|
| **Dendrogram** | Hierarchical clustering of which cards co-occur in the same group across participants | Higher co-occurrence = stronger mental link. Cut the tree at 40–60% agreement to find natural clusters. Don't force a pre-set number of clusters. |
| **Similarity matrix** | Pairwise percentage: how often two cards were grouped together | Values above 50% indicate strong association. Cards that cluster together in the matrix but not in the dendrogram signal multi-category content — a future navigation problem. |
| **Agreement matrix** (closed only) | Percentage of participants who placed each card in each category | Low agreement on a card means the label is ambiguous or the card belongs in a category you haven't created. Cells above 70% are solid. Below 40% is a failure. |
| **Popular categories** (open) | The labels participants invented, ranked by frequency | Direct copy for navigation labels. Merge near-synonyms by reading the underlying card distributions, not just the label names. |

### Anti-Patterns

- **Asking participants to invent labels they would never use in real life.** If your cards are abstract concepts, participants will create abstract categories that do not translate to a real nav. Card content must reflect real user tasks and real content objects.
- **Mixing card sort with task elicitation.** Do not ask participants to also complete tasks or answer questions about their goals mid-sort. It contaminates both data sets.
- **Running before content is stable.** If the content list will change significantly before launch, early sort results are wasted. Run card sorting when the content inventory is at least 80% settled.
- **Treating dendrogram clusters as the final IA.** Clusters are a signal, not a specification. Validate any derived structure with tree testing before building.

---

## 2. Tree Testing (Reverse Card Sort)

### When to Use

Tree testing validates a proposed or existing navigation structure before you build it into a prototype or usability test. Run it:

- After deriving an IA from card sorting results
- When restructuring an existing nav and you want a before/after comparison
- Before a full usability test to de-risk the navigation layer — usability tests are too expensive to waste on findability problems
- When stakeholders argue about category names: tree testing produces numbers, which ends the argument faster

Do not use tree testing to evaluate visual design, page layout, or interaction patterns. It tests labels and structure only.

### Tools

- **Optimal Workshop Treejack** — purpose-built; best reporting and participant management
- **Maze** — adequate for small trees (<50 nodes); reporting is less granular than Treejack
- **UserZoom** — enterprise; supports large panels and longitudinal comparison

### Sample Size

| Goal | Sample |
|---|---|
| Directional read — "is this broadly right?" | 50–100 |
| Confidence intervals for success rates | 200+ per condition |
| A/B comparison of two IA versions | 100 per variant minimum |

For consumer products, 75–100 participants gives you a reliable directional signal within a week if you use a panel.

### Protocol

1. **Task count**: Write 10–15 tasks. Fewer than 10 gives insufficient coverage; above 15 increases abandonment and fatigue errors.
2. **Write tasks as user goals, not feature names.** Wrong: "Find the Settings page." Right: "You want to turn off email notifications — where would you go?" Tasks written around feature names prime users toward matching labels rather than testing genuine findability.
3. **Task length**: Each task should take 2–3 minutes on average. If pilot participants average more than 3 minutes per task, simplify the wording.
4. **Randomise task order**: Present tasks in random order to prevent ordering effects. Most tools do this automatically — verify it is enabled.
5. **Do not randomise tree node order**: Alphabetic or fixed order is fine. Randomising tree branches introduces confounds.
6. **Pilot first**: Run 5 unmoderated participants before the full study. Look for tasks where everyone goes to the same wrong place — this usually means the task wording is leading, not that the tree is broken.

### Output Metrics and Interpretation Thresholds

| Metric | What it measures | Threshold |
|---|---|---|
| **Success rate** | % who found the correct destination | ≥80% on critical tasks = acceptable; 60–79% = needs attention; <60% = redesign required |
| **Directness** | % who reached the correct destination without backtracking | Low directness + high success = users are exploring, not navigating — label clarity issue |
| **Time on task** | Median seconds to completion | No universal threshold; use as a comparative metric between IA versions |
| **First-click correctness** | % who clicked the right top-level node first | Strong predictor of success; <50% on a critical top-level node is a structural problem, not a label problem |

**Reading directness vs success together:**
- High success + high directness: IA is working
- High success + low directness: Labels are ambiguous; users explore but eventually find it — acceptable for low-frequency tasks, unacceptable for primary flows
- Low success + high directness: Users confidently go to the wrong place — a category naming failure
- Low success + low directness: Users are lost — structural problem, not a labeling fix

### When to Stop Iterating

Stop when all critical-path tasks hit ≥80% success rate. "Critical-path" means tasks that correspond to the top 3–5 user goals identified in discovery. Do not chase 80% on every single task — low-frequency tasks often sit at 60–70% and that is acceptable if the task is rare.

### Anti-Patterns

- **Writing leading task labels.** If your task says "find Subscription Plans" and one of your tree nodes says "Subscription Plans," you are testing reading comprehension, not IA.
- **Testing the same labels you used in the tree.** If your tree has a node called "Insights" and your task says "find your insights dashboard," you have primed the answer. Paraphrase the destination in the task wording.
- **Ignoring "I'd give up" or "I don't know" data.** Most tools allow participants to indicate they cannot find the answer. Treat this as a failure, not a skip. High give-up rates on a task signal either a structural problem or a missing category.
- **Testing a tree that has never been validated against real content.** If the tree nodes do not map to actual pages or sections that will be built, results cannot be actioned.

---

## 3. First-Click Testing

### When to Use

First-click testing answers: given this screen, where does the user click first to accomplish a goal? Use it for:

- Evaluating a homepage or landing page before usability testing
- Testing a new feature's entry point — is the CTA in the right place with the right label?
- Comparing two layout or labeling alternatives quickly
- Any screen where the first decision is the critical decision (onboarding, checkout initiation, nav entry)

First-click testing is not a substitute for usability testing. It captures one decision; it cannot tell you what happens after that click.

### Sample Size

30–50 participants for stable heatmap patterns. Below 30, a few outlier clicks distort the heatmap. Above 50, diminishing returns unless you are running a close A/B comparison.

### Tools

- **Optimal Workshop Chalkmark** — purpose-built; best click-accuracy reporting and heatmap quality
- **Lyssna (formerly UsabilityHub)** — broad consumer panel, fast turnaround, affordable; good for quick directional reads
- **Maze** — works well if team is already on Maze; heatmap fidelity is comparable to Chalkmark
- **UserTesting** — use for moderated first-click with think-aloud; overkill for unmoderated click capture

### Protocol

1. **One task per screen.** Do not ask participants to complete multiple tasks on the same image. The second task is contaminated by the first click.
2. **Write the task as a goal.** "You want to upgrade your plan — what would you click first?" not "Click the upgrade button."
3. **No scrolling expected.** Show only what appears above the fold (or the full viewport for mobile). If the correct answer requires scrolling, you are not testing first-click — you are testing whether users know to scroll.
4. **30-second time limit.** Most tools enforce this. If a participant deliberates for more than 30 seconds, their click is not reflecting a natural first decision. The limit forces a representative response.
5. **Static image, not interactive prototype.** First-click testing works on screenshots or design exports. Using a live prototype introduces interaction noise.

### Metric: First-Click Success

The primary metric is **first-click success rate** — the percentage of participants who clicked the correct target on their first click. This is not arbitrary: Bob Bailey's research (and subsequent replications) shows that users who click correctly on the first click complete the full task successfully ~87% of the time. Users who click incorrectly on the first click succeed only ~46% of the time. First-click is a leading indicator of overall task success.

A first-click success rate below 60% on a primary CTA is a redesign trigger, not an iteration signal.

### Output

| Output | What it tells you |
|---|---|
| **Heatmap** | Where attention concentrates; reveals competing click targets and visual hierarchy failures |
| **Click sequence / scatter** | Whether clicks cluster or spread; tight clustering = confidence, spread = confusion |
| **Success rate by zone** | Aggregate: what % hit the intended target vs other areas |

### Anti-Patterns

- **Multi-step tasks dressed as first-click.** "Where would you go to find your invoices and then download last month's?" is a flow question, not a first-click question. Strip to a single atomic decision.
- **Expecting it to validate beyond the first decision.** First-click tells you whether the entry point works. It does not tell you whether the flow after that click succeeds. Follow up with a usability test or tree test for downstream validation.
- **Testing screens with competing primary actions.** If there are three equally prominent CTAs, first-click data will spread across all three and tell you nothing actionable. Fix the visual hierarchy before running the test.

---

## 4. Five-Second Testing

### When to Use

Five-second testing evaluates first impressions: what does a user understand about a page within the first five seconds of exposure? Use it for:

- Marketing landing pages before launch
- Onboarding hero screens where value proposition clarity is critical
- Redesigned homepages where brand perception has shifted
- Any screen where comprehension in the first glance determines whether the user continues

Do not use five-second testing to evaluate navigation, flows, or detailed content. It captures impression, not comprehension of complex systems.

### Sample Size

50–100 participants for directional results. The variance in impression data is high; below 50, individual responses dominate the aggregate. Above 100, you gain confidence intervals but the marginal return is low for most consumer product decisions.

### Tools

- **Lyssna (formerly UsabilityHub)** — best-in-class for five-second tests; large consumer panel, clean question flow, fast turnaround
- **Maze** — adequate; works well if team is already on Maze for other methods
- **UserTesting** — use only if you want moderated think-aloud during or after the five-second exposure; adds cost and complexity

### Protocol

1. **Show the screen for exactly 5 seconds.** Most tools enforce this. Do not extend it — longer exposure changes the task from impression capture to comprehension evaluation.
2. **Ask these four questions immediately after exposure:**
   - "What does this product or page do?" (recall — value proposition)
   - "Who is it for?" (audience comprehension)
   - "What would you do next?" (call-to-action clarity)
   - "What one word describes how it made you feel?" (sentiment)
3. **All questions are open-ended, text entry.** Avoid multiple choice — it primes responses. You want unprompted recall.
4. **One screen per participant session.** Testing multiple screens introduces contrast effects. If you need to compare two variants, split the sample and show each variant to a separate group.
5. **Do not show populated dashboards or data-dense screens.** Participants cannot meaningfully process them in 5 seconds. Five-second testing is for hero images, landing pages, and onboarding screens — not feature-dense product UIs.

### Output

| Output | What it tells you |
|---|---|
| **Recall accuracy** | % who correctly identified what the product does; below 50% = value proposition failure |
| **Audience comprehension** | Whether users self-identify as the target audience; mismatches signal positioning or imagery problems |
| **CTA clarity** | What users say they would do next; divergence from intended action = CTA placement or label failure |
| **Sentiment word cloud** | Aggregate of single-word responses; watch for unexpected negatives (confusing, busy, cheap) even at low frequencies |

Read recall and sentiment together. High recall with negative sentiment (e.g., "I know what it does but it feels overwhelming") is a design problem, not a messaging problem. Low recall with positive sentiment (e.g., "It felt clean but I'm not sure what it's for") is a messaging problem.

### Anti-Patterns

- **Showing populated dashboards.** Participants will fixate on data artifacts rather than the value proposition. Strip to hero content.
- **Expecting it to validate a flow.** Five-second testing gives you one data point: first impression. It cannot tell you whether users will complete registration, understand the pricing page, or navigate correctly. Do not use it as a proxy for usability.
- **Using multiple choice questions.** "Did this page feel: (a) trustworthy (b) confusing (c) exciting?" tells you which word the participant liked most, not what they actually felt.

---

## Method-Selection Decision Table

| Situation | Method |
|---|---|
| You have no IA and need to derive one from user mental models | Card sorting (open) |
| You have a proposed IA and want to validate it before building | Tree testing |
| You have a screen and want to know if users can find the entry point | First-click testing |
| You have a landing page and want to know if users understand it at a glance | 5-second testing |
| You want to compare two nav structures quantitatively | Tree testing (A/B, 100+ per variant) |
| You want to refine category labels your team has already drafted | Card sorting (closed) |

---

## Common Cross-Method Anti-Pattern

**Running IA testing without a researchable hypothesis.**

"We want to test our nav" is not a hypothesis. Before running any of these methods, state what you believe is true and what would change your decision:

- "We believe users will find pricing under 'Plans'. If success rate is below 70%, we will rename or relocate it."
- "We believe the homepage communicates our value prop clearly. If recall is below 60%, we will revise the hero copy."

Without a hypothesis and a pre-set decision threshold, results get presented in a review, stakeholders argue about interpretation, and nothing changes. The research was theatre.

**Running IA testing after launch when changes are politically expensive.**

Card sorting and tree testing are pre-build methods. Running them after a nav is live, indexed by search engines, and defended by a product team adds political friction to every finding. If you are conducting post-launch IA research, frame it explicitly as input to the next version and get stakeholder alignment on that framing before fielding.

---

## Tool Comparison

| Tool | Strengths | Weaknesses | Best for |
|---|---|---|---|
| **Optimal Workshop** (OptimalSort, Treejack, Chalkmark) | Gold standard outputs; full suite covers all four methods; dendrograms and matrices are the best available | Expensive; panel quality varies by region; UI has a learning curve | Teams with dedicated UX research budget running formal IA programmes |
| **Maze** | Fast setup; integrates with Figma; good for design-team-owned research | Participant pool skews toward designers and tech-literate users; can introduce sample bias; less granular IA metrics | Product and design teams running lightweight IA checks within a sprint |
| **Lyssna / UsabilityHub** | Affordable; large, broad consumer panel; fastest turnaround for first-click and 5-second tests | Limited tree testing capability; less sophisticated analysis for card sorting | First-click and 5-second testing with consumer audiences; tight budgets |
| **UserZoom** | Enterprise panel management; longitudinal studies; integrates with existing research ops | High cost; overkill for most consumer product teams; complex setup | Large organisations with formal research ops, participant management needs, and compliance requirements |
