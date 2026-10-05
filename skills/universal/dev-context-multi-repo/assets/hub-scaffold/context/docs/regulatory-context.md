# Regulatory Context

> Template stub. The regulatory frame the portfolio operates under, so an
> agent knows *why* the `rules/` constraints exist. Swap every regime
> reference for your own. Illustrative scaffolding, not legal advice.

## Applicable regimes (replace)

| Regime | Applies to | Hub rule |
|--------|------------|----------|
| &lt;e.g. PCI DSS&gt; | &lt;card data flows&gt; | `rules/02-data-handling.md` |
| &lt;e.g. GDPR/CCPA&gt; | &lt;personal data&gt; | `rules/02-data-handling.md` |
| &lt;e.g. sector regulator&gt; | &lt;regulated services&gt; | `rules/01-compliance.md` |
| &lt;e.g. resilience standard&gt; | &lt;important business services&gt; | `rules/05-operational-resilience.md` |

## Important business services

&lt;The flows/repos that, if degraded, cause regulatory or customer harm.
Maintained in the relevant `&lt;domain&gt;/as-is/`. The knowledge graph's
blast-radius queries must respect this mapping.&gt;

## Source templates

The example regime templates live in
`dev-context-engineering/assets/` (compliance, data-handling, AI
governance). They are labelled examples — replace, do not ship as-is.
