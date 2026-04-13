# Receipts Engine v1

Deterministic reference kernel.

## Verify tests
```bash
python3 impl/verify.py --test vectors/test_vectors.json
```

Expected:
```
ALL PASS (3/3)
```

## Verify artifact hash
```bash
sha256sum receipts_engine_v1.tar.gz
```

Expected:
```
5a758a658c1d398963029733cc8c3b1b2546ed193b1b46dba58ba54fa109113d  receipts_engine_v1.tar.gz
```

## Seal Status

RECEIPTS ENGINE v1 — PENDING PUBLIC VERIFICATION  
Artifact frozen, hash generated, awaiting external verification.
