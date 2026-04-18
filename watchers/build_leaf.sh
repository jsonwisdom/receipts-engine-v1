#!/usr/bin/env bash
set -euo pipefail
SRC="${1:-}"
[ -n "$SRC" ] && [ -f "$SRC" ] || { echo "missing source"; exit 1; }
mkdir -p _artifacts/current _receipts

# 1. canonical text extraction
TXT=$(watchers/extract_text.sh "$SRC")

# 2. deterministic content hash
BYTES=$(wc -c < "$TXT" | tr -d ' ')
CONTENT_HASH=$(sha256sum "$TXT" | awk '{print $1}')

# 3. canonical artifact JSON
CANON=$(SRC="$SRC" HASH="$CONTENT_HASH" BYTES="$BYTES" python3 - <<'PY'
import json,os
print(json.dumps({
  "source_path": os.environ['SRC'],
  "content_sha256": os.environ['HASH'],
  "bytes": int(os.environ['BYTES'])
}, sort_keys=True, separators=(',',':')))
PY
)
printf '%s\n' "$CANON" > _artifacts/current/artifact.json

# 4. receipt
printf '{"artifact_sha256":"%s"}\n' "$(sha256sum _artifacts/current/artifact.json | awk '{print $1}')" > _receipts/receipt.json

# 5. Merkle leaf (domain separated)
LEAF=$(HASH="$CONTENT_HASH" python3 - <<'PY'
import hashlib,os
h=os.environ['HASH']
leaf=hashlib.sha256(("\\x00v1"+h).encode()).hexdigest()
print(leaf)
PY
)

printf '{"leaf_hash":"%s","content_sha256":"%s"}\n' "$LEAF" "$CONTENT_HASH" > _artifacts/current/leaf.json

echo "ok"
