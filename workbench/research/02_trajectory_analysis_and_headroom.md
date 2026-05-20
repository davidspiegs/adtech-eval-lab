# Trajectory Analysis & Headroom Research

## Part 1: Sample Task Trajectory Analysis

### Task: Restaurant Weekly Cost Control Audit
**Model:** gemini-3-flash-preview | **Reward:** 0.0 (failed) | **Runtime:** 1m 47s | **Cost:** $0.08

### What Happened

Gemini 3 Flash **passed 4 out of 5 tests** but failed on the final one:

| Test | Result | Details |
|------|--------|---------|
| Required sheets exist | PASSED | All 5 sheets created correctly |
| COGS values and flags | PASSED | Food COGS = 2147.5 (exact match), ALERT flag correct |
| Variance flags match threshold | PASSED | Exactly correct flagged ingredients |
| Labor analysis (daily + overtime) | PASSED | Weekend days, alerts, overtime premium all correct |
| Prime cost + executive summary | FAILED | Week-over-week change: got 0.04413 vs expected 0.0453 |

### The Specific Failure

The model computed `weekly_prime_cost_pct` slightly wrong. The error is in the **labor cost calculation**:

**Root cause:** The model computed `daily_cost = hours * hourly_rate` without accounting for overtime premium in the total labor cost. The oracle solution computes overtime premium (0.5x rate for hours over 40) and ADDS it to the total labor cost. The model's code also computes overtime premium but **does not add it back** to the daily labor cost aggregation.

In the model's `process_data.py`:
```python
labor_data['daily_cost'] = labor_data['hours'] * labor_data['hourly_rate']
```

This misses the overtime premium for Sara (1 hour overtime * $14 * 0.5 = $7.00). This $7 difference propagates through:
- weekly_labor_cost (off by $7)
- weekly_prime_cost_pct (off by ~0.0012)
- week_over_week_change (off by ~0.0012)

Expected: 0.0453, Got: 0.04413 -- difference is ~0.00117, which matches the $7 overtime premium / ~$6000 total revenue.

### Key Observations About the Agent's Behavior

1. **Good: Parallel data loading** -- Read all CSVs, JSON, and Excel in a single step
2. **Good: Recovered from tool error** -- PDF extraction script expected 1 file, model adapted to call it 3 times
3. **Good: Activated relevant skills** -- xlsx, pdf, csv-tools, business-kpi-formulas
4. **Bad: Did not use the formulas skill correctly** -- The business-kpi-formulas skill explicitly states `daily_labor_cost = sum(hours * hourly_rate + overtime_premium)` but the model ignored this
5. **Bad: No self-verification** -- After generating the workbook, the model only checked file existence (ls -lh), not the actual cell values
6. **Bad: Subtle computation chain error** -- The overtime premium was computed correctly but not folded back into daily totals. This is exactly the kind of multi-step accumulation error that compounds.

### What This Tells Us About Headroom

This is a **textbook example** of the failure modes identified in the benchmarks:

- **Multi-step numerical reasoning with state accumulation** (FinSheet-Bench pattern)
- **Constraint integration failure** -- the model had the formula in its context (from the skill) but didn't integrate it into the computation
- **Compounding error** -- a $7 error in one intermediate calculation propagates to fail the entire task
- **Near-miss makes it harder** -- 4/5 tests pass, so the task is well-calibrated (not too easy, not impossibly hard)

---

## Part 2: APEX-Agents Leaderboard Data (May 2026)

Source: https://www.mercor.com/apex/apex-agents-leaderboard/

### Pass@1 Scores (ReAct Toolbelt Agent)

| Model | Pass@1 | Mean Score |
|-------|--------|------------|
| GPT 5.5 (xHigh) | 38.4% | 53.9% |
| GPT 5.4 (xHigh) | 36.0% | 52.3% |
| GPT 5.2 (xHigh) | 34.4% | 49.3% |
| Opus 4.7 (Max) | 33.9% | 50.6% |
| Gemini 3.1 Pro (High) | 33.5% | 49.1% |
| GPT 5.4 mini (xHigh) | 24.6% | 37.5% |
| Gemini 3 Flash (High) | ~24% | ~36% |
| Claude Sonnet 4.5 (High) | 20.5% | 34.6% |
| GLM 5 (Thinking) | 17.2% | 30.8% |
| GPT 5.4 nano (xHigh) | 16.9% | 25.5% |
| Claude Haiku 4.5 (High) | 8.9% | 21.4% |
| DeepSeek v3.2 | 7.0% | 18.8% |
| Gemini 2.5 Pro (On) | 6.6% | 17.0% |
| Gemini 2.5 Flash (On) | 1.8% | 6.4% |
| GPT 4o | 1.1% | 5.4% |

### Key Insight for Task Design
- Gemini 3 Flash fails ~76% of professional knowledge-work tasks at pass@1
- Even the best model (GPT 5.5) fails ~62% of the time
- The benchmark covers: investment banking, management consulting, corporate law
- Failure modes: managing ambiguity, file navigation in complex dirs, holding context across workflows

---

## Part 3: FinSheet-Bench Key Findings (March 2026)

Source: arxiv.org/abs/2603.07316

- **Best model overall:** Claude Opus 4.6 (~74% accuracy)
- **Gemini 3.1 Pro:** ~65% accuracy
- **Simple lookups:** ~80-90% accuracy across models
- **Complex multi-step reasoning:** drops to **<40%** for most models
- **Key failure categories:**
  - Cross-sheet calculations
  - Multi-step formulas (exactly what our sample task failed on)
  - Reconciling numbers across messy formatting
  - Percentage/ratio computations with intermediate steps

The "reasoning gap" -- difference between simple lookups and complex reasoning -- is 30-50 percentage points for all tested models. This gap is the headroom.

---

## Part 4: Failure Taxonomy for Knowledge Work Tasks

Based on trajectory analysis + benchmark research, here are the distinct failure modes ranked by prevalence and relevance:

### Tier 1: High-Frequency, High-Impact (target these)

1. **Multi-step numerical accumulation errors**
   - Evidence: Our trajectory (overtime premium not folded in), FinSheet-Bench reasoning gap
   - Pattern: Model computes intermediate values correctly but fails to propagate them through a chain
   - Task design: Require 3+ dependent calculation steps where each builds on the last

2. **Cross-source data integration**
   - Evidence: APEX-Agents (file navigation failures), our trajectory (PDF + CSV + XLSX + JSON)
   - Pattern: Model must extract data from 3+ different formats and reconcile them
   - Task design: Mix PDFs, CSVs, Excel files, and JSON; require answers that combine data from multiple sources

3. **Constraint integration from context**
   - Evidence: Our trajectory (skill had the formula, model ignored it), tau-bench (policy following)
   - Pattern: Model has the correct rule in its context window but doesn't apply it to the computation
   - Task design: Provide domain-specific rules/policies and require the model to apply them, not just acknowledge them

### Tier 2: Medium-Frequency, Medium-Impact

4. **Structured output conformance**
   - Evidence: Our trajectory (model got schema right on 4/5 sheets), APEX-Agents
   - Pattern: Complex schemas with multi-section layouts, specific cell positions, conditional content
   - Task design: Require precise output schemas where small deviations break the verifier

5. **Self-verification and error recovery**
   - Evidence: Our trajectory (no self-check after generation)
   - Pattern: Model declares "done" without verifying output correctness
   - Task design: Tasks where the first attempt is likely to have subtle errors, rewarding models that check and fix

### Tier 3: Lower Frequency, Still Relevant

6. **Long-context synthesis (50k+ tokens)**
   - Evidence: MRCR v2 benchmarks (67.2% at 128k for Gemini 3 Flash)
   - Pattern: Model must find and combine information scattered across a large document

7. **Domain-specific convention knowledge**
   - Evidence: Our trajectory (Jordan weekend days correctly identified), APEX-Agents (professional knowledge)
   - Pattern: Tasks requiring non-obvious domain conventions (fiscal years, local regulations, industry-specific terminology)

---

## Part 5: Domain Options Mapped to Your Background

### Option A: Financial Operations / Accounting Audit (strongest match to sample)
- **Your advantage:** You understand SaaS metrics (MRR, churn, ARR) and operational data
- **Headroom source:** FinSheet-Bench (<40% on complex reasoning), APEX-Agents investment banking (~24% pass@1)
- **Data sources:** SEC EDGAR filings, Kaggle financial datasets, synthetic based on real schemas
- **Task idea:** Monthly SaaS revenue reconciliation across Stripe export CSVs, billing system JSON, and a partially-filled investor report template
- **Scalability:** Thousands of public SEC filings, endless Stripe-like data schemas, parameterizable scenarios

### Option B: Legal / Contract Analysis
- **Your advantage:** You describe yourself as a "word-cel" and understand legal/writing domains
- **Headroom source:** APEX-Agents corporate law (~24% pass@1), Harvey AI's own admission of incremental improvement
- **Data sources:** SEC contract exhibits, open legal corpora, synthetic NDAs/MSAs
- **Task idea:** Cross-reference a master services agreement with 3 statement-of-work amendments to identify conflicting terms and produce a structured issues table
- **Scalability:** Enormous corpus of public contracts, systematically generatable conflicts

### Option C: Marketing / Growth Analytics
- **Your advantage:** Direct professional experience
- **Headroom source:** Multi-step analytical reasoning (FinSheet-Bench pattern), cross-source data
- **Data sources:** Synthetic ad platform exports, Google Analytics-like CSVs, CRM data
- **Task idea:** Build a weekly marketing performance report from ad platform CSVs, attribution data, and CRM exports -- requiring channel-level ROAS calculation, cohort analysis, and budget reallocation recommendations
- **Scalability:** Parameterizable campaigns, budgets, channels, attribution models

### Option D: Writing / Editorial Quality (your "word-cel" strength)
- **Your advantage:** Deep intuition for what good writing looks like
- **Headroom source:** Less benchmarked but real -- models are mediocre at substantive editing
- **Data sources:** Public domain texts, synthetic documents with planted errors
- **Risk:** Harder to verify deterministically (may need LLM-as-judge)

---

## Part 6: Recommendations

### Strongest case for the portfolio:

**Financial operations** (Option A or close variant) is the safest bet because:
1. It directly mirrors their sample task (shows you understand the pattern)
2. FinSheet-Bench + APEX-Agents provide strong published evidence of headroom
3. Deterministic verification is straightforward (exact numbers, correct flags)
4. Adtech Eval Lab's own sample is in this domain, suggesting it's what they consider good eval design
5. Scalability story is clean (SEC filings, parameterizable financial data)

**Legal contract analysis** (Option B) is the strongest "differentiated" pick because:
1. It targets a different failure mode (cross-document reasoning, not just numerical)
2. APEX-Agents explicitly benchmarks corporate law
3. Your writing/language intuition helps with quality
4. It's narrow enough to be defensible

**Marketing analytics** (Option C) is where your deepest domain expertise lies, which per your friend's advice, is the most valuable asset.

### What to do next:
1. Pick a domain based on your gut
2. Sketch 2-3 task ideas in that domain
3. For each, answer: "Can I write a deterministic verifier for this?" and "Can I write a solve.sh that produces the correct answer?"
4. Build the one that feels most natural
