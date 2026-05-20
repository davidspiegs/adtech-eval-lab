---
title: "RL Data for Knowledge Work: Adtech Revenue Operations"
subtitle: "Harbor Eval Tasks with Demonstrated Headroom"
author: "David S."
date: "May 2026"
---

# Executive Summary

I built two Harbor-format evaluation tasks in the adtech/publisher revenue-operations domain. Both produce measurable, reproducible headroom across frontier models.

**Task 1 — Revenue Reconciliation** (binary scoring, 15 checks): A 5-sheet Excel workbook audit requiring multi-source joins, fuzzy matching, PDF parsing, and numerical reasoning. Headroom signal: non-deterministic unit-interpretation error on percentage-change computation.

**Task 2 — Campaign Discrepancy Investigation** (partial scoring, 14 checks): A multi-step forensic investigation into advertiser complaints across 13 data files. Headroom signal: failure to identify the largest gap component (non-viewable impressions) which requires connecting a configuration setting to a column-level computation across files.

| Model | Task 1 (binary) | Task 2 (partial) | Primary Failure Modes |
|---|---|---|---|
| GPT-5.5 (Codex) | **1/1 pass (100%)** | **1.000 avg (6 trials)** | T1: passes consistently |
| Claude Opus 4.6 | **1/1 pass (100%)** | **0.929 avg (6 trials)** | T2: non-viewable component (33%) |
| Gemini 3 Flash | **0/5 pass (0%)** | **0.843 avg (10 trials)** | T1: 3 distinct failure modes; T2: non-viewable (50%) + timezone (70%) |

Task 2 produces a clear, reproducible capability gradient: GPT-5.5 achieves a perfect score across all 6 trials; Opus 4.6 is strong but inconsistent; Gemini Flash scores lowest with consistent failures on the same investigation step. This gap reflects genuine reasoning differences in multi-step forensic tasks — Gemini's strengths in code generation and instruction following do not transfer to long-horizon data investigation.

---

# 1. Why Adtech Knowledge Work

## What is adtech revenue operations?

Digital publishers — websites, apps, streaming platforms — sell advertising inventory programmatically through multiple Supply-Side Platforms (SSPs) like Magnite, Index Exchange, and PubMatic. Every single ad impression gets counted independently by the publisher's own ad server, by each SSP that facilitated the sale, and by third-party verification vendors (Moat, DoubleVerify, IAS) hired by the advertiser to confirm delivery.

These counts never perfectly agree. Invalid Traffic (IVT) filtering removes bot impressions at different pipeline stages. Verification vendors may use UTC while the ad server uses US/Eastern, shifting impressions across day boundaries. Viewability definitions differ — an ad server counts a "served" impression, while a verification vendor may only count "viewable completions." Tag latency means some impressions are never measured at all.

Publisher revenue operations teams spend significant time each month reconciling these counts, investigating advertiser complaints about discrepancies, and producing audit reports that explain every gap. A single miscounted campaign can trigger a $50K+ advertiser credit or, worse, a lost account. Both of our evaluation tasks model real workflows that ops teams perform routinely: Task 1 is a standard monthly reconciliation audit across SSPs and the ad server; Task 2 is a triggered forensic investigation when an advertiser flags a discrepancy.

Despite being common knowledge work in a large industry — global programmatic ad spend exceeds $700B annually — there are no public datasets or benchmarks that capture this end-to-end reconciliation workflow. The closest published work is AD-Bench (Hu et al., 2026), which evaluates agents on advertising *analytics* tasks (campaign performance queries, metric lookups) using marketing platform tools. Our tasks are fundamentally different: they test *investigation and reconciliation* — cross-referencing multiple independent measurement systems, identifying root causes of discrepancies, and producing structured audit deliverables. This makes our eval a unique contribution to an underserved but economically significant domain.

## The capability we're targeting

Gemini 3 Flash is a remarkable model. It's fast, cheap, and genuinely strong at what it does well: instruction following, code generation, and structured output. On IFEval-style benchmarks, frontier models (Flash included) score near-ceiling. On AIME 2025 (clean competition math), Flash scores 95.2%. On SWE-Bench, it achieves ~78% — competitive with models 10x its cost.

But there's a documented gap between "follows instructions well" and "reasons through messy, ambiguous, multi-step problems." Flash scores 95.2% on clean AIME problems but drops 11 places on LMArena Math, where quantitative reasoning is embedded in natural language and mixed formats. That pattern — strong on clean, isolated tasks; weak on messy, integrated ones — is exactly what knowledge-work tasks require and what RL training data should target.

## External benchmark evidence

The gap shows up consistently across benchmarks that test investigation, long-horizon planning, and factual reasoning:

| Benchmark | What It Tests | Gemini 3 Flash | SOTA / Comparison | Source |
|---|---|---|---|---|
| APEX-Agents (Management Consultant) | Long-horizon professional tasks | ~19% Pass@1 | GPT 5.5 xHigh: ~44% | Mercor (arxiv 2601.14242) |
| tau2-Bench | Multi-turn conversational agents | 4.1% Pass^4 | GPT 5.4: 16.5% | Sierra Research (taubench.com) |
| AA-Omniscience | Factual recall + hallucination | ~8% non-hallucination rate* | Opus 4.7: ~64% | Artificial Analysis |
| AA Long-Context Reasoning | Extract + synthesize from long docs | ~66% | GPT-5.2: ~74% | Artificial Analysis |
| LiveBench Reasoning | Broad reasoning average | 74.6% | Opus 4.6 Thinking: 88.7% | LiveBench |
| AD-Bench (L3 hardest) | Adtech analytics, multi-tool | ~49% Pass@1 (Pro)** | — | arxiv 2602.14257 |

*Scores as of late 2025 / early 2026; may have shifted with subsequent model updates.*

\* *On questions outside its training data — i.e., when Flash doesn't know the answer, it invents one ~92% of the time rather than abstaining.*

\*\* *Note: AD-Bench tested Gemini 3 Pro, not Flash. Flash would likely score lower on these multi-step analytics tasks, which strengthens the headroom case.*

The hallucination data is particularly striking. As Better Stack's independent review put it: "Gemini 3 Flash lacks *epistemic humility* — the ability to recognize the limits of its own knowledge. When faced with a question it cannot answer, instead of saying 'I don't know,' it will invent a confident-sounding but incorrect answer over 90% of the time." This maps directly to what we see in Task 2: Flash confidently produces an incomplete gap reconciliation without flagging that its components don't sum to the total.

## Why this domain specifically

Adtech revenue operations sits at the intersection of these documented weaknesses:

- **Multi-source reasoning**: 10-13 input files across CSV, JSON, PDF, and Markdown formats that must be cross-referenced.
- **Ambiguous specifications**: Business rules with room for interpretation (e.g., "include pairs no SSP billed for" — does that mean add rows or note them?).
- **Numerical reasoning in context**: Not clean math problems, but percentage changes, tolerance thresholds, and unit interpretations embedded in business logic.
- **Investigation under uncertainty**: Multiple plausible root causes that must be systematically identified, not guessed.

The recently published AD-Bench (Hu et al., 2026) validates this domain choice — even Gemini 3 Pro drops to 49.4% Pass@1 on the hardest adtech analytics tasks, with a trajectory coverage of only 70.1%. Notably, AD-Bench tests analytics queries (campaign metrics, performance lookups) rather than the cross-system reconciliation and root-cause investigation that our tasks require — a harder, more open-ended class of problem.

---

# 2. Task 1: Revenue Reconciliation

## Scenario

Pinnacle Digital Media needs an April 2026 monthly performance audit. The agent processes 10 input files (CSV, PDF, JSON, Markdown) and produces a 5-sheet Excel workbook covering revenue reconciliation, delivery pacing, SSP (Supply-Side Platform) yield analysis, month-over-month variance, and executive summary.

**Key difficulty mechanisms:** fuzzy SSP name matching (e.g., "Homepage Billboard 970x250" vs "Homepage_Billboard_970x250"), PDF billing extraction, PMP floor exception logic, percentage-change computation with implicit unit expectations, and dual-threshold flagging.

## The headroom signal

The decisive test is `test_variance_change_pct_revenue` — an internal consistency check. It takes the model's own `current_month` and `prior_month` values, computes `(current - prior) / prior * 100`, and checks whether the model's `change_pct` agrees within 1 percentage point. The model fails when its own numbers don't agree with each other.

**What Gemini Flash writes (~60% of trials):**

```python
change = (current - prior) / prior if prior != 0 else 0  # BUG: missing * 100
variance_rows.append({
    'change_pct': round(change, 4),  # writes 1.0615 instead of 106.15
    'status': status
})
```

The instruction says "percentage change" and the status thresholds use percentage values (10%, 25%), but Flash doesn't make the connection. It computes `(65658.89 - 31850.00) / 31850.00 = 1.06` and writes it directly without multiplying by 100.

**Proof this is real headroom:** When I tested an instruction variant that explicitly said "Express change_pct as a percentage value (e.g., a doubling is 100.0, not 1.0)," Gemini passed every time. The failure is specifically in unit interpretation — the model must connect "change_pct" + "percentage" + threshold semantics to determine the scale.

## Results

| Model | Trials | Pass Rate | Primary Failure |
|---|---|---|---|
| Claude Opus 4.6 | 1 | **100%** | — |
| GPT-5.5 | 1 | **100%** | — |
| Gemini 3 Flash | 5 | **0%** | `change_pct` (3/5), reconciliation logic (1/5), executive summary (1/5) |

Gemini Flash fails every trial on binary scoring across three distinct failure modes (validated from agent trajectories):

1. **Unit interpretation (3/5 trials):** The `change_pct` error described above — writes `1.06` instead of `106.15`.
2. **Weak name resolution (1/5 trials):** Uses exact string matching instead of fuzzy matching for SSP ad-unit names. Names like "Homepage Billboard 970x250" vs "Homepage_Billboard_970x250" fail to resolve, causing 3 SSP billing rows to be incorrectly dropped instead of held. This cascades: row count drops from 33 to 32, held rows drop from 4 to 1, and yield values miss ~$10.5K of revenue.
3. **Pacing formula bug (1/5 trials):** Computes `start = max(contract_start, April_1)` correctly but then uses `contract_start` (not `start`) for `days_elapsed`. For a deal starting January 1, this inflates the denominator from 30 to 120 days, halving the projected delivery and doubling makegood exposure ($98K vs expected $50K).

These three modes share a common pattern: Gemini identifies the right approach during planning but downgrades to a simpler implementation. In the fuzzy-matching trial, the agent's own code comments acknowledge the shortcut:

```python
# Fuzzy match logic (simplified for script, can use fuzzy-match skill if needed)
# Let's try case-insensitive and stripping whitespace
ssp_name_clean = ssp_name.strip().lower()
```

Despite loading a fuzzy-match skill and writing "can use fuzzy-match skill if needed," the agent never invokes it — SSP names with typos (e.g., "MAG_Lifstyle_Interstitial" vs "MAG_Lifestyle_Interstitial") silently fail to match. In the pacing trial, the agent computes `start = max(contract_start, April_1)` correctly but references the wrong variable on the next line. These are not knowledge gaps — the model knows what to do — but execution gaps where it takes shortcuts or loses track of its own intermediate results.

GPT-5.5 and Opus 4.6 pass consistently, confirming the task is solvable and the verifier is working correctly.

---

# 3. Task 2: Campaign Discrepancy Investigation

## Scenario

MegaBrand Auto's programmatic campaign ran April 1-30, 2026. Three advertiser complaints are filed: (1) a 50% impression gap between ad server and verification vendor, (2) a mid-month viewability collapse, and (3) ads appearing on excluded gambling domains. The agent must investigate all three using 13 data files and produce a 4-sheet investigation report.

**Six planted root causes (all discoverable from data):**

| Root Cause | Magnitude | Discovery Mechanism |
|---|---|---|
| Invalid Traffic (IVT) filtered by Moat (GIVT + SIVT) | ~389K imps | Moat verification columns + IVT detail report |
| Non-viewable impressions | ~1.44M imps | `campaign_config.json` count_method + Moat verified vs viewable |
| Timezone boundary (US/Eastern vs UTC) | ~80K imps | `campaign_config.json` timezone settings + April 30 anomaly |
| QA test traffic | ~134K imps | `internal_qa_log.csv` + Moat `test_flag_impressions` |
| Viewability drop (PL-010 below-fold) | April 21 onset | `creative_assignment_log` + `placement_specs` + daily data |
| Domain violation (taxonomy reclassification) | ~333K post-Apr-15 | `domain_delivery` + taxonomy v4.1 vs v4.2 + exclusion list |

**Scoring:** `reward = passed_count / total_count` across 14 deterministic tests. No LLM-as-judge.

## The headroom signal: non-viewable impressions

The non-viewable component (~1.44M impressions, 71% of the total gap) is the single most discriminating test. Identifying it requires a 3-step reasoning chain:

1. Read `campaign_config.json` and notice `count_method = "viewable_completions"` (Moat only reports viewable impressions).
2. Understand that this means Moat's number excludes verified-but-not-viewable impressions.
3. Compute `verified_impressions - viewable_impressions` from the Moat data to quantify the gap.

**What Gemini Flash does (~50% of trials):**

```python
total_moat_verified = moat['verified_impressions'].sum()   # 3,436,733
gap = total_ad_server - total_moat_verified                # = 599,876 (WRONG)
```

Flash compares ad server impressions (4.04M) against Moat *verified* impressions (3.44M) instead of *viewable* impressions (2.00M). This produces a gap of ~600K instead of ~2.04M. It then accounts for IVT and QA within this smaller gap and labels the remainder "technical discrepancy." The investigation report reads as complete and confident — there's no acknowledgment that 1.4 million impressions are unaccounted for. Across all failing trials, none of the agent transcripts contain the keyword `count_method` or `viewable_completions` — Flash never reads the configuration that would tell it which column to use.

**What GPT-5.5 does (100% of trials):**

```python
moat_viewable_total = moat.viewable_impressions.sum()       # 1,998,322
total_gap = ad_total - moat_viewable_total                  # 2,038,287 (CORRECT)
non_viewable = moat.verified_impressions.sum() - moat_viewable_total  # 1,438,411
```

GPT-5.5 reads `campaign_config.json`, notices the `viewable_completions` count method, and correctly uses `viewable_impressions` as the denominator. Its initial observation in the logs reads: *"The setup shows a measurement-method mismatch: ad server counts raw served impressions in US/Eastern with no IVT filtering, while Moat is configured for UTC verification with IVT and test-traffic filtering."* It then systematically identifies all six root causes.

## Results

10 Gemini trials, 6 GPT trials, 6 Opus trials across multiple rounds (Round 1 adjusted for a verifier keyword false negative on timezone detection, fixed in subsequent rounds):

| Model | Trials | Avg Score | Std Dev | Range |
|---|---|---|---|---|
| **GPT-5.5** | 6 | **1.000** | 0.000 | 14/14 all trials |
| **Opus 4.6** | 6 | **0.929** | 0.101 | 11-14/14 |
| **Gemini Flash** | 10 | **0.843** | 0.105 | 10-14/14 |

Gemini's failures cluster into two validated patterns (from trajectory analysis):

1. **Non-viewable chain (5/10 trials):** Flash computes `ad_server - verified` (gap = 599K) instead of `ad_server - viewable` (gap = 2.04M). When this happens, `total_gap`, `non_viewable_component`, and `components_sum` all fail together (cascading), producing a characteristic 10-11/14 score. The 1.44M non-viewable component simply doesn't exist in the agent's model of the problem.

2. **Timezone attribution (7/10 trials):** Flash either misses the timezone boundary entirely (labeling 77K as "measurement failures") or computes the correct residual but categorizes it as "technical discrepancy" without connecting it to the UTC vs US/Eastern configuration. Both sub-modes stem from insufficient investigation of *why* the residual exists. In one representative trial, the agent reads `campaign_config.json` and sees `timezone: "UTC"` for Moat alongside `timezone: "US/Eastern"` for the ad server — direct evidence of a reporting-boundary mismatch. Despite this, it labels the 77K residual as *"a small technical discrepancy (3.8%) within industry standards"* and moves on. The agent computes the right number but doesn't investigate why it exists.

Opus 4.6 intermittently hits the same non-viewable failure (2/6 trials), but catches it 67% of the time. GPT-5.5 never misses it.

---

# 4. Evidence Summary

## Combined headroom

| | Task 1 (Binary) | Task 2 (Partial) | Combined Signal |
|---|---|---|---|
| **GPT-5.5** | 100% pass (1/1) | 1.000 avg (6 trials) | Strong overall; passes both tasks consistently |
| **Opus 4.6** | 100% pass (1/1) | 0.929 avg (6 trials) | Intermittently misses non-viewable |
| **Gemini Flash** | 0% pass (0/5) | 0.843 avg (10 trials) | Consistent weaknesses on both tasks |

## Research alignment

Our results align with the external benchmark landscape:

- **Task 1 (unit interpretation)** mirrors the AIME-vs-LMArena-Math pattern: Flash handles clean math (computing the fraction) but fails when contextual reasoning is required (realizing the fraction needs to be a percentage). This is the "messy real-world math" gap documented across multiple benchmarks.

- **Task 2 (investigation)** mirrors APEX-Agents and tau2-Bench: Flash struggles with long-horizon tasks requiring multi-file cross-referencing and hypothesis formation. Its ~84% average score across 10 trials on our 14-test partial scoring maps to the general pattern of 19-24% pass rates on professional-services benchmarks.

- **The confident-but-incomplete output** in Task 2 mirrors the AA-Omniscience hallucination finding. Flash doesn't flag uncertainty — it produces a gap reconciliation that accounts for ~600K of a ~2M gap and presents it as complete. This "epistemic humility" failure is precisely the weakness that RL training data should target.

## Why partial scoring matters for RL

Task 2's partial scoring (`reward = passed/total`) provides a dense training signal:

- Even failed Gemini trials score 10-13/14 (not 0). The model gets credit for correctly identifying IVT, QA traffic, viewability drop, and domain violations — only the non-viewable and timezone components are missed.
- This gradient means RL can optimize from a non-trivial starting reward, which is significantly better for training than binary pass/fail tasks where most trajectories score 0.

---

# 5. Quality Assurance

## Verifier evolution

The verifier went through three iterations — and this process is itself evidence of quality:

1. **V1 (strict):** 37 tests, tight tolerances. GPT-5.5's first trial failed 5 checks — but all 5 were valid alternative interpretations of ambiguous spec language (e.g., fill rate as percentage vs decimal). These were false negatives in the verifier, not errors in the model.
2. **V2 (consolidated):** Reduced to 15 tests (Task 1) and 14 tests (Task 2), following Harbor's structural patterns. Relaxed tolerances for defensible ambiguities. Added lenient handling for unbilled rows, fill-rate scaling, and total-row label variations.
3. **V3 (hardened):** Expanded keyword matching for timezone detection (category name + explanation column), flexible total-row detection ("grand_total", "overall", "sum"), and additional non-viewable keywords. Each change was validated against the oracle.

This iteration ensured that verifier failures represent genuine capability gaps, not formatting disagreements.

## Independent audits

10 automated worker-agent audits across both tasks:

| Audit | Scope | Result |
|---|---|---|
| Task 1: GT engine formulas | All 10 reconciliation computation steps | All CORRECT |
| Task 1: Pacing/yield/variance | Forward-projection, eCPM, change_pct | All CORRECT |
| Task 1: Edge cases | 10 boundary conditions | 0 real bugs (4 theoretical, not triggerable) |
| Task 1: Instruction review | Eval leaks, contradictions | CLEAN |
| Task 2: Verifier stress test | 14 tests, false-negative enumeration | 0 blockers (1 HIGH risk noted) |
| Task 2: Data integrity | 6 root causes discoverable? | All DISCOVERABLE |
| Task 2: Oracle cross-check | 14 tests format alignment | 14/14 MATCH |
| Task 2: Container security | Solution leak, skill hints | PASS all 9 checks |

## Container security

The public versions use static, task-visible datasets copied directly into `/root/data`. The programmatic revenue task ships the Index Exchange billing statement as a PDF-only task input, rather than generating it from a hidden CSV during image build. Solution files (`solve.py`, `test_outputs.py`) are never copied into the agent workspace by the Dockerfiles.

---

# 6. Scale Plan

## From 2 tasks to 1,000

Both tasks are fully parameterized and deterministically generated from seed configurations. The generation pipeline:

```
seed_config → build_inputs.py → {CSVs, JSONs, PDFs, policy docs}
                              → Docker environment (data only, source cleaned)
           → solve.py (oracle) → reference output → verify N/N
           → test_outputs.py   → deterministic checks → reward
```

## Public data sources

All data is synthetically generated but modeled on publicly documented schemas:

| Source | What We Use | Access |
|---|---|---|
| Google Ad Manager report dimensions | Column schemas, delivery metrics | Public documentation |
| IAB Content Taxonomy (v4.x) | Category hierarchies, version diffs | Public standard, versioned |
| OpenRTB 2.6 bid request specification | SSP billing fields, deal structures | IAB Tech Lab, public |
| TAG/MRC IVT taxonomy | GIVT/SIVT classification | Industry standard, public |
| Moat/DoubleVerify documentation | Verification metric definitions | Partially public |
| SSP billing formats (Magnite, Index, PubMatic) | CSV/PDF billing structures | Public via seller documentation |

## Variation dimensions

| Dimension | Range | Headroom Impact |
|---|---|---|
| Deal count | 5-50 | More joins, more edge cases |
| SSP count | 2-8 | More billing sources to reconcile |
| Discrepancy patterns | Under/overbilled, within-tolerance, missing | Tests different flagging logic |
| Fuzzy name complexity | Exact match to aggressive abbreviation | Tests matching capability |
| Investigation depth | 2-8 root causes, 5-20 data files | Tests long-horizon reasoning |
| Policy complexity | Simple thresholds to conditional exceptions | Tests rule application |

## Augmentation strategy

Beyond parameterized variants, three additional task types test different reasoning capabilities:

1. **Programmatic Deal Troubleshooting:** Diagnose why a PMP deal underperforms from bid request logs, deal settings, and targeting config. Tests causal reasoning — the model must distinguish creative-mismatch, floor-price, targeting, and budget hypotheses.
2. **Publisher Yield Optimization:** Recommend floor price adjustments per ad unit from header-bidding analytics. Tests statistical/economic reasoning — balance fill rate against eCPM.
3. **Campaign Trafficking QA:** Identify setup errors in ad server configuration exports. Tests attention-to-detail constraint checking.

## QA loop

Every generated task goes through:

1. **Oracle validation**: Run `solve.py` → verify N/N on all tests
2. **Verifier stress test**: Automated worker enumerates false-negative risks per test
3. **Smoke test**: Run 3 models × 1 trial to confirm headroom signal exists
4. **False-negative check**: Review any trial where model output looks correct but fails — fix verifier if needed
5. **Container audit**: Verify no solution files or generator scripts are accessible

## Throughput

- New task variant: ~1s generation + ~30s oracle validation
- Trial execution: ~3-8 minutes depending on model
- With Harbor parallelism: 1,000 tasks × 5 trials each ≈ 1 day with rate-limit-aware batching

---

# 7. Methodology

- **Tools:** Harbor for eval execution. Factory.ai Droid (Claude Opus 4.6 Max) for task construction. Worker agents for parallel QA audits.
- **Verifier design:** All checks are deterministic — no LLM-as-judge. Task 1 uses binary scoring (15 checks, all-or-nothing). Task 2 uses partial scoring (14 checks, reward = passed/total).
- **Trial count:** Task 1: 7 trials with final verifier (5 Gemini, 1 GPT, 1 Opus). Task 2: 22 trials (10 Gemini, 6 GPT, 6 Opus across multiple rounds with verifier improvements).
- **Cost:** Gemini trials: ~$0.10-0.27 each. GPT trials: ~$1.40-2.30 each. Opus trials: ~$1.16-3.07 each. Total spend across all trials: ~$50.

## How I used agents

| What | My role | Agent-assisted |
|---|---|---|
| Domain & headroom hypothesis | Selected adtech revenue ops; identified unit-interpretation and multi-step reasoning as target failure modes | — |
| Literature research | Researched benchmarks where Gemini 3 Flash underperforms, studied task construction patterns and dataset design across APEX-Agents, tau2-Bench, AD-Bench, and others to inform headroom strategy; selected and verified all citations | GPT-5.5 Pro accelerated paper discovery and benchmark search |
| Task design | Decided failure modes to plant, scoring strategy (binary vs partial), data file structure, difficulty mechanisms | — |
| Synthetic data | Directed iterative improvements for realism (column schemas, naming conventions, magnitude ranges) | Factory.ai Droid generated CSVs, JSONs, PDFs, and Dockerfiles |
| Verifier & oracle | Reviewed logic, validated against ground truth | Factory.ai Droid wrote initial code; I directed 3 iterations of hardening |
| QA & audits | Reviewed all audit results and trajectory analyses; verified data and report accuracy multiple times with Opus 4.6 | 10 independent worker-agent audits ran in parallel (stress tests, data integrity, container security) |
| Trial execution & analysis | Reviewed every trial result and failure pattern before including in report | Factory.ai Droid orchestrated Harbor runs and compiled results |
| Report | Guided narrative, framing, and structure; iterated multiple rounds of revision and fact-checked all data | Factory.ai Droid populated data and drafted sections |

---

# Appendix A: Ground Truth

**Task 1:**
```
total_adjusted_revenue_usd  = $62,030.51  (29 matched pairs)
total_ssp_reported_revenue  = $65,658.89  (33 SSP billing rows)
flagged_discrepancy_count   = 4
held_row_count              = 4
overall_health              = Red (4 flagged >= 3)
```

**Task 2:**
```
total_impression_gap        = 2,038,287   (ad_server - moat_viewable)
ivt_component               = 388,762     (GIVT 214,184 + SIVT 174,578)
non_viewable_component      = 1,438,411   (verified - viewable)
timezone_component          = 80,388      (April 30 US/Eastern → UTC)
qa_test_traffic             = 133,992     (flagged in QA log + Moat)
viewability_drop_date       = 2026-04-21  (PL-010 below-fold launched)
offending_domains           = gamblingreviews.com, pokerstrategyhub.com, sportsodds.net
domain_violation_imps       = 332,766     (post-April-15 taxonomy reclassification)
```

# Appendix B: Full Trial Results

**Task 1 — 7 Trials with Final Verifier (binary scoring):**

| Trial | Model | Score | Failed Tests | Cost |
|---|---|---|---|---|
| t1-b | GPT-5.5 | 15/15 PASS | — | $1.43 |
| t1-c | Opus 4.6 | 15/15 PASS | — | $3.07 |
| t1-k | Gemini Flash | 12/15 | row_count, held_and_zeroed, yield_values | $0.11 |
| t1-l | Gemini Flash | 14/15 | change_pct_revenue | $0.13 |
| t1-m | Gemini Flash | 14/15 | change_pct_revenue | $0.17 |
| t1-n | Gemini Flash | 13/15 | held_and_zeroed, change_pct_revenue | $0.17 |
| t1-o | Gemini Flash | 14/15 | executive_summary | $0.10 |

*Additional early trials with prior verifier versions also showed GPT and Opus passing consistently. Only trials run with the final verifier (V3) and corrected Dockerfile are included above.*

**Task 2 — All 22 Trials (partial scoring):**

| Trial | Model | Score | Failed Tests | Cost |
|---|---|---|---|---|
| R1 | Opus 4.6 | 13/14 → 14/14 adj | timezone (verifier FN) | $2.04 |
| R2a | Opus 4.6 | 11/14 | total_gap, non_viewable, components_sum | $1.16 |
| R2b | Opus 4.6 | 14/14 | — | $1.74 |
| R3a | Opus 4.6 | 14/14 | — | $1.62 |
| R3b | Opus 4.6 | 11/14 | total_gap, non_viewable, components_sum | $1.48 |
| t2-f | Opus 4.6 | 14/14 | — | $2.20 |
| R1 | GPT-5.5 | 13/14 → 14/14 adj | timezone (verifier FN) | $1.42 |
| R2a | GPT-5.5 | 14/14 | — | $1.55 |
| R2b | GPT-5.5 | 14/14 | — | $2.34 |
| R3a | GPT-5.5 | 14/14 | — | $2.27 |
| R3b | GPT-5.5 | 14/14 | — | $1.61 |
| t2-f | GPT-5.5 | 14/14 | — | $1.49 |
| R1 | Gemini Flash | 10/14 | total_gap, non_viewable, timezone, components_sum | $0.16 |
| R2a | Gemini Flash | 11/14 | total_gap, non_viewable, components_sum | $0.17 |
| R2b | Gemini Flash | 13/14 | timezone | $0.15 |
| R3a | Gemini Flash | 14/14 | — | $0.19 |
| R3b | Gemini Flash | 10/14 | total_gap, non_viewable, timezone, components_sum | $0.12 |
| t2-k | Gemini Flash | 13/14 | timezone | $0.16 |
| t2-l | Gemini Flash | 10/14 | total_gap, non_viewable, timezone, components_sum | $0.16 |
| t2-m | Gemini Flash | 13/14 | timezone | $0.16 |
| t2-n | Gemini Flash | 13/14 | timezone | $0.19 |
| t2-o | Gemini Flash | 11/14 | total_gap, non_viewable, components_sum | $0.19 |

# References

1. Veneris et al. "APEX-Agents: AI Productivity Index for Agents." arXiv:2601.14242, Jan 2026. (Mercor)
2. Hu et al. "AD-Bench: A Real-World, Trajectory-Aware Advertising Analytics Benchmark for LLM Agents." arXiv:2602.14257, Feb 2026.
3. Artificial Analysis. "AA-Omniscience: Knowledge and Hallucination Benchmark." artificialanalysis.ai/evaluations/omniscience
4. Artificial Analysis. "Long Context Reasoning Benchmark." artificialanalysis.ai/evaluations/artificial-analysis-long-context-reasoning
5. Sierra Research. "tau2-Bench: Evaluating Conversational Agents in a Dual-Control Environment." taubench.com, arxiv:2506.07982
6. Better Stack. "A Look into Gemini 3 Flash: Speed, Smarts, and Hallucination Rate." betterstack.com, Dec 2025.
7. LiveBench. "A Challenging, Contamination-Free LLM Benchmark." livebench.ai, arXiv:2406.19314
8. Zhou et al. "Instruction-Following Evaluation for Large Language Models." arXiv:2311.07911 (IFEval)
9. Agrawal et al. "Finch: Benchmarking Finance & Accounting across Spreadsheet-Centric Enterprise Workflows." arXiv:2512.13168
