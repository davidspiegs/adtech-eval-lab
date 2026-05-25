# Ad Ops in AdTech: A Harbor Eval Suite

## Summary

This project recreates two realistic Ad Operations workflows from the AdTech and
digital media domains as Harbor-format AI evaluation tasks.

I chose this domain specifically because Ad Operations ("Ad Ops") work is currently an overlooked area of knowledge work in AI research. Surprisingly, I couldn't find a single AI research paper or dataset specific to Ad Ops — there were a few advertising analytics papers, but nothing came close to the complexity of real Ad Ops work. Ad Ops work often involves analyzing multiple inconsistent, messy, complicated datasets from different sources, with specific rules to follow. [APEX and APEX-Agents benchmarks](https://www.mercor.com/apex/) have shown that even the latest frontier models still struggle with executing long-horizon, cross-application tasks in professional services.

The tasks I created ask an AI agent to do perform the kind of messy, multi-file tasks that show up
in real ad ops, such as: reconciling ad server and SSP billing data, parsing PDFs, handling
inconsistent naming, investigating advertiser discrepancy complaints, applying
business rules, and producing structured Excel reports.

This is a small, synthetic eval suite. It is not meant to be a universal
leaderboard or a definitive benchmark for the whole industry. I built it to
explore how practical AI evals are designed: what makes a task realistic, what
makes a verifier fair, and where long-horizon agent workflows still break down.

The datasets in this repo are synthetic, but they are designed based off of personal experience working at Supply-Side Platforms (SSPs) and digital publishers. No customer, production, or platform-private data are included.

This evaluation involved a limited number of trials, primarily due to budget constraints. The model focused on here was Gemini 3 Flash due to it's low cost, and because benchmarks have shown that it performs well at instruction following, but has a high hallucination rate. I ran limited trials with GPT 5.5 and Opus 4.6 to prove that the tasks were achievable by LLMs — GPT 5.5 passed every trial, but even Opus 4.6 failed on the campaign discrepancy investigation task.

For the detailed evaluation writeup, see the [headroom report](report/headroom-report.md).

## Why Ad Operations?

Ad Operations is a good domain for agent evaluation because the work is rarely a
single clean question. A real analyst often has to piece together evidence from
ad servers, SSPs, verification vendors, rate cards, taxonomy files, campaign
configuration, finance policies, and stakeholder emails.

That makes it a useful testbed for the kinds of failures that show up in
long-horizon professional work. Benchmarks like APEX-Agents point to the same
general problem: even strong models can struggle when a task requires many files,
many steps, numerical precision, and a final deliverable that has to be
internally consistent.

I built this as my first Harbor eval project and as a way to learn the mechanics
of eval design from end to end: task construction, synthetic data generation,
oracle solutions, deterministic verifiers, and result analysis.

## What The Tasks Test

These tasks are designed around practical agent skills:

- Multi-file reasoning across CSV, PDF, JSON, and Markdown inputs
- Spreadsheet and report generation
- PDF extraction from partner billing statements
- Fuzzy matching and entity resolution across inconsistent naming conventions
- Numerical consistency across chained business calculations
- Root-cause investigation under realistic operational ambiguity

## Tasks

| Task | Workflow | Output | Scoring |
|---|---|---|---|
| `programmatic-ad-revenue-reconciliation` | Monthly publisher revenue audit across ad server delivery, IVT deductions, deal rate cards, SSP billing, pacing, yield, and prior-month variance | 5-sheet Excel audit report | Binary verifier with 15 deterministic checks |
| `campaign-discrepancy-investigation` | Advertiser complaint investigation covering impression gaps, viewability collapse, and domain violations | 4-sheet Excel investigation report | Partial-credit verifier with 14 deterministic checks |

The first task is closer to a month-end revenue and finance close workflow. The
second task is closer to a forensic ad ops investigation after an advertiser
escalates a campaign issue.

## Result Summary

These are limited trial results from my testing. They show the kind of signal
the tasks produced, but they should not be read as a broad model ranking.

| Model | Revenue Reconciliation | Campaign Investigation | Notes |
|---|---:|---:|---|
| GPT-5.5 | 1/1 pass | 1.000 avg over 6 trials | Passed every Task 2 trial reviewed |
| Claude Opus 4.6 | 1/1 pass | 0.929 avg over 6 trials | Intermittently failed the non-viewable reconciliation step |
| Gemini 3 Flash Preview | 0/5 pass rate | 0.843 avg over 10 trials | Repeated failures on metric selection and timezone attribution |

More detail is available in:

- [`report/headroom-report.md`](report/headroom-report.md)
- [`workbench/results/model-results-summary.md`](workbench/results/model-results-summary.md)

## How To Run

Clone the repo:

```bash
git clone https://github.com/davidspiegs/adtech-eval-lab.git
cd adtech-eval-lab
```

Prerequisites:

- Harbor installed
- Docker running
- Agent credentials configured if you want to run model-backed agents

Run the oracle solution for the revenue reconciliation task:

```bash
harbor run \
  --path samples/programmatic-ad-revenue-reconciliation \
  --agent oracle \
  --job-name oracle-revenue-reconciliation \
  --n-concurrent 1 \
  --yes \
  --artifact /root/audit_report.xlsx
```

Run the oracle solution for the campaign investigation task:

```bash
harbor run \
  --path samples/campaign-discrepancy-investigation \
  --agent oracle \
  --job-name oracle-campaign-investigation \
  --n-concurrent 1 \
  --yes \
  --artifact /root/investigation_report.xlsx
```

Run a model-backed agent by replacing the agent and model:

```bash
harbor run \
  --path samples/programmatic-ad-revenue-reconciliation \
  --agent codex \
  --model gpt-5.5 \
  --job-name codex-revenue-reconciliation \
  --n-concurrent 1 \
  --yes \
  --artifact /root/audit_report.xlsx
```

Exact agent and model setup depends on your local Harbor installation and the
credentials you have configured.

## Repository Layout

```text
samples/            Harbor-format eval tasks
report/             Main write-up and task design review
workbench/research/ Research notes from the build process
workbench/results/  Curated result summaries
logs/sanitized/     Public-safe verifier outputs and compact run metadata
scripts/            Archived data-generation notes and utilities
```

Each task follows the same basic Harbor layout:

```text
instruction.md      Prompt received by the agent
task.toml           Harbor task metadata and resource settings
environment/        Dockerfile, static task data, and agent skills
solution/           Oracle solution used for validation
tests/              Deterministic verifier
```

For manual review, all task data is visible under each task's
`environment/data/` directory. The revenue reconciliation task includes the Index
Exchange billing statement as a static PDF, rather than generating it at build
time.

## Notes

- The datasets are synthetic and intentionally compact enough to inspect.
- The public archive includes sanitized verifier outputs and compact run
  metadata under `logs/sanitized/`.
- Raw agent trajectories and transcripts are excluded because they are noisy and
  contain local execution details.
- The reports and workbench notes are included to show the design thinking
  behind the tasks, including what worked, what failed, and where the evals could
  be improved.
