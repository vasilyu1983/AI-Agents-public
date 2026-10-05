# Conversational Feedback Signals

Explicit feedback (thumbs, stars, "did we solve your problem?") is sparse and
biased. Conversational products leak a far richer signal: users correct,
abandon, rephrase, edit, regenerate, and delete — all without being asked. This
file is a taxonomy of those signals, what each licenses you to conclude, and how
to collect them without corrupting them.

Scope: **conversational** signals only. Search-relevance feedback (clicks, dwell
time) is a different instrument owned by the `software-search` skill's [user-feedback-learning](../../software-search/references/user-feedback-learning.md) reference; do not model it with the signals below.
[online-production-eval.md](online-production-eval.md) owns the measurement
apparatus (A/B, guardrails, drift, replay); this file owns *what the user is
telling you*, and everything harvested here flows into that replay set.

Primary source: Chip Huyen, *AI Engineering: Building Applications with
Foundation Models* (O'Reilly, 2024), Ch. 10.

## Table of Contents

- [Implicit natural-language signals](#implicit-natural-language-signals)
- [Action-derived signals](#action-derived-signals)
- [User edits as preference pairs](#user-edits-as-preference-pairs)
- [Complaint taxonomy](#complaint-taxonomy)
- [When to collect](#when-to-collect)
- [Feedback biases](#feedback-biases)
- [Degenerate feedback loops](#degenerate-feedback-loops)
- [Checklist](#checklist)

## Implicit natural-language signals

Signals inferred from message content. Each is a hypothesis generator, not a
verdict — instrument it, then validate against labeled cases before gating.

| Signal | Detection | What it licenses |
|--------|-----------|------------------|
| **Early termination** | User stops generation, closes the session, or abandons a pending choice mid-turn | Conversation is going badly; strongest when paired with a rephrase |
| **Error-correction opener** | Follow-up begins "No, …", "I meant …", "Actually …" | Prior response was off the mark; cheap regex/classifier, high precision |
| **Rephrase after abandon** | Semantically similar re-ask following a terminated or ignored response | Model misread intent, not just style; heuristics or a small classifier |
| **Action-correcting feedback** | User names a specific thing the system should have done ("check their GitHub page too") | Missing step or tool call — most common in agentic flows |
| **Explicit-confirmation request** | "Are you sure?", "Check again", "Show me the sources" | Not necessarily a wrong answer: signals missing detail or general distrust |
| **Refusal rate** | Responses containing "I don't know", "As a language model, I can't …" | Dissatisfaction proxy; track as a rate, not per-turn |
| **Sentiment trajectory** | Sentiment scored across turns, not per message | A conversation starting angry and ending calm resolved; the reverse did not |

Read trajectory, not snapshots: one negative turn is noise, a monotone descent
is signal. Refusal rate is two-sided — it is also an over-refusal guardrail in
[safety-redteam-eval.md](safety-redteam-eval.md), so a drop is not automatically
good.

## Action-derived signals

Signals from what users do to a conversation rather than what they say in it.

- **Regeneration** — usually dissatisfaction, but ambiguous: users also
  regenerate to compare options or check consistency. Huyen notes the signal is
  stronger under usage-based billing than under subscriptions, where regenerating
  is free. A "better/worse/same" prompt after regeneration yields direct
  preference data.
- **Delete** — strong negative on the conversation, with one confound: users
  also delete embarrassing-but-good conversations to remove the trace.
- **Rename** — the conversation was good but the auto-generated title was bad.
  A signal about the titling model, not the main model.
- **Share / bookmark** — genuinely ambiguous: some users share great answers,
  others share glaring failures. Corroborate with a second signal (a rephrase
  after a share suggests the shared conversation disappointed).
- **Turn count with dialogue diversity** — turn count alone has no fixed sign
  (long is good for a companion, bad for support deflection). Paired with
  dialogue diversity (distinct token or topic count) it detects **loops**: long
  plus low-diversity means stuck, not engaged. Neither half is interpretable
  alone.

Governing rule: the same action means different things in different products and
to different users. Study your users before signing the signal.

## User edits as preference pairs

When users edit a model response directly — corrected code, rewritten copy — the
edit is both the strongest available negative on the original and a ready-made
preference example:

- **Winner** = the user-edited response
- **Loser** = the original generated response

Each edit drops into a preference-tuning dataset (DPO-style pairs, reward-model
training) at no annotation cost. Cautions: edits skew toward users willing to do
the work, so the slice is self-selected; de-identify before storing, since edits
carry user content; and keep edits out of the eval set if they are in the
training set — split hygiene as in
[fine-tuning-eval-loop.md](fine-tuning-eval-loop.md).

Workflow-integrated products harvest this far better than standalone assistants,
which never learn whether their output was used at all.

## Complaint taxonomy

Many users complain without attempting a correction. Huyen reports eight
complaint groups from automatic clustering of the FITS (Feedback for Interactive
Talk & Search) dataset — Xu et al. (2022), clustering by Yuan et al. (2023):

1. Clarify their demand again
2. Complain that the bot does not answer the question, gives irrelevant
   information, or tells the user to find the answer on their own
3. Point out specific search results that can answer the question
4. Suggest that the bot should use the search results
5. State that the answer is factually incorrect or not grounded in the search
   results
6. Point out that the answer is not specific / accurate / complete / detailed
7. Point out that the bot is not confident and always opens with "I am not
   sure" or "I don't know"
8. Complain about repetition or rudeness in bot responses

Use the *groups* as a starting label set for your own complaints — they
generalize better than the counts do. The per-group percentages in that table
are properties of the FITS dataset as clustered by Yuan et al. (2023), not a
general distribution: cite them only with that attribution and re-derive your own
before acting. The label set is what turns free-text complaints into a
per-failure-mode metric you can trend.

## When to collect

- **At signup (calibration)** — a voice sample, a skill-level question, a stated
  preference. Necessary for some systems, optional for most; optional
  calibration is friction on first use, so fall back to a neutral default and
  calibrate over time.
- **When something bad happens** — the highest-value moment. On a hallucination,
  a wrongly blocked request, or a slow response, let the user report it *and
  still finish the task*: downvote, regenerate, switch model, edit the wrong
  output directly. Collaboration on the failure yields better outcomes and better
  feedback than a rating widget.
- **At low model confidence** — surface uncertainty as a choice. Two candidate
  outputs plus "which do you prefer?" converts a low-confidence moment into a
  comparative preference signal. Keep the ask answerable: never force a choice
  between options the user cannot evaluate (a factual question has a right
  answer, not a preference), and offer a "not sure" escape.
- **Not on success.** Apple's Human Interface Guidelines advise against
  soliciting both positive and negative feedback: the product should produce good
  results by default, and asking for praise implies they are the exception. The
  counter-argument Huyen reports from practitioners: positive feedback identifies
  the small set of high-impact features users love. If you collect it, sample a
  small fraction of users — accepting that a smaller sample carries more bias
  risk.

Cross-cutting: feedback must be non-intrusive, easy to ignore, and free of extra
work. Ambiguous widgets manufacture noise — Huyen's workshop survey whose emoji
scale ran in reverse order, attaching positive comments to one-star ratings, is
the canonical failure. Feedback is also user data: state how it will be used and
get consent before attaching surrounding dialogue turns as context.

## Feedback biases

- **Leniency bias** — users rate more positively than warranted, to avoid
  conflict or the follow-up questions a negative rating triggers. Ratings
  compress toward the top of the scale and stop discriminating. Huyen's
  illustration: Uber in 2015, average driver rating 4.8, with scores below 4.6
  putting drivers at risk of deactivation — an example of scale compression, not
  a benchmark. Detect it by inspecting the ratings *distribution*, not the mean.
  **Fix: degranularize** — replace 1–5 stars with verbal anchors ("Nothing to
  complain about but nothing stellar either") that strip the negative
  connotation from the low end; Huyen flags the specific wordings as
  illustrative and unvalidated. Corollary: never make users do extra work for
  feedback — required justification on negatives itself causes leniency bias.
- **Randomness** — unmotivated users click arbitrarily. Common when a
  side-by-side shows two long responses no one will read.
- **Position bias** — the slot an option occupies changes how often it is
  chosen; a click on the first suggestion is not evidence it was better.
  Mitigate by randomizing positions or modeling true success rate conditioned on
  position. Same failure mode as judge position bias
  ([llm-judge-bias.md](llm-judge-bias.md)), in human raters.
- **Preference bias** — raters favor longer responses even when less accurate,
  since length is easier to notice than inaccuracy; recency bias favors the
  answer seen last.

Biased feedback read literally produces confidently wrong product decisions —
the same failure this skill guards against in judges.

## Degenerate feedback loops

Feedback is incomplete by construction: you only get it on what you showed. When
that feedback trains the model, the model's predictions shape the feedback that
shapes the next model, amplifying whatever bias started the loop (exposure bias,
popularity bias, filter bubbles). Two consequences to gate against:

- **Product drift** — a small early cohort's preference compounds until the
  product serves only that cohort. The same mechanism amplifies racism, sexism,
  and preference for explicit content, not only harmless niches.
- **Sycophancy** — training on human feedback teaches the model to tell users
  what they want to hear rather than what is accurate (Stray 2023; Sharma et
  al. 2023). Keep an accuracy-anchored held-out set that user preference cannot
  move.

## Checklist

- [ ] Implicit signals instrumented: early termination, correction openers, rephrase, confirmation requests, refusal rate, sentiment trajectory
- [ ] Turn count is never read without dialogue diversity alongside it
- [ ] Ambiguous signals (share, regenerate, delete) validated against your own users before being signed
- [ ] User edits captured as (edited = winner, original = loser) preference pairs, de-identified, held out of the eval set
- [ ] Free-text complaints clustered into a stable label set and trended per failure mode
- [ ] FITS percentages cited as that dataset's reported figures, never as a general distribution
- [ ] Feedback solicited on failure and low confidence, not on success
- [ ] Comparative asks are answerable, with a "not sure" option
- [ ] Rating scales inspected as a distribution for leniency-bias compression
- [ ] Verbal anchors preferred over 1–5 stars where granularity matters
- [ ] Option positions randomized or position-corrected
- [ ] Consent obtained before storing surrounding dialogue turns as feedback context
- [ ] An accuracy-anchored held-out set exists that user preference cannot move (sycophancy gate)
