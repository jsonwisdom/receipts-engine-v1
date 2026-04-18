#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT/_truth/apple"
LOG_DIR="$ROOT/_truth/logs"
OUT_JSON="$OUT_DIR/april26_leaf.json"
LOG_FILE="$LOG_DIR/apple_watcher.log"
URL="https://www.apple.com/newsroom/"
TMP_HTML="$(mktemp)"
TMP_TXT="$(mktemp)"
trap 'rm -f "$TMP_HTML" "$TMP_TXT"' EXIT

mkdir -p "$OUT_DIR" "$LOG_DIR"

curl -LfsS "$URL" -o "$TMP_HTML"

perl -0pe 's/<script\b[^>]*>.*?<\/script>//gis; s/<style\b[^>]*>.*?<\/style>//gis; s/<[^>]+>/ /g; s/&nbsp;/ /g; s/&amp;/\&/g; s/\s+/ /g' "$TMP_HTML" | sed 's/^ //; s/ $//' > "$TMP_TXT"

TEXT_SHA256="$(sha256sum "$TMP_TXT" | awk '{print $1}')"
PLATFORM_EXPANSION=false
SWIFT_CONCURRENCY=false
WWDC_PREP=false
DESIGN_PUSH=false
ANALYTICS_UPGRADE=false
UIKIT_LIFECYCLE=false

grep -qi 'ipad' "$TMP_TXT" && PLATFORM_EXPANSION=true || true
grep -qi 'swift concurrency' "$TMP_TXT" && SWIFT_CONCURRENCY=true || true
grep -qi 'wwdc' "$TMP_TXT" && WWDC_PREP=true || true
grep -qi 'design' "$TMP_TXT" && DESIGN_PUSH=true || true
grep -qi 'analytics' "$TMP_TXT" && ANALYTICS_UPGRADE=true || true
grep -qi 'uikit' "$TMP_TXT" && UIKIT_LIFECYCLE=true || true

TEXT_LEN="$(wc -c < "$TMP_TXT" | tr -d ' ')"
NOW_UTC="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

cat > "$OUT_JSON" <<EOF
{
  "source": "apple_newsroom_april26",
  "url": "$URL",
  "captured_at_utc": "$NOW_UTC",
  "text_sha256": "$TEXT_SHA256",
  "text_bytes": $TEXT_LEN,
  "signals": {
    "platform_expansion": $PLATFORM_EXPANSION,
    "swift_concurrency": $SWIFT_CONCURRENCY,
    "wwdc_prep": $WWDC_PREP,
    "design_push": $DESIGN_PUSH,
    "analytics_upgrade": $ANALYTICS_UPGRADE,
    "uikit_lifecycle": $UIKIT_LIFECYCLE
  }
}
EOF

printf '%s apple_watcher ok sha256=%s bytes=%s\n' "$NOW_UTC" "$TEXT_SHA256" "$TEXT_LEN" >> "$LOG_FILE"
echo "$OUT_JSON"
