# &lt;library-repo&gt;

> Catalog-page template for a **shared library / package** repo.

- **Domain:** &lt;domain&gt; (often `core`/`infra`)
- **Kind:** library
- **Stack:** &lt;language / package ecosystem&gt;
- **Status:** active | legacy
- **Confidence:** verified | inferred

## What it provides

&lt;The capability it factors out. One paragraph.&gt;

## Consumers

&lt;Repos that depend on it — from dependency edges, not guesswork. This
list drives blast-radius scoring; keep it evidence-backed.&gt;

| Consumer repo | Version pinned | Evidence |
|---------------|----------------|----------|
| &lt;repo&gt; | &lt;ver&gt; | &lt;manifest ref&gt; |

## Change risk

&lt;Why a breaking change here is high blast radius. Tie to graph
articulation-point / impact output.&gt;

## Provenance

- Profile: `context/graphs/&lt;repo&gt;.json` · Rebuild: `context/scripts/README.md`
