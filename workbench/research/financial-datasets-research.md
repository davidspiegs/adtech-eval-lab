# Financial Datasets & Benchmarks for Multi-Source Reconciliation Evals

Research date: 2026-05-09  
Target model weaknesses: 92% hallucination when uncertain, poor long-context reasoning (66% vs 74% peers), multi-step numerical errors

---

## Ranked List of Relevant Datasets/Benchmarks

### 1. ⭐ PHANTOM — Hallucination Detection in Financial QA (HIGHEST RELEVANCE)
- **Source**: https://openreview.net/forum?id=5YQAo0S3Hm (NeurIPS 2025 Poster)
- **Size**: Large-scale (seed dataset of "query-answer-document" triplets from financial documents, expanded via human annotation)
- **What it tests**: Hallucination detection in financial question-answering — generates triplets with either hallucinated or correct answers, validated by human annotators
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐⭐ — Directly targets our #1 weakness (92% hallucination). Built for financial QA with explicit hallucinated vs. correct answer pairs. Could be used as raw material for crafting reconciliation tasks where the model must identify which "source" contains errors.

### 2. ⭐ FAITH — Framework for Assessing Intrinsic Tabular Hallucinations in Finance
- **Source**: https://arxiv.org/abs/2508.05201
- **Size**: Large-scale benchmark from S&P 500 annual reports (masked span prediction tasks)
- **What it tests**: LLM hallucination on numerical values in financial tables — uses a masking strategy where the model must predict masked financial values from context
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐⭐ — Extremely relevant. Tests exactly the failure mode we want: LLMs fabricating numbers when reading real financial tables. The S&P 500 annual report data can serve as raw material for our multi-source reconciliation tasks. Stratified hallucination rates across model types provide baselines.

### 3. ⭐ FinanceReasoning Benchmark
- **Source**: https://arxiv.org/abs/2506.05828 | ACL 2025 Long Paper
- **Size**: Multi-category benchmark (extends FinQA and TAT-QA with more credible, comprehensive, and challenging tasks)
- **What it tests**: Financial numerical reasoning — multi-step arithmetic, percentage calculations, ratio analysis from financial documents. Goes beyond simple table lookups to require genuine reasoning chains.
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐⭐ — Directly targets multi-step numerical reasoning failures. Built to be "more challenging" than FinQA/TAT-QA, which aligns with our goal of creating tasks that expose Gemini 3 Flash's weak multi-step arithmetic.

### 4. ⭐ FinanceBench
- **Source**: https://github.com/patronus-ai/financebench | https://huggingface.co/datasets/PatronusAI/financebench
- **Size**: 10,231 questions about publicly traded companies, with evidence from actual SEC filings
- **What it tests**: Open-book financial QA — questions require extracting and reasoning over real financial data from 10-K/10-Q filings. Each answer has traceable evidence.
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐⭐ — Massive scale, uses real SEC filings, and questions require numerical extraction and reasoning. The traceable evidence format makes it perfect for building reconciliation tasks where the model must cross-reference multiple sources. Already widely used as a financial LLM benchmark.

### 5. ⭐ SEC EDGAR Financial Statement Data Sets (Raw Data Source)
- **Source**: https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets
- **Size**: Quarterly releases covering all XBRL-tagged financial filings (thousands of companies, millions of data points)
- **What it tests**: Raw structured data — not a benchmark itself, but the richest source of real, authoritative financial data
- **Harbor format?**: No — raw data source for task construction
- **Relevance**: ⭐⭐⭐⭐⭐ — This is the gold-standard source for building reconciliation tasks. Real XBRL financial statements with structured numeric data. We can cross-reference values across quarterly reports, compare balance sheet items, and create tasks where the agent must verify consistency across sources. Also available as Kaggle dataset: https://www.kaggle.com/datasets/securities-exchange-commission/financial-statement-extracts

### 6. ⭐ FinBench-QA-Hallucination (FinReflectKG)
- **Source**: https://arxiv.org/abs/2603.20252 (March 2026)
- **Size**: 755 annotated examples from SEC 10-K filings
- **What it tests**: Hallucination detection in KG-augmented financial QA over SEC filings — specifically tests whether models fabricate answers when the knowledge graph doesn't contain the information
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐ — Very recent (March 2026), directly uses SEC 10-K filings, and specifically tests for hallucination in financial contexts. The KG-augmentation angle adds a multi-source dimension.

### 7. ⭐ AuditBench — Financial Statement Auditing
- **Source**: https://openreview.net/forum?id=4MaWVsVb2g | https://link.springer.com/chapter/10.1007/978-981-96-8912-5_3
- **Size**: Not specified in abstracts (benchmarks financial statement auditing tasks)
- **What it tests**: LLM capability in financial statement auditing — verification, error detection, and assessing financial health from statements
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐ — Directly in our auditing/reconciliation domain. Tests error detection in financial statements, which maps closely to our "multi-source reconciliation" task concept.

### 8. ⭐ vals/financeagent (Harbor Hub)
- **Source**: https://hub.harborframework.com/datasets/vals/financeagent
- **Size**: 50 tasks (vals/0 through vals/49)
- **What it tests**: Financial agent evaluation — details not fully described on the hub page, but tasks are published by Vals (domain-specific benchmark org). Published 2026-03-24.
- **Harbor format?**: ✅ YES — already in Harbor format, run with `harbor run -d vals/financeagent`
- **Relevance**: ⭐⭐⭐⭐ — Already in Harbor format, which is a major advantage. Directly usable as reference for task structure and can serve as inspiration/baseline for our new tasks. 50 tasks focused on financial analysis.

### 9. ⭐ FinQA
- **Source**: https://finqasite.github.io/ | https://github.com/czyssrs/FinQA
- **Size**: 8,281 Q&A pairs from 2,789 financial reports
- **What it tests**: Numerical reasoning over financial data — each question requires multi-step numerical reasoning (addition, subtraction, multiplication, division, etc.) over data extracted from financial reports including tables and text
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐ — Large, well-established benchmark for financial numerical reasoning. Expert-annotated by finance professionals. The multi-step reasoning chains make it directly relevant to testing Gemini's numerical reasoning failures.

### 10. FinSheet-Bench
- **Source**: https://arxiv.org/abs/2603.07316 (March 2026)
- **Size**: Not explicitly stated (benchmark across multiple difficulty tiers)
- **What it tests**: LLM ability to extract and reason over structured tabular data in financial spreadsheets — ranges from simple lookups to complex reasoning. Targets alternative investment due diligence.
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐⭐ — Very recent, tests exactly the spreadsheet-level financial reasoning we need. The tiered difficulty (simple lookups → complex reasoning) provides a good template for designing multi-step reconciliation tasks.

### 11. APEX-Agents (Investment Banking Subset)
- **Source**: https://arxiv.org/abs/2601.14242 | https://epoch.ai/benchmarks/apex-agents
- **Size**: 480 "worlds" across investment banking, consulting, law, and primary care
- **What it tests**: Whether AI models can perform economically valuable knowledge work. The investment banking portion tests financial analysis, modeling, and multi-application tasks.
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐ — The investment banking subset is relevant but APEX-Agents is broader than just finance. Top AI models score under 25% accuracy, confirming the difficulty level we want.

### 12. DataClaw — Process-Oriented Agent Benchmark for Exploratory Data Analysis
- **Source**: https://arxiv.org/abs/2605.02503 (May 2026)
- **Size**: Not specified (multi-dataset benchmark)
- **What it tests**: Autonomous data analysis agents performing exploratory analysis — evaluates the process, not just the final answer. Tests ability to navigate underexplored data environments.
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐ — While not finance-specific, the process-oriented evaluation approach is highly relevant. Tests exactly the kind of multi-step data exploration and analysis our reconciliation tasks require. Could adapt the evaluation methodology.

### 13. virattt/financial-datasets (LLM Financial QA Generator)
- **Source**: https://github.com/virattt/financial-datasets | HuggingFace: virattt/financial-qa-10K
- **Size**: Tooling to generate arbitrary quantities from SEC 10-K filings
- **What it tests**: Financial Q&A from 10-K filings — provides a Python library for generating financial question-and-answer datasets
- **Harbor format?**: No — it's a generation tool, not a benchmark
- **Relevance**: ⭐⭐⭐ — Useful as a task generation tool. Can programmatically create financial QA pairs from real SEC filings, which we could use to generate raw material for our Harbor tasks. Pre-generated dataset on HuggingFace.

### 14. FinAgentBench — Agentic Retrieval in Finance
- **Source**: https://arxiv.org/abs/2508.14052 (NeurIPS 2025)
- **Size**: Not specified (benchmark with agentic retrieval pipeline)
- **What it tests**: End-to-end agentic retrieval over financial document collections — tests whether agents can find relevant info across large document sets, aligning LLMs with domain expert annotations
- **Harbor format?**: No — would need conversion
- **Relevance**: ⭐⭐⭐ — The multi-document retrieval aspect is relevant to our multi-source reconciliation angle, but focuses more on retrieval than numerical reasoning or hallucination.

### 15. Kaggle Financial Statements of Major Companies (2009-2023)
- **Source**: https://www.kaggle.com/datasets/rish59/financial-statements-of-major-companies-2009-2023
- **Size**: Multi-year financial data for major companies
- **What it tests**: Raw data source — structured financial statements (income statement, balance sheet, cash flow)
- **Harbor format?**: No — raw data source
- **Relevance**: ⭐⭐⭐ — Pre-cleaned, multi-year financial data in CSV format. Ideal raw material for creating reconciliation tasks where the agent must cross-reference values across years or detect intentionally introduced discrepancies.

---

## Harbor Hub Financial Dataset Status

### Already in Harbor Format:
1. **adyen/dabstep** — 450 tasks, financial data analysis (page 1)
2. **vals/financeagent** — 50 tasks, financial agent evaluation (page 2)

### Not Found in Harbor Format:
- No datasets for financial reconciliation, auditing, or accounting
- No hallucination-specific financial benchmarks
- This confirms the gap our eval tasks should fill

---

## Key Observations

1. **PHANTOM + FAITH are the most directly relevant** for our hallucination-trap angle — they explicitly test LLMs fabricating financial numbers
2. **SEC EDGAR XBRL data** is the best raw material source — authoritative, structured, and freely available
3. **FinanceBench (10K+ questions)** provides the largest existing financial QA dataset with traceable evidence chains
4. **No Harbor-format financial reconciliation/auditing benchmarks exist** — this is an open niche our tasks would uniquely fill
5. **FinanceReasoning** specifically addresses the "multi-step numerical reasoning" weakness we're targeting
6. **AuditBench** is the closest existing benchmark to our reconciliation/auditing concept but is not in Harbor format

## Recommended Strategy for Task Construction

Use **SEC EDGAR XBRL data** (rank #5) as the raw financial data source, combined with task design patterns from:
- **PHANTOM/FAITH** (for hallucination trap methodology)
- **FinanceReasoning** (for multi-step numerical reasoning task templates)
- **AuditBench** (for auditing/verification task patterns)
- **vals/financeagent** (for Harbor format structure reference)
