# Technical Writing Best Practices

Rules for technical documentation prose. General writing mechanics are assumed; this file keeps the decisions that differ in technical docs and the checks worth running before merge. House style for Markdown syntax is in [markdown-style-guide.md](markdown-style-guide.md).

## Table of Contents

- [Doc Types](#doc-types)
- [Structure](#structure)
- [Style Rules](#style-rules)
- [Code Examples](#code-examples)
- [Visuals](#visuals)
- [Review Before Merge](#review-before-merge)
- [AI-Writing Tells: Recognition and Fixes](#ai-writing-tells-recognition-and-fixes)

---

## Doc Types

Use the [Diátaxis](https://diataxis.fr/) split. Each page is one type. Mixed pages fail both readers: the learner drowns in reference detail, the expert cannot find the fact.

| Type | Reader's need | Shape | Voice |
|------|---------------|-------|-------|
| Tutorial | Learn by doing, first time | What you'll build → prerequisites → steps → verify → next steps | Guiding; every step works as written |
| How-to guide | Accomplish a specific task | Goal → prerequisites → numbered steps → verify | Imperative, no teaching detours |
| Reference | Look up a fact | Consistent entry format, complete parameters, one example per entry | Neutral, exhaustive, no narrative |
| Explanation | Understand why | Context → concepts → trade-offs → links to ADRs | Discursive; no step lists |

When a page mixes types, split it and link the parts, rather than adding headings inside one page.

## Structure

- **Lead with the answer.** First paragraph states what the page covers and the most important fact or action. Readers and retrieval systems both weight the opening.
- **Self-contained pages.** Each page must make sense when landed on from search or an agent citation; restate the minimum context and link the rest.
- **Headings are labels for scanning**, specific enough to be linked ("Rotate the signing key", not "Overview 2").
- **Numbered steps for sequences, bullets for sets, tables for comparisons** across more than two attributes.
- **Prerequisites before step 1**, with versions and access needed.

## Style Rules

### Use active voice

Name the actor: "The scheduler retries the job", not "The job is retried". Passive voice hides who does the work, which is often the fact the reader needs.

### Use imperative mood for instructions

"Run `make migrate`", not "You should run" or "The user can run".

### Overusing "should"

"Should" is ambiguous between requirement and suggestion. Use "must" for requirements, the imperative for instructions, and "we recommend ... because ..." for advice.

### Avoid filler words

Cut "in order to", "it is important to note that", "simply", "just", "basically", and stacked hedges ("could potentially"). "Simply" and "just" also tell a struggling reader they are failing at something easy.

### Be specific

Numbers, names, and limits over adjectives: "times out after 30 s" beats "may take a while". Define each acronym on first use per page, and use one term per concept across the doc set.

### Unambiguous references

Replace "it", "this", and "that" with the noun when more than one candidate precedes it.

## Code Examples

- Complete and runnable, or explicitly labeled illustrative. Show imports and setup the reader needs.
- Language tag on every fenced block.
- Show expected output and at least one error case for operations that commonly fail.
- Keep examples in tested files and include them when the toolchain allows (see [documentation-testing.md](documentation-testing.md#technical-accuracy)).

## Visuals

- Use a diagram when the reader must hold more than a few interacting components in mind; keep diagram source in the repo as text (see the `docs-diagram-design` skill).
- Screenshots only where the UI itself is the subject; they go stale on every UI change, so each needs an owner.
- Every image needs alt text or an adjacent prose explanation.

## Review Before Merge

- Follow the steps yourself on a clean environment, or have someone unfamiliar do it.
- Check the page against its Diátaxis type: no tutorial detours in reference, no reference dumps in tutorials.
- Scan for the AI-writing tells below.
- Verify every path, command, count, and version the page states.

---

## AI-Writing Tells: Recognition and Fixes

**Scope: this section governs authored documentation prose** (READMEs, guides, ADRs, runbooks, reference docs) — the same axis as every other section in this file. **It does not govern agent conversational output** (what an agent says in chat while doing a task); that is a different axis and this library currently has no dedicated guidance for it (see [Residual Gap](#residual-gap) below). Where a tell shows up differently in the two contexts, the table notes it.

These patterns exist because LLM text generation has predictable statistical habits: it reaches for the same intensifiers, the same three-item lists, the same hedges, more often than a human writer would. None of them prove a document was AI-written on their own — flag **clusters** of tells, not one isolated hit, and never gut a sentence that happens to use one flagged word in a legitimate way. A single "however" or one em dash is not a defect.

| Tell | Why it reads as AI-generated | Fix |
|------|------------------------------|-----|
| **Inflated significance** — "stands as a testament to," "marks a pivotal moment," "underscores its importance," "represents a shift" | Puffs up an ordinary fact by claiming it symbolizes something larger, without evidence for the larger claim. | State the fact plainly. Cut the claim about broader significance unless a source supports it. |
| **AI-vocabulary words** — delve, crucial, intricate, tapestry, testament, underscore (verb), pivotal, landscape (abstract noun), foster, garner, showcase, leverage (verb) | These words spike sharply in frequency in post-2023 text and cluster together. | Replace with the plain word: "use" not "leverage," "detailed" not "intricate," "show" not "showcase." |
| **Copula avoidance** — "serves as," "stands as," "boasts," "features [a]," "offers [a]" in place of "is"/"are"/"has" | Elaborate constructions substituted for simple statements of fact. | Use "is," "are," or "has" directly: "the tool is X," not "the tool serves as X." |
| **Negative parallelisms / tailing negations** — "It's not just X, it's Y," or a clause tacked on as "no guessing," "no wasted effort" | An overused rhetorical shape that reads as templated rather than considered. | Write the plain positive statement, or turn the tailing fragment into a real clause: "so the user doesn't have to guess." |
| **Rule-of-three overuse** — forcing every list or claim into exactly three items ("faster, safer, and more reliable") | Real requirements rarely come in even groups of three; the pattern signals a filled-in template rather than an observed fact. | List however many items are actually true. Two is fine. Five is fine. |
| **Elegant variation** — cycling synonyms for the same referent across sentences ("the function," "this method," "the routine," "said logic") | Avoids repeating a word at the cost of clarity — a reader has to work out these all mean the same thing. | Repeat the exact term. In technical docs, consistent terminology (already required above, see [Be specific](#be-specific)) beats variety. |
| **False ranges** — "from X to Y" where X and Y are not points on a real scale ("from the smallest bug fix to the grandest architectural vision") | Manufactures a sense of comprehensive scope without the range being meaningful or measurable. | Name the actual set of things covered, without the borrowed structure of a scale. |
| **Em dash / en dash overuse** — leaning on `—` or `–` as a universal connector | One of the most statistically reliable single-token AI tells; overuse also just makes prose harder to parse (was that an aside, a list break, or a new clause?). | Replace with a period, comma, colon, or parentheses depending on the relationship. A single em dash for a genuine aside is fine; several per paragraph is the tell. |
| **Boldface overuse** — bolding phrases mechanically throughout a paragraph, not just true key terms | Turns emphasis into noise; if everything is bold, nothing is. | Bold only the term being defined or the one thing a scanning reader must not miss. |
| **Inline-header vertical lists** — `- **Term:** sentence restating the term` repeated down a list | A templated shape, not a description of an actual capability list. | Either drop the bold lead-in and let the sentence stand, or convert to prose if the items relate to each other. |
| **Emojis as bullet/heading decoration** | Decorative emojis on every bullet or heading read as autogenerated formatting rather than an intentional signal. | Remove unless the emoji itself carries meaning the reader needs (e.g., a status icon in a table). |
| **Knowledge-cutoff disclaimers and speculative gap-filling** — "as of [date]," "while specific details are limited," followed by invented plausible-sounding filler | Two related tells: stale training-cutoff caveats left in text, and confident-sounding guesses dressed up as fact when a source is missing. | State plainly that the information is not available, or cut the sentence. Never fill an unknown with a plausible-sounding guess. |
| **Hyphenated word pair overuse** — hyphenating compounds like "high-quality," "data-driven," "real-time" even in predicate position ("the report is high-quality") | Humans hyphenate attributive compounds ("a high-quality report") but usually drop the hyphen in predicate position ("the report is high quality"). AI applies the hyphen uniformly. | Keep the hyphen only when the compound sits before the noun it modifies. Drop it when the compound follows the noun. |
| **Persuasive authority tropes** — "the real question is," "at its core," "what really matters," "fundamentally" | Signals a manufactured pivot to a "deeper truth" that the following sentence usually doesn't deliver — it just restates an ordinary point with more ceremony. | Cut the framing phrase and state the point directly. |
| **Signposting and announcements** — "Let's dive in," "here's what you need to know," "let's break this down," in explanatory prose | Announces what the text is about to do instead of doing it; reads as a tutorial-script narrator rather than the documentation itself. | Delete the announcement and start with the content. |
| **Fragmented headers** — a heading immediately followed by a one-line paragraph that just restates the heading before real content starts | A rhetorical warm-up that adds a sentence without adding information. | Delete the throwaway line; start the section with the first substantive sentence. |
| **Diff-anchored writing** — documentation phrased as narrating a change ("this replaces the old approach of...") rather than describing the current state | Forces a reader to reconstruct history to understand what the code does today. Correct in changelogs and migration guides, wrong everywhere else. | Describe the thing as it is now. Save "replaces X" framing for changelog and migration-guide entries, where it's the point. |
| **Aphorism formulas** — "X is the language of Y," "X becomes a trap," "the architecture of Z" | Turns an ordinary claim into a reusable-sounding aphorism that feels profound but adds no precision. | Replace with the concrete claim the aphorism is gesturing at. |
| **Conversational rhetorical openers** — "Honestly?," "Here's the thing," "Look," used as a theatrical pause before an ordinary point | Manufactures fake candor before delivering a routine statement — the tell is the pause-and-reveal structure, not the word itself. | State the point without the staged lead-in. |
| **Curly quotation marks** in plain-text contexts (code comments, config, CLI examples) | Straight quotes are required where curly quotes break parsing; curly quotes appearing there usually means text was pasted from a chat UI without adjustment. | Use straight quotes (`"`) in anything that might be parsed. This is a mechanical check, not a style judgment — curly quotes in prose alone are not a tell (most editors auto-curl by default). |
| **Sycophantic/servile tone** — "Great question!," "You're absolutely right," "That's an excellent point" | People-pleasing filler that has no place in reference material and, in agent conversation, reads as flattery rather than a genuine assessment. | In docs: delete outright. In agent speech: give the direct assessment without the preamble. |
| **Collaborative-communication artifacts** — "I hope this helps!," "Let me know if you'd like me to expand," "Would you like examples?" | Text written as chatbot correspondence, pasted into content that has no reader to address this way. | Delete. Documentation has no back-and-forth to refer to. |

### Already covered elsewhere in this guide

Three tells from the source taxonomy overlap with sections earlier in this file. Rather than duplicate them, this section defers to the existing guidance:

- **Passive voice and subjectless fragments** ("No configuration file needed") — see [Use active voice](#use-active-voice).
- **Filler phrases** ("in order to," "it is important to note that") and **excessive hedging** ("could potentially possibly") — see [Avoid filler words](#avoid-filler-words).
- **Overusing "should"** as a substitute for imperative instructions — see [Overusing "should"](#overusing-should).

### Docs prose vs. agent speech

Most tells above read as defects in both axes — inflated significance, copula avoidance, false ranges, and the vocabulary list are just as wrong in a chat response as in a README. A few apply asymmetrically:

- **Signposting** ("Let's dive in") and **conversational rhetorical openers** ("Honestly?") are near-universal complaints about agent chat replies, but appear far less often in already-written docs, since nobody drafts a README by narrating their own process.
- **Collaborative-communication artifacts** ("I hope this helps!") and **sycophantic tone** ("Great question!") are almost exclusively an agent-speech problem — they leak into docs only when a chat transcript gets pasted into a file without cleanup.
- **Diff-anchored writing** and **fragmented headers** are near-exclusively a docs problem; they describe a written artifact's structure, not a conversational turn.

### Attribution

This taxonomy is adapted, in this file's own voice and condensed, from [blader/humanizer](https://github.com/blader/humanizer) at commit `523374dee72d67c7b2b5f858ea0094ffda49c3ac` (MIT license), extracted 2026-08-09. The source project itself derives its taxonomy from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide (WikiProject AI Cleanup).

Of the source's 33 patterns: **22** are reproduced above as distinct table rows; **3** are covered by cross-reference to this file's existing sections (passive voice, filler phrases, excessive hedging — see [Already covered elsewhere in this guide](#already-covered-elsewhere-in-this-guide)); **8** were cut:

- Too narrow to Wikipedia-style encyclopedic or travel-article prose, with little application to technical docs: undue emphasis on media coverage/notability, promotional heritage-article language ("nestled," "breathtaking"), vague sourcing attributions ("experts believe"), formulaic "Challenges and Future Prospects" sections, generic upbeat closing paragraphs.
- Too subjective to check by reading a single paragraph, requiring a broader read of the whole document's rhythm: manufactured-punchline / staccato-drama pacing, superficial "-ing"-ending analysis treated as a category distinct from inflated significance (folded into that row instead).
- **Title case in headings** was cut deliberately, not as noise: it is a genuine style choice, not a reliable AI tell. Sentence case vs. title case is a house-style decision (this file already uses sentence case in its own H2/H3 headings, which is worth noting as the convention here, but that's a style pick, not evidence of AI authorship either way).

### Residual gap

This section governs written documentation only. **Agent conversational output — how an agent talks while doing a task, in chat, in commit messages, in PR descriptions — remains otherwise ungoverned in this library.** Several of the tells above (signposting, sycophantic tone, collaborative-communication artifacts, conversational rhetorical openers) were originally flagged as an agent-speech problem, not a docs-prose problem, and this file does not close that gap; it only borrows the taxonomy for the axis it already owns. A dedicated agent-speech style contract, if one gets built, belongs in a different file (likely alongside `.claude/rules/coding-behavior.md` or an agent-persona reference), not here.

---

## Resources

- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/)
- [Write the Docs](https://www.writethedocs.org/)
