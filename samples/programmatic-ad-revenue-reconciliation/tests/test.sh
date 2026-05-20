#!/bin/bash

echo "=== Programmatic Ad Revenue Reconciliation Verifier ==="
mkdir -p /logs/verifier

pip3 install --break-system-packages pytest==8.4.1 pytest-json-ctrf==0.3.5 rapidfuzz==3.10.1 openpyxl==3.1.5 pdfplumber==0.11.4 2>/dev/null

set +e
pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA -v
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo "ALL CHECKS PASSED"
    echo 1 > /logs/verifier/reward.txt
else
    echo "SOME CHECKS FAILED"
    echo 0 > /logs/verifier/reward.txt
fi

exit 0
