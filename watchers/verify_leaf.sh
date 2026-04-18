#!/usr/bin/env bash
set -euo pipefail
A="_artifacts/current/artifact.json"
R="_receipts/receipt.json"
[ -f "$A" ] && [ -f "$R" ] || { echo "missing outputs"; exit 1; }
AH=$(sha256sum "$A" | awk '{print $1}')
RH=$(python3 - <<'PY'
import json
print(json.load(open('_receipts/receipt.json'))['artifact_sha256'])
PY
)
[ "$AH" = "$RH" ] && echo "verify:pass" || { echo "verify:fail"; exit 1; }
