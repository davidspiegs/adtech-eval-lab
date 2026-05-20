---
title: "Adtech Evaluation Task Design Review"
subtitle: "Prompt, Dataset, Validator, and Real-World Alignment Assessment"
author: "David S."
date: "May 2026"
---

# Executive Summary

This report reviews two Harbor-format evaluation tasks in the adtech / ad operations domain:

1. **Task 1 — Programmatic Ad Revenue Reconciliation**
2. **Task 2 — Campaign Discrepancy Investigation**

The goal is not to correct the tasks, but to assess whether the model prompts, datasets, expected outputs, and validators are well-designed to test the intended real-world abilities:

- Programmatic publisher revenue reconciliation
- Ad operations investigation of advertiser campaign discrepancies

Overall, both tasks are credible and substantively aligned with real ad ops work. Task 1 is a stronger deterministic reconciliation benchmark because its validator recomputes a full ground truth from raw inputs and checks many business rules. Task 2 is a stronger investigation-style benchmark because it forces root-cause discovery across files, but its validator is more keyword/tolerance based and misses one planted root cause as an individual check.

| Area | Task 1: Revenue Reconciliation | Task 2: Campaign Investigation |
|---|---:|---:|
| Prompt realism | 8.5 / 10 | 8.5 / 10 |
| Dataset realism | 8.0 / 10 | 7.5 / 10 |
| Validator design | 8.0 / 10 | 7.0 / 10 |
| Real-world task alignment | 8.5 / 10 | 8.0 / 10 |
| Overall design quality | 8.2 / 10 | 7.8 / 10 |

Key conclusions:

- **Task 1 tests the right mechanics** for publisher-side revenue operations: IVT deduction, weighted CPMs, fuzzy SSP ad-unit mapping, PG/PMP business rules, pacing, make-good exposure, SSP yield, and executive summary roll-up.
- **Task 2 tests the right investigative pattern** for ad ops discrepancy work: read an escalation, inspect ad server vs verification data, isolate viewability and domain-compliance root causes, and produce an Excel investigation report.
- **Task 1's earlier design weakness** was that the Index Exchange source CSV remained available in the build context. The public version now ships a static PDF-only Index Exchange statement in `/root/data/ssp_billing/`, so the task-visible dataset matches the intended PDF parsing challenge.
- **Task 2's biggest design weakness** is that one planted root cause, internal QA/test traffic, is not individually validated; it is only indirectly covered by the component-sum check.
- Both tasks are somewhat cleaner than real ad ops work: real-world investigations often involve platform exports, missing columns, inconsistent timezones, reissued files, screenshots, email threads, invoice PDFs, and stakeholder ambiguity.

---

# Task 1: Programmatic Ad Revenue Reconciliation

## 1.1 What the Model Prompt Is

The model's main instruction is in:

`samples/programmatic-ad-revenue-reconciliation/instruction.md`

The prompt asks the model to complete an April 2026 monthly performance audit for Pinnacle Digital Media and save the result to:

`/root/audit_report.xlsx`

The prompt lists all input files under `/root/data`:

- `ad_server_delivery.csv`
- `ivt_report.csv`
- `deal_rate_card.csv`
- `ad_unit_metadata.csv`
- `ssp_billing/`
- `deal_contract_goals.csv`
- `ssp_request_log.csv`
- `historical_metrics.json`
- `reconciliation_policy.md`
- `client_request.md`

It also warns the model about several data-quality traps:

- IVT dates may be mixed between ISO and `MM/DD/YYYY`.
- SSP ad unit names may have typos or formatting differences.
- Inactive ad units should not be matched.
- Unknown deal IDs should be held.
- PG and PMP deals have different flagging logic.

The prompt then specifies an exact five-sheet workbook:

1. `Revenue_Reconciliation`
2. `Pacing_And_MakeGoods`
3. `SSP_Yield_Analysis`
4. `Variance_vs_Prior_Month`
5. `Executive_Summary`

Each sheet has explicit headers, expected statuses, and computation requirements.

The model also has two business-context files in the dataset:

- `client_request.md`: an email from Sarah Chen, VP Finance, describing the operational request in business language.
- `reconciliation_policy.md`: a policy document defining the detailed rules for reconciliation, pacing, yield, variance, and summary health.

### Prompt Realism Assessment

The prompt is realistic for a structured internal ad ops / revenue operations task. It is not just a generic "analyze data" prompt; it provides a finance stakeholder, a close deadline, specific source systems, known data-quality warnings, and internal workbook conventions.

The prompt is more explicit than many real-world requests because it gives exact sheet names, headers, status enums, and row placement. In practice, an analyst might get an email plus a prior-month report template rather than such a precise output spec. But for an evaluation task, this explicitness is appropriate: it isolates reasoning and data operations rather than penalizing formatting ambiguity.

## 1.2 What the Task Actually Requires

The model must perform a full monthly publisher revenue audit. The work can be decomposed into five operational domains.

### A. Revenue Reconciliation

The model must:

1. Aggregate ad server delivery by `deal_id` and `ad_unit_id`.
2. Deduct IVT impressions from `ivt_report.csv`.
3. Compute billable impressions.
4. Use the rate card to compute a delivery-weighted effective CPM across device and geo combinations.
5. Compute expected publisher revenue.
6. Parse SSP billing from three CSVs and one PDF.
7. Resolve SSP ad-unit names to canonical ad-unit IDs using exact and fuzzy matching.
8. Hold rows with unknown deals, inactive ad units, or unresolved ad-unit names.
9. Compare SSP net revenue to expected revenue.
10. Apply the discrepancy thresholds:
    - More than `$5` off
    - And more than `3%` off
11. Apply the PMP floor exception:
    - If a PMP floor deal clears above the floor, do not flag it as overbilled.
    - Only flag PMP floor deals when SSP reported revenue is below expected floor revenue.

### B. Pacing and Make-Goods

The model must:

1. Restrict pacing analysis to PG/fixed-rate deals in `deal_contract_goals.csv`.
2. Compute days elapsed and total contract days.
3. Project end-of-contract impressions.
4. Compute make-good exposure for underdelivery.
5. Classify status as `complete`, `ahead`, `on_track`, `at_risk`, or `behind`.

### C. SSP Yield Analysis

The model must:

1. Aggregate requests from `ssp_request_log.csv`.
2. Aggregate billed impressions and net revenue from SSP files.
3. Compute fill rate.
4. Compute eCPM.
5. Compute discrepancy rate.
6. Rank SSPs by eCPM descending.

### D. Variance vs Prior Month

The model must compare current-month metrics to `historical_metrics.json`:

- `total_net_revenue_usd`
- `ivt_rate_pct`
- `discrepancy_rate_pct`
- `held_row_count`
- `avg_ecpm_usd`

It must compute percentage change and classify each as:

- `normal`: absolute change <= 10%
- `watch`: 10-25%
- `alert`: >25%

### E. Executive Summary

The model must compute:

- `overall_health`: Green, Yellow, or Red
- `total_makegood_exposure_usd`
- `flagged_revenue_at_risk_usd`
- Top 3 concerns ranked by financial impact

### Skill Profile Tested

This is a strong test of:

- Multi-file data ingestion
- CSV and PDF parsing
- Fuzzy string matching
- Business-rule execution
- Weighted average calculation
- Financial reconciliation
- Time-window calculations
- Workbook generation
- Roll-up reasoning from detailed rows to executive summary

It is not primarily a natural-language reasoning task; it is a structured, deterministic data operations task with realistic business rules.

## 1.3 Dataset Quality Assessment

### Data Files and Roles

| File | Role | Realism Assessment |
|---|---|---|
| `ad_server_delivery.csv` | Daily delivery by deal, ad unit, device, geo | Realistic grain for publisher ad-server delivery exports. Includes clicks/viewability/measurable fields as extra columns, which mirrors real exports. |
| `ivt_report.csv` | Invalid traffic deductions | Realistic concept. Mixed ISO and `MM/DD/YYYY` dates are a useful data-quality trap. |
| `deal_rate_card.csv` | Deal/ad-unit/device/geo CPMs | Strong realism. Multi-device and multi-geo CPMs force weighted CPM logic. |
| `ad_unit_metadata.csv` | SSP-to-canonical ad unit mapping | Strong realism. Per-SSP aliases, inactive ad units, and naming variations reflect real publisher metadata. |
| `ssp_billing/*.csv` | SSP billing statements | Realistic fields: line ID, month, deal ID, SSP ad-unit name, billed impressions, gross/net revenue, fees. |
| `indexexchange_april_2026.pdf` | PDF billing statement | Realistic in concept. Some partners still send non-CSV statements. |
| `deal_contract_goals.csv` | PG contracted impression goals | Realistic source for pacing and make-good analysis. |
| `ssp_request_log.csv` | Daily ad requests by SSP | Realistic input for fill-rate calculation. |
| `historical_metrics.json` | Prior month KPIs | Useful for variance analysis, though JSON is cleaner than many real-world exports. |
| `client_request.md` | Stakeholder request email | Realistic internal finance/ad ops tasking. |
| `reconciliation_policy.md` | Internal policy | Realistic as a controlled definition of audit rules. |

### Planted Data Challenges

The dataset includes several intentional complications:

1. **Mixed IVT date formats**
   - Some IVT rows use `MM/DD/YYYY`.
   - Other rows use ISO `YYYY-MM-DD`.
   - This tests robust date parsing.

2. **SSP naming variation**
   - Example: `MAG_Lifstyle_Interstitial` has a typo.
   - Example: `PDM Travel Banner 728` uses spaces instead of canonical underscores.
   - Example: `IX Sports PreRoll` differs from `IX_Sports_PreRoll`.
   - This tests fuzzy matching.

3. **Inactive ad units**
   - `AU-115` and `AU-116` are inactive.
   - A row referencing an inactive ad unit must be held.

4. **Unknown deals**
   - Rows like `DEAL-9999`, `DEAL-8888`, and `DEAL-7777` appear in SSP billing.
   - These must be held rather than forced into the reconciliation.

5. **PG vs PMP business rules**
   - `rate_type = fixed` means exact CPM.
   - `rate_type = floor` means a PMP floor, so above-floor clearing should not be flagged as overbilling.

6. **PDF billing**
   - Index Exchange is presented to the agent as a PDF in `/root/data/ssp_billing/`.
   - This tests table extraction from non-CSV billing statements.

### Dataset Strengths

The dataset is strong because it captures several real ad ops pain points at once:

- Different source systems with different grains.
- Multiple SSPs.
- Billing rows that do not cleanly match publisher metadata.
- Deal-level and ad-unit-level joins.
- Business rules that depend on deal type.
- Month-over-month variance.
- Pacing and make-good exposure.
- Executive summary roll-up from underlying detail.

This is a credible synthetic version of what a publisher revenue operations analyst would do near month-end close.

### Dataset Weaknesses

The dataset is still cleaner and more constrained than reality:

1. **The PDF is too structured**
   - It is pipe-delimited text embedded in a PDF.
   - Real partner PDFs often have wrapped rows, page headers, merged cells, footnotes, or scanned content.

2. **PDF parsing remains intentionally simplified**
   - The public task now copies static files directly into `/root/data`.
   - The Index Exchange billing file is visible only as a PDF in the task data.
   - The PDF itself is still pipe-delimited text, so it tests extraction mechanics but not the hardest class of scanned or irregular partner invoices.

3. **No duplicate or revised billing files**
   - Real SSP reconciliation often involves revised statements, duplicate line items, late adjustments, or "final" vs "preliminary" exports.

4. **No invoice-level artifact**
   - The task has billing statements but no final invoice or GL export.

5. **No timezone or reporting-window mismatch**
   - Real revenue reconciliation often includes time-zone boundary issues, late-arriving events, or reporting cutoffs.

6. **No currency conversion**
   - All data is USD. Real international publishers may need FX handling.

7. **No supply-path hierarchy**
   - Real programmatic reconciliation may involve SSP, exchange, buyer seat, deal, placement, line item, and ad-unit hierarchies.

Overall dataset quality is high for an evaluation task, but it intentionally compresses real-world complexity into a clean, deterministic benchmark.

## 1.4 Validator Deep Dive

The verifier lives at:

`samples/programmatic-ad-revenue-reconciliation/tests/test_outputs.py`

It uses `openpyxl` to read `/root/audit_report.xlsx` and recomputes ground truth from the task data. It is a deterministic verifier with 15 tests.

Important implementation details:

- It reads most data from `/root/data`.
- It reads SSP billing files from `/root/data/ssp_billing/`, including the static Index Exchange PDF.
- It uses `rapidfuzz` with a fuzzy threshold of 80.
- It has flexible sheet lookup: exact match, normalized match, then fuzzy fallback.
- It has flexible header lookup via normalized key matching.

### Ground Truth Computation

The verifier recomputes:

- Ad server delivery by deal/ad unit/device/geo.
- IVT by deal/ad unit.
- Weighted average CPM from delivery-weighted device/geo rate-card rows.
- Expected revenue.
- SSP billing row matching.
- Held rows.
- Flagged discrepancy IDs.
- PG pacing and make-good exposure.
- SSP yield metrics.
- Month-over-month variance.
- Executive summary health and risk totals.

This is the right approach: it does not rely on hardcoded expected output rows, and it validates the same business logic the model is supposed to implement.

### Validator Tests

#### TestWorkbookStructure

**`test_workbook_structure`**

Checks:

- `/root/audit_report.xlsx` exists.
- Workbook has at least 5 sheets.
- Required sheets are present:
  - `Revenue_Reconciliation`
  - `Pacing_And_MakeGoods`
  - `SSP_Yield_Analysis`
  - `Variance_vs_Prior_Month`
  - `Executive_Summary`

Assessment:

- Good structural test.
- Allows extra sheets, which is reasonable.
- Fuzzy sheet lookup makes the test robust to minor naming variation, though the prompt asks for exact names.

#### TestReconciliation

**`test_recon_row_count`**

Checks:

- Revenue reconciliation row count equals matched rows + held rows, with tolerance for up to 5 optional unbilled rows.

Assessment:

- Good because the prompt explicitly allows optional unbilled rows.
- The tolerance prevents over-penalizing a valid choice.

**`test_recon_flagged_count`**

Checks:

- Number of flagged rows is at least the expected flagged count.
- Allows up to 4 extra flagged rows for optional unbilled or conservative flagging.

Assessment:

- Good for catching models that miss true discrepancies.
- Slightly lenient because extra false-positive flags are tolerated.

**`test_recon_held_and_zeroed`**

Checks:

- Exact count of `held_unmatched` rows.
- Held rows have `delivered_impressions = 0`.

Assessment:

- Strong test of hold-row logic.
- Realistic because unresolved rows should not be forced into publisher-side revenue.

**`test_recon_total_expected_revenue`**

Checks:

- Sum of `expected_revenue_usd` is close either to:
  - Total expected revenue across all valid delivery/rate-card pairs, or
  - Adjusted expected revenue for matched SSP rows only.
- Tolerance is less than `$1`.

Assessment:

- Good because the prompt allows inclusion or exclusion of unbilled rows.
- Strong numerical check.

**`test_recon_billable_spot_check`**

Checks:

- For up to 5 matched deal/ad-unit pairs, `billable_impressions = delivered - IVT`.

Assessment:

- Good targeted check.
- Only spot-checks up to 5 rows, so it may miss row-specific errors outside the sample.

**`test_recon_flagged_deal_ids`**

Checks:

- All expected flagged deal/ad-unit pairs are present among submitted flagged rows.

Assessment:

- Very important test.
- Directly checks whether the model identified the correct revenue-risk rows.

**`test_recon_valid_statuses`**

Checks:

- Every row has a valid status.
- Accepted statuses:
  - `reconciled`
  - `reconciled_above_floor`
  - `flagged_underbilled`
  - `flagged_overbilled`
  - `held_unmatched`
  - `flagged_unbilled`
  - `unbilled`

Assessment:

- Good output-quality check.
- Allows `flagged_unbilled`, which is not in the prompt's status list, but this leniency is reasonable if an agent explicitly flags unbilled exposure.

#### TestPacing

**`test_pacing_structure`**

Checks:

- Row count matches the ground-truth pacing rows.
- Every status is valid.
- At least one row is `behind` or `at_risk`.

Assessment:

- Good structural and semantic check.
- Ensures the model did not omit make-good risk.

**`test_pacing_values`**

Checks:

- `delivery_pct` is between 0 and 200.
- Any row marked `behind` has positive `makegood_dollars`.
- Contracted impressions match source data.

Assessment:

- Good sanity check, but not exhaustive.
- Does not verify every projected EOM or make-good dollar calculation exactly.

#### TestYield

**`test_yield_structure_and_ranking`**

Checks:

- Exactly 4 SSP rows.
- Rankings are 1 through 4.
- Rankings correspond to eCPM descending.
- Ad requests are positive.

Assessment:

- Strong test of yield-table structure and ranking.
- Realistic because SSP eCPM ranking is a common ops/finance view.

**`test_yield_values`**

Checks:

- eCPM is in a reasonable range: 1 to 30.
- Fill rate is valid.
- Total net revenue is within 5% of SSP total.

Assessment:

- Good aggregate validation.
- Somewhat loose on individual SSP values.

#### TestVarianceAndSummary

**`test_variance_structure`**

Checks:

- Exactly 5 variance rows.
- Required metrics are present.
- Status values are valid.
- Prior-month values match `historical_metrics.json`.

Assessment:

- Good test of source-file use and metric coverage.

**`test_variance_change_pct_revenue`**

Checks:

- `change_pct` for `total_net_revenue_usd` is computed as a percentage, not a fraction.
- Tolerance is within 1 percentage point.

Assessment:

- Very important because this was a known model failure mode.
- It tests a subtle but common spreadsheet/reporting error.

**`test_executive_summary`**

Checks:

- `overall_health` is Green/Yellow/Red.
- Health matches verifier's computed health.
- Make-good exposure is within 5% or `$1`.
- At least one top concern is listed.
- Each top concern has a `source_sheet`.

Assessment:

- Good high-level business-output validation.
- Does not validate all top 3 concerns exactly, but checks enough to ensure a meaningful summary exists.

## 1.5 Alignment Assessment: Does Task 1 Test the Right Thing?

### What Task 1 Tests Well

Task 1 is well-designed for testing whether a model can perform a real programmatic revenue reconciliation workflow.

It tests:

- Understanding the difference between ad server delivery and SSP billing.
- Applying IVT deductions.
- Computing billable impressions.
- Joining rate-card data at a more granular device/geo level.
- Computing weighted CPMs.
- Handling PG vs PMP deal semantics.
- Resolving messy SSP names.
- Holding unresolved billing rows instead of forcing bad matches.
- Parsing a PDF billing statement.
- Building a multi-sheet Excel workbook.
- Rolling detailed findings into executive-level health and concerns.

These are all real skills for ad ops / revenue operations work.

### Validator Design Quality

The validator is strong because it recomputes ground truth from raw data rather than comparing against a static workbook. It tests both structure and business logic. It also includes enough tolerance to avoid penalizing optional unbilled-row choices.

The strongest validator checks are:

- Correct flagged deal/ad-unit IDs.
- Correct held row count.
- Correct billable impressions spot checks.
- Correct total expected revenue.
- Correct variance percentage calculation.
- Correct executive health.

### Main Gaps

1. **PDF parsing realism is limited**
   - The public version removes the task-visible source CSV and uses the static PDF.
   - The PDF is still cleanly structured, so future variants could add wrapped rows, continuation pages, or OCR-like artifacts.

2. **Pacing calculations are not exhaustively checked**
   - Contracted impressions are checked.
   - Behind rows must have makegood dollars.
   - But exact projected EOM and make-good dollar calculations are not checked row-by-row.

3. **Yield values are mostly aggregate/range checked**
   - Total revenue is checked within 5%.
   - eCPM range and rank are checked.
   - Individual SSP fill rate and discrepancy rate are not tightly validated.

4. **False-positive flags are tolerated**
   - The validator requires all expected flagged IDs but allows some extras.
   - This is reasonable for robustness but means an overzealous model may still pass.

5. **Real-world reconciliation context is simplified**
   - No revised invoices.
   - No currency conversion.
   - No timezone close-window issue.
   - No buyer-seat or line-item hierarchy.
   - No source-system API pulls.

### Binary Scoring Assessment

Task 1 appears intended as a binary-scored hard task. That is defensible because monthly reconciliation is operationally deterministic: either the workbook is materially correct or it is not.

However, the task has many independent subskills. A partial score could reveal more nuanced capability differences. For example, a model could correctly reconcile revenue but fail the executive summary, or parse the PDF but miss make-good logic. Binary scoring is good for demonstrating end-to-end operational reliability, but partial scoring would be better for diagnosing which subskills failed.

### Final Task 1 Assessment

Task 1 is a strong benchmark for programmatic ad revenue reconciliation. The task is realistic, the output is operationally plausible, and the validator mostly tests the right things.

The largest remaining design issue is not the business logic; it is that the PDF statement is cleaner than many real partner invoices, which makes the extraction component more controlled than production work.

---

# Task 2: Campaign Discrepancy Investigation

## 2.1 What the Model Prompt Is

The model's main instruction is in:

`samples/campaign-discrepancy-investigation/instruction.md`

The model is told:

> You are an ad operations analyst at Pinnacle Digital Media. An advertiser (MegaBrand Auto) has filed a formal complaint about their April 2026 campaign. Your job is to investigate each complaint, identify root causes, and produce a structured investigation report.

The model must read:

`/root/data/advertiser_complaint.md`

The prompt lists all files under `/root/data`:

- `ad_server_delivery.csv`
- `moat_verification.csv`
- `ivt_detailed_report.csv`
- `placement_specs.csv`
- `creative_catalog.csv`
- `creative_assignment_log.csv`
- `domain_delivery.csv`
- `advertiser_exclusion_list.csv`
- `iab_taxonomy_v41.json`
- `iab_taxonomy_v42.json`
- `campaign_config.json`
- `internal_qa_log.csv`

The model must save:

`/root/investigation_report.xlsx`

The workbook must have four sheets:

1. `Impression_Reconciliation`
2. `Viewability_Analysis`
3. `Domain_Compliance`
4. `Investigation_Summary`

The prompt specifies sheet layouts but does not explicitly reveal the planted root causes. The model must discover them from the data.

### Complaint Email

The complaint comes from James Whitfield, Digital Media Director at MegaBrand Auto, CC'ing an agency contact at Omnicom Media Group.

It raises three issues:

1. **Impression Count Discrepancy**
   - Ad server shows about 4 million impressions.
   - Moat shows about 2 million.
   - Advertiser demands a breakdown of the gap.

2. **Viewability Collapse**
   - First 20 days: 68-72% viewability.
   - Last 10 days: around 30%.
   - Contractual target is 65%.

3. **Brand Safety Violation**
   - Ads ran on gambling-related domains:
     - `gamblingreviews.com`
     - `pokerstrategyhub.com`
     - `sportsodds.net`
   - Advertiser excludes IAB category `IAB9-27` (Gambling).

### Prompt Realism Assessment

The complaint email is strong and realistic. It has:

- A senior advertiser contact.
- A named agency CC.
- A specific campaign/deal ID.
- Specific vendor reference: Moat.
- A billing approval consequence.
- A viewability contractual threshold.
- Specific offending domains.
- A deadline tied to a CMO call.

This reads like a real advertiser escalation. It is somewhat more organized than many real escalations, but that is appropriate for an eval where the model must map the complaint to data sources.

## 2.2 What the Task Actually Requires

Task 2 requires a forensic ad ops investigation across three complaint areas.

### A. Impression Gap Reconciliation

The model must compare ad server delivery to Moat verification and decompose the gap into root-cause categories.

There are four planted gap components:

1. **IVT filtered by Moat**
   - GIVT and SIVT are counted in ad server impressions but filtered by Moat.

2. **Non-viewable impressions**
   - Moat count method is `viewable_completions`.
   - Ad server count method is `ad_request_served`.
   - This is the largest and most important component.

3. **Timezone boundary**
   - Ad server uses US/Eastern.
   - Moat uses UTC.
   - April 30 evening impressions are shifted out of the April UTC reporting window.

4. **Internal QA/test traffic**
   - Ad server counts QA/test impressions.
   - Moat filters them.
   - QA activity is visible in `internal_qa_log.csv` and `test_flag_impressions`.

### B. Viewability Collapse Investigation

The model must identify:

- The date the viewability issue started: `2026-04-21`.
- The placement responsible: `PL-010`.
- The cause: a below-fold sticky placement with low viewability and high traffic allocation.

Relevant evidence:

- `ad_server_delivery.csv` shows the traffic and viewability trend.
- `placement_specs.csv` identifies `PL-010` as below-fold with an 18% benchmark.
- `creative_assignment_log.csv` shows the placement launch/assignment on April 21.

### C. Domain Compliance Investigation

The model must identify:

- Three offending domains.
- Their previous vs current IAB categories.
- Whether they are on the exclusion list via category.
- Impressions before and after issue start.
- Wasted spend.
- Root cause: domains were recategorized from `IAB9` to `IAB9-27` in taxonomy v4.2 on April 15, but the system effectively allowed delivery based on stale taxonomy/category handling.

### Skill Profile Tested

Task 2 tests:

- Reading a business complaint and translating it into data questions.
- Reconciling ad server vs third-party verification data.
- Understanding measurement methodology differences.
- Detecting root causes from configuration settings.
- Identifying a time-series anomaly.
- Connecting placement metadata to performance collapse.
- Checking domain delivery against category exclusions.
- Comparing taxonomy versions.
- Quantifying financial impact.
- Producing a structured investigation report.

This is closer to an ad ops "investigation" task than Task 1, which is more deterministic reconciliation.

## 2.3 Dataset Quality Assessment

The public dataset is static and task-visible under:

`samples/campaign-discrepancy-investigation/environment/data/`

It creates a synthetic April 2026 campaign for deal:

`DEAL-MB-2026Q2`

### Generated Data Files

| File | Role | Realism Assessment |
|---|---|---|
| `advertiser_complaint.md` | Escalation email | Very realistic tone and content. |
| `ad_server_delivery.csv` | Daily delivery by date, placement, device, geo | Realistic schema and dimensions. |
| `moat_verification.csv` | Verification counts by UTC date and placement | Realistic high-level verification export. |
| `ivt_detailed_report.csv` | GIVT/SIVT detail | Realistic IVT category breakdown. |
| `placement_specs.csv` | Placement metadata and viewability benchmarks | Realistic operational metadata. |
| `creative_catalog.csv` | Creative definitions | Realistic but mostly unused by validator. |
| `creative_assignment_log.csv` | Placement/creative assignment changes | Useful evidence for viewability root cause. |
| `domain_delivery.csv` | Impressions/clicks/spend by domain/date | Realistic domain compliance input. |
| `advertiser_exclusion_list.csv` | Category and domain exclusions | Realistic brand safety artifact. |
| `iab_taxonomy_v41.json` | Prior taxonomy version | Strong root-cause artifact. |
| `iab_taxonomy_v42.json` | Current taxonomy version | Strong root-cause artifact. |
| `campaign_config.json` | Ad server and verification settings | Useful and realistic abstraction of setup/config. |
| `internal_qa_log.csv` | QA test impressions | Realistic concept, though cleaner than real ops logs. |

### Planted Root Causes

#### Root Cause 1: IVT filtered by Moat

Real-world occurrence:

- Very realistic.
- Ad servers often report raw delivery while verification vendors deduct invalid traffic.

Magnitude realism:

- The build script uses approximately 4.8-5.8% GIVT and 3.8-4.8% SIVT.
- Combined IVT around 9% is high but plausible for broad display inventory.

Discovery mechanism:

- Sum `givt_impressions` and `sivt_impressions` in `moat_verification.csv` or `ivt_detailed_report.csv`.
- This mirrors real verification reconciliation.

#### Root Cause 2: Non-viewable impressions

Real-world occurrence:

- Very realistic.
- Comparing ad server served impressions to Moat viewable completions is a classic apples-to-oranges discrepancy.

Magnitude realism:

- The non-viewable component is intentionally large.
- This is plausible if the advertiser is comparing served delivery to viewable-only vendor counts.

Discovery mechanism:

- Read `campaign_config.json`.
- Notice:
  - Ad server count method: `ad_request_served`
  - Moat count method: `viewable_completions`
- Compare `verified_impressions` to `viewable_impressions`.

This is the best-designed part of Task 2 because it tests whether the model can connect a configuration setting to a column-level calculation.

#### Root Cause 3: Timezone boundary

Real-world occurrence:

- Realistic.
- Month-end time-zone cutoffs are a known cause of ad server vs verification discrepancies.

Magnitude realism:

- The script shifts 55-70% of April 30 impressions.
- This is exaggerated for US/Eastern vs UTC. A 4-5 hour offset would usually shift closer to 20-25% of a day's impressions, depending on traffic distribution.

Discovery mechanism:

- Notice timezones in `campaign_config.json`.
- Inspect April 30 differences between expected verified and actual verified.

The mechanism is realistic, but the magnitude is larger than expected.

#### Root Cause 4: Internal QA/test traffic

Real-world occurrence:

- Realistic.
- QA bots and manual testing can generate ad server impressions that verification vendors filter.

Magnitude realism:

- The generated QA volume is plausible for a synthetic campaign.

Discovery mechanism:

- Compare `internal_qa_log.csv` with `test_flag_impressions` in Moat.
- This is realistic, though in real organizations QA logs may not be neatly available.

#### Root Cause 5: Below-fold placement launch causing viewability collapse

Real-world occurrence:

- Very realistic.
- A newly launched low-viewability placement can collapse blended campaign viewability.

Magnitude realism:

- Pre-change viewability around 68-72% and post-change around 30% is plausible for a severe operational mistake.
- However, the traffic behavior is somewhat artificial: existing above-fold placements drop from healthy volume to very low volume while PL-010 gets 80-95K impressions/day.
- In reality, new inventory often adds volume or changes allocation less abruptly; complete cannibalization at this level is less common.

Discovery mechanism:

- Aggregate daily viewability.
- Identify April 21 change.
- Inspect placement-level delivery and `placement_specs.csv`.
- Confirm PL-010 is below-fold and low-viewability.

This is a realistic ad ops investigation workflow.

#### Root Cause 6: IAB taxonomy recategorization causing brand safety violations

Real-world occurrence:

- Realistic and sophisticated.
- Taxonomy/category mapping changes and stale classification caches can cause exclusion failures.

Magnitude realism:

- Three domains with several hundred thousand total impressions and a few thousand dollars of wasted spend is plausible.

Dataset realism issue:

- The offending domains jump from 300-900 impressions/day before April 15 to 5,000-9,000 impressions/day after April 15.
- A taxonomy recategorization should not itself cause delivery volume to jump. It should change whether the same delivery is classified as compliant or non-compliant.

Discovery mechanism:

- Compare `iab_taxonomy_v41.json` to `iab_taxonomy_v42.json`.
- Check `advertiser_exclusion_list.csv`.
- Sum post-April-15 delivery in `domain_delivery.csv`.

The mechanism is realistic, but the volume pattern is less realistic.

### Dataset Strengths

Task 2's dataset is strong because:

- It provides multiple independent evidence sources.
- It includes a realistic advertiser complaint.
- It forces models to investigate rather than merely transform data.
- It includes both numerical and configuration-based root causes.
- It requires understanding measurement methodology, not just summing columns.
- It covers delivery, viewability, IVT, QA, taxonomy, and brand safety.

### Dataset Weaknesses

Main weaknesses:

1. **Timezone magnitude is exaggerated**
   - 55-70% of April 30 shifting to May 1 is too high for Eastern-to-UTC.

2. **Domain delivery jump is unrealistic**
   - Taxonomy changes classification, not traffic volume.

3. **Viewability traffic shift is extreme**
   - PL-010 appears and captures overwhelming traffic while above-fold placements collapse.

4. **QA evidence is too clean**
   - Real QA/test traffic evidence may require logs, IP ranges, internal tickets, or tag firing records.

5. **No raw log-level data**
   - Real discrepancy investigations often require impression-level or event-level logs.

6. **No invoice or billing artifact**
   - The complaint references invoice approval, but there is no invoice file to reconcile.

7. **No click/conversion discrepancy**
   - Real complaints often include clicks, conversions, or CTR alongside impression discrepancies.

8. **No platform screenshots or vendor exports**
   - Real Moat/IAS/DV investigations often involve portal exports and screenshots.

Overall dataset quality is good, with realistic root-cause categories but some exaggerated synthetic magnitudes.

## 2.4 Validator Deep Dive

The verifier lives at:

`samples/campaign-discrepancy-investigation/tests/test_outputs.py`

It uses partial scoring: reward equals passed tests divided by total tests.

It reads `/root/investigation_report.xlsx`, computes ground truth from `/root/data`, and checks for required sheets, numerical components, and root-cause evidence.

Important implementation details:

- It uses flexible sheet lookup.
- It uses flexible header lookup.
- It uses keyword matching to identify category rows.
- It uses numerical tolerance bands rather than exact matches.

### Ground Truth Computation

The verifier computes:

- Total ad server impressions.
- Total Moat verified impressions.
- Total Moat viewable impressions.
- Total gap: ad server impressions minus Moat viewable impressions.
- IVT total from GIVT + SIVT.
- QA/test total from `test_flag_impressions`.
- Timezone total as positive residual after IVT and QA by day.
- Non-viewable total as Moat verified minus Moat viewable.
- Pre- and post-change viewability.
- Post-taxonomy wasted domain impressions and spend.

### Validator Tests

#### TestStructure

**`test_workbook_sheets`**

Checks:

- `/root/investigation_report.xlsx` exists.
- Required sheets are present:
  - `Impression_Reconciliation`
  - `Viewability_Analysis`
  - `Domain_Compliance`
  - `Investigation_Summary`

Assessment:

- Good basic structure test.
- Allows flexible sheet name matching.

#### TestImpressionRecon

**`test_total_gap`**

Checks:

- Finds a total row in `Impression_Reconciliation`.
- Reported `gap` is within 10% of ground-truth total gap.

Assessment:

- Good high-level reconciliation check.
- It ensures the model computed the overall discrepancy.

**`test_ivt_component`**

Checks:

- Finds rows whose category includes keywords like `ivt`, `invalid`, or `fraud`.
- Sums their gaps.
- Requires IVT gap within 15% of ground truth, with a minimum tolerance of 5,000 impressions.

Assessment:

- Good test of IVT identification and quantification.
- Keyword matching is pragmatic but can be brittle if a model uses unexpected labels.

**`test_non_viewable_component`**

Checks:

- Finds category rows containing viewability-related keywords.
- Requires non-viewable component within 15% of ground truth, with minimum tolerance of 10,000 impressions.

Assessment:

- This is the most important validator in Task 2.
- It tests the key reasoning step: recognizing that Moat viewable completions are not the same as Moat verified impressions or ad server served impressions.
- This is well-aligned with the intended headroom signal.

**`test_timezone_component`**

Checks:

- Finds timezone-related rows using category or explanation keywords:
  - `timezone`
  - `utc`
  - `eastern`
  - `boundary`
  - `month_end`
  - `reporting_period`
- Requires timezone gap within 25% of ground truth, with minimum tolerance of 5,000 impressions.

Assessment:

- Good conceptual test.
- Higher tolerance is appropriate because timezone residual calculation may vary.
- Keyword matching could allow a vague explanation to pass if the number is close.

**`test_components_sum`**

Checks:

- Non-total component rows sum to within 5% of total gap, with minimum tolerance of 10,000 impressions.

Assessment:

- Important check because it forces comprehensive reconciliation.
- This is the only place where the untested QA/test component can indirectly matter.

#### TestViewability

**`test_drop_date_identified`**

Checks:

- Finds `root_cause_date` in the `Viewability_Analysis` sheet.
- Requires a value matching April 21, 2026.

Assessment:

- Good direct root-cause test.

**`test_placement_identified`**

Checks:

- Finds `root_cause_placement` or `root_cause_description`.
- Requires keywords like `PL-010`, `sticky`, `below_fold`, `below-fold`, `below fold`, or `320x50`.

Assessment:

- Good test of placement-level root cause.
- Keyword-based but appropriate for a narrative field.

**`test_daily_trend`**

Checks:

- Reads daily rows from `Viewability_Analysis`.
- Aggregates impressions and viewable impressions by date.
- Requires at least 20 daily rows.
- Requires pre-April-21 viewability to exceed post-April-21 viewability by more than 10 percentage points.

Assessment:

- Strong trend-validation test.
- It checks that the output contains data supporting the claimed drop.

#### TestDomainCompliance

**`test_offending_domains`**

Checks:

- All three offending domains are present:
  - `gamblingreviews.com`
  - `pokerstrategyhub.com`
  - `sportsodds.net`

Assessment:

- Good direct test.

**`test_wasted_impressions`**

Checks:

- Uses `total_wasted_impressions` if present.
- Otherwise sums `impressions_after_issue` or `impressions_after_change`.
- Requires within 15% of ground truth, with minimum tolerance of 5,000.

Assessment:

- Good numerical compliance test.
- Does not strongly verify per-domain values.

**`test_taxonomy_cause`**

Checks:

- Finds `root_cause` or `taxonomy_update_date`.
- Requires taxonomy-related keywords:
  - `taxonomy`
  - `recategor`
  - `IAB`
  - `v4.2`
  - `2026-04-15`
  - `april 15`

Assessment:

- Good root-cause text validation.
- Does not require a precise explanation of stale taxonomy/cache behavior.

#### TestSummary

**`test_summary_structure`**

Checks:

- `Investigation_Summary` contains text referencing all three complaint areas:
  - Impression gap/discrepancy
  - Viewability drop/collapse
  - Domain/brand/gambling/exclusion

Assessment:

- Good coverage test.
- Keyword-based and therefore lenient.

**`test_financial_impact`**

Checks:

- Finds a total financial impact label.
- Requires value to be:
  - Greater than `$1,000`
  - Less than `$500,000`

Assessment:

- Very loose.
- It ensures a financial impact exists but does not validate exact calculation.

## 2.5 Alignment Assessment: Does Task 2 Test the Right Thing?

### What Task 2 Tests Well

Task 2 is well-designed as a root-cause investigation benchmark.

It tests:

- Whether the model can convert an advertiser complaint into an investigation plan.
- Whether the model can reconcile ad server and verification vendor data.
- Whether the model recognizes methodology mismatches.
- Whether the model can identify a temporal break in performance.
- Whether the model can isolate a placement-level cause.
- Whether the model can compare taxonomy versions to diagnose brand safety failures.
- Whether the model can quantify impact in a structured workbook.

The strongest part of the task is the non-viewable impressions component. It requires the model to read `campaign_config.json`, understand that Moat is configured for `viewable_completions`, and then compute the right gap component from the Moat data. This tests real ad ops reasoning rather than simple arithmetic.

### Validator Design Quality

The Task 2 validator is appropriate for an investigation task because it uses partial scoring and tolerance bands. Real investigations can have multiple valid phrasings and slightly different categorization choices.

The strongest checks are:

- Non-viewable component identified and quantified.
- Viewability drop date and placement identified.
- Offending domains listed.
- Taxonomy cause identified.
- Components sum to total gap.

### Main Gaps

1. **QA/test traffic is not individually tested**
   - The dataset plants QA/test traffic as one of four impression-gap components.
   - The validator computes QA but does not have a `test_qa_component`.
   - A model can omit QA as a named root cause and still pass if the total components sum correctly via residual or another category.

2. **Financial impact validation is weak**
   - The summary test only requires total financial impact between `$1,000` and `$500,000`.
   - It does not check whether the model correctly computes impression-gap cost, domain wasted spend, or total impact.

3. **Per-domain compliance fields are under-validated**
   - The test verifies domains and total wasted impressions.
   - It does not strongly validate:
     - `category_at_serving`
     - `category_current`
     - `on_exclusion_list`
     - `impressions_before_issue`
     - per-domain wasted spend

4. **Keyword matching can produce false positives/negatives**
   - A correct model using unusual labels may fail.
   - A weak model using the right keywords and approximate numbers may pass.

5. **Narrative quality is not deeply assessed**
   - The complaint asks for root cause identification, supporting evidence, and explanation.
   - The validator mostly checks numeric values and keyword presence.

6. **The validator does not check use of all relevant evidence**
   - It does not require the model to cite `creative_assignment_log.csv`.
   - It does not verify `placement_specs.csv` values.
   - It does not verify `advertiser_exclusion_list.csv` rows directly.
   - It does not verify `campaign_config.json` beyond the effect reflected in non-viewable calculations.

### Partial Scoring Assessment

Partial scoring is the right choice for Task 2. Investigation tasks are naturally multi-part, and a model can partially solve the case while missing a root cause. The partial score makes it possible to identify capability gradients across models.

This is especially appropriate because:

- The task has several independent evidence chains.
- Some findings are easier than others.
- The non-viewable component is a known discriminator.
- Total failure would hide useful subskill information.

### Final Task 2 Assessment

Task 2 is a strong evaluation of ad ops investigation ability. It captures the structure of a real advertiser escalation and requires the model to synthesize multiple files into a structured workbook.

Its main weakness is validator coverage: it validates the biggest and most important findings, but not every planted root cause and not the quality of the explanatory evidence. The dataset is realistic in concept but includes a few synthetic exaggerations in magnitude and traffic behavior.

---

# Cross-Task Assessment

## Prompt Design Comparison

| Dimension | Task 1 | Task 2 |
|---|---|---|
| Prompt style | Operational audit specification | Advertiser escalation investigation |
| Output format | Highly prescribed 5-sheet workbook | Prescribed 4-sheet investigation report |
| Ambiguity level | Low to medium | Medium |
| Main challenge | Deterministic business-rule execution | Root-cause discovery and evidence synthesis |
| Real-world analogue | Monthly revenue ops close process | Ad ops escalation / discrepancy investigation |

Task 1 is more "process execution." Task 2 is more "forensic reasoning."

Both prompts are appropriate for their intended capability, but they test different model strengths:

- Task 1 tests whether a model can reliably run a complex operational workflow.
- Task 2 tests whether a model can infer why something went wrong.

## Validator Design Comparison

| Dimension | Task 1 | Task 2 |
|---|---|---|
| Scoring style | Binary / deterministic style | Partial scoring |
| Ground truth | Full recomputation from raw data | Full recomputation plus keyword/tolerance checks |
| Numeric strictness | Moderate to high | Moderate |
| Text/narrative validation | Low | Medium but keyword-based |
| Best validator feature | Flagged IDs and held-row logic | Non-viewable component test |
| Biggest validator gap | PDF parse can be bypassed; pacing not exhaustive | QA not individually tested; weak financial-impact check |

Task 1's validator is stronger as a deterministic business-rule validator. Task 2's validator is necessarily more flexible, but that flexibility creates some blind spots.

## Dataset Design Comparison

| Dimension | Task 1 | Task 2 |
|---|---|---|
| Data realism | Strong for structured revenue ops exports | Strong for investigation artifacts |
| Messiness | Naming variation, mixed dates, PDF, inactive units | Root-cause breadcrumbs across configs, taxonomy, domain logs |
| Synthetic artifacts | Clean files, regular structures, possible `/tmp` leakage | Exaggerated timezone shift, unrealistic domain volume jump |
| Breadth | Revenue, IVT, rate cards, pacing, yield, variance | Delivery, verification, IVT, QA, viewability, brand safety |
| Depth | Strong financial math and joins | Strong root-cause synthesis |

Both datasets are high-quality for synthetic evaluations. Task 1 is cleaner but mechanically richer. Task 2 is more investigative but has a few magnitude realism issues.

## Do These Tasks Test Real Ad Ops Ability?

Yes, with caveats.

### Task 1: Real-World Alignment

Task 1 is highly aligned with publisher revenue operations. A model that passes it must demonstrate many skills a real analyst needs:

- Matching ad-server delivery to SSP billing.
- Applying IVT deductions.
- Handling messy partner naming.
- Understanding fixed CPM vs floor CPM.
- Calculating make-good exposure.
- Producing an executive finance summary.

This is a good test of whether a model can support a real monthly close process.

The main caveat is that real revenue reconciliation often includes more ambiguity, more file-format messiness, and more back-and-forth with stakeholders.

### Task 2: Real-World Alignment

Task 2 is well-aligned with an advertiser discrepancy investigation. A model that performs well must:

- Understand advertiser complaint language.
- Compare first-party and third-party measurement systems.
- Identify viewability collapse by placement/date.
- Investigate brand safety against exclusion rules.
- Quantify financial exposure.

This is a good test of whether a model can act like an ad ops analyst investigating a campaign issue.

The main caveat is that the validator mostly rewards finding the expected root causes and approximate numbers, not the full quality of an analyst's supporting explanation.

## Are the Validators Testing the Right Things?

Mostly yes.

### Strong Validator Coverage

The validators correctly check:

- Workbook existence and sheet names.
- Required output structures.
- Key numerical calculations.
- Core business statuses.
- Important root causes.
- Summary-level outputs.

### Under-Tested Areas

Across both tasks, the weakest coverage areas are:

1. **Narrative explanation quality**
   - Real ad ops work requires clear written explanation for clients or finance.
   - The tests mostly validate cells and keywords.

2. **Evidence citation**
   - The tasks ask for evidence, but the validators do not require source-file references except in limited summary fields.

3. **Robustness to messier files**
   - The datasets include some messiness, but not enough to fully mirror real exports.

4. **Exact financial impact in Task 2**
   - Task 2's financial impact check is too loose.

5. **Individual root-cause completeness in Task 2**
   - QA/test traffic should be directly tested if it is a planted root cause.

6. **PDF parsing integrity in Task 1**
   - The public static-data version removes the task-visible source CSV for the Index Exchange statement.

## Overall Recommendations

No code changes are made here, but if these tasks were revised later, the highest-impact improvements would be:

### Task 1 Improvements

1. Keep the Index Exchange PDF static and task-visible, with no parallel task-visible source CSV.
2. Add row-level checks for pacing projections and make-good dollars.
3. Add tighter per-SSP yield metric checks.
4. Add a revised-billing or duplicate-line-item edge case.
5. Add an invoice-level artifact if the goal is to mirror finance close even more closely.

### Task 2 Improvements

1. Add an explicit validator for QA/test traffic as its own impression-gap component.
2. Tighten total financial impact validation.
3. Validate per-domain category fields and wasted spend.
4. Make the timezone shift magnitude closer to realistic Eastern-to-UTC behavior.
5. Remove the artificial post-taxonomy domain volume jump, or explain it as an independent trafficking change.
6. Add a requirement or validator for evidence-source references.
7. Consider a lightweight narrative-quality rubric if the benchmark framework supports it.

# Final Judgment

Both tasks are well-designed adtech evaluation tasks.

**Task 1** is the stronger deterministic benchmark. It tests a realistic programmatic revenue operations workflow with many concrete business rules and a robust ground-truth recomputation validator.

**Task 2** is the stronger investigative benchmark. It tests whether a model can connect complaint language, configuration settings, verification data, placement behavior, and taxonomy changes into a coherent root-cause report.

Together, the tasks form a credible evaluation suite for adtech / ad ops knowledge work. They do not fully capture the messiness of production operations, but they test the intended core capabilities: reconciliation accuracy, business-rule application, multi-source evidence synthesis, and structured reporting.
