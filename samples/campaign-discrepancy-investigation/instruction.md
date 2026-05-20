You are an ad operations analyst at Pinnacle Digital Media. An advertiser (MegaBrand Auto) has filed a formal complaint about their April 2026 campaign. Your job is to investigate each complaint, identify root causes, and produce a structured investigation report.

Read the complaint at `/root/data/advertiser_complaint.md`. It contains three issues that need investigation.

All data files are in `/root/data`:
- `ad_server_delivery.csv` — daily impression delivery from our ad server
- `moat_verification.csv` — third-party verification data from Moat
- `ivt_detailed_report.csv` — invalid traffic breakdown by category
- `placement_specs.csv` — ad placement definitions and benchmarks
- `creative_catalog.csv` — creative specifications
- `creative_assignment_log.csv` — creative-to-placement assignment history
- `domain_delivery.csv` — impression delivery by domain
- `advertiser_exclusion_list.csv` — advertiser's domain and category exclusions
- `iab_taxonomy_v41.json` — IAB content taxonomy version 4.1
- `iab_taxonomy_v42.json` — IAB content taxonomy version 4.2
- `campaign_config.json` — campaign setup and configuration
- `internal_qa_log.csv` — internal QA test impression log

Save your report to `/root/investigation_report.xlsx` with four sheets.

**Sheet 1: `Impression_Reconciliation`** — one table starting at row 1:
category, ad_server_count, moat_count, gap, pct_of_total_gap, explanation

One row for each category contributing to the impression gap between ad server and Moat. Include a final row with category="total" summing the counts. Categories should describe the actual root causes you discover.

**Sheet 2: `Viewability_Analysis`** — two sections:
Section 1 (rows 1-31): daily timeline starting at row 1:
date, placement_id, impressions, viewable_impressions, viewability_pct

Section 2 (starting after the daily data): root cause summary as key-value pairs:
Column A = label, Column B = value
- root_cause_date = the date the problem started
- root_cause_placement = the placement that caused the drop
- root_cause_description = what changed

**Sheet 3: `Domain_Compliance`** — two sections:
Section 1: one table starting at row 1:
domain, category_at_serving, category_current, on_exclusion_list, impressions_before_issue, impressions_after_issue, wasted_spend_usd

One row per offending domain.

Section 2 (starting after domain rows): root cause summary as key-value pairs:
Column A = label, Column B = value
- root_cause = description of why the exclusion failed
- issue_start_date = when the problem started
- total_wasted_impressions = sum of impressions during the violation
- total_wasted_spend_usd = sum of wasted spend

**Sheet 4: `Investigation_Summary`** — key-value layout:
Row 1: A=finding, B=impression_gap, C=[total gap found], D=[total financial impact]
Row 2: A=finding, B=viewability_drop, C=[root cause], D=[date identified]
Row 3: A=finding, B=domain_violation, C=[number of domains], D=[total wasted impressions]
Row 5: A=total_financial_impact_usd, B=[sum of all financial impacts]
Row 7 header: rank, concern, financial_impact_usd, evidence_source
Rows 8-10: top 3 concerns ranked by financial impact

All numerical values should be stored as numbers, not text.
