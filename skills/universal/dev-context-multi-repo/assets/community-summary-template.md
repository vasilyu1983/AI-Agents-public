# {{ community_id }} — {{ community_name }}

Generated from `query_graph.py --communities --resolution {{ resolution }}` on {{ generated_at }}.

## Snapshot

- **Size**: {{ size }} nodes
- **Modularity contribution**: {{ modularity_contribution }}
- **Resolution**: γ = {{ resolution }}
- **Detection seed**: {{ seed }}

## Composition

| Type | Count | % |
|------|-------|---|
{{ #type_breakdown }}| {{ type }} | {{ count }} | {{ percent }}% |
{{ /type_breakdown }}

| Domain | Count |
|--------|-------|
{{ #domain_breakdown }}| {{ domain }} | {{ count }} |
{{ /domain_breakdown }}

## Anchor nodes

The 5–10 most central nodes by weighted PPR within this community.

{{ #anchor_nodes }}- `{{ id }}` — {{ label }} ({{ type }}); ppr_score = {{ ppr_score }}
{{ /anchor_nodes }}

## What this community does

One paragraph describing the shared responsibility, integration boundary, or business capability that ties these nodes together. Generate from anchor-node summaries plus the dominant edge relations between members.

Avoid prose that re-lists every member. Reference the member-ids list at the bottom for full enumeration.

## Cross-community ties

Edges that leave this community and where they go.

| External node | Relation | Direction | Weight |
|---------------|----------|-----------|--------|
{{ #external_edges }}| {{ external_id }} | {{ relation }} | {{ direction }} | {{ weight }} |
{{ /external_edges }}

## Verification status

- **Verified**: claims grounded in manifests, schemas, or workflow files
- **Inferred**: claims derived from naming, topology, or graph-edge patterns
- **Unverified**: claims that need re-checking against source

## Members

<details>
<summary>Full member list ({{ size }})</summary>

{{ #member_ids }}- `{{ id }}`
{{ /member_ids }}

</details>

## Lifecycle

- **Generated from**: `graphs/knowledge-graph.json` at version {{ graph_contract_version }}
- **Source detection run**: `reports/community-runs/{{ run_id }}.json`
- **Refresh trigger**: regenerate when graph membership churn exceeds 10% or modularity changes by more than 0.05
