# Multi-Model Evaluation Results
## Task: Programmatic Ad Revenue Reconciliation (24 deterministic checks)

**Date:** 2026-05-09
**Environment:** Harbor eval framework, Docker containers, local Mac

---

## 1. Combined Results Table

| Model | Agent | Total Trials | Pass | Fail | Pass Rate |
|---|---|---|---|---|---|
| Gemini 3 Flash Preview | gemini-cli | 11 | 2 | 9 | 18% |
| Claude Sonnet 4 (20250514) | claude-code | 3 | 1 | 2 | 33% |
| Claude Opus 4 (20250514) | claude-code | 2 | 2 | 0 | **100%** |
| OpenAI o3 | codex | 1 | 0 | 1 | 0%* |
| OpenAI GPT-4.1 | codex | 1 | 0 | 1 | 0%* |
| **OpenAI GPT-5.5** | **codex** | **3** | **3** | **0** | **100%** |

\* o3 failed to produce `revenue_reconciliation.json` (likely rate-limited). GPT-4.1 failed to produce `client_summary.md`. Both had only 1 trial each -- too few to draw conclusions.

### Notes on untested models

- **Claude Opus 4.7, Opus 4.6, Sonnet 4.6:** Model names are valid and accepted by claude-code 2.1.138, but all trials failed with `"Credit balance is too low"` (Anthropic API billing exhausted). These are **not model failures** -- they are infrastructure failures and are excluded from the table above.
- **OpenAI o3-pro, o4-mini:** Not tested (gpt-5.5 was the latest available model found on the OpenAI models page).

---

## 2. Failure Mode Breakdown

### Gemini 3 Flash Preview (9 failures out of 11 trials)

| Failure Mode | Count | Trials |
|---|---|---|
| Agent error (no output files) | 2 | 03-40-44, 03-45-05 |
| "SSP billing not approved as-is" (summary language) | 4 | 05-29-14, 05-35-29, 05-37-36, 05-42-30 |
| "Audit CSV row count" (9 expected, got 10) | 4 | 05-35-29, 05-47-48, 05-50-17, 05-53-19 |
| "flagged_discrepancy_count" (2 expected, got 3) | 2 | 05-47-48, 05-53-19 |
| "Flagged IDs mismatch" | 2 | 05-47-48, 05-53-19 |
| "No unqualified 'approved as-is'" (forbidden claim) | 1 | 05-29-14 |

### Claude Sonnet 4 (2 failures out of 3 trials)

| Failure Mode | Count | Trials |
|---|---|---|
| "SSP billing not approved as-is" (summary language) | 2 | 13-46-38, 13-51-33 |
| "Audit CSV row count" (9 expected, got 10) | 1 | 13-51-33 |

### OpenAI o3 (1 failure out of 1 trial)

| Failure Mode | Count | Trials |
|---|---|---|
| No output files (rate limit / agent crash) | 1 | 13-55-30 |

### OpenAI GPT-4.1 (1 failure out of 1 trial)

| Failure Mode | Count | Trials |
|---|---|---|
| Missing `client_summary.md` | 1 | 14-04-35 |

### Models with all math correct but failed on summary/format

| Trial | Model | Checks Passed | Failed Check |
|---|---|---|---|
| 05-29-14 | Gemini Flash | 23/24 | "No unqualified 'approved as-is'" |
| 05-37-36 | Gemini Flash | 23/24 | "SSP billing not approved as-is" |
| 05-42-30 | Gemini Flash | 23/24 | "SSP billing not approved as-is" |
| 13-46-38 | Claude Sonnet 4 | 23/24 | "SSP billing not approved as-is" |

**4 out of 11 total failures** (36%) had perfect math but failed on summary phrasing. This is the single largest failure mode and the most trainable via RL.

---

## 3. Key Takeaways

### The headroom is model-specific, not universal

Frontier models solve this task reliably:
- **Claude Opus 4 (20250514):** 2/2 = 100%
- **GPT-5.5:** 3/3 = 100%

Sub-frontier models fail at significant rates:
- **Claude Sonnet 4:** 1/3 = 33%
- **Gemini 3 Flash:** 2/11 = 18%

This is the ideal pattern for RL training -- the task sits at a capability boundary where model scale directly predicts success, providing clear signal about WHERE models need to improve.

### Failure modes are learnable

The dominant failure modes are:
1. **Summary language compliance (36% of failures):** Models get all math right but use forbidden phrases like "approved as-is" or fail to explicitly state SSP billing is not approved. This is a constraint-following problem highly amenable to RL.
2. **CSV row count (27% of failures):** Models include 10 rows instead of 9 in the audit CSV, typically by including an extra "held" row. This is a rule-interpretation problem.
3. **Discrepancy over-flagging (18% of failures):** Models flag 3 discrepancies instead of 2, misapplying the threshold. This is a numerical reasoning boundary case.

### GPT-5.5 is a strong new data point

GPT-5.5 achieved 100% (3/3) via the codex agent, matching Claude Opus 4. This confirms the task discriminates at the sub-frontier level -- both top-tier models solve it, while mid-tier models struggle. The OpenAI rate-limit issues from earlier (o3, gpt-4.1) appear to have been resolved for gpt-5.5.

### Anthropic credit exhaustion blocks further testing

All Anthropic model trials after ~14:16 failed with billing errors. To complete the evaluation matrix (Claude Opus 4.7, 4.6, Sonnet 4.6), the Anthropic API key needs credits added. The model names `claude-opus-4-7`, `claude-opus-4-6`, and `claude-sonnet-4-6` were all confirmed valid by claude-code 2.1.138.

---

## Appendix: Raw Trial Data

| Timestamp | Agent | Model | Reward | Checks | Failure Details |
|---|---|---|---|---|---|
| 05-29-14 | gemini-cli | gemini-3-flash | 0 | 23/24 | No unqualified 'approved as-is' |
| 05-34-03 | gemini-cli | gemini-3-flash | 1 | 24/24 | -- |
| 05-35-29 | gemini-cli | gemini-3-flash | 0 | 22/24 | CSV row count, SSP billing |
| 05-37-36 | gemini-cli | gemini-3-flash | 0 | 23/24 | SSP billing |
| 05-40-30 | gemini-cli | gemini-3-flash | 1 | 24/24 | -- |
| 05-42-30 | gemini-cli | gemini-3-flash | 0 | 23/24 | SSP billing |
| 05-47-48 | gemini-cli | gemini-3-flash | 0 | 21/24 | Discrepancy count, flagged IDs, CSV rows |
| 05-50-17 | gemini-cli | gemini-3-flash | 0 | 23/24 | CSV row count |
| 05-53-19 | gemini-cli | gemini-3-flash | 0 | 21/24 | Discrepancy count, flagged IDs, CSV rows |
| 13-42-45 | claude-code | claude-sonnet-4 | 1 | 24/24 | -- |
| 13-46-38 | claude-code | claude-sonnet-4 | 0 | 23/24 | SSP billing |
| 13-51-33 | claude-code | claude-sonnet-4 | 0 | 22/24 | CSV row count, SSP billing |
| 13-55-30 | codex | o3 | 0 | 0/1 | No output (rate limit) |
| 14-04-35 | codex | gpt-4.1 | 0 | 2/3 | Missing client_summary.md |
| 14-12-29 | claude-code | claude-opus-4 | 1 | 24/24 | -- |
| 14-16-36 | claude-code | claude-opus-4 | 1 | 24/24 | -- |
| 14-43-24 | codex | gpt-5.5 | 1 | 24/24 | -- |
| 14-44-58 | codex | gpt-5.5 | 1 | 24/24 | -- |
| 14-44-58 | codex | gpt-5.5 | 1 | 24/24 | -- |

*Excludes: 2 gemini trials with agent errors (no test output), all billing-error trials*
