---
name: adunit-matching
description: Resolve SSP ad unit names to canonical ad unit IDs using metadata lookups and approximate matching. Use when SSP billing reports use different naming conventions than the publisher's ad server.
---

# Ad Unit Matching

Use this skill when SSP billing reports reference ad units by names that differ
from the publisher's canonical names.

## Workflow

1. Load ad unit metadata with canonical names and per-SSP name columns.
2. For each SSP billing row, look up `ssp_ad_unit_name` against that SSP's
   name column in the metadata (e.g., `adflow_name`, `magnite_name`).
3. If no exact match on the SSP-specific column, fall back to `canonical_name`.
4. If still no exact match, try approximate/fuzzy matching against all name
   columns. SSP data often has minor formatting differences: typos, casing
   changes, underscores vs spaces. Use a similarity threshold (e.g., 85+%)
   to find the best match.
5. If no match meets the threshold, hold the row for review.
6. After resolving to a canonical ad unit, check the `active` flag.
   Only match to active ad units. Inactive ad units -> hold for review.

## Edge Cases

- **Alias mismatch**: One SSP may use an abbreviated or prefixed name
  (e.g., "PDM_Sports_LB_728" instead of "Sports_Leaderboard_728x90").
  The metadata maps these explicitly.
- **Fuzzy variants**: SSP names may have typos (missing letters), different
  casing, or spaces instead of underscores. Approximate string matching
  handles these if the similarity score is high enough.
- **Unknown deal**: If the SSP row's `deal_id` doesn't exist in the rate card
  or ad server data, hold the entire row regardless of ad unit match.
- **Inactive ad unit**: A valid ad unit that has been deactivated. The SSP may
  still report billing for it — hold for review, do not force-match.
