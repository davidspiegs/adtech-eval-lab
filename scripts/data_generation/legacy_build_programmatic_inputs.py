#!/usr/bin/env python3
"""Build task inputs at Docker build time.

Copies source data to /root/data/ and converts the Index Exchange billing
CSV into a pipe-delimited PDF.
"""

import csv
import shutil
from pathlib import Path

from fpdf import FPDF

SOURCE = Path("/tmp/task-data")
TARGET = Path("/root/data")


def copy_core_files():
    for name in [
        "ad_server_delivery.csv", "ivt_report.csv", "deal_rate_card.csv",
        "ad_unit_metadata.csv", "reconciliation_policy.md", "client_request.md",
        "deal_contract_goals.csv", "ssp_request_log.csv", "historical_metrics.json",
    ]:
        src = SOURCE / name
        if src.exists():
            shutil.copy2(src, TARGET / name)


def copy_csv_billing():
    ssp_dir = TARGET / "ssp_billing"
    ssp_dir.mkdir(exist_ok=True)
    for name in ["adflow_exchange_april_2026.csv", "magnite_april_2026.csv",
                 "pubmatic_april_2026.csv"]:
        src = SOURCE / "ssp_billing" / name
        if src.exists():
            shutil.copy2(src, ssp_dir / name)


def generate_ix_pdf():
    csv_path = SOURCE / "ssp_billing" / "indexexchange_april_2026.csv"
    pdf_path = TARGET / "ssp_billing" / "indexexchange_april_2026.pdf"
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        rows = list(reader)

    pdf = FPDF(orientation="L", format="letter")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Index Exchange", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Monthly Billing Statement - April 2026", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Publisher: Pinnacle Digital Media (PDM-001)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Courier", "", 8)
    header = " | ".join(cols)
    pdf.cell(0, 5, header, new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "-" * len(header), new_x="LMARGIN", new_y="NEXT")
    for row in rows:
        pdf.cell(0, 5, " | ".join(str(row[c]) for c in cols), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "All amounts in USD. Net revenue is after deduction of SSP fees.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(pdf_path))


def main():
    TARGET.mkdir(parents=True, exist_ok=True)
    (TARGET / "ssp_billing").mkdir(parents=True, exist_ok=True)
    copy_core_files()
    copy_csv_billing()
    generate_ix_pdf()
    print("Build inputs complete.")


if __name__ == "__main__":
    main()
