# Monthly Publisher Performance Audit Policy

## Overview
This document defines Pinnacle Digital Media's monthly performance audit
process covering revenue reconciliation, delivery pacing, SSP yield analysis,
and variance tracking.

## Data Sources

| Source | Purpose |
|---|---|
| `ad_server_delivery.csv` | Daily delivery data — our source of truth for impressions. Contains device and geo breakdowns. Clicks, viewable, and measurable columns are informational. |
| `ivt_report.csv` | IVT deductions from verification vendors. **Note**: some rows may use MM/DD/YYYY date format. Sum all IVT for each deal/ad unit regardless of category. |
| `deal_rate_card.csv` | Contracted CPM rates per deal, ad unit, device, and geo. `rate_type` indicates `fixed` (PG) or `floor` (PMP). Contract dates and currency are informational. |
| `ad_unit_metadata.csv` | Maps canonical ad unit IDs to each SSP's naming. Contains per-SSP name columns and active/inactive status. Format and viewability columns are informational. |
| `ssp_billing/` | Monthly billing from each SSP. May include CSVs and PDFs. Use net-to-publisher revenue. Gross revenue and fee columns are informational. |
| `deal_contract_goals.csv` | Contracted impression volumes for PG deals with start/end dates. |
| `ssp_request_log.csv` | Daily ad request counts per SSP — use for fill rate. |
| `historical_metrics.json` | Prior month headline metrics — use for variance analysis. |

## Part 1: Revenue Reconciliation

### Compute billable impressions
Aggregate delivered impressions from the ad server by deal and ad unit. Deduct
IVT impressions to get billable impressions.

### Compute expected publisher revenue
Each deal/ad unit may have different contracted CPM rates depending on device type
and geography. Compute the effective CPM for each deal/ad unit pair, weighted by
the actual delivery volume across device and geo combinations. Use this effective
CPM with billable impressions to compute expected revenue. Round to 2 decimal places.

### Total expected revenue
Sum expected revenue across all deal/ad unit pairs that have both delivery data
and rate card entries — include pairs no SSP billed for.

### Match SSP billing rows
Resolve SSP ad unit names to canonical IDs using the metadata file. SSP names may
not match exactly — use approximate matching. Only match to active ad units. Hold
rows with unknown deals or unresolvable names.

### Identify discrepancies and apply flagging
Use the tolerance thresholds from the client request. Both a dollar amount and
percentage threshold must be exceeded to flag.

**PMP floor exception**: For PMP deals, the rate card CPM is a floor. If the SSP
reported more than expected, that is normal — do not flag. Only flag PMP deals
when the SSP reports less than expected.

### Adjusted revenue
Sum expected revenue for matched SSP rows only. Excludes held and unbilled pairs.

## Part 2: Delivery Pacing & Make-Goods

For each PG (fixed-rate) deal in the contract goals file:
- Compute days elapsed from the later of contract start or month start through the reporting date (April 30)
- Compute total contract days
- Project end-of-contract delivery based on current pace
- Compute make-good exposure: impressions shortfall times effective CPM
- Classify status:
  - **complete**: delivery >= 100% of contracted
  - **ahead**: delivery > 105% of expected pace
  - **on_track**: delivery within 5% of expected pace
  - **at_risk**: delivery 5-15% behind expected pace
  - **behind**: delivery more than 15% behind expected pace

Expected pace = days_elapsed / days_total as a percentage of contracted.

## Part 3: SSP Yield Analysis

For each SSP:
- Aggregate ad requests from the request log
- Sum filled impressions and net revenue from their billing
- Compute eCPM, fill rate, and discrepancy rate
- Rank SSPs by eCPM descending

## Part 4: Variance vs Prior Month

Compare current month metrics to historical_metrics.json:
- total_net_revenue_usd, ivt_rate_pct, discrepancy_rate_pct, held_row_count, avg_ecpm_usd
- Compute percentage change
- Status: normal (|change| <= 10%), watch (10-25%), alert (>25%)

## Part 5: Executive Summary

Traffic-light overall health based on flagged count and make-good exposure.
Top 3 concerns ranked by financial impact, pulling from all analysis domains.
