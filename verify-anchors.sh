#!/usr/bin/env bash
set -euo pipefail

ENS_NAME="jaywisdom.eth"
ENS_REGISTRY="0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e"
ENS_KEY="receipts_engine_v1_sha256"
RPC_URL="${ETH_RPC_URL:-https://ethereum.publicnode.com}"
SHA_FILE="receipts_engine_v1.tar.gz.sha256"

normalize() {
  printf '%s' "$1" | tr -d '\r\n"' | xargs
}

namehash() {
  cast namehash "$ENS_NAME"
}

resolve_resolver() {
  local node
  node="$(namehash)"
  cast call "$ENS_REGISTRY" \
    "resolver(bytes32)(address)" \
    "$node" \
    --rpc-url "$RPC_URL" | tr -d '\r\n"'
}

read_ens_text() {
  local node resolver
  node="$(namehash)"
  resolver="$(resolve_resolver)"
  cast call "$resolver" \
    "text(bytes32,string)(string)" \
    "$node" \
    "$ENS_KEY" \
    --rpc-url "$RPC_URL"
}

read_expected_hash() {
  [[ -f "$SHA_FILE" ]] || { echo "FAIL: missing $SHA_FILE"; exit 1; }
  awk '{print $1}' "$SHA_FILE"
}

main() {
  local resolver expected onchain
  resolver="$(resolve_resolver)"
  expected="$(normalize "$(read_expected_hash)")"
  onchain="$(normalize "$(read_ens_text)")"

  echo "ENS_NAME=$ENS_NAME"
  echo "ACTIVE_RESOLVER=$resolver"
  echo "ENS_KEY=$ENS_KEY"
  echo "EXPECTED_SHA256=$expected"
  echo "ONCHAIN_VALUE=$onchain"

  [[ "$onchain" =~ ^[a-f0-9]{64}$ ]] || {
    echo "RESULT=FAIL"
    echo "DETAIL=missing_or_invalid_onchain_value"
    exit 1
  }

  if [[ "$onchain" == "$expected" ]]; then
    echo "RESULT=PASS"
    echo "DETAIL=onchain value matches expected sha256"
  else
    echo "RESULT=FAIL"
    echo "DETAIL=onchain value does not match expected sha256"
    exit 1
  fi
}

main "$@"
