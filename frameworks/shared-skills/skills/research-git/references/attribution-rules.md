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
| Proprietary / no LICENSE | Cannot extract | DO NOT EXTRACT |
| Unlicense / CC0 / WTFPL | Public domain — no attribution required | Still cite for traceability |

If the LICENSE file is missing or unclear, treat the repo as proprietary and skip it.

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

> **Source**: Adapted from [<owner>/<repo>](https://github.com/<owner>/<repo>) at commit `<sha>`. License: <SPDX-ID>. Extracted 2026-04-23.

<rest of content>
```

### For a new section in an existing reference file

At the start of the new section:

```markdown
## <Section title>

<!-- Source: github.com/<owner>/<repo>@<sha> (<license>), extracted 2026-04-23 -->

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
      "commit_sha": "<sha at extraction>",
      "license": "MIT",
      "extracted_date": "2026-04-23",
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
| Forgetting to update data/sources.json | Loses audit trail | Update sources.json on every apply |
| Treating GPL repos as "fine for derivatives" | Viral copyleft contaminates the catalog | NEVER extract from GPL/AGPL |
| Skipping NOTICE preservation for Apache 2.0 | License violation | Always check for NOTICE file |

## When in Doubt

If you're unsure whether extraction is safe:
- Default to NOT extracting
- Cite the source in your research pack as "reviewed but not extracted"
- Ask the user for explicit approval before proceeding

License compliance is non-negotiable. A polluted catalog is worse than a smaller catalog.
