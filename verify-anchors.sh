#!/usr/bin/env bash
set -euo pipefail

ENS_NAME="jaywisdom.eth"
RESOLVER="0x231b0ee14048e9dccd1d247744d114a4eb5e8e63"
RPC_URL="${ETH_RPC_URL:-https://ethereum.publicnode.com}"
ANCHORS_FILE="attestations/anchors.json"

declare -A ENS_KEY_SOURCE=(
  ["anchors_json_sha256"]="file:attestations/anchors.json"
  ["receipts_engine_v1_sha256"]="file:receipts_engine_v1.tar.gz"
)

normalize_hash() {
  printf '%s' "$1" | tr -d '\r\n"' | xargs
}

compute_file_hash() {
  local file="$1"
  [[ -f "$file" ]] || return 1
  sha256sum "$file" | awk '{print $1}'
}

read_ens_text() {
  local key="$1"
  local node result
  node="$(cast namehash "$ENS_NAME")" || { echo "ERROR: namehash failed"; return 1; }
  result="$(cast call "$RESOLVER" "text(bytes32,string)(string)" "$node" "$key" --rpc-url "$RPC_URL" 2>&1)" || {
    echo "RPC_ERROR"
    return 1
  }
  printf '%s\n' "$result"
}

main() {
  [[ -f "$ANCHORS_FILE" ]] || { echo "FAIL: missing $ANCHORS_FILE"; exit 1; }

  local local_hash onchain_raw onchain_hash source_info failed=0 verified=0 unverified=0
  local_hash="$(normalize_hash "$(compute_file_hash "$ANCHORS_FILE")")"

  echo "ENS_NAME=$ENS_NAME"
  echo "RESOLVER=$RESOLVER"
  echo "ANCHORS_FILE=$ANCHORS_FILE"
  echo "LOCAL_ANCHORS_SHA256=$local_hash"
  echo

  for key in "${!ENS_KEY_SOURCE[@]}"; do
    source_info="${ENS_KEY_SOURCE[$key]}"
    echo "KEY=$key"
    echo "SOURCE=$source_info"

    onchain_raw="$(read_ens_text "$key")" || true
    if [[ "$onchain_raw" == "RPC_ERROR" || "$onchain_raw" == ERROR:* || -z "$onchain_raw" ]]; then
      echo "RESULT=FAIL"
      echo "DETAIL=unable to read onchain value"
      echo
      ((failed+=1))
      continue
    fi

    onchain_hash="$(normalize_hash "$onchain_raw")"
    echo "ONCHAIN_VALUE=$onchain_hash"

    if [[ ! "$onchain_hash" =~ ^[a-f0-9]{64}$ ]]; then
      echo "RESULT=FAIL"
      echo "DETAIL=onchain value is not a valid 64-char sha256"
      echo
      ((failed+=1))
      continue
    fi

    if [[ "$source_info" == file:* ]]; then
      compare_file="${source_info#file:}"
      compare_hash="$(normalize_hash "$(compute_file_hash "$compare_file")")" || compare_hash=""
      echo "LOCAL_FILE=$compare_file"
      echo "LOCAL_HASH=$compare_hash"
      if [[ -z "$compare_hash" ]]; then
        echo "RESULT=FAIL"
        echo "DETAIL=unable to compute local file hash"
        ((failed+=1))
      elif [[ "$onchain_hash" == "$compare_hash" ]]; then
        echo "RESULT=PASS"
        echo "DETAIL=local hash matches onchain"
        ((verified+=1))
      else
        echo "RESULT=FAIL"
        echo "DETAIL=local hash does not match onchain"
        ((failed+=1))
      fi
    else
      echo "RESULT=UNVERIFIED_REFERENCE"
      echo "DETAIL=no local file comparison defined"
      ((unverified+=1))
    fi
    echo
  done

  echo "SUMMARY verified=$verified unverified=$unverified failed=$failed"
  [[ "$failed" -eq 0 ]]
}

main "$@"
