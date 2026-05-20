---
name: csv-tools
description: Parse, validate, join, and aggregate CSV datasets with deterministic outputs. Use for schema checks, grouped metrics, multi-file joins, and stable exports.
---

# CSV Tools

Use this skill for reliable CSV pipelines in reconciliation tasks.

## Checklist

- Validate required columns before calculations.
- Parse numeric fields explicitly (avoid string comparisons on numbers).
- Normalize date formats consistently.
- Sort output rows by stable business keys (deal_id, ad_unit_id).

## Typical Operations

- Group by and aggregate totals (sum impressions across dates).
- Join multiple CSV sources by shared identifiers (deal_id, ad_unit_id).
- Handle multiple input files from a directory (e.g., one billing CSV per SSP).
- Export deterministic output with consistent column order.

## Multi-File Handling

When SSP billing comes in separate files per SSP, iterate the billing directory
and process each file independently. Tag each row with its source SSP for
traceability in the audit output.
