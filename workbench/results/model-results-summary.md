# Curated Model Results

These are public-safe summaries from selected Harbor runs. Raw agent trajectories,
session dumps, and transcripts are intentionally excluded from the public archive.

| Task | Model | Selected Run Score | Notes |
|---|---:|---:|---|
| Programmatic Ad Revenue Reconciliation | GPT-5.5 | 1.000 | Passed all 15 deterministic checks |
| Programmatic Ad Revenue Reconciliation | Claude Opus 4.6 | 1.000 | Passed all 15 deterministic checks |
| Programmatic Ad Revenue Reconciliation | Gemini 3 Flash Preview | 0.000 | Failed the binary verifier; selected run missed percentage-scale variance |
| Campaign Discrepancy Investigation | GPT-5.5 | 1.000 | Passed all 14 deterministic checks |
| Campaign Discrepancy Investigation | Claude Opus 4.6 | 1.000 | Passed all 14 deterministic checks |
| Campaign Discrepancy Investigation | Gemini 3 Flash Preview | 0.7143 | Missed total gap, non-viewable component, timezone component, and component sum |
