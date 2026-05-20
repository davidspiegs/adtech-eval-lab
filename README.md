# Adtech Eval Lab

Adtech Eval Lab is an independent research project building Harbor-format AI
evaluation tasks for synthetic adtech revenue operations workflows.

The project focuses on messy, multi-file knowledge work: reconciling publisher ad
revenue, investigating advertiser discrepancy complaints, parsing mixed file
formats, applying business rules, and producing structured Excel reports.

All datasets are synthetic. No production, customer, or platform-confidential data
is included.

## Tasks

| Task | Objective | Data Shape | Scoring |
|---|---|---|---|
| `programmatic-ad-revenue-reconciliation` | Reconcile ad server delivery, IVT, rate cards, SSP billing, pacing, yield, and prior-month variance into a 5-sheet workbook | CSV, PDF, JSON, Markdown; static task-visible dataset | Binary verifier with 15 deterministic checks |
| `campaign-discrepancy-investigation` | Investigate advertiser complaints about impression gaps, viewability collapse, and domain violations | 13 static CSV/JSON/Markdown files | Partial-credit verifier with 14 deterministic checks |

## Selected Results

| Model | Revenue Reconciliation | Campaign Investigation |
|---|---:|---:|
| GPT-5.5 | 1.000 | 1.000 |
| Claude Opus 4.6 | 1.000 | 1.000 |
| Gemini 3 Flash Preview | 0.000 | 0.7143 |

The full write-up is in [`report/headroom-report.md`](report/headroom-report.md).
The task design audit is in [`report/task-design-review.md`](report/task-design-review.md).

## Repository Layout

```text
samples/            Harbor-format tasks
report/             Research and task-design reports
workbench/research/ Sanitized research notes
workbench/results/  Curated model-result summaries
logs/sanitized/     Public-safe verifier artifacts
scripts/            Archived reproducibility utilities
```

## Running The Tasks

Each task follows the Harbor task layout with:

- `instruction.md`
- `task.toml`
- `environment/`
- `solution/`
- `tests/`

For manual inspection, all task data is visible under each task's
`environment/data/` directory. The revenue reconciliation task intentionally ships
the Index Exchange billing statement as a static PDF rather than generating it at
build time.

If Harbor is installed, run the tasks from the repository root using your local
Harbor workflow for a single task or sample directory. The solution and verifier
files are deterministic and can also be inspected directly.

## Notes

Raw agent transcripts, trajectories, and session dumps are excluded from the
public archive. The public logs preserve verifier evidence and compact run
metadata without local paths or private execution telemetry.
