#!/usr/bin/env bash
set -euo pipefail
SRC="${1:-}"
[ -n "$SRC" ] && [ -f "$SRC" ] || { echo "missing source"; exit 1; }
mkdir -p _artifacts/current
OUT="_artifacts/current/source.txt"
pdftotext -layout -nopgbrk "$SRC" - \
  | sed 's/[[:space:]]\+/ /g' \
  | sed 's/ *$//' \
  | tr -d '\r' \
  > "$OUT"
[ -s "$OUT" ] || { echo "empty extraction"; exit 1; }
echo "$OUT"
