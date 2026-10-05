# Excel Accessibility and Compliance

Use this reference when the workbook will be shared outside the authoring team or when accessibility requirements matter for procurement, regulated delivery, or public-sector use.

---

## Baseline Rules

| Rule | Why it matters |
|------|----------------|
| Give every worksheet a descriptive name | Screen-reader and keyboard users rely on tab names |
| Avoid blank worksheets | Blank tabs create noise and confusion |
| Put workbook context in `A1` | Readers should know what the sheet is for immediately |
| Use accessible tables with one header row | Tables are easier to navigate than arbitrary ranges |
| Avoid merged or split header cells | They break navigation and header association |
| Use meaningful hyperlink text | "View source export" is better than a raw URL |
| Do not rely on color alone | Status and meaning need labels or icons too |
| Add alt text where charts or images convey meaning | Non-text content needs a text equivalent |

---

## Authoring Checklist

- `A1` explains the purpose of the sheet before the main table or content block
- Workbook contains no blank worksheets
- Sheet names are unique and descriptive
- Primary data blocks are Excel Tables or clearly labeled bounded ranges
- Header row is the first row of the table, not merged across multiple rows
- Important formulas, assumptions, or controls are labeled in plain language
- Hyperlinks describe the destination or purpose
- Charts include a title, units, timeframe, and nearby explanatory text or alt text
- Accessibility Checker is run before delivery

---

## Distribution Notes

- If a workbook is customer-facing or part of an accessibility-sensitive process, expect requirements that align with Microsoft accessibility guidance and, in many enterprise or public-sector contexts, Section 508 (US) or EN 301 549 (EU) expectations.
- Before a conformance statement, identify the applicable legislation, national implementation and contractual requirements. Check the [Official Journal references for that legislation](https://single-market-economy.ec.europa.eu/single-market/goods/european-standards/harmonised-standards_en), the cited EN 301 549 revision and the requirements it covers. A reference under another directive does not establish EAA presumption of conformity; [EAA Article 15](https://eur-lex.europa.eu/eli/dir/2019/882/oj) limits it to the covered requirements. Select the technical WCAG target from the applicable requirements and report workbook validation separately from legal scope.
- Accessibility review should happen before PDF export as well as before `.xlsx` distribution.
- If the workbook is primarily a decision artifact, add an Instructions or Summary sheet that explains purpose, owner, version, and key assumptions.

---

## Do / Avoid

**Do:**
- Keep a simple reading order from top-left to bottom-right
- Use tables, labels, and notes instead of layout tricks
- Include units and timeframe on charts and summary cells
- Run Excel's built-in Accessibility Checker before sharing

**Avoid:**
- Blank tabs
- Merged multi-row headers
- Hidden meaning behind colors only
- Hyperlinks that expose raw tracking URLs when a readable label would work
