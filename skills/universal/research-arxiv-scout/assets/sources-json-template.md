# `02_sources-*.json` template for arXiv papers

Use this when proposing additions to a `custom-gpt/**/02_sources-*.json` file. Keep the target file's existing category names and schema; use `add_as_web_search: false` for arXiv abstract links.

## Example category: `research_papers`

```json
{
  "metadata": {
    "title": "Agent Name - Sources",
    "description": "Curated web resources for this agent's domain",
    "last_updated": "YYYY-MM-DD"
  },
  "research_papers": [
    {
      "name": "Paper Title (YYYY)",
      "url": "https://arxiv.org/abs/YYYY.NNNNN",
      "description": "1-2 sentences on what it adds and why it matters for this agent",
      "add_as_web_search": false
    }
  ]
}
```

## Recommended fields for descriptions

- What capability it improves (agents, RAG, evaluation, testing, safety)
- What is new or different (method, benchmark, failure mode, scaling result)
- What to do next in this repo (update sources, add reference, adjust workflow)
