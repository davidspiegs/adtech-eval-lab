From: Sarah Chen, VP Finance — Pinnacle Digital Media
To: Ad Operations Team
Subject: April 2026 Monthly Performance Audit

Team,

We need the April monthly performance audit completed before month-end close on May 5th. This month I'm asking for the full audit — not just reconciliation, but pacing, yield, and variance analysis too.

This month we have billing reports from four SSPs — AdFlow Exchange, Magnite, Index Exchange, and Pubmatic. Index Exchange sent a PDF this time — just pull the numbers from that. Everything's in the ssp_billing folder.

For reconciliation:
1. Reconcile each SSP's reported figures against our ad server delivery data
2. Apply IVT deductions per our standard policy
3. Flag any discrepancies that exceed our tolerance — flag anything that's more than $5 off AND also more than 3% off. Both thresholds need to be exceeded, not just one.
4. Remember that PMP floor deals may legitimately clear above the floor — don't flag those as overbilled
5. Note any deals where we have delivery but the SSP didn't send a billing row
6. Hold any SSP rows we can't match to a known deal or an active ad unit

Heads up on data quality: I've heard the IVT vendor has been sending some dates in MM/DD/YYYY format instead of ISO. Also SSP naming isn't always perfectly consistent with our metadata, so watch out for that.

For pacing and make-goods:
7. Check all PG deals against their contracted impressions in the goals file
8. Project whether each deal will deliver in full by end of contract
9. Calculate make-good exposure for any deals that won't make it

For yield analysis:
10. Break down performance by SSP — eCPM, fill rate, discrepancy rate
11. Rank them so I can see who's performing best

For variance:
12. Compare this month's key metrics to last month (historical_metrics.json)
13. Flag anything that's moved more than 25% — that needs investigation

Executive summary:
14. Give me a traffic-light health indicator and the top 3 financial concerns

Thanks,
Sarah
