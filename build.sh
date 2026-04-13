#!/usr/bin/env bash
set -euo pipefail

tar --sort=name \
    --mtime='UTC 2020-01-01' \
    --owner=0 --group=0 --numeric-owner \
    -czf receipts_engine_v1.tar.gz impl spec vectors README.md

echo "Built deterministic receipts_engine_v1.tar.gz"
