---
name: fuzzy-match
description: Approximate string matching for typo-tolerant entity resolution. Use when exact matching fails due to spelling variation, casing differences, or formatting inconsistencies.
---

# Fuzzy Matching

Use this skill when exact text matching is too strict.

## Workflow

1. Normalize casing and whitespace.
2. Compute similarity scores (e.g., with rapidfuzz or difflib).
3. Apply an acceptance threshold (typically 80%+).
4. Log chosen match and score for auditability.
5. If no match meets threshold, flag for manual review.

## Common Variations in Ad Ops Data

- Underscores vs spaces: `PDM_Sports_LB_728` vs `PDM Sports LB 728`
- Case differences: `IX_Tech_MR_300` vs `IX_Tech_mr_300`
- Typos: `MAG_Lifstyle_Interstitial` vs `MAG_Lifestyle_Interstitial`
- Abbreviations: `PUB_Finance_MR` vs `PUB Finance_MR`
