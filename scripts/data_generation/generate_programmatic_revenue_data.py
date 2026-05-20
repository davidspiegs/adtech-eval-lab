#!/usr/bin/env python3
"""Generate synthetic data for programmatic-ad-revenue-reconciliation Harbor task.

Deterministic (seed=42). Produces:
- Ad server delivery, IVT reports, deal rate cards, ad unit metadata
- Per-SSP billing (CSVs + 1 PDF source), contract goals, SSP request log
- Historical metrics for variance analysis
- Ground truth JSON for verifier

Usage: python3 generate_data.py [output_directory]
"""

import csv
import json
import os
import random
import sys
from collections import defaultdict
from datetime import date, timedelta

SEED = 42
random.seed(SEED)

PUBLISHER_ID = "PDM-001"
MONTH_START = date(2026, 4, 1)
MONTH_END = date(2026, 4, 30)
REPORTING_DATE = MONTH_END

SSPS = {
    "adflow": {"name": "AdFlow Exchange", "fee_pct": 0.15,
               "billing_filename": "adflow_exchange_april_2026.csv"},
    "magnite": {"name": "Magnite", "fee_pct": 0.12,
                "billing_filename": "magnite_april_2026.csv"},
    "indexexchange": {"name": "Index Exchange", "fee_pct": 0.18,
                      "billing_filename": "indexexchange_april_2026.csv"},
    "pubmatic": {"name": "Pubmatic", "fee_pct": 0.16,
                 "billing_filename": "pubmatic_april_2026.csv"},
}

AD_UNITS = [
    {"ad_unit_id": "AU-101", "canonical_name": "Homepage_Billboard_970x250",
     "adflow_name": "Homepage_Billboard_970x250", "magnite_name": "MAG_Homepage_Billboard",
     "indexexchange_name": "IX_Home_Bill_970", "pubmatic_name": "PUB_Home_Billboard",
     "site_section": "homepage", "format": "display", "size": "970x250",
     "viewability_vendor": "DoubleVerify", "active": True},
    {"ad_unit_id": "AU-102", "canonical_name": "Homepage_MedRect_300x250",
     "adflow_name": "Homepage_MedRect_300x250", "magnite_name": "MAG_Homepage_MedRect",
     "indexexchange_name": "IX_Home_MR_300", "pubmatic_name": "PUB_Home_MR",
     "site_section": "homepage", "format": "display", "size": "300x250",
     "viewability_vendor": "DoubleVerify", "active": True},
    {"ad_unit_id": "AU-103", "canonical_name": "News_Leaderboard_728x90",
     "adflow_name": "News_Leaderboard_728x90", "magnite_name": "MAG_News_LB_728",
     "indexexchange_name": "IX_News_LB_728", "pubmatic_name": "PUB_News_LB",
     "site_section": "news", "format": "display", "size": "728x90",
     "viewability_vendor": "IAS", "active": True},
    {"ad_unit_id": "AU-104", "canonical_name": "News_Native_InFeed",
     "adflow_name": "News_Native_InFeed", "magnite_name": "MAG_News_Native",
     "indexexchange_name": "IX_News_Native_Feed", "pubmatic_name": "PUB_News_Native",
     "site_section": "news", "format": "native", "size": "fluid",
     "viewability_vendor": "DoubleVerify", "active": True},
    {"ad_unit_id": "AU-105", "canonical_name": "Sports_Leaderboard_728x90",
     "adflow_name": "PDM_Sports_LB_728", "magnite_name": "MAG_Sports_LB_728",
     "indexexchange_name": "IX_Sports_LB_728", "pubmatic_name": "PUB_Sports_LB",
     "site_section": "sports", "format": "display", "size": "728x90",
     "viewability_vendor": "IAS", "active": True},
    {"ad_unit_id": "AU-106", "canonical_name": "Sports_Video_PreRoll",
     "adflow_name": "Sports_Video_PreRoll", "magnite_name": "MAG_Sports_VidPre",
     "indexexchange_name": "IX_Sports_PreRoll", "pubmatic_name": "PUB_Sports_Video",
     "site_section": "sports", "format": "video", "size": "640x480",
     "viewability_vendor": "DoubleVerify", "active": True},
    {"ad_unit_id": "AU-107", "canonical_name": "Finance_Skyscraper_160x600",
     "adflow_name": "Finance_Skyscraper_160x600", "magnite_name": "MAG_Finance_Sky_160",
     "indexexchange_name": "IX_Finance_Sky_160", "pubmatic_name": "PUB_Finance_Sky",
     "site_section": "finance", "format": "display", "size": "160x600",
     "viewability_vendor": "DoubleVerify", "active": True},
    {"ad_unit_id": "AU-108", "canonical_name": "Finance_MedRect_300x250",
     "adflow_name": "Finance_MedRect_300x250", "magnite_name": "MAG_Finance_MR_300",
     "indexexchange_name": "IX_Finance_MR_300", "pubmatic_name": "PUB_Finance_MR",
     "site_section": "finance", "format": "display", "size": "300x250",
     "viewability_vendor": "DoubleVerify", "active": True},
    {"ad_unit_id": "AU-109", "canonical_name": "Lifestyle_Interstitial_320x480",
     "adflow_name": "Lifestyle_Interstitial_320x480", "magnite_name": "MAG_Lifestyle_Interstitial",
     "indexexchange_name": "IX_Life_Interstit", "pubmatic_name": "PUB_Life_Interstit",
     "site_section": "lifestyle", "format": "interstitial", "size": "320x480",
     "viewability_vendor": "MOAT", "active": True},
    {"ad_unit_id": "AU-110", "canonical_name": "Tech_Banner_468x60",
     "adflow_name": "Tech_Banner_468x60", "magnite_name": "MAG_Tech_Banner_468",
     "indexexchange_name": "IX_Tech_Banner_468", "pubmatic_name": "PUB_Tech_Banner",
     "site_section": "tech", "format": "display", "size": "468x60",
     "viewability_vendor": "IAS", "active": True},
    {"ad_unit_id": "AU-111", "canonical_name": "Tech_MedRect_300x250",
     "adflow_name": "Tech_MedRect_300x250", "magnite_name": "MAG_Tech_MR_300",
     "indexexchange_name": "IX_Tech_MR_300", "pubmatic_name": "PUB_Tech_MR",
     "site_section": "tech", "format": "display", "size": "300x250",
     "viewability_vendor": "IAS", "active": True},
    {"ad_unit_id": "AU-112", "canonical_name": "Travel_Video_PreRoll",
     "adflow_name": "Travel_Video_PreRoll", "magnite_name": "MAG_Travel_VidPre",
     "indexexchange_name": "IX_Travel_PreRoll", "pubmatic_name": "PUB_Travel_Video",
     "site_section": "travel", "format": "video", "size": "640x480",
     "viewability_vendor": "DoubleVerify", "active": True},
    {"ad_unit_id": "AU-113", "canonical_name": "Travel_Banner_728x90",
     "adflow_name": "PDM_Travel_Banner_728", "magnite_name": "MAG_Travel_Banner_728",
     "indexexchange_name": "IX_Travel_Banner", "pubmatic_name": "PUB_Travel_Banner",
     "site_section": "travel", "format": "display", "size": "728x90",
     "viewability_vendor": "IAS", "active": True},
    {"ad_unit_id": "AU-114", "canonical_name": "Entertainment_Sticky_320x50",
     "adflow_name": "Entertainment_Sticky_320x50", "magnite_name": "MAG_Ent_Sticky_320",
     "indexexchange_name": "IX_Ent_Sticky", "pubmatic_name": "PUB_Ent_Sticky",
     "site_section": "entertainment", "format": "display", "size": "320x50",
     "viewability_vendor": "MOAT", "active": True},
    {"ad_unit_id": "AU-115", "canonical_name": "Auto_Sidebar_300x600",
     "adflow_name": "Auto_Sidebar_300x600", "magnite_name": "MAG_Auto_Sidebar",
     "indexexchange_name": "IX_Auto_Sidebar", "pubmatic_name": "PUB_Auto_Sidebar",
     "site_section": "auto", "format": "display", "size": "300x600",
     "viewability_vendor": "IAS", "active": False},
    {"ad_unit_id": "AU-116", "canonical_name": "Opinion_Leaderboard_728x90",
     "adflow_name": "Opinion_Leaderboard_728x90", "magnite_name": "MAG_Opinion_LB_728",
     "indexexchange_name": "IX_Opinion_LB", "pubmatic_name": "PUB_Opinion_LB",
     "site_section": "opinion", "format": "display", "size": "728x90",
     "viewability_vendor": "DoubleVerify", "active": False},
]

# Compact deal specs: (deal_id, ssp, rate_type, [(au_id, [(device, geo, cpm)])])
# rate_type: "fixed" = PG, "floor" = PMP
DEAL_SPECS = [
    ("DEAL-1001", "adflow", "floor", [("AU-101", [("desktop","US",8.50),("mobile","US",6.00),("desktop","UK",7.50)])]),
    ("DEAL-1002", "adflow", "fixed", [("AU-105", [("desktop","US",12.00),("mobile","US",9.50)])]),
    ("DEAL-1003", "adflow", "fixed", [
        ("AU-107", [("desktop","US",15.00),("mobile","US",11.00),("desktop","DE",13.50)]),
        ("AU-108", [("desktop","US",14.00),("mobile","US",10.50),("tablet","US",9.00)])]),
    ("DEAL-1004", "magnite", "floor", [("AU-109", [("desktop","US",7.00),("mobile","US",5.50),("desktop","FR",6.50)])]),
    ("DEAL-1005", "adflow", "fixed", [
        ("AU-103", [("desktop","US",5.00),("mobile","US",4.00),("desktop","UK",4.50)]),
        ("AU-110", [("desktop","US",4.50),("mobile","US",3.50)])]),
    ("DEAL-1006", "magnite", "floor", [("AU-112", [("desktop","US",18.00),("mobile","US",14.00),("desktop","DE",16.00)])]),
    ("DEAL-1007", "adflow", "floor", [("AU-101", [("desktop","US",9.00),("mobile","US",6.50)])]),
    ("DEAL-1008", "indexexchange", "fixed", [("AU-106", [("desktop","US",20.00),("mobile","US",16.00)])]),
    ("DEAL-1009", "magnite", "floor", [
        ("AU-114", [("desktop","US",3.00),("mobile","US",2.50)]),
        ("AU-102", [("desktop","US",5.00),("mobile","US",4.00)])]),
    ("DEAL-1010", "indexexchange", "fixed", [
        ("AU-104", [("desktop","US",6.00),("mobile","US",4.50)]),
        ("AU-111", [("desktop","US",5.50),("mobile","US",4.00)])]),
    ("DEAL-1011", "adflow", "floor", [("AU-113", [("desktop","US",5.50),("mobile","US",4.00)])]),
    # --- NEW DEALS ---
    ("DEAL-1012", "pubmatic", "fixed", [("AU-103", [("desktop","US",5.50),("mobile","US",4.20)])]),
    ("DEAL-1013", "pubmatic", "floor", [("AU-106", [("desktop","US",19.00),("mobile","US",15.00)])]),
    ("DEAL-1014", "adflow", "fixed", [("AU-104", [("desktop","US",6.50),("mobile","US",5.00)])]),
    ("DEAL-1015", "magnite", "floor", [("AU-101", [("desktop","US",8.00),("mobile","US",5.50)])]),
    ("DEAL-1016", "indexexchange", "fixed", [
        ("AU-105", [("desktop","US",11.50),("mobile","US",9.00)]),
        ("AU-112", [("desktop","US",17.00),("mobile","US",13.00)])]),
    ("DEAL-1017", "pubmatic", "floor", [
        ("AU-108", [("desktop","US",6.00),("mobile","US",4.50)]),
        ("AU-111", [("desktop","US",5.00),("mobile","US",3.50)])]),
    ("DEAL-1018", "adflow", "fixed", [("AU-107", [("desktop","US",14.50),("mobile","US",10.50)])]),
    ("DEAL-1019", "magnite", "floor", [("AU-113", [("desktop","US",5.00),("mobile","US",3.80)])]),
    ("DEAL-1020", "pubmatic", "fixed", [("AU-102", [("desktop","US",5.20),("mobile","US",4.00)])]),
    ("DEAL-1021", "indexexchange", "fixed", [("AU-114", [("desktop","US",3.50),("mobile","US",2.80)])]),
    ("DEAL-1022", "adflow", "floor", [("AU-110", [("desktop","US",4.00),("mobile","US",3.00)])]),
    ("DEAL-1023", "magnite", "fixed", [("AU-109", [("desktop","US",7.50),("mobile","US",5.80)])]),
    ("DEAL-1024", "pubmatic", "floor", [("AU-103", [("desktop","US",5.80),("mobile","US",4.50)])]),
    ("DEAL-1025", "adflow", "fixed", [("AU-112", [("desktop","US",16.50),("mobile","US",12.50)])]),
]

SCENARIOS = {
    ("DEAL-1001","AU-101"): "underbilled",
    ("DEAL-1002","AU-105"): "alias_correct",
    ("DEAL-1003","AU-107"): "overbilled",
    ("DEAL-1003","AU-108"): "overbilled",
    ("DEAL-1004","AU-109"): "within_tolerance",
    ("DEAL-1005","AU-103"): "correct",
    ("DEAL-1005","AU-110"): "correct",
    ("DEAL-1006","AU-112"): "correct",
    ("DEAL-1007","AU-101"): "no_ssp_row",
    ("DEAL-1008","AU-106"): "correct",
    ("DEAL-1009","AU-114"): "above_floor",
    ("DEAL-1009","AU-102"): "above_floor",
    ("DEAL-1010","AU-104"): "correct",
    ("DEAL-1010","AU-111"): "correct",
    ("DEAL-1011","AU-113"): "within_tolerance",
    ("DEAL-1012","AU-103"): "correct",
    ("DEAL-1013","AU-106"): "above_floor",
    ("DEAL-1014","AU-104"): "correct",
    ("DEAL-1015","AU-101"): "underbilled",
    ("DEAL-1016","AU-105"): "overbilled",
    ("DEAL-1016","AU-112"): "correct",
    ("DEAL-1017","AU-108"): "within_tolerance",
    ("DEAL-1017","AU-111"): "above_floor",
    ("DEAL-1018","AU-107"): "correct",
    ("DEAL-1019","AU-113"): "above_floor",
    ("DEAL-1020","AU-102"): "correct",
    ("DEAL-1021","AU-114"): "underbilled",
    ("DEAL-1022","AU-110"): "correct",
    ("DEAL-1023","AU-109"): "correct",
    ("DEAL-1024","AU-103"): "above_floor",
    ("DEAL-1025","AU-112"): "no_ssp_row",
}

# Contract dates for pacing analysis (contract_start, contract_end)
# Deals NOT listed here use the month boundaries (2026-04-01 to 2026-04-30)
DEAL_CONTRACT_DATES = {
    "DEAL-1001": ("2026-01-01","2026-12-31"),
    "DEAL-1002": ("2026-01-01","2026-06-30"),
    "DEAL-1003": ("2026-03-01","2026-08-31"),
    "DEAL-1004": ("2026-01-01","2026-12-31"),
    "DEAL-1005": ("2026-04-01","2026-09-30"),
    "DEAL-1006": ("2026-02-01","2026-07-31"),
    "DEAL-1007": ("2026-04-01","2026-06-30"),
    "DEAL-1008": ("2026-03-01","2026-08-31"),
    "DEAL-1009": ("2026-04-01","2026-12-31"),
    "DEAL-1010": ("2026-04-01","2026-09-30"),
    "DEAL-1011": ("2026-03-01","2026-12-31"),
    "DEAL-1012": ("2026-04-01","2026-06-30"),
    "DEAL-1013": ("2026-04-01","2026-09-30"),
    "DEAL-1014": ("2026-04-15","2026-07-14"),
    "DEAL-1015": ("2026-03-01","2026-08-31"),
    "DEAL-1016": ("2026-04-01","2026-09-30"),
    "DEAL-1017": ("2026-04-01","2026-12-31"),
    "DEAL-1018": ("2026-04-01","2026-06-30"),
    "DEAL-1019": ("2026-03-15","2026-12-31"),
    "DEAL-1020": ("2026-04-10","2026-07-09"),
    "DEAL-1021": ("2026-04-01","2026-06-30"),
    "DEAL-1022": ("2026-04-01","2026-09-30"),
    "DEAL-1023": ("2026-04-01","2026-06-30"),
    "DEAL-1024": ("2026-04-01","2026-12-31"),
    "DEAL-1025": ("2026-04-01","2026-06-30"),
}

# Pacing scenario overrides for PG deals: contracted impressions multiplier
# > 1.0 means contracted more than likely delivery → behind pace
# < 1.0 means contracted less than likely delivery → ahead of pace
# ~1.0 means on track. Only applies to PG (fixed) deals.
PACING_MULTIPLIERS = {
    "DEAL-1002": 1.0,
    "DEAL-1003": 0.85,
    "DEAL-1005": 1.6,
    "DEAL-1008": 1.0,
    "DEAL-1010": 1.4,
    "DEAL-1012": 0.7,
    "DEAL-1014": 1.0,
    "DEAL-1016": 1.8,
    "DEAL-1018": 1.0,
    "DEAL-1020": 0.9,
    "DEAL-1021": 1.5,
    "DEAL-1023": 1.0,
    "DEAL-1025": 1.3,
}

FUZZY_SSP_NAMES = {
    ("adflow","DEAL-1011","AU-113"): "PDM Travel Banner 728",
    ("magnite","DEAL-1004","AU-109"): "MAG_Lifstyle_Interstitial",
    ("indexexchange","DEAL-1008","AU-106"): "IX Sports PreRoll",
    ("indexexchange","DEAL-1010","AU-111"): "IX_Tech_mr_300",
    ("pubmatic","DEAL-1017","AU-108"): "PUB Finance_MR",
    ("pubmatic","DEAL-1013","AU-106"): "PUB_sports_Video",
}

IVT_REASONS = ["bot_traffic", "datacenter_ip", "suspicious_pattern", "known_crawler"]
IVT_CATEGORIES = ["GIVT", "SIVT"]

# Dates where IVT rows get written in MM/DD/YYYY format instead of ISO
IVT_MESSY_DATES = {date(2026,4,3), date(2026,4,7), date(2026,4,12),
                   date(2026,4,18), date(2026,4,23), date(2026,4,28)}


def expand_deal_specs():
    """Expand compact deal specs into RATE_CARD, DEAL_SSP dicts."""
    rate_card = []
    deal_ssp = {}
    for deal_id, ssp, rate_type, au_specs in DEAL_SPECS:
        deal_ssp[deal_id] = ssp
        start, end = DEAL_CONTRACT_DATES.get(deal_id, ("2026-04-01","2026-04-30"))
        deal_type = "programmatic_guaranteed" if rate_type == "fixed" else "pmp"
        for au_id, rates in au_specs:
            for device, geo, cpm in rates:
                rate_card.append({
                    "deal_id": deal_id, "ad_unit_id": au_id,
                    "device": device, "geo": geo,
                    "deal_type": deal_type, "rate_type": rate_type,
                    "cpm_usd": cpm, "currency": "USD",
                    "contract_start": start, "contract_end": end,
                })
    return rate_card, deal_ssp


def write_csv(filepath, rows, fieldnames):
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def get_ssp_name(ad_unit, ssp_id):
    return ad_unit.get(f"{ssp_id}_name", ad_unit["canonical_name"])


def main():
    random.seed(SEED)
    rate_card, deal_ssp = expand_deal_specs()

    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "samples", "programmatic-ad-revenue-reconciliation", "environment", "data",
        )
    os.makedirs(output_dir, exist_ok=True)
    ssp_billing_dir = os.path.join(output_dir, "ssp_billing")
    os.makedirs(ssp_billing_dir, exist_ok=True)

    au_lookup = {au["ad_unit_id"]: au for au in AD_UNITS}
    days = [date(2026, 4, d) for d in range(1, 31)]

    # ===== 1. ad_server_delivery.csv =====
    ad_server_rows = []
    for day in days:
        for rc in rate_card:
            if random.random() < 0.35:
                device = rc["device"]
                base_imps = {"desktop": random.randint(2500,22000),
                             "mobile": random.randint(4000,28000)}.get(device, random.randint(800,8000))
                if day.weekday() >= 5:
                    base_imps = int(base_imps * random.uniform(0.55, 0.75))
                clicks = max(0, int(base_imps * random.uniform(0.001, 0.008)))
                measurable = int(base_imps * random.uniform(0.92, 0.99))
                viewable = int(measurable * random.uniform(0.55, 0.85))
                ad_server_rows.append({
                    "date": day.isoformat(), "publisher_id": PUBLISHER_ID,
                    "ad_unit_id": rc["ad_unit_id"], "deal_id": rc["deal_id"],
                    "device": device, "geo": rc["geo"],
                    "delivered_impressions": base_imps,
                    "ad_server_clicks": clicks,
                    "viewable_impressions": viewable,
                    "measurable_impressions": measurable,
                })
    ad_server_rows.sort(key=lambda r: (r["date"], r["deal_id"], r["ad_unit_id"]))
    write_csv(os.path.join(output_dir, "ad_server_delivery.csv"), ad_server_rows,
              ["date","publisher_id","ad_unit_id","deal_id","device","geo",
               "delivered_impressions","ad_server_clicks","viewable_impressions","measurable_impressions"])
    print(f"ad_server_delivery.csv: {len(ad_server_rows)} rows")

    # ===== 2. ivt_report.csv (with messy dates on certain days) =====
    daily_dp_delivery = defaultdict(int)
    for row in ad_server_rows:
        daily_dp_delivery[(row["date"], row["deal_id"], row["ad_unit_id"])] += row["delivered_impressions"]

    ivt_rows = []
    for (day_str, deal_id, ad_unit_id), delivered in sorted(daily_dp_delivery.items()):
        is_high = deal_id == "DEAL-1003" and ad_unit_id == "AU-107"
        prob, lo, hi = (0.90, 0.13, 0.18) if is_high else (0.25, 0.03, 0.08)
        if random.random() < prob:
            ivt = max(1, int(delivered * random.uniform(lo, hi)))
            day_date = date.fromisoformat(day_str)
            fmt_date = day_date.strftime("%m/%d/%Y") if day_date in IVT_MESSY_DATES else day_str
            cat = random.choice(IVT_CATEGORIES)
            reason = random.choice(IVT_REASONS)
            n = random.choice([1, 1, 2])
            if n == 1 or ivt <= 1:
                ivt_rows.append({"date": fmt_date, "ad_unit_id": ad_unit_id, "deal_id": deal_id,
                                 "ivt_impressions": ivt, "ivt_category": cat, "ivt_reason": reason})
            else:
                split = random.randint(1, ivt - 1)
                r1, r2 = random.sample(IVT_REASONS, 2)
                ivt_rows.append({"date": fmt_date, "ad_unit_id": ad_unit_id, "deal_id": deal_id,
                                 "ivt_impressions": split, "ivt_category": random.choice(IVT_CATEGORIES), "ivt_reason": r1})
                ivt_rows.append({"date": fmt_date, "ad_unit_id": ad_unit_id, "deal_id": deal_id,
                                 "ivt_impressions": ivt - split, "ivt_category": random.choice(IVT_CATEGORIES), "ivt_reason": r2})
    ivt_rows.sort(key=lambda r: (r["date"], r["deal_id"]))
    write_csv(os.path.join(output_dir, "ivt_report.csv"), ivt_rows,
              ["date","ad_unit_id","deal_id","ivt_impressions","ivt_category","ivt_reason"])
    print(f"ivt_report.csv: {len(ivt_rows)} rows")

    # ===== 3. deal_rate_card.csv =====
    write_csv(os.path.join(output_dir, "deal_rate_card.csv"), rate_card,
              ["deal_id","ad_unit_id","device","geo","deal_type","rate_type",
               "cpm_usd","currency","contract_start","contract_end"])
    print(f"deal_rate_card.csv: {len(rate_card)} rows")

    # ===== 4. ad_unit_metadata.csv =====
    au_rows = [{
        "ad_unit_id": au["ad_unit_id"], "canonical_name": au["canonical_name"],
        "adflow_name": au["adflow_name"], "magnite_name": au["magnite_name"],
        "indexexchange_name": au["indexexchange_name"], "pubmatic_name": au["pubmatic_name"],
        "site_section": au["site_section"], "format": au["format"], "size": au["size"],
        "viewability_vendor": au["viewability_vendor"], "active": str(au["active"]).lower(),
    } for au in AD_UNITS]
    write_csv(os.path.join(output_dir, "ad_unit_metadata.csv"), au_rows,
              ["ad_unit_id","canonical_name","adflow_name","magnite_name","indexexchange_name",
               "pubmatic_name","site_section","format","size","viewability_vendor","active"])
    print(f"ad_unit_metadata.csv: {len(au_rows)} rows")

    # ===== 5. Ground truth computation =====
    del_dpdg = defaultdict(int)
    for row in ad_server_rows:
        del_dpdg[(row["deal_id"], row["ad_unit_id"], row["device"], row["geo"])] += row["delivered_impressions"]

    del_dp = defaultdict(int)
    for (d, au, dev, geo), v in del_dpdg.items():
        del_dp[(d, au)] += v

    ivt_dp = defaultdict(int)
    for row in ivt_rows:
        ivt_dp[(row["deal_id"], row["ad_unit_id"])] += int(row["ivt_impressions"])

    rc_lookup = {}
    rc_type_lookup = {}
    for rc in rate_card:
        rc_lookup[(rc["deal_id"], rc["ad_unit_id"], rc["device"], rc["geo"])] = rc["cpm_usd"]
        rc_type_lookup[(rc["deal_id"], rc["ad_unit_id"])] = rc["rate_type"]

    dp_combos = sorted(del_dp.keys())
    ground_truth = {}
    for dp_key in dp_combos:
        deal_id, ad_unit_id = dp_key
        total_del = del_dp[dp_key]
        total_ivt = ivt_dp.get(dp_key, 0)
        billable = total_del - total_ivt
        weighted_sum = sum(del_dpdg[(d,au,dev,geo)] * rc_lookup.get((d,au,dev,geo), 0)
                          for (d,au,dev,geo) in del_dpdg if d == deal_id and au == ad_unit_id)
        w_avg_cpm = weighted_sum / total_del if total_del > 0 else 0.0
        expected_rev = round(billable / 1000.0 * w_avg_cpm, 2)
        ground_truth[dp_key] = {
            "delivered": total_del, "ivt": total_ivt, "billable": billable,
            "weighted_avg_cpm": w_avg_cpm, "expected_revenue": expected_rev,
            "rate_type": rc_type_lookup.get(dp_key, "floor"),
        }

    # ===== 6. SSP billing =====
    ssp_rows_by_ssp = defaultdict(list)
    ssp_line_counters = defaultdict(lambda: 1)
    known_deals = set(rc["deal_id"] for rc in rate_card)

    for dp_key in dp_combos:
        deal_id, ad_unit_id = dp_key
        scenario = SCENARIOS.get(dp_key, "correct")
        if scenario == "no_ssp_row":
            continue
        ssp_id = deal_ssp.get(deal_id)
        if not ssp_id:
            continue
        gt = ground_truth[dp_key]
        au = au_lookup[ad_unit_id]
        fuzzy_key = (ssp_id, deal_id, ad_unit_id)
        ssp_name = FUZZY_SSP_NAMES.get(fuzzy_key, get_ssp_name(au, ssp_id))
        fee_pct = SSPS[ssp_id]["fee_pct"]
        w_cpm = gt["weighted_avg_cpm"]
        ln = ssp_line_counters[ssp_id]
        ssp_line_counters[ssp_id] += 1

        if scenario == "underbilled":
            ssp_billed = int(gt["billable"] * 0.92)
            net_rev = round(ssp_billed / 1000.0 * w_cpm, 2)
        elif scenario == "overbilled":
            ssp_billed = gt["delivered"]
            net_rev = round(ssp_billed / 1000.0 * w_cpm, 2)
        elif scenario == "above_floor":
            ssp_billed = gt["billable"]
            net_rev = round(gt["expected_revenue"] * random.uniform(1.15, 1.30), 2)
        elif scenario == "within_tolerance":
            ssp_billed = gt["billable"] + int(gt["billable"] * 0.005)
            net_rev = round(ssp_billed / 1000.0 * w_cpm, 2)
        elif scenario == "alias_correct":
            ssp_billed = gt["billable"]
            net_rev = gt["expected_revenue"]
        else:
            ssp_billed = gt["billable"]
            net_rev = gt["expected_revenue"]

        gross = round(net_rev / (1 - fee_pct), 2)
        fee = round(gross - net_rev, 2)
        ssp_rows_by_ssp[ssp_id].append({
            "ssp_line_id": f"{ssp_id.upper()}-LINE-{ln:03d}", "month": "2026-04",
            "deal_id": deal_id, "ssp_ad_unit_name": ssp_name,
            "billed_impressions": ssp_billed, "gross_revenue_usd": gross,
            "ssp_fee_pct": round(fee_pct * 100, 1), "ssp_fee_usd": fee,
            "net_revenue_usd": net_rev,
        })

    # Held rows: inactive AU + unknown deals
    for ssp_id, deal_id, au_name, imps, gross in [
        ("adflow","DEAL-1001","Auto_Sidebar_300x600",28500,285.00),
        ("adflow","DEAL-9999","Unknown_Placement_XYZ",45000,450.00),
        ("magnite","DEAL-8888","MAG_Unknown_Widget",32000,320.00),
        ("pubmatic","DEAL-7777","PUB_Mystery_Unit",18000,180.00),
    ]:
        ln = ssp_line_counters[ssp_id]
        ssp_line_counters[ssp_id] += 1
        fee_pct = SSPS[ssp_id]["fee_pct"]
        net = round(gross * (1 - fee_pct), 2)
        fee = round(gross - net, 2)
        ssp_rows_by_ssp[ssp_id].append({
            "ssp_line_id": f"{ssp_id.upper()}-LINE-{ln:03d}", "month": "2026-04",
            "deal_id": deal_id, "ssp_ad_unit_name": au_name,
            "billed_impressions": imps, "gross_revenue_usd": gross,
            "ssp_fee_pct": round(fee_pct * 100, 1), "ssp_fee_usd": fee,
            "net_revenue_usd": net,
        })

    billing_fields = ["ssp_line_id","month","deal_id","ssp_ad_unit_name","billed_impressions",
                      "gross_revenue_usd","ssp_fee_pct","ssp_fee_usd","net_revenue_usd"]
    for ssp_id, rows in ssp_rows_by_ssp.items():
        fname = SSPS[ssp_id]["billing_filename"]
        write_csv(os.path.join(ssp_billing_dir, fname), rows, billing_fields)
        print(f"ssp_billing/{fname}: {len(rows)} rows")

    # ===== 7. Contract goals (PG deals only) =====
    contract_goals = []
    for dp_key in dp_combos:
        deal_id, au_id = dp_key
        if dp_key not in ground_truth:
            continue
        rt = ground_truth[dp_key]["rate_type"]
        if rt != "fixed":
            continue
        mult = PACING_MULTIPLIERS.get(deal_id, 1.0)
        start_s, end_s = DEAL_CONTRACT_DATES.get(deal_id, ("2026-04-01","2026-04-30"))
        start_d, end_d = date.fromisoformat(start_s), date.fromisoformat(end_s)
        total_days = (end_d - start_d).days + 1
        elapsed_start = max(start_d, MONTH_START)
        elapsed_end = min(end_d, REPORTING_DATE)
        elapsed = (elapsed_end - elapsed_start).days + 1
        delivered = ground_truth[dp_key]["delivered"]
        projected = delivered * total_days / elapsed if elapsed > 0 else 0
        contracted = int(projected * mult)
        contracted = max(contracted, int(delivered * 0.5))
        contract_goals.append({
            "deal_id": deal_id, "ad_unit_id": au_id,
            "contracted_impressions": contracted,
            "contract_start": start_s, "contract_end": end_s,
        })
    write_csv(os.path.join(output_dir, "deal_contract_goals.csv"), contract_goals,
              ["deal_id","ad_unit_id","contracted_impressions","contract_start","contract_end"])
    print(f"deal_contract_goals.csv: {len(contract_goals)} rows")

    # ===== 8. SSP request log =====
    request_rows = []
    ssp_base_requests = {"adflow": 3200000, "magnite": 2400000, "indexexchange": 1800000, "pubmatic": 1500000}
    for day in days:
        for ssp_id, base in ssp_base_requests.items():
            daily = int(base / 30 * random.uniform(0.8, 1.2))
            if day.weekday() >= 5:
                daily = int(daily * 0.65)
            request_rows.append({"date": day.isoformat(), "ssp_id": ssp_id, "ad_requests": daily})
    request_rows.sort(key=lambda r: (r["date"], r["ssp_id"]))
    write_csv(os.path.join(output_dir, "ssp_request_log.csv"), request_rows,
              ["date","ssp_id","ad_requests"])
    print(f"ssp_request_log.csv: {len(request_rows)} rows")

    # ===== 9. Historical metrics =====
    hist = {
        "prior_month": "2026-03",
        "total_net_revenue_usd": 31850.00,
        "ivt_rate_pct": 4.2,
        "discrepancy_rate_pct": 5.3,
        "held_row_count": 2,
        "avg_ecpm_usd": 7.85,
    }
    with open(os.path.join(output_dir, "historical_metrics.json"), "w") as f:
        json.dump(hist, f, indent=2)
    print("historical_metrics.json written")

    # ===== 10. Ground truth summary =====
    ssp_name_to_auid = {}
    for au in AD_UNITS:
        for ssp_id in SSPS:
            name = get_ssp_name(au, ssp_id)
            ssp_name_to_auid[(ssp_id, name)] = (au["ad_unit_id"], au["active"])
    for (ssp_id, deal_id, au_id), fuzzy_name in FUZZY_SSP_NAMES.items():
        ssp_name_to_auid[(ssp_id, fuzzy_name)] = (au_id, au_lookup[au_id]["active"])

    all_ssp_rows = []
    for ssp_id, rows in ssp_rows_by_ssp.items():
        for r in rows:
            r["_ssp_id"] = ssp_id
            all_ssp_rows.append(r)

    total_expected = round(sum(gt["expected_revenue"] for gt in ground_truth.values()), 2)
    total_ssp = round(sum(float(r["net_revenue_usd"]) for r in all_ssp_rows), 2)

    total_adjusted = 0.0
    flagged_count = 0
    held_count = 0
    matched_dp_keys = set()

    for sr in all_ssp_rows:
        ssp_id = sr["_ssp_id"]
        au_info = ssp_name_to_auid.get((ssp_id, sr["ssp_ad_unit_name"]))
        if sr["deal_id"] not in known_deals or au_info is None or not au_info[1]:
            held_count += 1
            continue
        dp_key = (sr["deal_id"], au_info[0])
        if dp_key not in ground_truth:
            held_count += 1
            continue
        matched_dp_keys.add(dp_key)
        gt = ground_truth[dp_key]
        disc = round(gt["expected_revenue"] - float(sr["net_revenue_usd"]), 2)
        pct = round(abs(disc) / gt["expected_revenue"] * 100, 2) if gt["expected_revenue"] > 0 else 0.0
        total_adjusted += gt["expected_revenue"]
        if gt["rate_type"] == "floor" and disc < 0:
            pass
        elif abs(disc) > 5.0 and pct > 3.0:
            flagged_count += 1

    total_adjusted = round(total_adjusted, 2)
    unbilled = [dp for dp in dp_combos if dp not in matched_dp_keys]

    total_delivered = sum(gt["delivered"] for gt in ground_truth.values())
    total_ivt = sum(gt["ivt"] for gt in ground_truth.values())

    print(f"\n{'='*60}\nGROUND TRUTH\n{'='*60}")
    print(f"total_expected  = ${total_expected:.2f}")
    print(f"total_ssp       = ${total_ssp:.2f}")
    print(f"total_adjusted  = ${total_adjusted:.2f}")
    print(f"flagged         = {flagged_count}")
    print(f"held            = {held_count}")
    print(f"unbilled        = {unbilled}")
    print(f"total_delivered = {total_delivered}")
    print(f"total_ivt       = {total_ivt}")
    print(f"SSP billing rows: {sum(len(r) for r in ssp_rows_by_ssp.values())}")
    print(f"Deal/AU combos:   {len(dp_combos)}")

    gt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ground_truth.json")
    gt_export = {
        "total_expected_revenue_usd": total_expected,
        "total_ssp_reported_revenue_usd": total_ssp,
        "total_adjusted_revenue_usd": total_adjusted,
        "flagged_discrepancy_count": flagged_count,
        "held_row_count": held_count,
        "unbilled_deal_ad_units": [list(dp) for dp in unbilled],
        "total_delivered_impressions": total_delivered,
        "total_ivt_impressions": total_ivt,
        "deal_ad_unit_details": {},
    }
    for dp_key in dp_combos:
        gt = ground_truth[dp_key]
        gt_export["deal_ad_unit_details"][f"{dp_key[0]}_{dp_key[1]}"] = {
            "delivered": gt["delivered"], "ivt": gt["ivt"], "billable": gt["billable"],
            "weighted_avg_cpm": round(gt["weighted_avg_cpm"], 6),
            "expected_revenue": gt["expected_revenue"],
            "rate_type": gt["rate_type"],
            "scenario": SCENARIOS.get(dp_key, "correct"),
        }
    with open(gt_path, "w") as f:
        json.dump(gt_export, f, indent=2)
    print(f"\nGround truth → {gt_path}")


if __name__ == "__main__":
    main()
