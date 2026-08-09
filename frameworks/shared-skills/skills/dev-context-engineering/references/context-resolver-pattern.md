# Context Resolver Pattern

> **Source**: Adapted from [garrytan/gbrain](https://github.com/garrytan/gbrain) at commit `adb02b7826a010700efc968b18df8aaf17d8ffa1`. License: MIT. Extracted 2026-04-13.

A **resolver** is a routing table for context. It answers the question "when task type X appears, which document should the agent load first?" Skills say HOW to do something; resolvers say WHAT to load WHEN.

## Why Resolvers Matter

The temptation, when an agent gets something wrong, is to put more text into always-on context. Add a caveat to `AGENTS.md`. Add another rule file. Bolt on an extra section explaining the edge case. Repeat for six months and the hot instruction layer becomes a 20,000-line swamp that the model starts ignoring because attention degrades with length.

The resolver pattern fixes this by separating two things:

- **Execution policy** (hot layer): the small set of rules that must be true on every request.
- **Contextual triggers** (resolver layer): pointers that say "when the user asks about X, load document Y first."

The hot layer stays small. The body of knowledge that the model actually needs for any specific task stays out of the prompt until the resolver pulls it in.

## How Claude Code Already Does This

Claude Code ships with a built-in resolver: every skill has a `description` field, and the runtime matches user intent against those descriptions automatically. You don't have to remember `/ship` exists — the description *is* the resolver. The same mechanism applies to subagents and hooks.

This is why a terse, specific skill description matters more than a long one. The description is the selector. If the description doesn't distinguish your skill from a neighbor, the resolver can't route to it.

## Designing a Resolver Layer for Your Repo

Three rules keep the resolver healthy:

1. **One task type → one primary document.** When a user asks about deployments, the resolver should point at one deployment doc, not three. If three exist, consolidate or disambiguate.
2. **Descriptions carry the trigger vocabulary.** The words that appear in user requests should appear in the description. "Run the migration safely under load" → description contains "migration", "safe", "load", not "alters table schema."
3. **Leave deep content out of the resolver file.** The resolver is a map, not the territory. A ten-line pointer file that says "when the question is about payments, read `docs/payments/overview.md` + `docs/payments/webhooks.md`" is more useful than copying the content into the hot layer.

## Anti-Pattern: The 20,000-Line AGENTS.md

From the source essay: "A confession: my CLAUDE.md was 20,000 lines. Every single thing I ran across went in there. Every quirk, every pattern, every lesson. Completely ridiculous. The model's attention degraded. Claude Code literally told me to cut it back. The fix: about 200 lines. Just pointers to documents. The resolver loads the right one when it matters."

The diagnostic signal is straightforward: if your always-on context file is longer than a single printed page, you are almost certainly paying for it in two ways — slower sessions and lower adherence. Cut to pointers, move the body into skills or docs, and let description-matched routing handle loading.

## Skills vs Resolvers vs Rules

| Layer | Answers | Example |
|-------|---------|---------|
| **Skill** | How to perform a task | `dev-git-workflow/SKILL.md` describes branching strategy |
| **Resolver** | Which document to load when a task type appears | `AGENTS.md` says "for release steps, read `docs/release.md`" |
| **Rule** | What must always be true | `.claude/rules/no-force-push-main.md` is a hard constraint |

Rules go in the hot layer because they always apply. Resolvers go in the hot layer because they are short pointers. Skills live outside the hot layer and are summoned by the resolver.

## Related

- [context-development-lifecycle.md](context-development-lifecycle.md) — Progressive disclosure pattern and distribution hierarchy (the loading tiers that the resolver targets)
- [fast-track-guide.md](fast-track-guide.md) — When a repo is small enough that a resolver layer is premature
- [paradigm-comparison.md](paradigm-comparison.md) — Why rule files and resolver files serve different purposes
