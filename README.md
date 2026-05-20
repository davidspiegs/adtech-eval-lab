# Adtech Eval Lab

This is my first Harbor eval project.

I built it as a passion project to learn Harbor, AI eval design, and what makes
an eval useful for understanding agent behavior. I wanted to build something more
realistic than a toy task: messy files, business rules, spreadsheets, ambiguity,
and enough moving parts that a model has to actually keep track of what it is
doing.

The domain is synthetic adtech revenue operations. That means the tasks are about
publisher-side ad revenue reconciliation and campaign discrepancy investigation:
workflows where an analyst has to connect CSVs, PDFs, JSON files, policy notes,
and stakeholder requests into a clean final report.

All data in this repo is synthetic. No customer, production, or platform-private
data is included.

## What This Is

This repo contains two Harbor-format evaluation tasks for AI agents. Each task
gives the agent a realistic business request, a folder of source data, and a
required Excel output. The verifier then checks the output deterministically.

The goal is not to create a definitive leaderboard. The goal is to explore what
kind of eval tasks can expose useful training signal for agentic knowledge work:
multi-file reasoning, spreadsheet generation, PDF parsing, fuzzy matching,
business-rule execution, and numerical consistency.

## The Tasks

| Task | What The Agent Has To Do | Output | Scoring |
|---|---|---|---|
| `programmatic-ad-revenue-reconciliation` | Reconcile ad server delivery, IVT deductions, deal rate cards, SSP billing, pacing, yield, and prior-month variance | 5-sheet Excel audit report | Binary verifier with 15 deterministic checks |
| `campaign-discrepancy-investigation` | Investigate advertiser complaints about impression gaps, viewability collapse, and domain violations | 4-sheet Excel investigation report | Partial-credit verifier with 14 deterministic checks |

The first task is closer to a monthly finance/ad ops close workflow. The second
task is closer to a forensic investigation after an advertiser escalates a
campaign problem.

## Selected Results

These are a few selected runs from my testing. They are included to show the
kind of signal the tasks produced, not as a universal model ranking.

| Model | Revenue Reconciliation | Campaign Investigation |
|---|---:|---:|
| GPT-5.5 | 1.000 | 1.000 |
| Claude Opus 4.6 | 1.000 | 1.000 |
| Gemini 3 Flash Preview | 0.000 | 0.7143 |

More detail is available in:

- [`report/headroom-report.md`](report/headroom-report.md)
- [`report/task-design-review.md`](report/task-design-review.md)
- [`workbench/results/model-results-summary.md`](workbench/results/model-results-summary.md)

## Repository Layout

```text
samples/            The two Harbor-format eval tasks
report/             Main write-up and task design review
workbench/research/ Research notes from the build process
workbench/results/  Curated result summaries
logs/sanitized/     Public-safe verifier outputs and compact run metadata
scripts/            Archived data-generation notes and utilities
```

Each task follows the same basic Harbor layout:

```text
instruction.md      The prompt the agent receives
task.toml           Harbor task metadata and resource settings
environment/        Dockerfile, static task data, and agent skills
solution/           Oracle solution used for validation
tests/              Deterministic verifier
```

For manual review, all task data is visible under each task's
`environment/data/` directory. The revenue reconciliation task includes the Index
Exchange billing statement as a static PDF, rather than generating it at build
time.

## How To Run

Clone the repo:

```bash
git clone https://github.com/davidspiegs/adtech-eval-lab.git
cd adtech-eval-lab
```

Prerequisites:

- Harbor installed
- Docker running
- Agent credentials configured if you want to run non-oracle agents

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

## Notes On The Public Archive

The raw agent trajectories and transcripts are not included here. They can be
large, noisy, and full of local execution details. Instead, this repo keeps
sanitized verifier outputs and compact result metadata under `logs/sanitized/`.

The reports and workbench notes are included because they show the design
thinking behind the tasks: why I chose the domain, what kinds of failures I was
looking for, and where the tasks are strong or still imperfect.
