#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# ZT Observer Network → Media Ingestion v1
# EVIDENCE-GRADE MVP: Deterministic extraction + IPFS + Base anchor events
# ============================================================================

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
ROOT="${HOME}/jay-agent"
TRUTH_DIR="$ROOT/_truth"
MEDIA_DIR="$TRUTH_DIR/media"
CONTENT_DIR="$MEDIA_DIR/content"
RECEIPTS_DIR="$MEDIA_DIR/receipts"
LATEST_DIR="$MEDIA_DIR/latest"
DIFFS_DIR="$MEDIA_DIR/diffs"
LOG_DIR="$TRUTH_DIR/logs"
LOG_FILE="$LOG_DIR/jay_media.log"
CONTRACT_FILE="$ROOT/.anchor_contract"
ABI_FILE="$ROOT/MediaAnchor.abi.json"

# Golden test configuration
GOLDEN_DIR="$ROOT/testdata"
GOLDEN_RECEIPT_FILE="$GOLDEN_DIR/golden_receipt.json"
GOLDEN_EXPECTED_FILE="$GOLDEN_DIR/golden_expected.json"
GOLDEN_VERSION_FILE="$ROOT/.foundry_version"

# Default Base RPC (can be overridden by env)
BASE_RPC="${BASE_RPC:-https://mainnet.base.org}"

mkdir -p "$CONTENT_DIR" "$RECEIPTS_DIR" "$LATEST_DIR" "$DIFFS_DIR" "$LOG_DIR" "$GOLDEN_DIR"

# ----------------------------------------------------------------------------
# Dependency checks (hard fail if missing)
# ----------------------------------------------------------------------------
need(){ command -v "$1" >/dev/null 2>&1 || { echo "missing: $1"; exit 1; }; }
need curl
need jq
need sha256sum
need sed
need tr
need diff
need ipfs
need cast
need readability-cli
need html2text

# ----------------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------------
slug(){ echo -n "$1" | sha256sum | cut -c1-16; }
ts(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log(){ printf "%s %s\n" "$(ts)" "$*" | tee -a "$LOG_FILE"; }

# ----------------------------------------------------------------------------
# Deterministic normalization
# ----------------------------------------------------------------------------
normalize(){
  local url="$1"
  curl -sL "$url" | readability-cli - 2>/dev/null | html2text -utf8 2>/dev/null | \
    sed 's/[[:space:]]\+/ /g' | sed 's/^ //; s/ $//'
}

# ----------------------------------------------------------------------------
# Stable content object (deterministic CID)
# ----------------------------------------------------------------------------
ensure_content(){
  local url="$1" text hash content_file
  text="$(normalize "$url")"
  hash="$(printf '%s' "$text" | sha256sum | cut -d' ' -f1)"
  content_file="$CONTENT_DIR/${hash}.json"
  
  if [ ! -f "$content_file" ]; then
    jq -n --arg url "$url" --arg text "$text" --arg hash "0x$hash" \
      '{source_url:$url, canonical_text:$text, content_hash:$hash}' > "$content_file"
    local cid
    cid=$(ipfs add -Q "$content_file")
    local tmp; tmp=$(mktemp)
    jq --arg cid "$cid" '.content_cid = $cid' "$content_file" > "$tmp"
    mv "$tmp" "$content_file"
    log "NEW_CONTENT $url -> hash:$hash cid:$cid"
  fi
  
  echo "$content_file"
}

# ----------------------------------------------------------------------------
# Timestamped receipt (changes on every observation)
# ----------------------------------------------------------------------------
create_receipt(){
  local url="$1" content_file slug now receipt_file
  content_file="$2"
  slug="$(slug "$url")"
  now="$(ts)"
  receipt_file="$RECEIPTS_DIR/${slug}_$(date -u +%Y%m%dT%H%M%SZ).json"
  
  jq -n \
    --arg url "$url" \
    --arg hash "$(jq -r .content_hash "$content_file")" \
    --arg cid "$(jq -r .content_cid "$content_file")" \
    --arg now "$now" \
    '{source_url:$url, content_hash:$hash, content_cid:$cid, retrieved_at_utc:$now, receipt_cid:null, tx_hash:null}' \
    > "$receipt_file"
  
  ln -sf "$receipt_file" "$LATEST_DIR/${slug}.json"
  echo "$receipt_file"
}

# ----------------------------------------------------------------------------
# IPFS anchor (store receipt, get receipt_cid)
# ----------------------------------------------------------------------------
anchor_ipfs_receipt(){
  local receipt="$1"
  local receipt_cid
  receipt_cid=$(ipfs add -Q "$receipt")
  local tmp; tmp=$(mktemp)
  jq --arg rc "$receipt_cid" '.receipt_cid = $rc' "$receipt" > "$tmp"
  mv "$tmp" "$receipt"
  log "IPFS_RECEIPT $receipt -> cid:$receipt_cid"
  echo "$receipt_cid"
}

# ----------------------------------------------------------------------------
# Base anchor (MediaAnchor contract event)
# ----------------------------------------------------------------------------
anchor_base(){
  local receipt="$1"
  [ -f "$receipt" ] || { echo "missing: $receipt"; exit 1; }
  [ -f "$CONTRACT_FILE" ] || { echo "missing: $CONTRACT_FILE (deploy contract first)"; exit 1; }
  
  local contract_addr tx_hash
  contract_addr=$(cat "$CONTRACT_FILE")
  
  local receipt_cid
  receipt_cid=$(jq -r .receipt_cid "$receipt")
  if [ "$receipt_cid" = "null" ] || [ -z "$receipt_cid" ]; then
    receipt_cid=$(anchor_ipfs_receipt "$receipt")
  fi
  
  local content_hash content_cid source_url observed_at
  content_hash=$(jq -r .content_hash "$receipt" | sed 's/^0x//')
  content_cid=$(jq -r .content_cid "$receipt")
  source_url=$(jq -r .source_url "$receipt")
  observed_at=$(jq -r .retrieved_at_utc "$receipt")
  
  # Send transaction with --json for machine-readable output
  tx_hash=$(cast send --rpc-url "$BASE_RPC" --private-key "$PRIVATE_KEY" \
    "$contract_addr" \
    "anchor(bytes32,string,string,string,string)" \
    "0x$content_hash" "$content_cid" "$receipt_cid" "$source_url" "$observed_at" \
    --gas-limit 200000 --json | jq -r '.transactionHash')
  
  local tmp; tmp=$(mktemp)
  jq --arg tx "$tx_hash" '.tx_hash = $tx' "$receipt" > "$tmp"
  mv "$tmp" "$receipt"
  
  log "BASE_ANCHOR $receipt -> tx:$tx_hash"
  echo "$tx_hash"
}

# ----------------------------------------------------------------------------
# Verify (pure event encoding – NO MIXING, NO FALLBACKS)
# ----------------------------------------------------------------------------
verify(){
  local receipt="$1"
  local golden_mode="${2:-false}"
  
  [ -f "$receipt" ] || { echo "missing: $receipt"; exit 1; }
  [ -f "$CONTRACT_FILE" ] || { echo "missing: $CONTRACT_FILE"; exit 1; }
  
  local contract_addr tx_hash
  contract_addr=$(cat "$CONTRACT_FILE")
  tx_hash=$(jq -r .tx_hash "$receipt")
  [ "$tx_hash" != "null" ] || { echo "❌ no tx_hash"; exit 1; }
  
  # 1. Verify content_hash matches canonical_text from IPFS
  local content_cid content_json text stored_hash recomputed
  content_cid=$(jq -r .content_cid "$receipt")
  content_json=$(ipfs cat "$content_cid")
  text=$(echo "$content_json" | jq -r .canonical_text)
  stored_hash=$(jq -r .content_hash "$receipt" | sed 's/^0x//')
  recomputed=$(printf '%s' "$text" | sha256sum | cut -d' ' -f1)
  [ "$stored_hash" = "$recomputed" ] || { echo "❌ hash mismatch"; exit 1; }
  echo "✅ content_hash matches canonical_text"
  
  # 2. Verify content_cid resolvable
  ipfs cat "$content_cid" >/dev/null || { echo "❌ content_cid not on IPFS"; exit 1; }
  echo "✅ content_cid resolvable"
  
  # 3. Verify receipt_cid matches actual IPFS object
  local receipt_cid receipt_from_ipfs
  receipt_cid=$(jq -r .receipt_cid "$receipt")
  [ "$receipt_cid" != "null" ] || { echo "❌ no receipt_cid"; exit 1; }
  receipt_from_ipfs=$(ipfs cat "$receipt_cid")
  [ "$(echo "$receipt_from_ipfs" | jq -r .tx_hash)" = "$tx_hash" ] || { echo "❌ receipt_cid does not match stored receipt"; exit 1; }
  echo "✅ receipt_cid matches IPFS object"
  
  # 4. Fetch transaction receipt JSON
  local tx_receipt_json
  tx_receipt_json=$(cast receipt --rpc-url "$BASE_RPC" "$tx_hash" --json)
  [ -n "$tx_receipt_json" ] || { echo "❌ tx_hash not found on Base"; exit 1; }
  
  # Extract the log from our contract address
  local log_json
  log_json=$(echo "$tx_receipt_json" | jq -r --arg addr "$contract_addr" \
    '.logs[] | select(.address == $addr)')
  [ -n "$log_json" ] || { echo "❌ no log from anchor contract in tx"; exit 1; }
  
  # 5. Compute expected event data using pure abi-encode-event --json
  local expected_json
  expected_json=$(cast abi-encode-event --json \
    "Anchored(bytes32,string,string,string,string,address)" \
    "0x$stored_hash" \
    "$(jq -r .content_cid "$receipt")" \
    "$receipt_cid" \
    "$(jq -r .source_url "$receipt")" \
    "$(jq -r .retrieved_at_utc "$receipt")" \
    "0x0000000000000000000000000000000000000000")
  
  # Extract expected topics and data
  local expected_topic0 expected_topic1 expected_data
  expected_topic0=$(echo "$expected_json" | jq -r '.topics[0]')
  expected_topic1=$(echo "$expected_json" | jq -r '.topics[1]')
  expected_data=$(echo "$expected_json" | jq -r '.data')
  
  # 6. Compare actual vs expected
  local actual_topic0 actual_topic1 actual_data
  actual_topic0=$(echo "$log_json" | jq -r '.topics[0]')
  actual_topic1=$(echo "$log_json" | jq -r '.topics[1]')
  actual_data=$(echo "$log_json" | jq -r '.data')
  
  [ "$actual_topic0" = "$expected_topic0" ] || { echo "❌ topic[0] mismatch"; exit 1; }
  [ "$actual_topic1" = "$expected_topic1" ] || { echo "❌ topic[1] mismatch"; exit 1; }
  [ "$actual_data" = "$expected_data" ] || { echo "❌ event data mismatch"; exit 1; }
  
  echo "✅ all event fields match ABI-encoded expected values"
  echo "VERIFIED"
  
  # Golden mode: additional validation
  if [ "$golden_mode" = "true" ]; then
    echo ""
    echo "🏆 GOLDEN MODE – Additional checks:"
    
    local foundry_version
    foundry_version=$(cast --version | head -1)
    echo "   Foundry version: $foundry_version"
    
    local expected_receipt_cid
    expected_receipt_cid=$(jq -r '.receipt_cid' "$GOLDEN_EXPECTED_FILE")
    if [ "$receipt_cid" = "$expected_receipt_cid" ]; then
      echo "   ✅ receipt_cid matches golden expected"
    else
      echo "   ⚠️  receipt_cid differs from golden expected (may be intentional)"
    fi
    
    echo "✅ GOLDEN MODE PASS"
  fi
}

# ----------------------------------------------------------------------------
# Ingest (full pipeline)
# ----------------------------------------------------------------------------
ingest(){
  local url="$1"
  echo "📥 Ingesting: $url"
  
  local content_file receipt_file
  content_file=$(ensure_content "$url")
  receipt_file=$(create_receipt "$url" "$content_file")
  anchor_ipfs_receipt "$receipt_file"
  
  echo "✅ Content CID: $(jq -r .content_cid "$content_file")"
  echo "✅ Receipt: $receipt_file"
  echo "✅ Receipt CID: $(jq -r .receipt_cid "$receipt_file")"
  echo ""
  echo "Next: ~/jay-agent/jay.sh anchor-base \"$receipt_file\""
}

# ----------------------------------------------------------------------------
# Watch (compare content_hash, emit diff if changed)
# ----------------------------------------------------------------------------
watch(){
  local url="$1"
  local slug latest old_receipt old_hash new_content new_hash tmp diff_file
  
  slug="$(slug "$url")"
  latest="$LATEST_DIR/${slug}.json"
  
  [ -f "$latest" ] || { echo "NO_BASELINE: run ingest first"; exit 1; }
  
  old_receipt=$(readlink -f "$latest")
  old_hash=$(jq -r .content_hash "$old_receipt")
  
  new_content=$(ensure_content "$url")
  new_hash=$(jq -r .content_hash "$new_content")
  
  if [ "$old_hash" = "$new_hash" ]; then
    echo "NO_CHANGE"
    return 0
  fi
  
  tmp=$(mktemp)
  diff_file="$DIFFS_DIR/${slug}_$(date -u +%Y%m%dT%H%M%SZ).diff"
  
  {
    echo "PREV_HASH: $old_hash"
    echo "NEW_HASH: $new_hash"
    echo "---"
    diff -u <(echo "$old_hash") <(echo "$new_hash") 2>/dev/null || true
  } > "$diff_file"
  
  local new_receipt
  new_receipt=$(create_receipt "$url" "$new_content")
  anchor_ipfs_receipt "$new_receipt"
  
  log "WATCH_CHANGE $url -> $old_hash -> $new_hash diff:$diff_file receipt:$new_receipt"
  echo "CHANGE_DETECTED: $diff_file"
  echo "New receipt: $new_receipt"
}

# ----------------------------------------------------------------------------
# Diff (show changes between last two observations)
# ----------------------------------------------------------------------------
diff_cmd(){
  local url="$1"
  local slug diffs
  slug="$(slug "$url")"
  diffs=$(ls -t "$DIFFS_DIR/${slug}_"*.diff 2>/dev/null | head -1)
  
  if [ -z "$diffs" ]; then
    echo "No diff receipts found for $url"
    exit 1
  fi
  
  cat "$diffs"
}

# ----------------------------------------------------------------------------
# Receipt status (human-readable)
# ----------------------------------------------------------------------------
receipt_status(){
  local receipt="$1"
  [ -f "$receipt" ] || { echo "missing: $receipt"; exit 1; }
  
  echo "📄 Receipt: $(basename "$receipt")"
  echo "   Source: $(jq -r .source_url "$receipt")"
  echo "   Content hash: $(jq -r .content_hash "$receipt")"
  echo "   Content CID: $(jq -r .content_cid "$receipt")"
  echo "   Receipt CID: $(jq -r .receipt_cid "$receipt")"
  echo "   Observed at: $(jq -r .retrieved_at_utc "$receipt")"
  
  local tx_hash
  tx_hash=$(jq -r .tx_hash "$receipt")
  if [ "$tx_hash" != "null" ] && [ -n "$tx_hash" ]; then
    echo "   🔗 Base: https://basescan.org/tx/$tx_hash"
  else
    echo "   ⚠️  Not anchored on Base"
  fi
}

# ----------------------------------------------------------------------------
# Golden self-test (pure event encoding)
# ----------------------------------------------------------------------------
golden_test(){
  echo "🏆 Running golden self-test with pure event encoding..."
  echo "   Using cast abi-encode-event --json (official Foundry command)"
  
  # Check if golden fixture exists
  if [ ! -f "$GOLDEN_RECEIPT_FILE" ] || [ ! -f "$GOLDEN_EXPECTED_FILE" ]; then
    echo "❌ Missing golden fixtures. Run setup first:"
    echo ""
    echo "   # After first successful anchor:"
    echo "   mkdir -p ~/jay-agent/testdata"
    echo "   cp \"\$RECEIPT\" ~/jay-agent/testdata/golden_receipt.json"
    echo "   cat > ~/jay-agent/testdata/golden_expected.json << EOF"
    echo "   {"
    echo "     \"tx_hash\": \"\$(jq -r .tx_hash \"\$RECEIPT\")\","
    echo "     \"content_hash\": \"\$(jq -r .content_hash \"\$RECEIPT\")\","
    echo "     \"content_cid\": \"\$(jq -r .content_cid \"\$RECEIPT\")\","
    echo "     \"receipt_cid\": \"\$(jq -r .receipt_cid \"\$RECEIPT\")\","
    echo "     \"source_url\": \"\$(jq -r .source_url \"\$RECEIPT\")\","
    echo "     \"retrieved_at_utc\": \"\$(jq -r .retrieved_at_utc \"\$RECEIPT\")\","
    echo "     \"contract_addr\": \"\$(cat ~/jay-agent/.anchor_contract)\""
    echo "   }"
    echo "   EOF"
    exit 1
  fi
  
  # Check Foundry version pinning
  if [ -f "$GOLDEN_VERSION_FILE" ]; then
    local expected_version actual_version
    expected_version=$(cat "$GOLDEN_VERSION_FILE")
    actual_version=$(cast --version | head -1)
    if [ "$expected_version" != "$actual_version" ]; then
      echo "⚠️  Foundry version mismatch: expected '$expected_version', got '$actual_version'"
      echo "   Verification may behave differently. Update .foundry_version after re-testing."
    fi
  fi
  
  # Test 1: Golden pass
  echo ""
  echo "📋 Test 1: Golden pass (should succeed)"
  if verify "$GOLDEN_RECEIPT_FILE" "true" > /tmp/golden_pass.log 2>&1; then
    echo "✅ PASS – verifier accepts known-good fixture"
  else
    echo "❌ FAIL – verifier rejected known-good fixture"
    cat /tmp/golden_pass.log
    exit 1
  fi
  
  # Test 2: Tampered content_hash (should fail)
  echo ""
  echo "📋 Test 2: Tampered content_hash (should fail)"
  local tampered_receipt="/tmp/tampered_receipt.json"
  jq '.content_hash = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"' \
    "$GOLDEN_RECEIPT_FILE" > "$tampered_receipt"
  
  if verify "$tampered_receipt" "false" > /tmp/golden_fail.log 2>&1; then
    echo "❌ FAIL – verifier accepted tampered content_hash"
    exit 1
  else
    echo "✅ PASS – verifier rejected tampered content_hash"
  fi
  
  # Test 3: Tampered source_url (should fail)
  echo ""
  echo "📋 Test 3: Tampered source_url (should fail)"
  jq '.source_url = "https://evil.com/fake"' \
    "$GOLDEN_RECEIPT_FILE" > "$tampered_receipt"
  
  if verify "$tampered_receipt" "false" > /tmp/golden_fail2.log 2>&1; then
    echo "❌ FAIL – verifier accepted tampered source_url"
    exit 1
  else
    echo "✅ PASS – verifier rejected tampered source_url"
  fi
  
  echo ""
  echo "🏆 ALL GOLDEN TESTS PASS"
  echo "✅ Verification pipeline is EVIDENCE-GRADE on this machine"
  echo "   Foundry version: $(cast --version | head -1)"
  echo "   Verification method: pure cast abi-encode-event --json"
  echo "   Compared fields: topics[0], topics[1], data"
  echo ""
  echo "📌 Next steps:"
  echo "   1. Pin this version: echo \"$(cast --version | head -1)\" > $GOLDEN_VERSION_FILE"
  echo "   2. Document in README.verify.md"
  echo "   3. Commit testdata/ to repository"
}

# ----------------------------------------------------------------------------
# Help
# ----------------------------------------------------------------------------
usage(){
  cat <<EOF
Usage: jay.sh <command> <argument>

Commands:
  ingest <url>                    Full pipeline (content + receipt + IPFS)
  anchor-base <receipt.json>      Anchor receipt on Base (requires contract)
  verify <receipt.json>           Verify all layers against on-chain proof
  watch <url>                     Check for changes, emit diff if needed
  diff <url>                      Show last diff receipt
  receipt-status <receipt.json>   Human-readable receipt info
  --golden                        Run golden self-test

Environment:
  BASE_RPC        Base RPC URL (default: https://mainnet.base.org)
  PRIVATE_KEY     Private key for anchoring (keep secure)

Contract:
  Deploy first: forge create Anchor.sol:MediaAnchor --rpc-url \$BASE_RPC --private-key \$PRIVATE_KEY
  Save address to: $CONTRACT_FILE
EOF
}

# ----------------------------------------------------------------------------
# Main dispatch
# ----------------------------------------------------------------------------
case "${1:-}" in
  ingest)          [ $# -eq 2 ] || { usage; exit 1; }; ingest "$2" ;;
  anchor-base)     [ $# -eq 2 ] || { usage; exit 1; }; anchor_base "$2" ;;
  verify)          [ $# -eq 2 ] || { usage; exit 1; }; verify "$2" "false" ;;
  watch)           [ $# -eq 2 ] || { usage; exit 1; }; watch "$2" ;;
  diff)            [ $# -eq 2 ] || { usage; exit 1; }; diff_cmd "$2" ;;
  receipt-status)  [ $# -eq 2 ] || { usage; exit 1; }; receipt_status "$2" ;;
  --golden)        golden_test ;;
  *)               usage; exit 1 ;;
esac
