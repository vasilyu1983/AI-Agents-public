# &lt;service-repo&gt;

> Catalog-page template for a **service** repo. Generated from the repo
> profile + graph edges. Keep prose minimal; cite evidence.

- **Domain:** &lt;domain&gt;
- **Kind:** service
- **Stack:** &lt;lang / runtime / framework&gt;
- **Status:** active | legacy | deprecated
- **Owner:** &lt;team / named owner&gt;
- **Confidence:** verified | subset-verified | inferred

## Responsibility

&lt;What this service owns. One paragraph.&gt;

## Interfaces

| Direction | Interface | Contract | Evidence |
|-----------|-----------|----------|----------|
| in/out | &lt;API/topic/queue&gt; | &lt;schema ref&gt; | &lt;profile/graph ref&gt; |

## Dependencies

- **Upstream:** &lt;repos/services&gt;
- **Downstream:** &lt;repos/services&gt;
- **Datastores:** &lt;engines, from manifests not prose&gt;

## Operational notes

&lt;Resilience role, known failure modes — only if evidenced.&gt;

## Provenance

- Profile: `context/graphs/&lt;repo&gt;.json`
- Last scan: &lt;date&gt; · Rebuild: see `context/scripts/README.md`
