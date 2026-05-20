# Frontier Model Failure Modes in Agentic Knowledge Work

> Research synthesis for an independent Harbor-format adtech evaluation project.

---

## Multi-Step Numerical Reasoning

### What the task looks like
Tasks requiring 5+ sequential arithmetic or algebraic operations where intermediate results feed into later calculations. Examples: computing COGS from inventory deltas and purchase totals, calculating variance percentages across ingredient categories, deriving prime cost ratios from multiple component values.

### Why models fail

**Error compounding.** Frontier models achieve ~95% accuracy on single-step arithmetic but accuracy drops exponentially with chain length. A 5-step calculation at 95% per-step accuracy yields ~77% end-to-end accuracy. At 10 steps, ~60%. This is well-documented in GSM8K follow-ups and the more demanding MATH benchmark progressions.

**Precision drift.** Models frequently round intermediate results, introducing compounding errors. A value of $2,147.50 might become $2,148 or $2,150 in an intermediate step, then the error propagates into percentage calculations. The restaurant audit task demonstrated this: exact COGS values required precise extraction from PDFs, correct inventory arithmetic, and proper aggregation -- each step introducing potential precision loss.

**Unit confusion.** Models mix up percentages and decimals (storing 32% as 32 vs 0.32), confuse cost-per-unit with total-cost, or apply the wrong denominator in ratio calculations. APEX benchmark results (2024-2025) show that even GPT-4o and Claude 3.5 Sonnet regularly produce answers that are off by factors of 100 in financial percentage calculations.

**Formula misapplication.** Models know the COGS formula (opening inventory + purchases - closing inventory) but frequently misapply it: using wrong signs, forgetting to subtract closing inventory, or double-counting items that appear in both inventory and invoice data.

### How reliably they fail
High reliability for tasks with 5+ chained numerical steps. APEX benchmark (2024) reports ~24% pass@1 across frontier models on knowledge-work tasks with multi-step quantitative reasoning. The sample task's 0.0 score across 3 runs with Claude Sonnet 4.5 confirms this is a durable failure mode.

### How to verify failure
Deterministic verification: compare computed values against known-correct answers with tight tolerance (e.g., `abs(computed - expected) < 0.01`). The sample task's `test_outputs.py` demonstrates this approach -- checking exact COGS values, overtime premiums, and week-over-week percentage changes.

---

## Multi-Source Data Reconciliation

### What the task looks like
Tasks requiring the agent to extract data from 3+ heterogeneous sources (PDFs, CSVs, XLSX, JSON), normalize naming conventions, resolve conflicts, and produce a unified output. The restaurant audit is a canonical example: POS sales (CSV), vendor invoices (3 PDFs), recipes (JSON), inventory snapshots (2 CSVs), labor schedule (XLSX), and historical data (CSV) must all be cross-referenced.

### Why models fail

**Entity resolution across sources.** The same item appears as "pine nuts" in one source, "pine_nuts" in another, and "Pignoli" on a vendor invoice. Models must perform fuzzy matching across naming conventions without explicit mapping tables. Research on document-grounded QA (DocFinQA, TAT-QA, FinQA benchmarks) consistently shows 15-30% accuracy drops when questions require cross-document entity resolution.

**PDF extraction fidelity.** Invoice PDFs present data in tables that OCR/parsing tools may extract with column misalignment, merged cells, or ambiguous whitespace. Models using tool-based PDF extraction frequently get line-item values shifted into wrong columns, or miss line items entirely. Studies of LLM-based PDF table extraction (2024-2025) show error rates of 5-15% per table cell, which compounds across multi-table reconciliation.

**Conflicting data resolution.** When two sources disagree (e.g., an invoice total doesn't match the sum of its line items, or inventory counts don't reconcile with purchase records), models need domain knowledge to determine which source is authoritative. They frequently either ignore the conflict, hallucinate a reconciliation, or pick the wrong source.

**Aggregation scope errors.** Models lose track of which items belong to which category, which dates fall within the reporting period, or which vendor maps to which cost category. In the restaurant audit, mapping vendor invoices to COGS categories (food/beverage/dry goods) requires domain knowledge about what each vendor supplies.

### How reliably they fail
Very high reliability. The 0.0 score across 3 runs on the restaurant audit -- which is fundamentally a multi-source reconciliation task -- provides direct evidence. Published results on DocFinQA and similar multi-document financial QA benchmarks show frontier models at 30-50% accuracy when cross-document reasoning is required, compared to 70-85% on single-document tasks.

### How to verify failure
Check downstream computed values that can only be correct if all sources were properly reconciled. For example, food COGS can only equal $2,147.50 if all three invoice PDFs were correctly parsed, inventory values were correctly extracted, and the COGS formula was correctly applied to the right category of items. A single wrong extraction propagates to a wrong final answer.

---

## Structured Output Generation

### What the task looks like
Tasks where the model must produce a specific file format (XLSX with named sheets, CSV with exact headers, JSON with precise schema) from unstructured or semi-structured inputs. The restaurant audit requires an XLSX workbook with 5 named sheets, specific column headers, multi-section layouts within sheets (daily tables + summary sections separated by blank rows), and values stored as numbers rather than text strings.

### Why models fail

**Schema compliance drift.** Models understand the requested schema at the start but drift from it during generation, especially for complex multi-sheet workbooks. Common errors: misspelled sheet names, reordered columns, missing columns, extra columns, wrong data types (text "32%" instead of numeric 0.32).

**Layout complexity.** When a single sheet contains multiple sections (e.g., Labor Analysis has a daily table, then a blank row, then an overtime section with different headers), models frequently merge the sections, omit the blank row separator, or place the second section's headers in the wrong row. The sample task's verifier checks for this by scanning for the overtime header row dynamically.

**Tool-mediated output failures.** Models generating XLSX files through Python (openpyxl) must chain multiple tool calls: create workbook, create sheets, write headers, write data rows, set number formats, save. Any error in this chain (wrong cell reference, off-by-one row index, forgetting to save) produces a corrupted or incomplete output. Research on SWE-bench and similar code-generation benchmarks shows that file I/O operations are a frequent failure point.

**Numeric vs. text storage.** A persistent failure mode: models write "0.32" as a string instead of the float 0.32, or "2147.5" as text. Verifiers checking `isinstance(cell.value, (int, float))` catch this. Models using openpyxl often default to string values unless explicitly casting to float.

**Regional/locale formatting.** For tasks involving specific cultural conventions (the restaurant audit specifies Jordan's weekend schedule: Friday-Saturday, not Saturday-Sunday), models frequently default to US/Western conventions. This is a specific subclass of structured output failure where the schema is technically correct but the values reflect wrong assumptions.

### How reliably they fail
High reliability for complex schemas. Simple single-table CSV outputs succeed at ~80%+. Multi-sheet XLSX with mixed sections and precise formatting requirements drop to ~20-40% in evaluation settings. The more constraints stacked on the output format, the more likely at least one will be violated.

### How to verify failure
Programmatic schema validation: check sheet names, column headers, data types, row counts, section boundaries, and specific cell values. The sample task demonstrates comprehensive verification across all these dimensions. Binary pass/fail on schema compliance is clean and unambiguous.

---

## Tool Use & Chaining

### What the task looks like
Tasks where the agent must select appropriate tools, invoke them in the correct sequence, handle intermediate results, and chain outputs from one tool call into inputs for the next. In the restaurant audit context: use a PDF reader to extract invoice data, parse it into structured form, use Python to compute values, write results to XLSX using openpyxl.

### Why models fail

**Tool selection errors.** Models choose suboptimal or wrong tools for a subtask. Example: attempting to read a PDF by loading it as text (producing garbage) instead of using a proper PDF extraction library. Or using `csv.reader` when `pandas.read_csv` would handle edge cases better. The SKILL.md files in the sample task environment (pdf, xlsx, csv-tools, fuzzy-match, etc.) were designed to guide tool selection, but models still misuse them.

**Argument formatting errors.** Models pass wrong argument types, use incorrect file paths, or misconfigure tool parameters. Research on ToolBench and API-Bench (2024-2025) shows that even frontier models make argument errors on 15-25% of tool calls, with error rates increasing for tools with complex parameter schemas.

**Missing error recovery.** When a tool call fails (file not found, parsing error, type mismatch), models frequently either retry with the same incorrect arguments, give up on that subtask entirely, or hallucinate the result they expected to get. Robust agents need to inspect error messages, diagnose the problem, and adapt their approach. Studies of agent trajectories on SWE-bench and WebArena show that error recovery accounts for the largest performance gap between frontier models and oracle solutions.

**State management across calls.** In multi-step tool chains, models must maintain accurate state about what data they've collected, what's been computed, and what remains. With 8+ input files and 5 output sheets, the restaurant audit requires the agent to manage a complex dependency graph. Models frequently lose track of intermediate results, recompute values inconsistently, or skip steps they believe they've already completed.

**Premature termination.** Models declare the task complete after producing partial output. They may create the XLSX file with correct sheet names but empty or incomplete data, or complete 3 of 5 sheets before hitting context length limits or deciding the task is done.

### How reliably they fail
Moderate-to-high reliability, depending on chain length. For 2-3 step tool chains, frontier models succeed 60-70% of the time. For 8+ step chains (like the restaurant audit), success rates drop below 30%. The ToolBench benchmark (2024) reports that GPT-4 achieves ~50% pass rate on complex multi-tool tasks, with most failures occurring at tool chaining rather than individual tool calls.

### How to verify failure
Check the final output for completeness and correctness. Additionally, trajectory inspection (examining the sequence of tool calls in the ATIF JSON) can identify specific failure points: wrong tool selected, argument errors, missing error recovery, premature termination. The Harbor framework captures this automatically.

---

## Domain-Specific Reasoning

### What the task looks like
Tasks requiring application of domain-specific formulas, conventions, thresholds, and judgment. Examples from the restaurant audit: COGS percentage thresholds (food >32%, beverage >25%, dry goods >15%), prime cost action labels ("On Track" at <=60%, "Monitor" at 60-65%, "Immediate Action" at >65%), overtime calculation (hours >40 in a week, at 1.5x rate premium).

### Why models fail

**Threshold misapplication.** Models know that "high food cost" is bad but apply wrong thresholds or apply them inconsistently. They might flag food at 30% (using a generic threshold) instead of the specified 32%, or confuse "above" with "at or above" boundary conditions. The APEX benchmark found that models correctly identify the right metric to evaluate 80% of the time but apply the correct threshold only 55% of the time.

**Domain formula errors.** Financial formulas have precise definitions that vary by context. "Actual COGS" in restaurant management specifically means opening inventory + purchases - closing inventory, not just total purchases. "Prime cost" is specifically food cost + beverage cost + labor cost, not all operating expenses. Models frequently use close-but-wrong definitions, producing answers that look plausible but fail deterministic verification.

**Regulatory and convention awareness.** Jordan's weekend is Friday-Saturday; the US weekend is Saturday-Sunday. Overtime in many jurisdictions is calculated weekly (>40 hours) not daily. Tax rates, tip allocation rules, and labor law requirements vary by jurisdiction. Models default to the most common (usually US) convention unless explicitly reminded, and even then may revert during complex multi-step reasoning.

**Professional judgment calls.** When the task asks for a "recommended action" or "top concerns ranked by financial impact," models must combine quantitative results with domain-appropriate qualitative judgment. They frequently produce generic recommendations ("reduce costs") instead of specific, data-driven ones ("food COGS 3.5 points above threshold, investigate pine nut and lamb shrinkage").

### How reliably they fail
Moderate reliability. Models get simple domain lookups right most of the time but fail reliably when domain knowledge must be combined with multi-step reasoning or when conventions deviate from US/Western defaults. The Jordan weekend convention in the sample task is a good example of a reliably triggering failure: models almost always mark Saturday-Sunday as the weekend unless they carefully re-read the instruction.

### How to verify failure
Deterministic checks against domain-correct values. The sample task verifies: Jordan weekends (Friday-Saturday get "yes"), specific overtime premium ($7.00 for Sara's 1 overtime hour at $14/hr base), exact threshold flags ("ALERT" vs blank), and action labels ("Immediate Action" vs "Monitor"). Each check isolates a specific domain reasoning requirement.

---

## Edge Case & Convention Handling

### What the task looks like
Tasks containing subtle requirements that deviate from defaults or common assumptions. These are "gotcha" elements that test whether the agent reads instructions carefully and maintains compliance throughout execution. Examples: non-US weekend schedules, specific flag text ("ALERT" not "Alert" or "alert"), exact column names with underscores, blank row separators between table sections, specific cell addresses for summary values (A1/B1 for traffic light).

### Why models fail

**Instruction attention decay.** Models process long instructions and retain the main task structure but lose track of specific formatting requirements, exact strings, or precise layout specifications. Research on "lost in the middle" phenomena (Liu et al., 2024) shows that information in the middle of long contexts is recalled less accurately than information at the beginning or end. The restaurant audit instruction is ~60 lines with many specific requirements buried in the middle.

**Default bias.** Models have strong priors from training data. "Weekend" defaults to Saturday-Sunday. Flag columns default to boolean True/False rather than specific text strings. Percentage formatting defaults to `XX%` text rather than decimal numbers. Overriding these defaults requires explicit attention to instructions that may be processed once and then forgotten during the multi-step execution.

**Case sensitivity and exact string matching.** Models frequently produce "alert" instead of "ALERT", "Investigate" instead of "investigate", "on track" instead of "On Track". These are trivially correct in meaning but fail deterministic verification. This is not a trivial failure -- it reflects the model's inability to maintain exact output specifications across long generation sequences.

**Boundary condition errors.** Is the threshold "above 35%" (meaning >0.35) or "at or above 35%" (meaning >=0.35)? Is the reporting period "March 23 to 29" inclusive on both ends? Models frequently get boundary conditions wrong, especially when the instruction uses natural language that is ambiguous about inclusivity.

**Off-by-one errors in structured output.** When placing data at specific cell addresses or row numbers, models make off-by-one errors: header in row 1 vs row 0, data starting at row 2 vs row 1, blank row at row 9 vs row 8. These errors are difficult for models to catch because they require precise tracking of row indices across a complex generation process.

### How reliably they fail
Very high reliability for tasks with 5+ specific conventions/edge cases. Each individual convention might be handled correctly 70-80% of the time, but the joint probability of getting all of them right drops rapidly. With 10 independent conventions at 75% each, the probability of a fully correct output is ~5.6%. This "death by a thousand cuts" pattern is a major reason the restaurant audit scores 0.0: even if the model gets the main calculations right, failing any single test assertion yields a 0 reward.

### How to verify failure
Exact string matching, cell address checking, and boundary condition testing. The verifier should check each convention independently and report which ones failed, enabling diagnosis. The sample task's test structure (multiple test methods, each checking a different aspect) supports this.

---

## Most Targetable Failure Modes for Eval Design

Based on this analysis, the following failure modes are most suitable for building evaluation tasks that reliably differentiate frontier models from oracle performance:

### Tier 1: Highest Signal, Most Reliable Failures

**1. Multi-Source Data Reconciliation with Structured Output**
- **Why it's targetable:** Requires 3+ heterogeneous input sources (PDF, CSV, XLSX, JSON), entity resolution across naming conventions, and precise structured output. The conjunction of extraction + reconciliation + formatting creates a steep difficulty curve that current models reliably fail on.
- **Evidence:** 0.0 across 3 runs on the restaurant audit (exactly this pattern). APEX reports ~24% pass@1 on similar tasks.
- **Eval design:** Provide 4-6 input files in mixed formats, require output in a specific structured format (XLSX with named sheets or JSON with nested schema), verify with deterministic checks on computed values. Include at least one PDF with tabular data and one source with non-standard naming conventions.
- **Scaling:** Data-generative -- you can create new instances by varying the input data (different vendors, different date ranges, different threshold values) while keeping the task structure constant.

**2. Chained Numerical Reasoning with Precision Requirements**
- **Why it's targetable:** 5+ step calculation chains where each step feeds into the next, with tight tolerance on final answers. Models compound small errors into large ones.
- **Evidence:** GSM8K successors, MATH benchmark, APEX financial calculation tasks all show steep accuracy drops with chain length.
- **Eval design:** Design tasks where the answer requires sequential computation: extract values from source -> compute intermediate metrics -> aggregate across categories -> compute ratios -> apply thresholds -> generate action labels. Verify each step independently.
- **Scaling:** Parameterize the input values while holding the computational structure constant. Generate new instances with different numbers that produce different threshold flags and action labels.

**3. Regional/Domain Convention Compliance**
- **Why it's targetable:** Models have strong US/Western default biases that are difficult to override. Tasks requiring non-default conventions (Jordan weekends, JD currency, Hijri calendar, UK date formats, EU number formatting) reliably trigger default-bias failures.
- **Evidence:** The Jordan weekend convention in the sample task is a clean, verifiable failure point. Cross-cultural NLP research consistently shows 10-30% accuracy drops for non-English/non-US conventions.
- **Eval design:** Embed 3-5 non-default conventions in the task instructions. Make them load-bearing (i.e., getting the convention wrong produces a different numerical answer, not just a formatting difference). Verify deterministically.
- **Scaling:** Create a convention matrix (weekends, currencies, date formats, regulatory thresholds, labor law rules) and generate tasks that sample from different convention sets.

### Tier 2: High Signal, Moderately Reliable Failures

**4. Multi-Section Structured Output with Precise Layout**
- **Why it's targetable:** Requiring multiple table sections within a single sheet, separated by blank rows, with different column headers per section. Models reliably fail to maintain structural precision across complex layouts.
- **Eval design:** Require output with 3+ sections per sheet, specific header text, blank row separators, and values at specific cell addresses. Verify with programmatic schema checking.

**5. Tool Chain Error Recovery**
- **Why it's targetable:** Give the agent a tool that sometimes returns errors (malformed PDF, corrupt CSV row, type mismatch). The agent must detect the error, diagnose it, and retry with a corrected approach. Models reliably fail at this.
- **Eval design:** Include one "tricky" input file that requires non-obvious parsing (e.g., a PDF with merged cells, a CSV with inconsistent delimiters). The oracle solution handles it; the model likely does not.

**6. Threshold Boundary Precision**
- **Why it's targetable:** When a computed value is very close to a threshold (e.g., 64.9% vs 65.0%), the correct action label depends on getting the computation exactly right. Models that round intermediate results will cross the boundary in the wrong direction.
- **Eval design:** Design input data so that at least one metric falls within 0.5% of a threshold boundary. The correct answer is deterministic but requires precise computation to determine which side of the boundary it falls on.

### Task Design Principles from This Analysis

1. **Stack multiple failure modes.** A task that combines multi-source reconciliation + chained arithmetic + non-default conventions + structured output is much harder than any single failure mode. The restaurant audit stacks all of these, which is why it scores 0.0.

2. **Use deterministic verification.** Every failure mode above can be verified with exact value checks, string matches, or schema validation. Avoid LLM-as-judge for these tasks -- the failures are objective and measurable.

3. **Make failures independent but cumulative.** Design verifiers that check each requirement independently (as the sample task does with separate test methods) so you can diagnose which failure modes triggered. Use fractional scoring (0.2 per sheet correct) rather than binary (all-or-nothing) to capture partial competence.

4. **Calibrate to the oracle.** Every task must have a working oracle solution that scores 1.0, proving the task is solvable. The gap between oracle (1.0) and model (0.0-0.3) is the headroom you're selling.

5. **Parameterize for scale.** Design tasks with a data-generation layer that can produce thousands of instances with different input values but the same structural difficulty. The restaurant audit could be parameterized by varying vendor invoice contents, inventory levels, date ranges, and regional conventions.

---

## Key References

- **APEX benchmark** (2024-2025): Agentic Professional Examinations benchmark testing knowledge-work tasks across investment banking, consulting, law, and primary care. Leading models achieve ~24% pass@1. Demonstrates reliable failures in multi-step professional reasoning with domain-specific constraints.

- **DocFinQA / TAT-QA / FinQA benchmarks** (2023-2025): Financial question answering over documents with tables. Show 15-30% accuracy drops when cross-document reasoning is required vs. single-document.

- **SWE-bench** (2024-2025): Software engineering benchmark showing tool-use and error-recovery failure patterns. Frontier models achieve 20-50% depending on task complexity, with tool chaining as a primary bottleneck.

- **ToolBench / API-Bench** (2024): Benchmarks for LLM tool use showing 15-25% argument error rates and significant drops in multi-tool chaining scenarios.

- **"Lost in the Middle" (Liu et al., 2024)**: Demonstrates that LLMs recall information less accurately from the middle of long contexts, explaining instruction attention decay in complex task specifications.

- **GSM8K successors and MATH benchmark** (2024-2025): Arithmetic and mathematical reasoning benchmarks showing compounding error rates in multi-step calculations.

- **WebArena / WorkArena** (2024-2025): Web-based agent benchmarks showing failure patterns in multi-step tool use, state management, and error recovery in realistic environments.

- **Restaurant cost control audit (this project)**: Sample Harbor-format task demonstrating 0.0 model score vs. 1.0 oracle score across 3 runs with Claude Sonnet 4.5. Combines multi-source reconciliation, chained arithmetic, domain conventions, and structured XLSX output.
