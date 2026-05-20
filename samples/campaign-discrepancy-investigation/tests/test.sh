#!/bin/bash

echo "=== Campaign Discrepancy Investigation Verifier ==="
mkdir -p /logs/verifier

pip3 install --break-system-packages pytest==8.4.1 pytest-json-ctrf==0.3.5 rapidfuzz==3.10.1 openpyxl==3.1.5 2>/dev/null

set +e
pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA -v
EXIT_CODE=$?
set -e

# Partial scoring: reward = passed / total
REWARD=$(python3 -c "
import json, sys
try:
    data = json.load(open('/logs/verifier/ctrf.json'))
    results = data.get('results', {})
    tests = results.get('tests', [])
    total = len(tests)
    passed = sum(1 for t in tests if t.get('status') == 'passed')
    reward = passed / total if total > 0 else 0.0
    print(f'{reward:.4f}')
except Exception as e:
    print('0.0', file=sys.stderr)
    print('0')
")

echo "Reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

exit 0
