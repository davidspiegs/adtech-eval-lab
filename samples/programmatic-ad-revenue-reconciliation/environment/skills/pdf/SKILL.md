---
name: pdf
description: Extract structured data rows from PDF billing statements using pdfplumber. Use when SSP billing is in PDF format instead of CSV.
---

# PDF Processing

Use this skill when source data is in PDF format and you need to extract tabular data.

## Workflow

1. Open PDF with `pdfplumber.open(path)`.
2. Iterate all pages.
3. Extract text from each page.
4. Parse pipe-delimited or space-aligned rows.
5. Filter for data rows (skip headers, separators, footer text).
6. Normalize extracted values to match CSV column expectations.

## Extraction Pattern

Look for rows matching the billing line ID format (e.g., `SSPNAME-LINE-001`).
Split on pipe characters `|` and strip whitespace from each field.
Reject rows with fewer fields than expected or rows that are separator lines.
