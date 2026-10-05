# Reply Clarity Rules (ASD-STE100, Adapted)

Load this file when you write the "how the agent writes to me" section of a personal instruction file, or when you audit agent replies for clarity. It holds a paste-ready template, the reasoning behind the rule order, the cases where STE hurts, and a method to derive your own rules from transcripts.

## Table of Contents

- [Core Finding: Reply Structure Beats Sentence Length](#core-finding-reply-structure-beats-sentence-length)
- [Where the Rules Live](#where-the-rules-live)
- [Paste-Ready Template](#paste-ready-template)
- [Where STE Hurts](#where-ste-hurts)
- [Deriving Rules From Your Own Transcripts](#deriving-rules-from-your-own-transcripts)
- [Confusion Signals Mapped to Rules](#confusion-signals-mapped-to-rules)
- [Source](#source)

## Core Finding: Reply Structure Beats Sentence Length

ASD-STE100 (Simplified Technical English) is a controlled-language standard for maintenance documentation. Its sentence rules transfer to agent replies, but they are not where agent replies usually fail.

A transcript review of interactive coding sessions found that sentence metrics were already mostly within STE limits. The confusion came from reply structure:

- The answer, the blocker, or the next action came at the end of a long reply.
- A precondition came after the instruction it limited.
- One question carried two decisions, so a short answer such as "go" or "yes" matched neither.
- A success claim opened the reply, and its scope limit came later.
- The agent stated a cause before it saw the evidence, then changed the diagnosis.

Rank the rules in that order: reply-level rules first, sentence-level rules second. Shortening sentences alone does not repair a wrong diagnosis or a misread intent.

## Where the Rules Live

Reply clarity is a personal preference about how agents write to one person. It belongs in the personal layer, not in each repository:

- Put the rules once in the personal instruction file. To share one file between Claude Code and Codex, see [loading-and-layers.md](loading-and-layers.md#personal-layer-shared-by-claude-code-and-codex).
- Put only repository-specific reply lessons in a repo `AGENTS.md`. Examples: which of two sibling repos deploys separately, or what the user's shorthand ("keep it easy", "one by one") means in that project. If a lesson applies to every repo, move it to the personal file.
- Never copy the personal rules into repo files. Loaded layers concatenate, so a copy spends the instruction budget twice, and the two copies drift apart.

## Paste-Ready Template

The template is about 60 lines. If your personal file is near its instruction budget ([claude-md-instruction-budget.md](claude-md-instruction-budget.md)), keep rules 1–7 and drop the sentence-level section first. Replace the examples with ones from your own sessions; rules anchored in your own failures are followed more reliably than generic ones.

````markdown
## Reply Clarity (ASD-STE100, Adapted)

Basis: ASD-STE100 writing principles, adapted for conversation after a review of my own sessions. This is not a claim of full STE compliance.

Apply these rules to replies, status reports, and instructions to me.
Do not apply them to code, commands, quoted text, logs, or error messages.

### 1. Put the answer first

- Start each reply with the answer, the state, or the result in one sentence. Put the detail after it.
- For a status question ("all done?", "what next?"), start with "Done", "Not done", or "Blocked".
- Use "Done" only for the completed scope. State any material verification limit beside the result.
- Distinguish saved settings, simulated checks, and observed runtime behavior. Distinguish local changes, commits, pushes, merges, and deployments.
- Put pending work before completed work. Do not open with "All ..." when the scope is partial.
- End with one line: `Next: <who> <does what>`. If I have nothing to do, write `Next: nothing from you.`
- When you give options, write the recommendation first, then the other options.
- Put teaching asides after the answer and the next action, never before them.
- When an earlier statement was wrong, correct it in the first sentence.

### 2. Put the condition, blocker, or risk before the detail

- If you cannot do a step, the first sentence says so and names the blocker. Then give me the exact step.
- Put a precondition before its instruction: "If you deploy by hand, skip this step."
- Before a destructive question, state what you will delete and what you will not touch.
- Do not delete a condition to make a sentence shorter. Move the condition to the front.

### 3. One instruction or one question per sentence

- Ask for one decision in each question. Make the meaning of each answer explicit: "Delete the three folders? yes = delete, no = keep."
- If a reply such as "go" does not identify an option, clarify before changing consequential behavior.
- Give each logical command separately. Say where to run it.
- Keep commands safe to paste. Use valid shell continuations or a short script for long commands. Never insert a line break only to meet a length target.
- For 3 or more steps, use a numbered list.

### 4. Name the actor

- In each step, say who does it: "I run ...", "You run ...".
- Use the active voice for actions and results: "The hook blocked the command."

### 5. Define internal names once

- Give a short gloss when you first use an internal label (ticket codes, batch IDs, "the other session", flag names). Give it again after a context compaction.
- Name the repository and the branch when you refer to a deploy, a PR, or a command.

### 6. Say what you did not do

- In a change summary, state the completed scope and material omissions: "The saved config passes validation. Runtime behavior remains untested."

### 7. Use one hedge, and keep the honest ones

- Use one hedge or fewer for each claim. Mark inference clearly: "Guess, not checked: ...".
- Keep a hedge on unverified figures, recalled numbers, and legal caveats.
- Do not state a cause as fact before you see the evidence. Say what you need to confirm it.

### Sentence-Level Rules (Lower Priority)

- Write 25 words or fewer in a descriptive sentence and 20 or fewer in an instruction.
- Use the simple past for completed work ("I changed"), not the present perfect.
- Use the same term for the same thing. Name the mechanism when it matters: sandbox, hook, deny rule, prompt, or automatic review.
- Keep noun clusters to 3 words or fewer.
- Give each paragraph one topic and 6 sentences or fewer.
- Make each count match the items you list.
- Use familiar, concrete words instead of abstract terms.

### Where STE Does Not Apply

- Quote code, commands, file paths, user text, logs, and error messages exactly.
- Keep a table of exact values. Put the one-line answer above it.
- Do not drop a number, a date, a flag, a scope qualifier, or a safety warning to make a sentence shorter.
````

## Where STE Hurts

Applied blindly, STE damages agent replies in these ways:

| STE habit | Damage in an agent reply | Adaptation |
|---|---|---|
| Cut every hedge | Unverified figures read as measured facts | Remove stacked hedges, keep one honest hedge per claim |
| Cut long sentences | Conditions, scope limits, and safety warnings disappear | Move the condition to the front instead of deleting it |
| Wrap long lines | A pasted shell command breaks at the wrap | Use valid continuations or a script; never wrap only for length |
| Approved vocabulary only | Exact flags, setting names, and error text get paraphrased | Quote technical identifiers exactly |
| Flat procedural voice everywhere | Recommendations lose their reason | Keep "I recommend X, because Y" |

A full STE approved-vocabulary audit is not useful for conversation. Claim "STE-adapted", never "STE-compliant".

## Deriving Rules From Your Own Transcripts

Generic rules help less than rules derived from your own failures. To derive them:

1. **Define the window and eligibility.** Example: the last 7 days; at least two user turns and two assistant replies. Exclude subagent records, tool output, model reasoning, and the review session itself.
2. **Sample with a fixed seed.** Stratify by project so that one busy repo does not fill the sample, then draw the rest at random. Record the seed and the transcript paths so another reviewer can reproduce the sample.
3. **Find confusion events.** Look for user corrections, repeated questions, answers that match no offered option, paste or execution failures, and a changed diagnosis. Do not count continuation requests such as "next" as confusion.
4. **Map each event to one rule.** Quote the original assistant text with its line reference, and write the proposed rewrite.
5. **Label the evidence strength.** "Observed" means the user acted on the misreading or said so. "Inferred" means the rewrite looks clearer but no harm was seen. Wording is rarely the only cause; say so.
6. **Keep positive controls.** Note replies that already did the right thing. They show which rules are already followed and need no space in the file.
7. **Keep statistics out of the always-loaded file.** Counts and rates belong in the review report. The instruction file holds rules and short examples only.
8. **Reconcile independent reviews before merging.** When two reviewers (or two runtimes) audit the same period, merge only the findings that both support or that you can verify. Do not copy figures that the other review did not reproduce.

Re-run the review after a few weeks. A rule that no longer catches anything can move to the lower-priority section or out of the file.

## Confusion Signals Mapped to Rules

Generic patterns from one review. Use them as a checklist, not as measured frequencies.

| Signal in the transcript | Evidence | Rule |
|---|---|---|
| Combined question ("delete X, or push and archive?") answered "yes, keep them" | Observed | 3: one decision per question, explicit answer meanings |
| "Which way?" answered "go"; the agent chose against the user's intent | Observed | 3: clarify an answer that names no option |
| Long one-line command split on paste; the shell ran half of it | Observed | 3: paste-safe commands, say where to run them |
| Blocker named early ("the sandbox"), later found to be a different check | Observed | 7: no cause before evidence |
| Prerequisite stated after the settings block it limits | Inferred | 2: condition first |
| "Will work as written" before the required environment setup | Inferred | 1 and 6: scoped "Done", state omissions |
| "All checks green" while one check was still running | Inferred | 1: pending work first |
| Recommendation placed after an options table and an aside | Inferred | 1: recommendation first |
| Batch or ticket IDs used without a gloss | Inferred | 5: define internal names |
| "Three to go:" followed by four items | Inferred | Sentence level: counts match lists |
| Abstract phrase ("a measured lower bound") for a simple fact | Inferred | Sentence level: familiar words |

## Source

ASD-STE100 Issue 9: <https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf>. Rules used: 1.11 and 9.4 (consistent terms), 2.1 (noun clusters), 3.6 (active voice), 4.2 (no missing words), 5.1–5.4 (procedural sentences, one instruction, condition first), 6.1 and 6.3–6.6 (descriptive writing, paragraphs). Rule numbers can change between issues; check the current issue before you cite a number.

The answer-first status words, workflow-state distinctions, explicit answer meanings, and paste-safe command guidance are conversation adaptations, not STE rules.
