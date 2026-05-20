## Gemini 3 Flash Preview -- Benchmark Analysis & Known Weaknesses

**Date:** 2026-05-08
**Model under test:** `gemini-3-flash-preview` (also referred to as Gemini 3 Flash)
**Status:** Preview (not yet stable)
**Knowledge cutoff:** January 2025
**Output token limit:** 64k
**Input modalities:** Text, Image, Video, Audio, PDF
**Output modalities:** Text only (no native image generation)
**Pricing:** $0.50 / 1M input tokens, $3.00 / 1M output tokens

**Sources:**
- Google DeepMind official model page: https://deepmind.google/models/gemini/flash/
- Artificial Analysis: https://artificialanalysis.ai/models/gemini-3-flash
- LMArena (Chatbot Arena) leaderboard: https://arena.ai/leaderboard
- Google AI for Developers model docs: https://ai.google.dev/gemini-api/docs/models

---

### Model Overview

Gemini 3 Flash is Google DeepMind's latest efficiency-optimized frontier model, released in December 2025 as a Preview. Google positions it as delivering "Gemini 3 Pro's level of reasoning with Flash-level latency and efficiency -- at a fraction of the cost." It supports thinking (reasoning) mode and is multimodal across text, image, video, audio, and PDF inputs.

Key positioning claims from Google:
- "Speed and scale don't have to come at the cost of intelligence"
- "Frontier-level multimodal understanding across text, audio, images, code, and video"
- "High quality intelligence at a fraction of the cost"

On Artificial Analysis, Gemini 3 Flash (non-reasoning mode) ranks #20 out of 71 models on their Intelligence Index, with 167 output tokens per second. It is categorized as a non-reasoning model in its default mode, though it supports a thinking/reasoning mode.

On LMArena (Chatbot Arena), Gemini 3 Flash ranks **#16 overall** with a score of 1420 (compared to Claude Opus 4.7-thinking at #1 with 1503, and Gemini 3 Pro at #7 with 1486).

---

### Benchmark Results (Google's Official Numbers, with Thinking Enabled)

The following table is from Google's official model page (https://deepmind.google/models/gemini/flash/). All Gemini models use "Thinking" mode; Claude Sonnet 4.5 uses "Thinking" mode; GPT-5.2 uses "Extra high" reasoning; Grok 4.1 Fast uses "Reasoning" mode.

#### Academic & Reasoning Benchmarks

| Benchmark | What it measures | Gemini 3 Flash | Gemini 3 Pro | Claude Sonnet 4.5 (Thinking) | GPT-5.2 (Extra high) | Grok 4.1 Fast |
|---|---|---|---|---|---|---|
| Humanity's Last Exam (no tools) | Academic reasoning (text + MM) | 33.7% | 37.5% | 13.7% | 34.5% | 17.6% |
| Humanity's Last Exam (with search + code exec) | Academic reasoning (augmented) | 43.5% | 45.8% | -- | -- | 45.5% |
| ARC-AGI-2 | Visual reasoning puzzles | 33.6% | 31.1% | 13.6% | **52.9%** | -- |
| GPQA Diamond | Scientific knowledge | 90.4% | 91.9% | 83.4% | **92.4%** | 84.3% |
| AIME 2025 (no tools) | Mathematics | 95.2% | 95.0% | 87.0% | **100%** | 91.9% |
| AIME 2025 (with code exec) | Mathematics (augmented) | 99.7% | **100%** | -- | -- | -- |

#### Multimodal & Document Benchmarks

| Benchmark | What it measures | Gemini 3 Flash | Gemini 3 Pro | Claude Sonnet 4.5 | GPT-5.2 | Grok 4.1 Fast |
|---|---|---|---|---|---|---|
| MMMU-Pro | Multimodal understanding & reasoning | **81.2%** | 81.0% | 68.0% | 79.5% | 63.0% |
| ScreenSpot-Pro | Screen understanding | 69.1% | 72.7% | 36.2% | **86.3%** (w/ python) | -- |
| CharXiv Reasoning | Info synthesis from complex charts | 80.3% | 81.4% | 68.5% | **82.1%** | -- |
| OmniDocBench 1.5 | OCR (edit distance, lower=better) | 0.121 | **0.115** | 0.145 | 0.143 | -- |
| Video-MMMU | Knowledge acquisition from videos | 86.9% | **87.6%** | 77.8% | 85.9% | -- |

#### Coding Benchmarks

| Benchmark | What it measures | Gemini 3 Flash | Gemini 3 Pro | Claude Sonnet 4.5 | GPT-5.2 | Grok 4.1 Fast |
|---|---|---|---|---|---|---|
| LiveCodeBench Pro (Elo) | Competitive coding | 2316 | **2439** | 1418 | 2393 | -- |
| Terminal-Bench 2.0 | Agentic terminal coding | 47.6% | **54.2%** | 42.8% | -- | -- |
| SWE-bench Verified | Agentic coding (single attempt) | 78.0% | 76.2% | 77.2% | **80.0%** | 50.6% |

#### Agentic Task Benchmarks

| Benchmark | What it measures | Gemini 3 Flash | Gemini 3 Pro | Claude Sonnet 4.5 | GPT-5.2 | Grok 4.1 Fast |
|---|---|---|---|---|---|---|
| tau2-bench | Agentic tool use | 90.2% | **90.7%** | 87.2% | -- | -- |
| Toolathlon | Long horizon real-world software tasks | **49.4%** | 36.4% | 38.9% | 46.3% | -- |
| MCP Atlas | Multi-step workflows using MCP | 57.4% | 54.1% | 43.8% | **60.6%** | -- |
| Vending-Bench 2 (net worth) | Agentic long-term coherence | $3,635 | **$5,478** | $3,839 | $3,952 | $1,107 |

#### Knowledge & Factuality

| Benchmark | What it measures | Gemini 3 Flash | Gemini 3 Pro | Claude Sonnet 4.5 | GPT-5.2 | Grok 4.1 Fast |
|---|---|---|---|---|---|---|
| FACTS Benchmark Suite | Factuality (grounding, parametric, search, MM) | 61.9% | **70.5%** | 48.9% | 61.4% | 42.1% |
| SimpleQA Verified | Parametric knowledge | **68.7%** | 72.1% | 29.3% | 38.0% | 19.5% |
| MMMLU | Multilingual Q&A | **91.8%** | 91.8% | 89.1% | 89.6% | 86.8% |
| Global PIQA | Commonsense reasoning (100 languages) | 92.8% | **93.4%** | 90.1% | 91.2% | 85.6% |

#### Long Context

| Benchmark | What it measures | Gemini 3 Flash | Gemini 3 Pro | Claude Sonnet 4.5 | GPT-5.2 | Grok 4.1 Fast |
|---|---|---|---|---|---|---|
| MRCR v2 8-needle (128k avg) | Long context performance | 67.2% | 77.0% | 47.1% | **81.9%** | 54.6% |
| MRCR v2 8-needle (1M pointwise) | Long context at 1M tokens | 22.1% | **26.3%** | not supported | not supported | 6.1% |

---

### Comparative Weaknesses vs Other Frontier Models

Based on the benchmark data and LMArena rankings, here are the specific areas where Gemini 3 Flash underperforms:

#### 1. ARC-AGI-2: Massive Gap vs GPT-5.2
- **Gemini 3 Flash: 33.6% vs GPT-5.2: 52.9%** -- a 19.3 percentage point gap
- This tests abstract visual reasoning and pattern completion
- Even Gemini 3 Pro (31.1%) trails GPT-5.2 by 21.8 points here
- This suggests a systematic weakness in the Gemini 3 family on novel abstract reasoning tasks

#### 2. ScreenSpot-Pro: Large Gap vs GPT-5.2
- **Gemini 3 Flash: 69.1% vs GPT-5.2: 86.3%** -- a 17.2 point gap
- Screen understanding is critical for agentic GUI interaction
- GPT-5.2 used Python for this task; Gemini did not, but the gap is still substantial
- Gemini 2.5 Flash only scored 3.9%, so Gemini 3 Flash is a huge improvement, but still trails

#### 3. Long Context (128k): Significant Gap
- **Gemini 3 Flash: 67.2% vs GPT-5.2: 81.9%** on MRCR v2 8-needle at 128k
- Even vs Gemini 3 Pro (77.0%), Flash trails by ~10 points
- At 1M tokens, Flash gets only 22.1% (though it does support 1M context unlike Claude/GPT)
- Long context retrieval and reasoning is a clear weakness relative to its own Pro sibling

#### 4. Vending-Bench 2: Agentic Long-Term Coherence
- **Gemini 3 Flash: $3,635 vs Gemini 3 Pro: $5,478** -- a 33.6% performance gap vs its own Pro model
- Claude Sonnet 4.5 ($3,839) and GPT-5.2 ($3,952) also edge it out
- This measures coherence and decision quality over long agentic episodes

#### 5. MCP Atlas: Multi-Step MCP Workflows
- **Gemini 3 Flash: 57.4% vs GPT-5.2: 60.6%** -- modest gap, but more importantly
- **Only 57.4% accuracy** on multi-step MCP workflows means nearly half of complex tool-use chains fail
- This is directly relevant to agentic knowledge-work scenarios

#### 6. FACTS Benchmark / Factuality
- **Gemini 3 Flash: 61.9% vs Gemini 3 Pro: 70.5%** -- 8.6 point gap to its own Pro model
- 61.9% means the model makes factual errors roughly 38% of the time in a suite designed to test factuality
- GPT-5.2 ties at 61.4%, but Gemini 3 Pro substantially outperforms both

#### 7. LMArena Rankings -- Category-Level Weaknesses
From the Chatbot Arena leaderboard (overall rank #16, score 1420):
- **Coding:** Rank #17 (weaker than overall rank)
- **Math:** Rank #27 (significantly weaker -- 10 places below overall)
- **Hard Prompts:** Rank #15 (on par)
- **Creative Writing:** Rank #10 (relative strength)
- **Instruction Following:** Rank #21 (below overall -- 5 places)
- **Longer Query:** Rank #20 (below overall)

The Math weakness (rank #27 vs overall #16) is particularly notable given that Google reports strong AIME 2025 scores. This suggests the AIME benchmark may not capture real-world math problem-solving difficulty as well as human-preference-based evaluation does.

---

### Agentic Task Performance

#### Where Gemini 3 Flash is Surprisingly Strong

1. **Toolathlon (49.4%)** -- Flash actually *beats* Gemini 3 Pro (36.4%) and GPT-5.2 (46.3%) on long-horizon real-world software tasks. This is noteworthy and suggests Flash handles certain sustained tool-use patterns well.

2. **SWE-bench Verified (78.0%)** -- Near-SOTA performance, competitive with GPT-5.2 (80.0%) and Claude Sonnet 4.5 (77.2%). Strong on single-attempt agentic coding.

3. **tau2-bench (90.2%)** -- Very strong agentic tool use, near Gemini 3 Pro (90.7%).

#### Where It Struggles in Agentic Contexts

1. **MCP Atlas (57.4%)** -- Multi-step MCP workflows. Nearly half of complex multi-tool chains fail. This is a direct signal for eval design.

2. **Vending-Bench 2 ($3,635 vs $5,478 Pro)** -- Long-term coherence degrades significantly compared to Pro-class models. Flash may lose track of state or make compounding errors over extended agentic episodes.

3. **Terminal-Bench 2.0 (47.6%)** -- More than half of agentic terminal coding tasks fail. Pro scores 54.2%, suggesting a clear quality gap in complex terminal interactions.

4. **The "Preview" caveat** -- The model is still in Preview status. Google's docs note Preview models "might come with more restrictive rate limits and will be deprecated with at least 2 weeks notice." Behavior may change.

#### Third-Party Signals (Partner Testimonials from Google's Page)

Several partner quotes from Google's official page reveal specific capability profiles:
- **Cognition (Devin):** Called Flash "a major step above other models in its speed class when it comes to instruction following for coding" -- but this praises instruction following, not reasoning depth
- **Harvey (legal AI):** Noted "7% improvement on Harvey's BigLaw Bench" -- incremental, not transformative
- **Box:** Reported "15% relative improvement in overall accuracy compared to Gemini 2.5 Flash" -- good improvement but measured against the previous Flash, not against frontier Pro models
- **JetBrains:** Said Flash "delivered quality close to" larger models -- "close to" implies a gap remains
- **Bridgewater:** Specifically noted need for "reasoning over vast, unstructured multimodal datasets with low latency and high throughput" -- they value Flash for speed/throughput, not superior reasoning

---

### Identified Failure Modes

Based on the benchmark data, Arena rankings, and model characteristics, these are the most actionable failure modes for eval design:

#### 1. Multi-Step Tool Orchestration with State Management
- **Evidence:** MCP Atlas 57.4%, Vending-Bench 2 $3,635 (33% below Pro)
- **Failure pattern:** Model loses track of accumulated state across multiple tool calls, makes errors that compound, or fails to correctly chain outputs of one tool as inputs to the next
- **Eval target:** Tasks requiring 5+ sequential tool calls where each step depends on prior results, with state that must be maintained across the full chain

#### 2. Long-Context Reasoning and Retrieval
- **Evidence:** MRCR v2 at 128k: 67.2% (vs 81.9% GPT-5.2); at 1M: only 22.1%
- **Failure pattern:** Model struggles to retrieve and reason over specific information scattered across long documents, especially when multiple "needles" must be found and synthesized
- **Eval target:** Tasks requiring extraction and cross-referencing of specific data points from documents >50k tokens, especially when relevant information is distributed across non-adjacent sections

#### 3. Complex Mathematical Reasoning in Natural Language
- **Evidence:** LMArena Math rank #27 (vs overall #16); despite strong AIME scores
- **Failure pattern:** When math is embedded in natural language context (word problems, financial calculations with real-world constraints), performance degrades more than benchmark scores suggest. The disconnect between AIME scores (95.2%) and Arena Math rank (#27) suggests Flash handles clean, well-formatted math problems better than messy, real-world mathematical reasoning
- **Eval target:** Multi-step quantitative reasoning problems embedded in realistic business/knowledge-work contexts with ambiguous phrasing, unit conversions, and conditional logic

#### 4. Structured Output Generation Under Complex Constraints
- **Evidence:** LMArena Instruction Following rank #21 (vs overall #16); MCP Atlas 57.4%
- **Failure pattern:** When outputs must conform to complex schemas, combine multiple constraints, or fill structured templates based on unstructured inputs
- **Eval target:** Tasks requiring generation of well-formed structured data (JSON, tables, forms) from messy multi-modal inputs with specific formatting rules

#### 5. Document Processing with Cross-Reference Requirements
- **Evidence:** OmniDocBench 1.5 edit distance 0.121 (worse than Pro's 0.115); CharXiv 80.3% (vs 82.1% GPT-5.2)
- **Failure pattern:** When processing documents that require cross-referencing tables, charts, and text -- especially when answers require synthesis across modalities within the same document
- **Eval target:** Tasks involving financial statements, audit reports, or complex documents where the answer requires combining data from tables and narrative text

#### 6. Abstract Pattern Recognition and Novel Reasoning
- **Evidence:** ARC-AGI-2: 33.6% (vs 52.9% GPT-5.2)
- **Failure pattern:** When tasks require genuine novel reasoning rather than pattern matching against training data. The ARC-AGI-2 gap is one of the largest in the benchmark table
- **Eval target:** Tasks requiring analogical reasoning, novel problem decomposition, or transfer from unfamiliar domains -- less directly applicable to knowledge-work but informative about reasoning ceiling

#### 7. GUI Understanding and Interaction
- **Evidence:** ScreenSpot-Pro: 69.1% (vs 86.3% GPT-5.2)
- **Failure pattern:** Understanding screen layouts, identifying UI elements, and determining correct interaction targets
- **Eval target:** Tasks requiring the model to interpret application screenshots and specify correct actions

---

### Implications for Eval Design

Given the project brief (targeting agentic knowledge-work with Harbor-format tasks against `gemini-3-flash-preview`), the highest-value eval targets are:

#### Tier 1: Highest Headroom, Most Relevant to Knowledge Work

1. **Multi-step document analysis with cross-referencing** -- Combine the document processing weakness (OmniDocBench, CharXiv) with the long-context weakness (MRCR). Create tasks where a model must process a realistic multi-page business document (financial report, audit, contract) and answer questions that require synthesizing information across tables, charts, and text from different sections. This hits multiple failure modes simultaneously.

2. **Agentic tool-use chains with accumulated state** -- Combine the MCP Atlas weakness (57.4%) with the Vending-Bench coherence weakness. Design tasks requiring 5-10 sequential tool calls where errors compound (e.g., query a database, process results, update a spreadsheet, verify against a separate source, generate a report). Real knowledge work constantly requires this pattern.

3. **Quantitative reasoning embedded in messy real-world context** -- Exploit the disconnect between AIME (95.2%) and Arena Math rank (#27). Design tasks where mathematical reasoning is embedded in realistic business documents with ambiguous phrasing, mixed units, conditional logic, and data that must be extracted from tables/charts before computation.

#### Tier 2: Significant Headroom, Moderately Relevant

4. **Structured output generation from unstructured multi-modal inputs** -- Tasks requiring the model to read messy inputs (scanned documents, screenshots, mixed-format data) and produce well-structured outputs (JSON, completed forms, standardized reports) that must conform to specific schemas.

5. **Long-context synthesis tasks (50k-200k tokens)** -- Tasks where relevant information is deliberately scattered across a large document corpus and must be found, extracted, and synthesized into a coherent answer.

#### Domain Recommendation for Task Design

Based on the intersection of failure modes and knowledge-work domains:

- **Finance/Accounting audits**: Naturally combine document processing, cross-referencing, quantitative reasoning, and structured output requirements. A cost control audit, variance analysis, or financial reconciliation task would hit failure modes #1, #3, #4, and #5 simultaneously.
- **Legal document review**: Multi-document cross-referencing, long context, structured extraction, and precise instruction following.
- **Healthcare/clinical ops**: Structured data extraction from unstructured records, multi-step reasoning with real-world constraints.

The example task already provided (`restaurant-weekly-cost-control-audit`) aligns well with the Finance/Accounting direction, hitting several of the identified failure modes.

---

### Raw Performance Delta Summary

Areas with largest absolute gaps between Gemini 3 Flash and the best-performing model in each benchmark:

| Benchmark | Gemini 3 Flash | Best Competitor | Gap |
|---|---|---|---|
| ARC-AGI-2 | 33.6% | GPT-5.2: 52.9% | -19.3 pts |
| ScreenSpot-Pro | 69.1% | GPT-5.2: 86.3% | -17.2 pts |
| MRCR v2 128k | 67.2% | GPT-5.2: 81.9% | -14.7 pts |
| FACTS Benchmark | 61.9% | Gemini 3 Pro: 70.5% | -8.6 pts |
| Vending-Bench 2 | $3,635 | Gemini 3 Pro: $5,478 | -33.6% |
| Terminal-Bench 2.0 | 47.6% | Gemini 3 Pro: 54.2% | -6.6 pts |
| AIME 2025 (no tools) | 95.2% | GPT-5.2: 100% | -4.8 pts |
| MCP Atlas | 57.4% | GPT-5.2: 60.6% | -3.2 pts |

Note: On some benchmarks, Gemini 3 Flash leads its class (Toolathlon: 49.4% vs GPT-5.2's 46.3%; MMMU-Pro: 81.2% vs GPT-5.2's 79.5%; SimpleQA Verified: 68.7% vs all competitors).
