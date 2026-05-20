I need the April 2026 monthly performance audit completed for Pinnacle Digital Media. Save it to `/root/audit_report.xlsx`.

All the input files are under `/root/data`:
- Ad server delivery log: `ad_server_delivery.csv`
- IVT deductions: `ivt_report.csv`
- Deal rate card: `deal_rate_card.csv`
- Ad unit metadata: `ad_unit_metadata.csv`
- SSP billing: `ssp_billing/` folder — three CSVs and one PDF
- Deal contract goals: `deal_contract_goals.csv` (PG deals only)
- SSP request log: `ssp_request_log.csv` (daily ad requests per SSP)
- Historical metrics: `historical_metrics.json` (prior month numbers)
- Reconciliation policy: `reconciliation_policy.md`
- Client email from Sarah: `client_request.md`

We have four SSPs this month: AdFlow Exchange, Magnite, Index Exchange, and Pubmatic. Three sent CSV billing files. Index Exchange sent theirs as a PDF — you'll need to parse it. The metadata file maps each SSP's naming to our canonical ad unit IDs, though SSP naming isn't always perfectly consistent.

Watch out for:
- Some IVT dates are formatted as MM/DD/YYYY instead of ISO — you need to handle both.
- SSP ad unit names sometimes have typos or formatting differences from our metadata. Use approximate matching when needed.
- Some ad units are inactive — don't match billing to inactive units, hold those rows.
- If an SSP row references a deal ID we don't have in the rate card, hold it.
- The rate card has fixed-rate PG deals and floor-rate PMP deals. The policy explains how flagging differs for each.

The workbook needs five sheets. We use these exact names internally:
- Revenue_Reconciliation
- Pacing_And_MakeGoods
- SSP_Yield_Analysis
- Variance_vs_Prior_Month
- Executive_Summary

For Revenue_Reconciliation, use one table starting at row 1 with this header row:
deal_id, ad_unit_id, canonical_name, ssp, delivered_impressions, ivt_impressions, billable_impressions, cpm_usd, expected_revenue_usd, ssp_billed_impressions, ssp_net_revenue_usd, discrepancy_usd, discrepancy_pct, status

One row per matched deal/ad_unit pair from SSP billing, plus one row per held SSP row. If a deal/ad_unit has delivery and a rate card entry but no SSP billing row, you can include it as an unbilled row with 0 for all SSP-side fields, or leave it out — either way is fine. For cpm_usd, use the delivery-weighted effective CPM. Status should be one of: reconciled, reconciled_above_floor, flagged_underbilled, flagged_overbilled, held_unmatched, or unbilled. For held and unbilled rows, put 0 for the publisher-side fields.

For Pacing_And_MakeGoods, use one table starting at row 1 with this header row:
deal_id, ad_unit_id, contracted_impressions, contract_start, contract_end, days_elapsed, days_total, delivered_impressions, projected_eom_impressions, delivery_pct, makegood_impressions, makegood_dollars, status

Only PG (fixed-rate) deals that have entries in deal_contract_goals.csv. Compute days_elapsed from the later of contract start or April 1 through April 30. Project end-of-contract delivery based on current pace. Compute make-good exposure for any deals that won't deliver in full. Status should be complete, ahead, on_track, at_risk, or behind — the policy explains the thresholds.

For SSP_Yield_Analysis, use one table starting at row 1 with this header row:
ssp, ad_requests, impressions_filled, fill_rate, total_net_revenue_usd, ecpm, discrepancy_rate, ranked_position

One row per SSP. Aggregate ad requests from ssp_request_log.csv and billing from the SSP files. Rank SSPs by eCPM descending (1 = highest).

For Variance_vs_Prior_Month, use one table starting at row 1 with this header row:
metric, current_month, prior_month, change_pct, status

Compare current month to historical_metrics.json for these metrics: total_net_revenue_usd, ivt_rate_pct, discrepancy_rate_pct, held_row_count, avg_ecpm_usd. Status is normal (|change| <= 10%), watch (10-25%), or alert (>25%).

For Executive_Summary, use this layout:
A1 = overall_health, B1 = Green or Yellow or Red
A2 = total_makegood_exposure_usd, B2 = sum of makegood_dollars from pacing sheet
A3 = flagged_revenue_at_risk_usd, B3 = sum of absolute discrepancies for flagged deals
Row 5 header = rank, concern, financial_impact_usd, source_sheet
Rows 6-8 = top 3 concerns ranked by financial impact descending

For overall_health: Green if no flagged deals and makegood total under $500, Red if 3+ flagged or makegood over $2000, Yellow otherwise.

Make sure all cost and percentage values are stored as real numbers in the cells, not text.
