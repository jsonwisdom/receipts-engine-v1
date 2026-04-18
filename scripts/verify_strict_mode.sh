#!/usr/bin/env bash
set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  STRICT MODE VERIFICATION"
echo "═══════════════════════════════════════════════════════════════"

PATTERNS_DIR="analysis/patterns"

if [ ! -d "$PATTERNS_DIR" ]; then
  echo "ERROR: patterns directory not found: $PATTERNS_DIR"
  exit 1
fi

echo
echo "📋 Checking pattern severity declarations..."
MISSING=$(find "$PATTERNS_DIR" -name 'P*.json' -exec sh -c 'jq -e ".severity" "$1" > /dev/null 2>&1 || echo "$1"' _ {} \;)
if [ -n "$MISSING" ]; then
  echo "FAIL: Patterns missing severity:"
  echo "$MISSING"
  exit 1
else
  echo "OK: All patterns have severity declared"
fi

echo
echo "📋 Validating severity values..."
INVALID=$(find "$PATTERNS_DIR" -name 'P*.json' -exec sh -c 'jq -r ".severity" "$1"' _ {} \; | grep -v -E '^(P0|P1|P2|P3)$' || true)
if [ -n "$INVALID" ]; then
  echo "FAIL: Invalid severity values found:"
  echo "$INVALID"
  exit 1
else
  echo "OK: All severities are valid (P0/P1/P2/P3)"
fi

echo
echo "📊 Severity distribution:"
jq -r '.severity' "$PATTERNS_DIR"/P*.json 2>/dev/null | sort | uniq -c

echo
echo "═══════════════════════════════════════════════════════════════"
echo "  READY for strict mode"
echo "═══════════════════════════════════════════════════════════════"
