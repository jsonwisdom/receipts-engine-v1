#!/usr/bin/env bash
set -euo pipefail

tar --sort=name \
    --mtime='UTC 1970-01-01' \
    --owner=0 --group=0 --numeric-owner \
    -czf receipts_engine_v1.tar.gz receipts_engine_v1/

echo "Built deterministic tarball"
