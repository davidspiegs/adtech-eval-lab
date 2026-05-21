# Ad Ops in AdTech: A Harbor Eval Suite

## Summary

This project recreates two realistic Ad Operations workflows from the adtech and
digital media world as Harbor-format AI evaluation tasks.

The tasks ask an AI agent to do the kind of messy, multi-file work that shows up
in real ad ops: reconcile ad server and SSP billing data, parse PDFs, handle
inconsistent naming, investigate advertiser discrepancy complaints, apply
business rules, and produce structured Excel reports.

This is a small, synthetic eval suite. It is not meant to be a universal
leaderboard or a definitive benchmark for the whole industry. I built it to
explore how practical AI evals are designed: what makes a task realistic, what
makes a verifier fair, and where long-horizon agent workflows still break down.

All data in this repo is synthetic. No customer, production, or platform-private
data is included.

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

## Selected Results

These are selected runs from my testing. They show the kind of signal the tasks
produced, but they should not be read as a broad model ranking.

| Model | Revenue Reconciliation | Campaign Investigation |
|---|---:|---:|
| GPT-5.5 | 1.000 | 1.000 |
| Claude Opus 4.6 | 1.000 | 1.000 |
| Gemini 3 Flash Preview | 0.000 | 0.7143 |

More detail is available in:

- [`report/headroom-report.md`](report/headroom-report.md)
- [`report/task-design-review.md`](report/task-design-review.md)
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
