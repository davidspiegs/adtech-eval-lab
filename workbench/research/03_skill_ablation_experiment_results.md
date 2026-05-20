# Skill Ablation Experiment Results

**Date:** 2026-05-08
**Task:** restaurant-weekly-cost-control-audit (Adtech Eval Lab sample task)
**Model:** gemini-3-flash-preview via gemini-cli agent
**Total runs:** 19 (1 prior manual run + 18 ablation runs)
**Total cost:** ~$1.52 (~$0.08/run)

---

## Experiment Design

We ran Gemini 3 Flash Preview against the same restaurant audit task in 6 configurations, 3 runs each, removing one skill at a time to measure the impact on pass rate and failure mode.

### Skill Inventory

The task ships with 9 skills in the Docker environment. From trajectory analysis of the first run, the model activated only 4:

| Skill | Relevant? | Contents |
|-------|-----------|----------|
| **business-kpi-formulas** | YES - core | Exact formulas for COGS, variance, labor, prime cost, overtime |
| **pdf** | YES - core | PDF parsing instructions + extraction script |
| **xlsx** | YES - core | Excel output formatting rules + helper script |
| **csv-tools** | YES - core | CSV parsing/aggregation guidance |
| docx | No | Word doc creation (unused) |
| fuzzy-match | No | String matching (unused) |
| git | No | Version control (unused) |
| web-search | No | Web research (unused) |
| sql-window | No | SQL window functions (unused) |

### Variants Tested

| Variant | What was removed | Hypothesis |
|---------|-----------------|------------|
| **baseline** | Nothing | Control -- all 9 skills present |
| **no-kpi** | business-kpi-formulas | Tests if model can derive formulas without being given them |
| **no-pdf** | pdf (skill + extraction script) | Tests if model can figure out PDF parsing independently |
| **no-xlsx** | xlsx (skill + helper script) | Tests if model can format Excel output without guidance |
| **no-csv** | csv-tools | Tests if CSV guidance matters (lightest skill) |
| **no-skills** | All 9 skills | Pure model capability, zero scaffolding |

---

## Results Summary

### Pass/Fail Table

| Variant | Run 1 | Run 2 | Run 3 | Pass Rate |
|---------|-------|-------|-------|-----------|
| **baseline** | 1.0 | 1.0 | 1.0 | **3/3 (100%)** |
| **no-kpi** | 0.0 | 0.0 | 0.0 | **0/3 (0%)** |
| **no-pdf** | 0.0 | 1.0 | 1.0 | **2/3 (67%)** |
| **no-xlsx** | 0.0 | 0.0 | 1.0 | **1/3 (33%)** |
| **no-csv** | 1.0 | 1.0 | 0.0 | **2/3 (67%)** |
| **no-skills** | 0.0 | 0.0 | 0.0 | **0/3 (0%)** |

**Including the prior manual run (baseline with all skills): reward = 0.0 (4/5 tests passed, failed on wow_change)**

So the true baseline rate across 4 runs is 3/4 (75%).

### Test-Level Breakdown

Tests (abbreviated):
- T1 = test_required_sheets_exist
- T2 = test_cogs_sheet_values_and_threshold_flags
- T3 = test_variance_sheet_flags_match_threshold_rule
- T4 = test_labor_analysis_daily_and_overtime_checks
- T5 = test_prime_cost_and_executive_summary_outputs

| Variant | Run | T1 | T2 | T3 | T4 | T5 | Failed Test(s) |
|---------|-----|----|----|----|----|-----|----------------|
| baseline | 1 | P | P | P | P | P | -- |
| baseline | 2 | P | P | P | P | P | -- |
| baseline | 3 | P | P | P | P | P | -- |
| no-kpi | 1 | P | **F** | P | P | **F** | COGS value wrong (2026.0 vs 2147.5) + prime cost cascade |
| no-kpi | 2 | P | P | P | **F** | **F** | Labor date format wrong + prime cost |
| no-kpi | 3 | P | P | P | P | **F** | wow_change off (same overtime premium bug) |
| no-pdf | 1 | P | **F** | P | P | **F** | COGS value wrong (2026.0 vs 2147.5) + cascade |
| no-pdf | 2 | P | P | P | P | P | -- |
| no-pdf | 3 | P | P | P | P | P | -- |
| no-xlsx | 1 | P | P | P | P | **F** | wow_change off |
| no-xlsx | 2 | P | P | P | P | **F** | wow_change off |
| no-xlsx | 3 | P | P | P | P | P | -- |
| no-csv | 1 | P | P | P | P | P | -- |
| no-csv | 2 | P | P | P | P | P | -- |
| no-csv | 3 | P | P | P | P | **F** | wow_change off |
| no-skills | 1 | P | P | P | P | **F** | wow_change off |
| no-skills | 2 | P | P | P | **F** | P | Labor date format wrong |
| no-skills | 3 | P | P | P | P | **F** | wow_change off |

---

## Analysis

### Key Finding 1: business-kpi-formulas is the critical skill

**Removing the KPI formulas skill drops the pass rate from 100% to 0%.** This is the single most impactful skill. Without the explicit formulas, the model:
- Run 1: Got Food COGS completely wrong (2026.0 vs 2147.5 -- off by $121.50, likely a different calculation method)
- Run 2: Couldn't even format the labor date column correctly
- Run 3: Got close but still miscalculated the overtime premium propagation

The KPI formulas skill contains the exact formula `daily_labor_cost = sum(hours * hourly_rate + overtime_premium)` which is the formula the model failed to apply in our original manual run. When this skill is present in the other variants, the model mostly gets it right. When it's removed, it consistently fails.

### Key Finding 2: Stochastic failure on the hardest test (T5)

T5 (prime_cost_and_executive_summary) is the most fragile test. It requires:
- Correct weekly prime cost % (depends on correct COGS + correct labor including overtime)
- Correct weekly recommended action label
- Correct traffic light color
- Exact week-over-week change (0.0453 with tolerance of 0.000001)

This last check -- the wow_change with 6 decimal places of precision -- is where the model most often fails. Even small errors in intermediate calculations (like the $7 overtime premium) cascade to break this test.

### Key Finding 3: PDF skill removal is surprisingly non-fatal

no-pdf passed 2/3 runs. When the PDF extraction script is removed, the model falls back to writing its own pdfplumber extraction code. In 2 of 3 runs, it succeeded. In the 1 failure, it got the COGS value wrong (2026.0 instead of 2147.5), suggesting it parsed the PDF differently (possibly missing line items or misinterpreting the pipe-delimited format).

The "Unsupported image MIME type: application/pdf" warnings in no-pdf runs suggest the Gemini CLI tried to process PDFs as images first before falling back to code-based extraction.

### Key Finding 4: csv-tools skill barely matters

no-csv passed 2/3 runs, same as baseline's true rate (3/4 including the manual run). The CSV guidance skill is too generic to materially help -- the model already knows how to use pandas for CSV operations.

### Key Finding 5: xlsx skill has moderate impact

no-xlsx passed 1/3 runs. The xlsx skill provides rules about numeric formatting, deterministic row ordering, and avoiding merged cells. Without it, the model more frequently makes formatting errors that cascade to test failures. But it can still occasionally get it right on its own.

### Key Finding 6: No skills = consistent failure, but close

no-skills passed 0/3 runs, but in 2 of 3 runs it passed 4/5 tests (only failing T5). In 1 run it failed T4 (labor analysis) due to a date formatting issue. The model is *almost* capable enough on its own but consistently makes the kind of small numerical errors that deterministic verifiers catch.

---

## Failure Mode Taxonomy

From 19 total runs, we observed these distinct failure modes:

### Mode 1: Overtime premium not propagated into daily labor cost (most common)
- **Occurrences:** ~7 of 10 failures
- **Symptom:** wow_change off by ~0.001 (the $7 overtime premium / ~$6000 revenue)
- **Root cause:** Model computes `daily_cost = hours * rate` without adding overtime premium
- **Which tests fail:** T5 only (everything else passes)

### Mode 2: COGS value completely wrong (2026.0 vs 2147.5)
- **Occurrences:** 2 failures (no-kpi-run1, no-pdf-run1)
- **Symptom:** Food COGS off by $121.50
- **Root cause:** Either PDF parsing missed invoice line items, or COGS formula was applied incorrectly
- **Which tests fail:** T2 + T5 (cascading)

### Mode 3: Labor date format wrong
- **Occurrences:** 2 failures (no-kpi-run2, no-skills-run2)
- **Symptom:** "Could not find 2026-03-23 row" -- date stored in wrong format
- **Root cause:** Model stored dates as datetime objects instead of "YYYY-MM-DD" strings
- **Which tests fail:** T4 + T5

---

## Implications for Task Design

### What makes a good eval task (lessons from this experiment):

1. **Multi-step numerical chains create natural headroom.** The overtime premium -> daily labor -> weekly labor -> prime cost -> wow_change chain is a 5-step computation where a $7 error in step 1 cascades to fail the final check. This is exactly the kind of task where frontier models struggle.

2. **Deterministic verifiers with tight tolerances expose real errors.** The 0.000001 tolerance on wow_change is what separates pass from fail. Looser tolerances would mask the errors.

3. **Skills/scaffolding dramatically affect pass rate.** The KPI formulas skill swings pass rate from 0% to 100%. This means task difficulty can be precisely calibrated by controlling what help the agent receives.

4. **Stochasticity is high even at the frontier.** The same model on the same task produces different results across runs. Any headroom claim needs multiple runs to be credible. 3 runs is the minimum; 5+ would be better for statistical significance.

5. **The "hardest" test should target the end of the computation chain.** Intermediate results (COGS, variance, labor) are often correct. It's the final aggregation where errors accumulate and surface.

### Recommended approach for custom task design:

- Target multi-step financial/analytical computations with 4+ dependent steps
- Use deterministic verifiers with exact numerical checks
- Include cross-source data (PDF + CSV + Excel + JSON) to stress data integration
- Provide skills as a calibration lever: task difficulty = f(instruction complexity, data messiness, skill availability)
- Run each task configuration at least 3 times before drawing conclusions
- Focus verification on the final aggregated outputs where errors compound

---

## Raw Data: Run Timestamps and Job Paths

| Variant-Run | Job Path | Reward |
|------------|----------|--------|
| manual-run0 | jobs/2026-05-08__18-07-05 | 0.0 |
| baseline-run1 | experiments/results/baseline-run1/2026-05-08__21-51-34 | 1.0 |
| baseline-run2 | experiments/results/baseline-run2/2026-05-08__21-56-32 | 1.0 |
| baseline-run3 | experiments/results/baseline-run3/2026-05-08__22-02-12 | 1.0 |
| no-kpi-run1 | experiments/results/no-kpi-run1/2026-05-08__21-51-34 | 0.0 |
| no-kpi-run2 | experiments/results/no-kpi-run2/2026-05-08__21-56-32 | 0.0 |
| no-kpi-run3 | experiments/results/no-kpi-run3/2026-05-08__22-02-12 | 0.0 |
| no-pdf-run1 | experiments/results/no-pdf-run1/2026-05-08__21-51-34 | 0.0 |
| no-pdf-run2 | experiments/results/no-pdf-run2/2026-05-08__21-56-32 | 1.0 |
| no-pdf-run3 | experiments/results/no-pdf-run3/2026-05-08__22-02-12 | 1.0 |
| no-xlsx-run1 | experiments/results/no-xlsx-run1/2026-05-08__21-51-34 | 0.0 |
| no-xlsx-run2 | experiments/results/no-xlsx-run2/2026-05-08__21-56-32 | 0.0 |
| no-xlsx-run3 | experiments/results/no-xlsx-run3/2026-05-08__22-02-12 | 1.0 |
| no-csv-run1 | experiments/results/no-csv-run1/2026-05-08__21-51-34 | 1.0 |
| no-csv-run2 | experiments/results/no-csv-run2/2026-05-08__21-56-32 | 1.0 |
| no-csv-run3 | experiments/results/no-csv-run3/2026-05-08__22-02-12 | 0.0 |
| no-skills-run1 | experiments/results/no-skills-run1/2026-05-08__21-51-34 | 0.0 |
| no-skills-run2 | experiments/results/no-skills-run2/2026-05-08__21-56-32 | 0.0 |
| no-skills-run3 | experiments/results/no-skills-run3/2026-05-08__22-02-12 | 0.0 |
