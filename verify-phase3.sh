#!/usr/bin/env bash
set -euo pipefail

ENS_NAME="jaywisdom.eth"
RESOLVER="0x231b0ee14048e9dccd1d247744d114a4eb5e8e63"
RPC_URL="${ETH_RPC_URL:-https://ethereum.publicnode.com}"

ROOT_FILE="attestations/anchors.json"
MANIFEST_FILE="attestations/phase3-manifest.json"
RELEASE_FILE="attestations/phase3-release.json"
ARTIFACT_FILE="receipts_engine_v1.tar.gz"

normalize() { printf '%s' "$1" | tr -d '\r\n"' | xargs; }
sha() { sha256sum "$1" | awk '{print $1}'; }

read_ens() {
  local key="$1"
  local node
  node="$(cast namehash "$ENS_NAME")"
  cast call "$RESOLVER" "text(bytes32,string)(string)" "$node" "$key" --rpc-url "$RPC_URL" 2>/dev/null || echo ""
}

# Trust root must be zero-byte
[[ -f "$ROOT_FILE" ]] || { echo "FAIL: missing $ROOT_FILE"; exit 1; }
[[ ! -s "$ROOT_FILE" ]] || { echo "FAIL: trust root not zero-byte"; exit 1; }
ROOT_HASH=$(normalize "$(sha "$ROOT_FILE" || true)")
echo "ROOT_OK zero-byte sha256=$ROOT_HASH"

ENS_KEY=$(python3 -c "import json;print(json.load(open('attestations/phase3-manifest.json'))['artifacts'][0]['ens_key'])")
EXP_SHA=$(python3 -c "import json;print(json.load(open('attestations/phase3-release.json'))['artifact']['sha256'])")

[[ -f "$ARTIFACT_FILE" ]] || { echo "FAIL: missing artifact"; exit 1; }
LOC_SHA=$(normalize "$(sha "$ARTIFACT_FILE")")
echo "LOCAL_SHA=$LOC_SHA"

ONCHAIN=$(normalize "$(read_ens "$ENS_KEY")")
echo "ONCHAIN_$ENS_KEY=$ONCHAIN"

fail=0
[[ "$LOC_SHA" == "$EXP_SHA" ]] || { echo "FAIL: local != release"; fail=1; }
[[ "$ONCHAIN" =~ ^[a-f0-9]{64}$ ]] || { echo "FAIL: invalid onchain"; fail=1; }
[[ "$ONCHAIN" == "$LOC_SHA" ]] || { echo "FAIL: onchain != local"; fail=1; }

[[ $fail -eq 0 ]] && echo "PASS: phase-3 verified" || exit 1
