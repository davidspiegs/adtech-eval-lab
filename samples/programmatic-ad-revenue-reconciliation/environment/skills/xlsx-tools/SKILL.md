---
name: xlsx-tools
description: Create multi-sheet Excel workbooks with openpyxl. Use when the task requires structured Excel output with named sheets, headers, and numeric cell values.
---

# Excel Workbook Tools

Use this skill for structured Excel report generation.

## Workflow

1. Create workbook with `openpyxl.Workbook()`.
2. First sheet is `wb.active` — set its title.
3. Additional sheets via `wb.create_sheet("Name")`.
4. Write headers with `ws.append([...])`.
5. Write data rows with `ws.append([...])`.
6. For key-value layouts, write directly: `ws["A1"] = "label"`, `ws["B1"] = value`.
7. Store numbers as numbers, not strings — the QA checker validates cell types.
8. Save with `wb.save(path)`.

## Common Pitfalls

- Sheet names are case-sensitive and must match exactly.
- Append writes to the next empty row.
- Don't convert numbers to strings before writing — keep them as int/float.
- Row 1 is the header row when using append for tables.
