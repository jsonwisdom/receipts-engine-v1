#!/usr/bin/env bash
set -euo pipefail
SRC="${1:-}"
[ -n "$SRC" ] && [ -f "$SRC" ] || { echo "missing source"; exit 1; }
mkdir -p _artifacts/current _receipts
BYTES=$(wc -c < "$SRC" | tr -d ' ')
HASH=$(sha256sum "$SRC" | awk '{print $1}')
CANON=$(SRC="$SRC" HASH="$HASH" BYTES="$BYTES" python3 - <<'PY'
import json,os
src=os.environ['SRC']; h=os.environ['HASH']; b=int(os.environ['BYTES'])
print(json.dumps({"source_path":src,"content_sha256":h,"bytes":b},sort_keys=True,separators=(',',':')))
PY
)
printf '%s\n' "$CANON" > _artifacts/current/artifact.json
printf '{"artifact_sha256":"%s"}\n' "$(sha256sum _artifacts/current/artifact.json | awk '{print $1}')" > _receipts/receipt.json
echo "ok"
