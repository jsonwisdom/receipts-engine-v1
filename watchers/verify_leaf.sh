#!/usr/bin/env bash
set -euo pipefail
A="_artifacts/current/artifact.json"
T="_artifacts/current/source.txt"
R="_receipts/receipt.json"
S="_truth/state.json"
[ -f "$A" ] && [ -f "$T" ] && [ -f "$R" ] && [ -f "$S" ] || { echo "missing inputs"; exit 1; }

AH=$(sha256sum "$A" | awk '{print $1}')
RH=$(python3 - <<'PY'
import json
print(json.load(open('_receipts/receipt.json'))['artifact_sha256'])
PY
)

if [ "$AH" != "$RH" ]; then
  echo "verify:fail"
  exit 1
fi

CONTENT_HASH=$(python3 - <<'PY'
import json
print(json.load(open('_artifacts/current/artifact.json'))['content_sha256'])
PY
)

CID_TXT=$(ipfs add -Q "$T")
CID_ART=$(ipfs add -Q "$A")

TMP=$(mktemp)
python3 - <<PY > "$TMP"
import json
s=json.load(open("_truth/state.json"))
s["last_artifact_sha256"] = "${AH}"
s["last_content_sha256"] = "${CONTENT_HASH}"
s["last_cid_source"] = "${CID_TXT}"
s["last_cid_artifact"] = "${CID_ART}"
s["status"] = "verified"
print(json.dumps(s, sort_keys=True, separators=(",",":")))
PY
mv "$TMP" "$S"

echo "verify:pass"
echo "CID source.txt: $CID_TXT"
echo "CID artifact.json: $CID_ART"
