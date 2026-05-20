# APEX-Agents & Knowledge-Work Agentic Benchmarks

## APEX-Agents Overview

**Paper:** "APEX-Agents" (arXiv:2601.14242, Jan 2026) by Bertie Vidgen et al. (Mercor)
**Benchmark size:** 480 tasks (n=480), open-sourced with all prompts, rubrics, gold outputs, files, and metadata
**Infrastructure:** Archipelago (open-source agent execution and evaluation framework)
**License:** CC-BY on Hugging Face (mercor/apex-agents)

### What It Tests

APEX-Agents assesses whether AI agents can execute **long-horizon, cross-application tasks** in professional services. Unlike APEX-v1-extended (which tests single-turn model responses), APEX-Agents requires agents to:

- Navigate realistic work environments with files and tools
- Manage complex file systems (designed with Box to simulate real-world data rooms)
- Produce outputs that would justify a professional fee ("client-ready" work)
- Handle workplace context that is messy, incomplete, and spread across documents and chat threads

### Four Domains

| Domain | Tasks | Description |
|--------|-------|-------------|
| **Investment Banking** | ~120 | Financial modeling, DCF updates, stock price analysis, valuation calculations |
| **Management Consulting** | ~120 | Capital budget allocation, market analysis, strategic recommendations using matrix frameworks |
| **Corporate Law (Big Law)** | ~120 | Force majeure analysis, contract review, regulatory penalty assessment, legal document analysis |
| **Primary Care Medicine** | ~120 | Clinical assessments, diagnostic reasoning, treatment recommendations |

Note: The Artificial Analysis implementation (APEX-Agents-AA) evaluates 452 tasks, excluding two Investment Banking "worlds" with external API dependencies.

### How Tasks Are Designed

1. **Surveys:** Hundreds of experts from Goldman Sachs, McKinsey, Cravath surveyed on how they spend time
2. **Scenarios:** Mercor experts (VPs, MDs, Managers with 5-10 years experience) built realistic Google Workspace scenarios simulating week-long projects
3. **Task creation:** Experts defined specific tasks with exact grading criteria (1-10 pass/fail criteria per task)
4. **Validation:** Harvey AI validated the law tasks for realism and complexity

### Scoring Methodology

- **Rubric-based grading:** Each rubric decomposes response quality into discrete, objective criteria assessed as Pass or Fail (analogous to unit tests for code)
- **LM judge:** Gemini 2.5 Flash grades responses against expert-generated criteria
- **Pass@1:** Primary metric -- share of tasks where model fully satisfies ALL grading rubric criteria
- **Mean rubric score:** Secondary metric -- mean percentage of criteria satisfied across all tasks
- **8 runs per task:** Each prompt sent to model 8 times, mean taken for reliability
- **Source documents:** Averaging ~26,000 tokens per case

---

## Category-Level Performance Breakdown

### APEX-Agents (Agentic, Jan 2026) -- Pass@1 Scores

From the original paper leaderboard:

| Model | Pass@1 |
|-------|--------|
| Gemini 3 Flash (Thinking=High) | 24.0% |
| GPT-5.2 (Thinking=High) | ~23% |
| Claude Opus 4.5 (Thinking=High) | ~22% |
| Gemini 3 Pro (Thinking=High) | ~21% |

**Key finding:** Even with 8 tries (pass@8), the best agents can only complete ~40% of tasks.

### APEX-Agents-AA (Artificial Analysis, Latest May 2026)

| Model | Pass@1 | Tokens Used |
|-------|--------|-------------|
| GPT-5.5 (xhigh) | **37.7%** | ~250M |
| GPT-5.4 (xhigh) | 33.3% | ~370M |
| Claude Opus 4.6 (max) | 33.0% | ~180M |
| Gemini 3.1 Pro Preview | 32.0% | ~260M |
| GPT-5.4 mini (xhigh) | 28.2% | ~420M |
| Claude Sonnet 4.6 (max) | 28.0% | ~290M |
| Gemini 3 Flash | 27.7% | ~1.1B |
| GPT-5.4 nano (xhigh) | 24.9% | ~1.3B |
| Qwen3.5 397B A17B | 15.3% | ~270M |
| DeepSeek V3.2 | 14.5% | ~390M |
| MiniMax-M2.7 | 10.6% | ~440M |
| gpt-oss-120B (high) | 3.1% | ~670M |
| NVIDIA Nemotron 3 Super | 1.8% | ~77M |
| gpt-oss-20B (high) | 0.7% | ~65M |

**Observation:** Even the best model (GPT-5.5) only achieves 37.7% pass@1 as of May 2026. Open-source models dramatically underperform (Qwen at 15.3%, DeepSeek at 14.5%).

### APEX-v1-extended (Non-Agentic, Single-Turn) -- Domain Breakdown

From the APEX-v1-extended paper (arXiv:2509.25721), which provides the clearest per-domain performance data:

| Model | Overall | Invest. Banking | Law | Mgmt. Consulting | Medicine |
|-------|---------|----------------|-----|-------------------|----------|
| GPT 5 (High) | **67.0%** | 61.3% | **77.9%** | 63.1% | 65.5% |
| Gemini 3 Pro (High) | 64.3% | **63.0%** | 68.5% | **64.0%** | 61.6% |
| Grok 4 | 63.5% | 59.6% | 70.2% | 59.8% | 64.3% |
| o3 (On) | 63.5% | 57.7% | 75.5% | 59.0% | 61.5% |
| Opus 4.5 (On) | 63.1% | 55.2% | 74.0% | 58.4% | 64.6% |
| Sonnet 4.5 (On) | 57.2% | 45.7% | 72.4% | 50.7% | 59.6% |
| GPT 5.1 (High) | 59.4% | 44.3% | 77.4% | 51.9% | 64.0% |
| Gemini 2.5 Pro (On) | 59.4% | 54.1% | 68.5% | 58.9% | 55.8% |
| Gemini 2.5 Flash (On) | 57.3% | 51.1% | 68.8% | 55.6% | 53.6% |
| Opus 4.1 (On) | 51.4% | 42.0% | 61.8% | 49.4% | 52.1% |

**Domain difficulty ranking (hardest to easiest):**
1. **Investment Banking** -- top score 63.0% (hardest)
2. **Management Consulting** -- top score 64.0%
3. **Medicine** -- top score 65.5%
4. **Law** -- top score 77.9% (easiest, but still far from 100%)

### Key Dataset Statistics (APEX-v1-extended)

| Metric | Medicine | Law | Mgmt Consulting | Investment Banking | Mean |
|--------|----------|-----|------------------|--------------------|------|
| Cases (heldout) | 100 | 100 | 100 | 100 | 100 |
| Mean criteria/case | 18.39 | 13.98 | 14.71 | 12.17 | 14.81 |
| Mean sources/case | 3.77 | 4.79 | 3.21 | 3.01 | 3.70 |
| Mean tokens in prompt | 177 | 407 | 409 | 439 | 358 |

**Mean time for human expert:** 2.7 hours per task (range: 0.5 to 20 hours)
**Source file types:** PDF, XLSX, TXT, DOCX, CSV (up to 100,000 tokens combined)

---

## Specific Failure Modes in APEX-Agents

### Primary Failure Modes (from Mercor blog and paper)

1. **Ambiguity Management Failure:** Agents cannot handle workplace context that is messy, incomplete, and spread across documents and chat threads. When instructions are ambiguous (as real professional work always is), agents either hallucinate answers or fail to ask clarifying questions.

2. **File Navigation Failure:** Agents cannot find the right file in a complex file system. Real workplaces have deeply nested folder structures, inconsistent naming, and files spread across multiple locations. Agents struggle to locate relevant documents in datarooms.

3. **Cross-Workflow Context Loss:** Agents fail to hold context across the entire workflow. Professional tasks often require synthesizing information from multiple documents, applying it to a specific framework, and producing a coherent deliverable. Agents lose track of intermediate results.

4. **Multi-Step Numerical Reasoning:** Investment banking tasks require chaining multiple calculations (e.g., look up stock prices, apply a premium, input into a DCF model, recalculate cost of equity and after-tax cost of debt). Agents make errors in multi-step quantitative chains.

5. **Domain-Specific Framework Application:** Management consulting tasks require applying specific analytical frameworks (e.g., Amensa market matrix, competitor landscape analysis, BU allocation scores). Agents fail to correctly identify and apply the right framework from provided materials.

6. **Legal Reasoning with Precedent:** Law tasks require analyzing specific legal provisions (e.g., force majeure clauses) and applying case law precedent. Agents struggle with nuanced legal interpretation that requires cross-referencing multiple documents.

### Why Investment Banking Is Hardest

- Requires precise numerical calculations chained across multiple steps
- Financial models (XLSX) must be understood structurally, not just textually
- Real-time data lookups (stock prices for specific date ranges) add complexity
- Formulas and cell references in spreadsheets must be correctly traced
- Small numerical errors cascade through entire models

### Why Law Scores Highest (But Still Has Headroom)

- Legal analysis is more text-based and pattern-matching friendly
- Contract clause identification maps well to LLM text understanding
- But: complex multi-document legal reasoning (cross-referencing agreements, case law, and regulations) still fails frequently
- Tasks requiring novel legal argument construction vs. fact extraction show a significant gap

### Per-Task Variance

- Mean standard deviation across 8 runs per task: **9.05 percentage points** (range: 8.25 for Opus 4.5 to 9.5 for Grok 4)
- Model scores range from 0% to 100% across individual tasks, indicating high task-level variance
- Some tasks are essentially unsolvable by any model; others are consistently solved

---

## Other Relevant Benchmarks (with Scores)

### APEX-v1 / APEX-v1-extended (Mercor, Sep-Dec 2025)
- **Type:** Single-turn knowledge work (non-agentic)
- **Domains:** Same four (IB, consulting, law, medicine)
- **Top score:** GPT 5 at 67.0% mean rubric score
- **Key insight:** Even without agentic complexity, models fail ~33% of rubric criteria on professional tasks
- **Original v1.0 domain scores:** Medicine 47.5%, IB 47.6%, Consulting 52.6%, Law 56.9% (before extended)

### SWE-bench Verified
- **Type:** Software engineering -- resolve real GitHub issues
- **Top scores (late 2025/early 2026):** Frontier models crossed ~80% range
- **Key failures:** Complex multi-file refactoring, understanding large codebases, test generation
- **Relevance:** High -- shows agentic coding is further ahead than agentic knowledge work, making APEX-style tasks a bigger headroom opportunity

### GAIA (General AI Assistants)
- **Type:** Real-world assistant tasks requiring multi-step reasoning, tool use, web browsing
- **Levels:** 1 (simple) to 3 (complex, multi-step)
- **Key failures:** Multi-hop reasoning across sources, combining information from different modalities
- **Relevance:** High -- tests multi-document reasoning and cross-referencing, similar to APEX failure modes

### TAU-bench (Sierra, 2024-2026)
- **Type:** Dynamic conversational AI benchmark simulating customer service (airline, retail)
- **Key design:** Both agent and user are simulated; tests modifying shared world state
- **Top score (Airline):** Claude Sonnet 4.5 at 0.700 (70%)
- **Key failures:** Maintaining conversation state, correctly applying business rules, handling edge cases in policy
- **tau2-bench:** Extended to dual-control (agent + user) with telecom domain
- **Relevance:** Medium -- tests procedural knowledge application but in narrower domain than APEX

### WebArena
- **Type:** Web browsing agent benchmark
- **Tasks:** Complete tasks on realistic websites (shopping, forums, content management)
- **Scores:** Improving rapidly; frontier models approaching high performance
- **Key failures:** Multi-step navigation, form filling with constraints, handling dynamic content
- **Relevance:** Medium -- tests agentic web interaction but not professional knowledge work

### OSWorld
- **Type:** Full desktop OS interaction (open-ended tasks)
- **Tasks:** Multi-step tasks across real applications (spreadsheets, browsers, terminals)
- **Key failures:** Complex multi-application workflows, maintaining state across apps
- **Human baseline:** Models still below human performance despite gains from 2025 to 2026
- **Relevance:** High for agentic aspects -- similar to APEX's requirement to navigate files and tools

### BigLaw Bench (Harvey, 2024)
- **Type:** Legal task evaluation (LLM-specific)
- **Key insight:** One of few domain-specific professional benchmarks; Harvey used it to validate that law tasks are realistic
- **Relevance:** High -- directly comparable to APEX law domain; shows legal AI evaluation is an active area

### GDPval (OpenAI, 2025)
- **Type:** Economic value measurement across 44 occupations, 9 industries
- **Design:** Real-world tasks with Elo ratings from blind pairwise comparisons
- **Relevance:** High -- similar philosophy to APEX (measuring economic productivity), broader occupational coverage

### Terminal-Bench Hard
- **Type:** Agentic benchmark for terminal/shell environments
- **Tasks:** Software engineering, system administration, data processing
- **Relevance:** Medium -- tests agentic capabilities but in technical domain

### HealthBench (Arora et al., 2025)
- **Type:** Medical/health LLM evaluation
- **Referenced in:** APEX-v1-extended paper
- **Relevance:** Medium -- complements APEX medicine domain

---

## Cross-Cutting Failure Patterns

Analyzing across APEX-Agents, GAIA, TAU-bench, OSWorld, and related benchmarks, the following failure patterns emerge consistently:

### 1. Multi-Document Synthesis Failure
- Models can extract information from individual documents but fail to **synthesize across multiple sources**
- APEX: Consulting tasks requiring cross-referencing market matrix + competitor landscape + operational constraints
- GAIA Level 3: Multi-hop reasoning across different information sources
- This is the single most consistent failure mode across all knowledge-work benchmarks

### 2. Structured Output from Messy Inputs
- Models receive unstructured or semi-structured inputs (financial models, legal contracts, medical records) and must produce precisely structured outputs
- APEX IB: Parse XLSX financial models, extract specific values, chain calculations, output formatted results
- APEX Consulting: Navigate heatmaps, matrices, and metric files to compute budget allocations to 3 decimal places
- Key issue: Bridging from the "fuzzy" understanding of documents to the "precise" requirements of professional deliverables

### 3. Long-Horizon Planning and Execution
- Tasks that require many sequential steps with dependencies between them
- APEX-Agents pass@1 is dramatically lower than APEX-v1 mean score -- the agentic wrapper adds significant failure probability at each step
- Even with 8 attempts, best pass@8 is only ~40%
- Each additional step in a plan compounds error probability

### 4. Numerical Precision in Context
- Not just arithmetic, but knowing WHICH numbers to use, from WHERE in the documents, and HOW to combine them
- Investment banking is hardest precisely because it demands numerical precision chained across multiple documents
- Consulting budget allocation example: must convert percentages to decimals, compute products, normalize across units, round correctly

### 5. Ambiguity Resolution Without Clarification
- Real professional work is inherently ambiguous; experts use judgment and domain knowledge to resolve ambiguity
- Models either: (a) hallucinate a resolution, (b) give generic responses, or (c) fail to notice the ambiguity
- APEX tasks are explicitly designed with realistic ambiguity -- no artificially clean problem statements

### 6. File System Navigation and Information Retrieval
- In agentic settings, models must first FIND the right information before reasoning over it
- APEX-Agents uses realistic file systems designed with Box to simulate corporate data rooms
- Models fail at basic retrieval: wrong file, incomplete search, confusion between similarly named files

### 7. Domain-Specific Convention Application
- Each profession has implicit conventions (how a DCF model is structured, how a legal memo is formatted, how a clinical assessment is organized)
- Models may have general knowledge but fail to apply domain-specific formatting and structure conventions
- This is distinct from factual knowledge -- it's about professional norms and expectations

---

## Most Promising Headroom Areas for Eval Design

Based on the analysis above, here are the areas with the most headroom for designing new evaluation tasks in Harbor format:

### Tier 1: Maximum Headroom (Models Score < 40%)

1. **Multi-Step Financial Calculation from Documents**
   - Current best: ~24-38% pass@1 on APEX-Agents IB tasks
   - Design: Provide financial statements (XLSX/CSV) + instructions requiring 3-5 chained calculations
   - Example: "Extract revenue growth from the income statement, apply the peer median EV/EBITDA multiple from the comps table, adjust for the net debt on the balance sheet, and compute the implied equity value per share"
   - Why models fail: Each step requires finding the right number, applying the right operation, and carrying forward correctly

2. **Cross-Document Legal Analysis**
   - Current best: ~77.9% on single-turn law, much lower on agentic
   - Design: Provide contract + amendment + case law excerpt + regulatory text; ask for analysis of a specific clause interaction
   - Example: "Given the force majeure clause in the MSA, the recent amendment to Section 4.2, and the ruling in [Case X], determine whether the supplier is excused from performance"
   - Why models fail: Must reconcile potentially conflicting provisions across multiple documents

3. **Consulting Framework Application from Unstructured Data**
   - Current best: ~64% mean rubric on consulting
   - Design: Provide messy meeting notes, market data files, and a framework template; require structured strategic recommendation
   - Example: "Using the attached market sizing data, competitive analysis, and the GE/McKinsey matrix template, produce a prioritized investment recommendation for the three business units"
   - Why models fail: Must extract relevant data points from unstructured sources, apply a specific framework, and produce precise quantitative outputs

### Tier 2: Significant Headroom (Models Score 40-65%)

4. **Multi-Source Data Reconciliation**
   - Design: Provide 2-3 data sources with overlapping but inconsistent information; require identification of discrepancies and correct reconciliation
   - Example: Revenue figures that differ between an earnings call transcript, a 10-K filing, and an internal financial model
   - Why models fail: Must notice subtle differences and determine which source is authoritative

5. **Structured Output Formatting from Specification**
   - Design: Provide detailed output format requirements (specific columns, rounding rules, unit conversions) alongside source data
   - Example: "Produce a summary table with columns [A, B, C] where A is in millions (rounded to 1 decimal), B is a percentage (to 2 decimals), and C is computed as A * B / [value from Document X]"
   - Why models fail: Format compliance errors, rounding mistakes, and unit conversion errors

6. **Clinical Decision-Making Under Incomplete Information**
   - Design: Patient case with missing lab values, conflicting symptoms, and relevant but ambiguous imaging results
   - Example: Differential diagnosis where the model must explicitly state what additional information it would need
   - Why models fail: Tendency to over-commit to a diagnosis rather than maintaining appropriate uncertainty

### Tier 3: Emerging Headroom (Novel Evaluation Angles)

7. **Temporal Reasoning Across Documents**
   - Design: Documents from different time periods with evolving facts; require analysis as of a specific date
   - Example: Contract was amended 3 times; determine obligations as of a date between amendments 2 and 3

8. **Implicit vs. Explicit Information Extraction**
   - Design: Documents where key information must be inferred from context (e.g., a company's fiscal year from the dates in their financial statements)
   - Example: "The Q3 report mentions 'nine months ended March 31' -- what is the fiscal year end?"

9. **Professional Judgment Calls**
   - Design: Tasks where reasonable professionals might disagree, requiring the model to present a reasoned position
   - Example: Materiality thresholds in auditing, risk assessment in clinical triage

### Design Principles for Harbor-Format Tasks (from APEX methodology)

1. **Expert-designed:** Tasks should reflect real work that professionals do daily, not synthetic puzzles
2. **Rubric-based grading:** Decompose quality into discrete, objective Pass/Fail criteria (like unit tests)
3. **Mean 14.81 criteria per task:** Rubrics should have sufficient granularity to distinguish partial success
4. **Source documents as context:** Include realistic file attachments (PDF, XLSX, CSV, DOCX)
5. **Up to 100K tokens:** Source material should be substantial enough to require genuine information retrieval
6. **Binary criteria:** Each criterion is a specific, objective claim about the response (e.g., "States that the capital budget for SolisOne is $0.795B")
7. **Gold outputs:** Provide reference answers for each task
8. **Multiple domains:** Cross-domain coverage reveals different failure modes
9. **Time-anchored:** APEX estimates mean human expert time at 2.7 hours per task -- tasks should be substantial

### Example APEX-Agents Tasks (from Artificial Analysis)

**Law Task -- Force Majeure:**
- Instruction: Analyze whether a buyer's assertion about force majeure is correct, citing an attached case
- Rubric criteria: (1) States buyer is not correct (2) Identifies executive order as governmental action under force majeure provision (3) Explains TAC may be excused
- Output format: "Yes/No" + brief explanation

**Consulting Task -- Capital Budget Allocation:**
- Instruction: Use market matrix and competitor landscape to compute capital budgets for 4 business units for 2026
- Requires: Computing BU allocation scores (product of CAGR, TAM, chance of success), converting operational constraints (High/Medium/Low) to percentages, proportional allocation, rounding to 3 decimal places
- Rubric: Specific dollar amounts for each of 4 units (AmensaDrive: $0.000B, SkyLink Atmos: $0.004B, AmensaMech: $0.202B, SolisOne: $0.795B)

**IB Task -- DCF Update:**
- Instruction: Get average close price for KVUE for week of 12/15-12/19/2025, apply 10% premium, input into DCF model, recalculate cost of equity and after-tax cost of debt
- Rubric: Cost of Equity is 7.94%, After-tax Cost of Debt is 4.04%

---

## Key Takeaways for Eval Task Design

1. **Investment banking financial modeling** has the most headroom -- even top models score only ~63% on mean rubric (non-agentic) and much lower on pass@1 (agentic)
2. **Multi-step numerical reasoning from documents** is the single hardest capability for current models
3. **Cross-document synthesis** is the most consistent failure mode across all benchmarks
4. **Rubric-based grading with binary criteria** is the gold standard methodology (used by APEX, and analogous to Harbor format)
5. **The agentic gap** is massive: models that score 67% on single-turn APEX only achieve ~24-38% when they must navigate files and tools
6. **File formats matter:** XLSX/CSV tasks (requiring structured data extraction) are harder than pure text tasks
7. **Domain expert validation** is essential for realistic task design
8. **Pass@1 is the right metric** for professional work -- clients don't get 8 attempts

## Sources

- APEX-Agents paper: arXiv:2601.14242 (Vidgen et al., Jan 2026)
- APEX-v1-extended paper: arXiv:2509.25721 (Vidgen et al., Sep/Dec 2025)
- Epoch AI benchmark page: epoch.ai/benchmarks/apex-agents
- Mercor blog: mercor.com/blog/introducing-apex-agents
- Artificial Analysis leaderboard: artificialanalysis.ai/evaluations/apex-agents-aa
- Hugging Face dataset: huggingface.co/datasets/mercor/apex-agents
- TAU-bench: taubench.com (Sierra Research)
- SWE-bench: swebench.com
- GAIA: gaia-benchmark.com
- OSWorld: os-world.github.io
- BigLaw Bench: Harvey AI (harvey.ai)
- GDPval: OpenAI (2025)
