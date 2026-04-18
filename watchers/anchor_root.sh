#!/usr/bin/env bash
set -euo pipefail
STATE="_truth/state.json"
TREE="_artifacts/current/tree.json"
[ -f "$STATE" ] && [ -f "$TREE" ] || { echo "missing inputs"; exit 1; }

: "${ENS_NAME:?missing ENS_NAME}"
: "${RPC_URL:?missing RPC_URL}"
: "${ENS_RESOLVER:?missing ENS_RESOLVER}"
: "${EAS_CONTRACT:?missing EAS_CONTRACT}"
: "${EAS_SCHEMA_UID:?missing EAS_SCHEMA_UID}"
: "${PRIVATE_KEY:?missing PRIVATE_KEY}"

MERKLE_ROOT=$(python3 - <<'PY'
import json
print(json.load(open('_artifacts/current/tree.json'))['merkle_root'])
PY
)
CID_ARTIFACT=$(python3 - <<'PY'
import json
s=json.load(open('_truth/state.json'))
print(s.get('last_cid_artifact',''))
PY
)

[ -n "$MERKLE_ROOT" ] || { echo "missing merkle root"; exit 1; }
[ -n "$CID_ARTIFACT" ] || { echo "missing artifact CID in state"; exit 1; }

# 1) ENS text records (example keys; resolver must support text() writes via your chosen toolchain)
echo "ENS anchor target: $ENS_NAME"
echo "Set text records: receipts.latest_root=$MERKLE_ROOT receipts.latest_cid=$CID_ARTIFACT"

# 2) EAS attestation payload stub
ATTEST_JSON=$(MERKLE_ROOT="$MERKLE_ROOT" CID_ARTIFACT="$CID_ARTIFACT" ENS_NAME="$ENS_NAME" python3 - <<'PY'
import json,os
print(json.dumps({
  'ens_name': os.environ['ENS_NAME'],
  'merkle_root': os.environ['MERKLE_ROOT'],
  'artifact_cid': os.environ['CID_ARTIFACT']
}, sort_keys=True, separators=(',',':')))
PY
)
mkdir -p _receipts
printf '%s\n' "$ATTEST_JSON" > _receipts/eas_payload.json

echo "anchor:ready"
echo "merkle_root:$MERKLE_ROOT"
echo "artifact_cid:$CID_ARTIFACT"
echo "payload:_receipts/eas_payload.json"
