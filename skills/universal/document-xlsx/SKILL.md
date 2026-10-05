---
name: document-xlsx
description: "Builds Excel charts, pivots, validation, exports, Office Scripts/Graph automation, and workbook audits. Use when automating workbooks; for plain edits prefer official xlsx skill."
allowed-tools: Bash, Read, Write, Glob, Grep
compatibility: Claude Code + Codex. Uses runtime-specific allowed-tools / argument-hint fields.
version: "1.1"
last_validated: 2026-07-11
---

# Document XLSX Skill - Quick Reference

**Boundary:** when the official Anthropic `xlsx` skill is available, prefer it for plain create/edit, formula-first financial models, LibreOffice recalculation (`recalc.py`) and formula-error scans. Use this skill for its specialist lanes:
- native charts, pivots, data validation and conditional formatting
- Office Scripts, Microsoft Graph and xlwings automation
- very large (`write_only`/`read_only`) files
- untrusted-workbook audit and sanitising

## Core Decision Rules

- **Decide the runtime first:** local file generation, cloud workbook automation (Microsoft 365), desktop Excel automation, or audit and sanitising.
- **`XlsxWriter` is write-only.** It cannot open or edit an existing `.xlsx`. For "edit this workbook", use `openpyxl` (or ExcelJS in Node). Picking XlsxWriter for an edit task fails immediately.
- **Table-first exports:** headers in one row, a named Excel Table, a frozen header row and bounded ranges. The table brings its own autofilter, so a separate `autofilter()` over the same range raises `OverlappingRange`.
- **Libraries write formulas; a calculation engine computes them.** openpyxl does not evaluate formulas; XlsxWriter normally writes a placeholder cached `0` and requests recalculation, or accepts an explicitly supplied result. A nonblank cache is not calculation evidence. Keep formulas, recalculate in the target engine, and independently compute any result needed before that step. See [XlsxWriter formula results](https://xlsxwriter.readthedocs.io/working_with_formulas.html#formula-results).
- **Future functions need their specified OOXML spelling.** With openpyxl, check the function's required prefix in the [writer's future-function list](https://xlsxwriter.readthedocs.io/working_with_formulas.html#formulas-added-in-excel-2010-and-later); `openpyxl.utils.FORMULAE` is not a compatibility test. Default to XlsxWriter `write_dynamic_array_formula` for spill formulas. If the recipient's Excel build is unknown, prefer `INDEX/MATCH` and nested `IF`. Load [references/excel-formulas.md](references/excel-formulas.md) when writing future or array functions or reading cached results.
- **Library defaults fail open. Set them explicitly:**
  - Set validation error alerts and `errorStyle="stop"` explicitly for Excel entry checks; openpyxl itself never validates assigned values. Check inputs in code too.
  - XlsxWriter turns strings that start with `=` into formulas unless `strings_to_formulas` is off.
  - XlsxWriter `add_table` warns and returns a negative code instead of raising.
- **Native pivots:** use Office Scripts (Microsoft 365) or xlwings (desktop Excel). openpyxl and XlsxWriter cannot create them. For headless exports, write pre-computed summary tables.
- **Untrusted workbooks:** load with `keep_links=False` and `keep_vba=False`, and run `scripts/xlsx_audit.py` before anything else. This skill never authors or executes macros.
- **Large files:** install `lxml` and use `Workbook(write_only=True)` / `load_workbook(read_only=True)`. Both stream instead of building the full tree. A write-only workbook can be saved exactly once (`WorkbookAlreadySaved`).
- **Format ceilings:** 1,048,576 rows × 16,384 columns per sheet, set by the file format. Decide pagination or a multi-sheet layout up front.

## Quick Reference

| Task | Tool | When |
|------|------|------|
| New table-first export | XlsxWriter (pandas/Polars) | Reports with tables, formats, native charts, dynamic arrays |
| Edit existing workbook | openpyxl | Sheets, formulas, tables, validation, protection |
| Node/TS service | ExcelJS | Structure and styles. For native charts or pivots, check the installed release's documentation and test the required round trip |
| Microsoft 365 workbook | Office Scripts / Microsoft Graph Excel | Native pivots and tables; remote sessions |
| Desktop Excel features | xlwings | A machine with Excel installed; not headless CI |
| Pre-share audit (gate) | `scripts/xlsx_audit.py` | Exits non-zero on blocking findings |
| Text/link cleanup | `scripts/xlsx_sanitize.py` | Adds visible apostrophes to risky strings; optionally removes external-link parts. Sanitize CSV at export too |
| Repeatable export | `scripts/xlsx_export_report.py` | CSV/JSON/Parquet to a table-first `.xlsx`; input text is never turned into formulas |

## Scripts And Exit Codes

```bash
python3 scripts/xlsx_audit.py workbook.xlsx --format md       # gate
python3 scripts/xlsx_audit.py workbook.xlsx --report-only     # inventory; invalid input still exits 2
python3 scripts/xlsx_sanitize.py in.xlsx out.xlsx --strip-external-links
python3 scripts/xlsx_export_report.py data.csv report.xlsx --title "Sales"
python3 scripts/test_xlsx_sanitize.py                         # atomic output and alias rejection regressions
```

| Script | 0 | 1 | 2 |
|--------|---|---|---|
| `xlsx_audit.py` | No blocking findings (heuristic signals may still need a read) | Blocking findings: cached error values, newer functions without `_xlfn.`, dangerous text, external-link parts, VBA | File missing, not a zip, or not a workbook |
| `xlsx_sanitize.py` / `xlsx_export_report.py` | Written | n/a | Input missing or unreadable, or the write failed. No partial output is left behind |

Heuristic signals the audit reports but does not block on: hard-coded constants in formulas, hidden or very hidden sheets, `HYPERLINK` formulas, formulas without cached values. Read them before sharing. The audit is static: it cannot prove formulas evaluate correctly (see the calculation evidence gate below).

## Core Operations

### Table-First Export (XlsxWriter)

```python
import pandas as pd

with pd.ExcelWriter("report.xlsx", engine="xlsxwriter",
                    engine_kwargs={"options": {"strings_to_formulas": False}}) as writer:
    df.to_excel(writer, sheet_name="Sales", index=False, startrow=1)
    workbook, worksheet = writer.book, writer.sheets["Sales"]
    header_fmt = workbook.add_format({"bold": True, "bg_color": "#D9E2F3"})

    worksheet.write("A1", "Sales report")
    worksheet.freeze_panes(2, 0)
    # The table brings its own autofilter; a separate worksheet.autofilter() over the
    # same range raises OverlappingRange. Rows: header=1, data=2..len(df)+1, totals=len(df)+2.
    status = worksheet.add_table(1, 0, len(df) + 2, len(df.columns) - 1, {
        "name": "SalesTable",
        "style": "Table Style Medium 2",
        "total_row": True,
        "columns": [{"header": col, "header_format": header_fmt,
                     **({"total_function": "sum"} if col in ("qty", "total") else {})}
                    for col in df.columns],
    })
    if isinstance(status, int) and status < 0:   # XlsxWriter warns instead of raising
        raise ValueError("add_table rejected the table definition")
```

If the table range is one row short, the totals row silently overwrites the last data row. See [references/excel-tables-structured-references.md](references/excel-tables-structured-references.md#range-arithmetic).

### Edit Existing Workbook Safely (openpyxl)

```python
from openpyxl import load_workbook

wb = load_workbook("input.xlsx", keep_vba=False, keep_links=False)
ws = wb["Sales"]
ws["A1"] = "Sales report"
ws.freeze_panes = "A2"
wb.save("output.xlsx")
```

Never load with `data_only=True` and then save: that replaces every formula with its cached value, or with nothing.

## Known Limits And Caveats

- Google Sheets and LibreOffice do not preserve every Excel feature. Verify pivots, dynamic-array formulas, protection and advanced formatting in the target viewer.
- Data validation is UI metadata; paste can bypass it or replace a cell's rule. Combine validation with protection and checks in code. See [openpyxl validation limits](https://openpyxl.readthedocs.io/en/stable/validation.html).
- Sheet and workbook protection passwords are deterrents, not encryption. Use file-level encryption or platform access controls for sensitive data. See [references/excel-security-protection.md](references/excel-security-protection.md).
- `pandas.read_excel()` never surfaces conditional formatting, validation, protection or charts. When the audit needs them, read the OOXML parts directly or use openpyxl.

- Library behaviour changes between releases. Re-test a claimed default (for example a validation or formula option) against the installed version before relying on it.

## Default Workflow

1. **Create:** choose the runtime, start from a table-first layout, and keep inputs, calculations and outputs separate.
2. **Gate:** `python3 scripts/xlsx_audit.py out.xlsx --format md` must exit 0, then review against [assets/spreadsheet-model-review-checklist.md](assets/spreadsheet-model-review-checklist.md).
3. **Ship:** sanitise exported text, review external links, run Excel's Accessibility Checker, and open the file in Excel plus the target secondary viewer.

## Do / Avoid

Record assumptions with value, unit, source and date; include control totals and check cells. Hidden sheets do not protect PII or secrets.

## Calculation Evidence Gate

Define the calculation contract before release: authoritative inputs, the expected formulas or computed values, the calculation engine, the recalculation mode and the control totals. Where formulas matter, reopen the final workbook twice:
1. With formulas visible, to check consistency.
2. After a named calculation engine has recalculated it, to inspect cached results and error cells (`#REF!`, `#VALUE!`, `#DIV/0!`, `#NAME?`, `#N/A`).

If no calculation engine is available, mark the formula results **unverified** and provide independently computed control totals. Neither blank caches nor placeholder zeros prove calculation; supply cached values only when independently computed from the authoritative inputs.

## Navigation

**References**
- [references/excel-formulas.md](references/excel-formulas.md) - `_xlfn.` prefixes, spilling functions, array formulas, reading values back
- [references/excel-tables-structured-references.md](references/excel-tables-structured-references.md) - Table range arithmetic, structured formulas
- [references/excel-charts.md](references/excel-charts.md) - Chart choice, reference wiring, openpyxl chart gotchas
- [references/excel-formatting.md](references/excel-formatting.md) - Types before formats, conditional-formatting rules, layout
- [references/excel-data-validation.md](references/excel-data-validation.md) - Enforced dropdowns, named lists, cascading validation
- [references/excel-pivot-tables.md](references/excel-pivot-tables.md) - Native pivots vs pre-computed summaries
- [references/excel-security-protection.md](references/excel-security-protection.md) - Protection limits, encryption, injection, links
- [references/excel-cloud-automation.md](references/excel-cloud-automation.md) - Office Scripts, Microsoft Graph Excel, xlwings
- [references/excel-accessibility-compliance.md](references/excel-accessibility-compliance.md) - Accessibility, Section 508, EN 301 549 lookup
- [references/extraction-stack.md](references/extraction-stack.md) - Extraction tool candidates by job, for LLM/RAG pipelines
- [data/sources.json](data/sources.json) - Vendor and standards links

**Assets**
- [assets/financial-report.md](assets/financial-report.md) - Financial statement rules: linked statements, sign convention, check cells
- [assets/data-dashboard.md](assets/data-dashboard.md) - Dashboard layout gotchas (merged KPI cards, chart anchoring, hidden data)
- [assets/spreadsheet-model-review-checklist.md](assets/spreadsheet-model-review-checklist.md) - Workbook QA checklist

**Related Skills**
- [../document-pdf/SKILL.md](../document-pdf/SKILL.md) - PDF generation from spreadsheet data
- [../ai-ml-data-science/SKILL.md](../ai-ml-data-science/SKILL.md) - Data analysis and dataframe workflows
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) - Database-to-workbook pipelines

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
