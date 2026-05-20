---
name: adtech-glossary
description: Programmatic advertising terminology reference for publisher ad operations. Use when interpreting deal types, billing fields, and IVT classifications.
---

# AdTech Glossary

## Deal Types

- **Programmatic Guaranteed (PG)**: Fixed CPM, guaranteed impression volume.
  The rate card CPM is the exact price (`rate_type = "fixed"`).
- **Private Marketplace (PMP)**: Invitation-only auction with a floor price.
  The rate card CPM is a minimum (`rate_type = "floor"`). Actual clearing
  price may be higher.

## Billing Fields

- **gross_revenue_usd**: Total revenue before SSP fee deduction. Informational.
- **ssp_fee_pct / ssp_fee_usd**: The SSP's take rate. Informational.
- **net_revenue_usd**: Revenue payable to the publisher after SSP fees.
  This is the value to use for reconciliation.

## IVT (Invalid Traffic)

- **GIVT (General Invalid Traffic)**: Known bots, spiders, crawlers identified
  via industry lists (IAB/ABCe spider list). Easily detected.
- **SIVT (Sophisticated Invalid Traffic)**: Harder to detect — hijacked devices,
  ad injection, cookie stuffing. Requires advanced analysis.
- IVT data is sourced from third-party verification vendors (DoubleVerify, IAS,
  MOAT) whose measurement tags run on the publisher's ad units.
- The `ivt_category` column is informational for this reconciliation.
  Sum all IVT impressions regardless of category.

## Ad Server Delivery

- **delivered_impressions**: Raw count from the publisher's ad server (source of truth).
- **ad_server_clicks**: Click count. Informational only for revenue reconciliation.
- **viewable_impressions / measurable_impressions**: Active View metrics from the
  ad server. Informational only for revenue reconciliation.

## Ad Units

- An **ad unit** is a specific ad slot on a page (e.g., "Homepage_Billboard_970x250").
- Different SSPs may use different names for the same ad unit. Use the metadata
  file to resolve SSP names to canonical ad unit IDs.
