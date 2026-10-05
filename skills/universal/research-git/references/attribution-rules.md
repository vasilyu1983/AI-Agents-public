# Attribution Rules

## Table of Contents

- [License Check (mandatory before extraction)](#license-check-mandatory-before-extraction)
- [Never Copy Verbatim](#never-copy-verbatim)
- [Required Attribution Format](#required-attribution-format)
- [data/sources.json Update](#datasourcesjson-update)
- [Apache 2.0 Special Requirements](#apache-20-special-requirements)
- [Common Attribution Mistakes](#common-attribution-mistakes)
- [When in Doubt](#when-in-doubt)

License compliance and citation requirements before merging extracted content into the local skill catalog.

## License Check (mandatory before extraction)

Always verify the source repo's license BEFORE extracting any content.

```bash
gh api repos/<owner>/<repo>/license --jq '.license.spdx_id'
```

| License | Permits derived work? | Action |
|---------|----------------------|--------|
| MIT | Yes, with attribution | Safe to extract |
| Apache-2.0 | Yes, with attribution + patent grant notice | Safe to extract |
| BSD-2-Clause / BSD-3-Clause | Yes, with attribution | Safe to extract |
| CC-BY-4.0 | Yes, with attribution (docs) | Safe to extract |
| CC-BY-SA-4.0 | Yes, but derivatives must use same license | Avoid — viral |
| GPL-2.0 / GPL-3.0 | Viral copyleft — derivatives must be GPL | DO NOT EXTRACT |
| AGPL-3.0 | Stronger viral — DO NOT EXTRACT | DO NOT EXTRACT |
| LGPL | Library exception — case-by-case | Avoid for skill content |
| Proprietary / no LICENSE | All rights reserved — cannot extract | DO NOT EXTRACT |
| Unlicense / CC0 / WTFPL | Public domain — no attribution required | Still cite for traceability |

If the LICENSE file is missing or unclear, treat the repo as all rights reserved and skip it. Public visibility on GitHub grants viewing and forking under the site terms, not reuse.

### Author: cite the upstream, not the fork

The author on every ledger entry is the upstream original. When the repo you fetched is a fork (`fork: true` in `_metadata.json`, or `gh api repos/<owner>/<repo> --jq '.parent.full_name'` returns a parent), follow the chain to the root and record that owner as the author, with the fork noted only if it is where you took the content from. For a file, `git log --follow --diff-filter=A` in a clone (or the file's blame on GitHub) can show whether it was written there or carried in from elsewhere.

### Screen before ingesting

A permissive licence covers the licensor's copyright; it does not make everything in the repo safe to copy. Before any content enters a research pack, screen it and drop:

- secrets and credentials (API keys, tokens, private keys, `.env` values, signed URLs)
- PII (names, emails, phone numbers in fixtures, logs, or test data)
- organisation-specific details: internal hostnames, private package registries, customer or account names, ticket IDs, Slack channels

Reject the item, not just the line, when the surrounding example only makes sense with those details. A secret found in a public repo is still not yours to reuse, and copying it into a pack widens the leak.

## Never Copy Verbatim

Even with a permissive license, copying content verbatim creates two problems:
1. **Voice drift** — your skill catalog has a consistent style that copy-paste breaks
2. **Quality control loss** — verbatim content can't be improved or rewritten over time

Always rewrite extracted patterns in the local voice. Three rules:
1. **Patterns**: extract the idea, rewrite the explanation in your own words
2. **Code snippets**: short snippets (<10 lines) can be reused with attribution; longer code should be paraphrased or reduced to the essential pattern
3. **Citations**: copy URLs and version numbers verbatim — they're facts, not creative content

## Required Attribution Format

Every extracted insight MUST include attribution in the new content. Use this format:

### For a new reference file

At the top of the file:

```markdown
# <Title>

> **Source**: Adapted from [<owner>/<repo>](https://github.com/<owner>/<repo>) by <upstream author> at commit `<sha>`. License: <SPDX-ID>. Extracted YYYY-MM-DD.

<rest of content>
```

### For a new section in an existing reference file

At the start of the new section:

```markdown
## <Section title>

<!-- Source: github.com/<owner>/<repo>@<sha> (<license>), extracted YYYY-MM-DD -->

<content>
```

### For a SKILL.md table update

Inline citation in the row:

```markdown
| Pattern X | Description ([source](https://github.com/<owner>/<repo>)) |
```

## data/sources.json Update

After applying any extraction, update the target skill's `data/sources.json`:

```json
{
  "external_sources": [
    {
      "name": "<repo name>",
      "url": "https://github.com/<owner>/<repo>",
      "author": "<upstream author or org, not the fork owner>",
      "commit_sha": "<sha at extraction>",
      "license": "MIT",
      "extracted_date": "YYYY-MM-DD",
      "patterns_used": ["pattern-x", "pattern-y"]
    }
  ]
}
```

This creates a permanent audit trail that survives skill updates.

## Apache 2.0 Special Requirements

Apache 2.0 requires preserving NOTICE file content if present. Before extracting from an Apache 2.0 repo:

```bash
gh api repos/<owner>/<repo>/contents/NOTICE 2>/dev/null && echo "NOTICE file exists — preserve its content"
```

If a NOTICE file exists, include its relevant content in your skill's `data/sources.json` under a `notices` field.

## Common Attribution Mistakes

| Mistake | Why it fails | Fix |
|---------|--------------|-----|
| Extracting without checking the license | License violation, legal risk | Always check LICENSE first |
| Copying verbatim "because it's open source" | Voice drift + creates a maintenance burden | Always rewrite in local voice |
| Citing only the repo URL without commit SHA | Future readers can't verify against the right version | Always pin to commit SHA |
| Crediting the fork you fetched from | Misattributes the work; the fork owner may have changed nothing | Record the upstream author; note the fork only as the fetch location |
| Ingesting fixtures or configs with real hostnames, names, or keys | Leaks organisation data into the catalog under cover of a permissive licence | Screen every copied item; drop the item, not just the line |
| Forgetting to update data/sources.json | Loses audit trail | Update sources.json on every apply |
| Treating GPL repos as "fine for derivatives" | Viral copyleft contaminates the catalog | NEVER extract from GPL/AGPL |
| Skipping NOTICE preservation for Apache 2.0 | License violation | Always check for NOTICE file |

## When in Doubt

If you're unsure whether extraction is safe:
- Default to NOT extracting
- Cite the source in your research pack as "reviewed but not extracted"
- Ask the user for explicit approval before proceeding

License compliance is non-negotiable. A polluted catalog is worse than a smaller catalog.
