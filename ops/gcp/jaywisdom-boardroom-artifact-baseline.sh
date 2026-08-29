#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-jaywisdom-boardroom}"
LOCATION="${LOCATION:-us-central1}"
REPOSITORY="${REPOSITORY:-cloud-run-source-deploy}"

cat <<EOF
GCP Artifact Registry Baseline Check
project=$PROJECT_ID
location=$LOCATION
repository=$REPOSITORY
timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
mode=read_only
EOF

gcloud config set project "$PROJECT_ID" >/dev/null

echo
echo "=== Artifact Registry API ==="
gcloud services list --enabled --filter="artifactregistry.googleapis.com" || true

echo
echo "=== Repository Metadata ==="
gcloud artifacts repositories describe "$REPOSITORY" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" \
  --format="yaml(name,format,mode,createTime,updateTime,sizeBytes,cleanupPolicies)" || true

echo
echo "=== Docker Images Summary ==="
gcloud artifacts docker images list "$LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY" \
  --include-tags \
  --format="table(package,version,tags,updateTime,IMAGE_SIZE)" || true

echo
echo "=== Untagged Images Older Than 7 Days Candidate View ==="
gcloud artifacts docker images list "$LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY" \
  --include-tags \
  --filter="NOT tags:*" \
  --format="table(package,version,updateTime,IMAGE_SIZE)" || true

echo
echo "=== Cleanup Policy Apply Reminder ==="
cat <<'EOF'
Create cleanup-policy.yaml:
---
- name: delete-untagged-older-than-7d
  action: DELETE
  condition:
    tagState: UNTAGGED
    olderThan: 7d
- name: keep-latest
  action: KEEP
  condition:
    tagNames: ["latest"]
- name: keep-recent-7d
  action: KEEP
  condition:
    olderThan: 7d
    negate: true

Apply:
gcloud artifacts repositories set-cleanup-policies cloud-run-source-deploy \
  --location=us-central1 \
  --project=jaywisdom-boardroom \
  --policy=cleanup-policy.yaml
EOF

echo
echo "EXPECTED_BASELINE: repository exists, old untagged images visible, cleanupPolicies absent or pending until policy applied."
