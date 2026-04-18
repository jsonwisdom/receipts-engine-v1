#!/usr/bin/env bash
set -euo pipefail

PATTERNS_DIR="analysis/patterns"

if [ ! -d "$PATTERNS_DIR" ]; then
  echo "ERROR: patterns directory not found: $PATTERNS_DIR"
  exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "  P0/P1 PROMOTION CANDIDATES"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "🔴 P0 CANDIDATES (Critical - Block Merge)"
echo "───────────────────────────────────────────────────────────────"
grep -l -i -E \
  -e "(secret|password|api[_-]?key|token|credential|private[_-]?key)" \
  -e "(sql[_-]?injection|command[_-]?injection|eval\(|exec\(|system\(|\bexec\b)" \
  -e "(auth[n]? bypass|privilege escalation|rbac|role[_-]?binding)" \
  -e "(cve-|[0-9]{4}-[0-9]{4,})" \
  "$PATTERNS_DIR"/P*.json 2>/dev/null | while read -r file; do
    if ! grep -q '"severity": "P0"' "$file"; then
      name=$(basename "$file" .json)
      desc=$(jq -r '.description // .message // "No description"' "$file" 2>/dev/null | cut -c1-80)
      echo "  📁 $name"
      echo "     $desc"
      echo ""
    fi
done || true

echo ""
echo "🟠 P1 CANDIDATES (High - Diff-Aware Block)"
echo "───────────────────────────────────────────────────────────────"
grep -l -i -E \
  -e "(debug|console\.log|print_r|var_dump|logger\.debug)" \
  -e "(deprecated|legacy|obsolete|old[_-]api)" \
  -e "(hardcoded|magic[_-]?number|inline[_-]?constant)" \
  -e "(todo.*security|fixme.*security|xxx.*security)" \
  -e "(http://|plain[_-]?text|unencrypted|no[_-]?tls)" \
  -e "(weak[_-]?crypto|md5|sha1|des|rc4)" \
  "$PATTERNS_DIR"/P*.json 2>/dev/null | while read -r file; do
    if ! grep -q '"severity": "P[01]"' "$file"; then
      name=$(basename "$file" .json)
      desc=$(jq -r '.description // .message // "No description"' "$file" 2>/dev/null | cut -c1-80)
      echo "  📁 $name"
      echo "     $desc"
      echo ""
    fi
done || true

echo ""
echo "📊 CURRENT SEVERITY DISTRIBUTION (post-backfill)"
echo "───────────────────────────────────────────────────────────────"
for file in "$PATTERNS_DIR"/P*.json; do
  [ -e "$file" ] || continue
  sev=$(jq -r '.severity // "MISSING"' "$file" 2>/dev/null)
  echo "  $sev - $(basename "$file")"
done | sort | uniq -c | sort -rn

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  NEXT STEPS"
echo "═══════════════════════════════════════════════════════════════"
echo "  1. Review P0 candidates → set 'severity': 'P0'"
echo "  2. Review P1 candidates → set 'severity': 'P1'"
echo "  3. Run: git diff analysis/patterns/ | grep 'severity'"
echo "  4. Commit with: git commit -m 'chore: promote P0/P1 patterns'"
echo "═══════════════════════════════════════════════════════════════"
