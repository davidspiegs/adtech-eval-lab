# Curated Model Results

These are public-safe summaries from selected Harbor runs, with aggregate context
where multiple final-verifier trials were run. Raw agent trajectories, session
dumps, and transcripts are intentionally excluded from the public archive.

| Task | Model | Result | Notes |
|---|---:|---:|---|
| Programmatic Ad Revenue Reconciliation | GPT-5.5 | 1.000 selected | Passed all 15 deterministic checks |
| Programmatic Ad Revenue Reconciliation | Claude Opus 4.6 | 1.000 selected | Passed all 15 deterministic checks |
| Programmatic Ad Revenue Reconciliation | Gemini 3 Flash Preview | 0/5 pass rate | Repeated binary-verifier failures across final trials |
| Campaign Discrepancy Investigation | GPT-5.5 | 1.000 avg over 6 trials | Passed all final-verifier trials reviewed |
| Campaign Discrepancy Investigation | Claude Opus 4.6 | 0.929 avg over 6 trials | Intermittently failed total gap, non-viewable component, and component-sum checks |
| Campaign Discrepancy Investigation | Gemini 3 Flash Preview | 0.843 avg over 10 trials | Repeated failures on metric selection and timezone attribution |
