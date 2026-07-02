#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-jaywisdom-boardroom}"
MODE="${1:-verify}"

BUCKETS=(
  "jaywisdom-boardroom-ledger-1774147674"
  "jaywisdom-boardroom-ledger-1774149480"
  "jaywisdom-boardroom-ledger-1774149642"
  "jaywisdom-boardroom-ledger-1774150648"
)

echo "GCP Zombie Ledger Purge Receipt"
echo "project=$PROJECT_ID"
echo "mode=$MODE"
echo "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

gcloud config set project "$PROJECT_ID" >/dev/null

verify_bucket() {
  local bucket="$1"
  echo "=============================="
  echo "VERIFY: gs://$bucket/"
  echo "=============================="
  if gcloud storage ls -L "gs://$bucket/"; then
    echo "VERIFY_STATUS: present"
  else
    echo "VERIFY_STATUS: missing_or_inaccessible"
  fi
  echo
}

purge_bucket() {
  local bucket="$1"
  echo "=============================="
  echo "PURGE: gs://$bucket/"
  echo "=============================="
  gcloud storage rm --recursive "gs://$bucket/" || echo "PURGE_STATUS: missing_or_already_removed"
  echo
}

for bucket in "${BUCKETS[@]}"; do
  verify_bucket "$bucket"
done

if [[ "$MODE" == "purge" ]]; then
  echo "PURGE_AUTHORIZED_BY_LOCAL_OPERATOR=true"
  for bucket in "${BUCKETS[@]}"; do
    purge_bucket "$bucket"
  done
else
  echo "DRY_RUN_ONLY=true"
  echo "To purge after verifying stale residue, run:"
  echo "bash ops/gcp/jaywisdom-boardroom-zombie-ledger-purge.sh purge"
fi

echo "=============================="
echo "POST_CHECK"
echo "=============================="
gcloud storage ls | grep "jaywisdom-boardroom-ledger" || echo "LEDGER_ZOMBIES_CLEARED_OR_NOT_LISTED"
