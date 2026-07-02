#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-jaywisdom-boardroom}"
DATASET="${DATASET:-gcp_billing_export}"
LOCATION="${LOCATION:-US}"

cat <<EOF
GCP Billing Truth Layer Check
project=$PROJECT_ID
dataset=$DATASET
location=$LOCATION
timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
mode=read_only
EOF

gcloud config set project "$PROJECT_ID" >/dev/null

echo
echo "=== BigQuery API ==="
gcloud services list --enabled --filter="bigquery.googleapis.com" || true

echo
echo "=== Datasets ==="
bq ls --project_id "$PROJECT_ID" || true

echo
echo "=== Reservations ==="
bq ls --reservation --location="$LOCATION" --project_id "$PROJECT_ID" || true

echo
echo "=== Capacity Commitments ==="
bq ls --capacity_commitment --location="$LOCATION" --project_id "$PROJECT_ID" || true

echo
echo "=== Billing Export Dataset Tables ==="
if bq show --format=prettyjson "$PROJECT_ID:$DATASET" >/dev/null 2>&1; then
  bq query --use_legacy_sql=false \
    "SELECT table_name FROM \`$PROJECT_ID.$DATASET.INFORMATION_SCHEMA.TABLES\` ORDER BY table_name"
else
  echo "DATASET_MISSING: $PROJECT_ID:$DATASET"
  echo "Create with: bq --location=$LOCATION mk --dataset \"$PROJECT_ID:$DATASET\""
fi

echo
echo "=== Latest Billing Rows Probe ==="
echo "Run this after INFORMATION_SCHEMA shows a gcp_billing_export_v1_<BILLING_ACCOUNT_ID> table:"
cat <<'SQL'
SELECT
  service.description AS service_name,
  sku.description AS sku_name,
  usage_start_time,
  cost,
  currency
FROM
  `jaywisdom-boardroom.gcp_billing_export.gcp_billing_export_v1_<BILLING_ACCOUNT_ID>`
ORDER BY
  usage_start_time DESC
LIMIT 20;
SQL

echo
echo "EXPECTED_SAFE_STATE: no reservations, no capacity commitments, billing export table exists only after console wiring and data delay."
