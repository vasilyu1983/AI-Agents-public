---
name: document-xlsx
description: "Create/edit .xlsx spreadsheets with tables, formulas, charts, validation, and workbook automation. Use when asked to generate Excel reports, models, exports, or audit spreadsheets."
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.1"
last_validated: 2026-07-11
---

# Document XLSX Skill - Quick Reference

This skill enables creation, editing, inspection, and safe distribution of `.xlsx` workbooks. Use it for report exports, spreadsheet models, spreadsheet QA, workbook automation, and Excel-compatible deliverables.

Modern best practices (July 2026):
- Prefer Excel Tables over loose ranges.
- Separate inputs, calculations, and outputs.
- Treat spreadsheets as software: checks, owners, change control, and review loops.
- Treat untrusted workbooks as hostile: formulas, hyperlinks, external links, hidden content, and macros all need review.
- If workbooks are shared externally, include accessibility hygiene and run Excel's Accessibility Checker.

## Core Decision Rules (2026)

- First decide the runtime:
  local file generation, cloud workbook automation, or workbook audit/sanitization.
- Default to table-first exports:
  headers in row 1, frozen header row, autofilter, named table, bounded ranges.
- For native pivots:
  use Office Scripts or Excel automation; for headless exports prefer pre-computed summary tables.
- Libraries usually write formulas, but Excel calculates them when the file opens.
  If server-side computed values are required, calculate them in code and write values.
- `XlsxWriter` is write-only: it cannot open, read, or edit an existing `.xlsx` file.
  If the task is "edit this workbook" rather than "create a new one," reach for `openpyxl` (or ExcelJS in Node) instead — choosing `XlsxWriter` for an edit task is a common non-expert mistake that fails immediately.
- A formula written by `openpyxl` or `XlsxWriter` has no cached result until some calculation engine (Excel, LibreOffice headless, or a session-based tool such as xlwings) opens and recalculates the file.
  Reading that same file back with `openpyxl(..., data_only=True)` before any recalculation returns `None`, not the computed value — this looks like a bug but is expected behavior. If a downstream step (pandas, another script, an LLM) needs the number immediately, compute it in Python and write the literal value, or write both the formula and a plausible cached value only if you can guarantee it matches.
- ExcelJS is strong for workbook structure and styling, but it does not provide native chart generation; ExcelJS pivot-table support shipped as an experimental, limited feature only in recent 4.x releases — treat it as unstable and verify round-trip fidelity before relying on it in production.
- `openpyxl` can preserve VBA with `keep_vba=True`, but this skill does not author or execute macros.
- If ingesting untrusted workbooks with `openpyxl`, default to `keep_links=False` unless external links must be preserved.
- For very large exports (hundreds of thousands of rows or more), default `openpyxl` usage can balloon memory (a ~150MB source DataFrame has been observed using 2GB+ RAM with the default XML parser). Install `lxml` and use `Workbook(write_only=True)` for writing or `load_workbook(read_only=True)` for reading — both stream rather than build a full in-memory tree, and `lxml` alone materially cuts memory even outside those modes. Write-only workbooks can be saved exactly once; a second `save()` call raises `WorkbookAlreadySaved`, so batch all writes before saving.
- Row/column ceilings are fixed by the file format, not the library: 1,048,576 rows and 16,384 columns per worksheet. Exports approaching this need a pagination or multi-sheet strategy decided up front, not discovered at write time.

## Quick Reference

| Task | Tool/Library | Language | When to Use |
|------|--------------|----------|-------------|
| Table-first exports | XlsxWriter | Python | New `.xlsx` reports with tables, formats, and charts |
| Edit existing workbook | openpyxl | Python | Modify sheets, formulas, tables, validation, and protection |
| DataFrame export | pandas + XlsxWriter/openpyxl | Python | Data pipeline to Excel with styling and reviewable outputs |
| DataFrame export | Polars + XlsxWriter | Python | Fast dataframe pipeline with Excel output |
| Server-side workbook generation | ExcelJS | Node.js | Typed Node/TS stacks, workbook structure, styles, tables |
| Workbook ingestion | SheetJS / pandas / openpyxl | Node.js / Python | Parse existing spreadsheet data and metadata |
| Cloud automation | Office Scripts | TypeScript | Excel on the web, OneDrive/SharePoint workbooks, native pivots/tables |
| Microsoft 365 workbook API | Microsoft Graph Excel | REST | Remote workbook sessions, ranges, tables, charts, named items |
| Desktop Excel automation | xlwings | Python | Native Excel features on a machine with Excel installed |
| Workbook review | `scripts/xlsx_audit.py` | Python | Read-only QA pass before sharing or refactoring |
| Safe distribution | `scripts/xlsx_sanitize.py` | Python | Sanitize dangerous text prefixes and strip external links |
| Repeatable export | `scripts/xlsx_export_report.py` | Python | Opinionated CSV/JSON/Parquet to `.xlsx` export helper |

## When To Use This Skill

Invoke this skill when a user requests:

- Generate `.xlsx` reports, dashboards, models, or exports
- Add formulas, validation, tables, conditional formatting, or protection
- Audit an existing workbook for formulas, links, hidden sheets, or risky content
- Prepare a workbook for distribution, accessibility review, or safer ingestion
- Automate Excel features that depend on Microsoft 365 or desktop Excel

## Default Workflow

- Create:
  pick local generation (`XlsxWriter`, `openpyxl`, `ExcelJS`) or cloud automation (Office Scripts, Graph, xlwings), then start from a table-first layout.
- Review:
  run `python3 scripts/xlsx_audit.py workbook.xlsx --format md` and compare the results against `assets/spreadsheet-model-review-checklist.md`.
- Ship:
  sanitize exported text, review external links, run Accessibility Checker, and verify behavior in Excel plus the target secondary viewer if interoperability matters.

## ASCII Flow

```text
XLSX request
  |
  v
Classify workbook task
  |-- new export / report
  |-- edit existing workbook
  |-- audit / sanitize
  |-- cloud or desktop automation
  |
  v
Choose runtime
  |-- Python data pipeline -----> pandas / Polars + XlsxWriter
  |-- Python workbook edits ----> openpyxl
  |-- Node / TS service --------> ExcelJS
  |-- M365 live workbook -------> Office Scripts or Graph Excel
  |-- desktop Excel ------------> xlwings
  |
  v
Apply table-first structure
  |-- inputs
  |-- calculations
  |-- outputs
  |-- instructions / summary
  |
  v
Review formulas, links, hidden content, and accessibility
  |
  v
Sanitize and verify in target viewers
```

## Known Limits And Caveats

- Native pivots remain runtime-specific.
  `openpyxl` and `XlsxWriter` still do not create native pivot tables.
- Google Sheets and LibreOffice do not perfectly preserve all Excel features.
  Validate if you rely on pivots, formulas, protection, or advanced formatting.
- Data validation is UI metadata, not a full security boundary.
  Users can paste around it unless protection and process controls are in place.
- Workbook and sheet protection passwords are deterrents, not encryption.
  Use file-level encryption or platform controls for sensitive data.
- External links and hyperlinks can be both a security and reproducibility problem.
  Strip or document them before distribution.
- Dynamic-array and modern lookup formulas (`XLOOKUP`, `FILTER`, `UNIQUE`, `SORT`, `IFS`, `SEQUENCE`) require Microsoft 365 / current Excel.
  Writing them into a workbook targeted at Excel 2019/2016, Google Sheets (partial support), or older LibreOffice will show `#NAME?` for recipients on those versions — confirm the audience's Excel channel before defaulting to these over `VLOOKUP`/`INDEX-MATCH`/nested `IF`.
- `pandas.read_excel()` picks its engine by file extension (`openpyxl` for `.xlsx`), not by what wrote the file. It never surfaces conditional formatting, data validation, protection, or charts — if the audit needs those, read the OOXML parts directly (see `scripts/xlsx_audit.py`) or use `openpyxl` directly instead of pandas.

## Decision Tree

```text
Excel Task: [What do you need?]
    ├─ New workbook export?
    │   ├─ Python data/report pipeline → pandas/Polars + XlsxWriter
    │   ├─ Edit-heavy workbook logic → openpyxl
    │   └─ Node/TypeScript service → ExcelJS
    │
    ├─ Existing workbook review?
    │   ├─ Read-only audit → scripts/xlsx_audit.py
    │   ├─ Data extraction → pandas or SheetJS
    │   └─ Structural edits → openpyxl
    │
    ├─ Native Excel features on a live workbook?
    │   ├─ Web / M365 workbook → Office Scripts or Graph Excel
    │   └─ Desktop Excel installed → xlwings
    │
    └─ Safe distribution?
        ├─ Sanitize text / strip links → scripts/xlsx_sanitize.py
        ├─ Accessibility review → Excel checker + accessibility reference
        └─ Sensitive data → encryption + platform access controls
```

## Core Operations

### Table-First Export (Python - XlsxWriter)

```python
import pandas as pd

df = pd.DataFrame(
    [
        {"product": "Widget A", "qty": 100, "price": 10.0},
        {"product": "Widget B", "qty": 50, "price": 25.0},
    ]
)
df["total"] = df["qty"] * df["price"]

with pd.ExcelWriter("report.xlsx", engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Sales", index=False, startrow=1)

    workbook = writer.book
    worksheet = writer.sheets["Sales"]
    header_fmt = workbook.add_format({"bold": True, "bg_color": "#D9E2F3"})
    money_fmt = workbook.add_format({"num_format": "$#,##0.00"})

    worksheet.write("A1", "Sales report")
    worksheet.freeze_panes(2, 0)
    worksheet.autofilter(1, 0, len(df), len(df.columns) - 1)
    worksheet.set_column("C:D", 14, money_fmt)
    worksheet.add_table(
        1,
        0,
        len(df) + 1,
        len(df.columns) - 1,
        {
            "name": "SalesTable",
            "style": "Table Style Medium 2",
            "columns": [{"header": col, "header_format": header_fmt} for col in df.columns],
            "total_row": True,
        },
    )
```

### Edit Existing Workbook Safely (Python - openpyxl)

```python
from openpyxl import load_workbook

wb = load_workbook("input.xlsx", keep_vba=False, keep_links=False)
ws = wb["Sales"]

ws["A1"] = "Sales report for Q1 2026"
ws.freeze_panes = "A2"
ws.sheet_view.showGridLines = True

wb.save("output.xlsx")
```

### Native Pivot Creation (Office Scripts)

```typescript
function main(workbook: ExcelScript.Workbook) {
  const dataSheet = workbook.getWorksheet("Raw Data");
  const sourceRange = dataSheet.getUsedRange();
  const sourceTable = dataSheet.addTable(sourceRange, true);
  sourceTable.setName("SalesTable");

  const pivotSheet = workbook.addWorksheet("Pivot");
  const pivot = workbook.addPivotTable("SalesPivot", sourceTable, pivotSheet.getRange("A1"));
  pivot.addRowHierarchy(pivot.getHierarchy("Region"));
  pivot.addColumnHierarchy(pivot.getHierarchy("Product"));
  pivot.addDataHierarchy(pivot.getHierarchy("Revenue"));
}
```

## Do / Avoid (July 2026)

### Do

- Default to named tables, bounded ranges, and frozen headers.
- Keep assumptions explicit with value, unit, source, and date.
- Add control totals, duplicate checks, and fail-loud QA cells.
- Use descriptive sheet names and place workbook context in `A1`.
- Audit hidden sheets, external links, formulas, and named items before sharing.

### Avoid

- Raw cell-block exports when a table would work.
- Hardcoded constants buried in formulas.
- Blank worksheets, merged header cells, or color-only meaning in delivered reports.
- Preserving external links by default on untrusted ingest.
- Sharing workbooks with PII or secrets without explicit approval and controls.

## What Good Looks Like

- Structure:
  clear Inputs, Calculations, Outputs, and Instructions or Summary tabs as needed.
- Data model:
  named tables or ranges, no silent range drift, and no unexplained hidden sheets.
- Integrity:
  no `#REF!`, broken names, stale links, or silent formula inconsistencies.
- Accessibility:
  descriptive tabs, meaningful hyperlinks, proper table headers, alt text where applicable, and a clean Accessibility Checker run.
- Release hygiene:
  owner named, review loop completed, and workbook sanitized or justified before distribution.

## Optional: AI / Automation

Use only when explicitly requested and policy-compliant.

- Generate first-pass formulas, charts, or summary tabs; humans verify results and edge cases.
- Produce a workbook audit summary from `scripts/xlsx_audit.py`; humans review the findings.
- Draft assumptions and glossary tabs from known source data; do not invent metrics or provenance.

## Navigation

**Resources**
- [references/excel-tables-structured-references.md](references/excel-tables-structured-references.md) - Excel Tables, totals rows, and structured formulas
- [references/excel-cloud-automation.md](references/excel-cloud-automation.md) - Office Scripts, Microsoft Graph Excel, xlwings
- [references/excel-accessibility-compliance.md](references/excel-accessibility-compliance.md) - Accessibility, Section 508, EN 301 549 considerations
- [references/excel-formulas.md](references/excel-formulas.md) - Formula reference and patterns
- [references/excel-formatting.md](references/excel-formatting.md) - Styling and conditional formatting
- [references/excel-charts.md](references/excel-charts.md) - Chart types and customization
- [references/excel-data-validation.md](references/excel-data-validation.md) - Dropdowns, input constraints, cascading validation
- [references/excel-pivot-tables.md](references/excel-pivot-tables.md) - Pivot workarounds and runtime-specific options
- [references/excel-security-protection.md](references/excel-security-protection.md) - Protection, links, injection prevention
- [data/sources.json](data/sources.json) - Current vendor and standards links

**Scripts**
- `python3 scripts/xlsx_audit.py workbook.xlsx --format md`
- `python3 scripts/xlsx_export_report.py input.csv output.xlsx`
- `python3 scripts/xlsx_sanitize.py input.xlsx output.xlsx --strip-external-links`

**Templates**
- [assets/financial-report.md](assets/financial-report.md) - Financial statement template
- [assets/data-dashboard.md](assets/data-dashboard.md) - Dashboard with charts and KPIs
- [assets/spreadsheet-model-review-checklist.md](assets/spreadsheet-model-review-checklist.md) - Workbook QA checklist

**Related Skills**
- [../document-pdf/SKILL.md](../document-pdf/SKILL.md) - PDF generation from spreadsheet data
- [../ai-ml-data-science/SKILL.md](../ai-ml-data-science/SKILL.md) - Data analysis and dataframe workflows
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) - Database-to-workbook pipelines

## Fact-Checking

- Use web search/web fetch to verify current external facts, versions, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources and stable vendor docs over blog posts.
- If a Microsoft Learn landing page is session-dependent, prefer a retrievable API/reference page for the source list.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
