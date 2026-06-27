#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib
import sys

PLACEHOLDER_PREFIX = "TO_BE_COMPUTED"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compute_state_root(rows):
    canonical = "\n".join(f"{row['path']}:{row['actual']}" for row in sorted(rows, key=lambda r: r["path"]))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Witness Replay v2.7 verifier")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    manifest_path = pathlib.Path(args.manifest)
    root = manifest_path.parent.parent.resolve()
    manifest = load_json(manifest_path)

    if manifest.get("authority") is not False:
        print("FAIL authority must be false", file=sys.stderr)
        return 2

    rows = []
    errors = []
    for item in manifest.get("inputs", []):
        rel = item["path"]
        expected = item["sha256"]
        p = root / rel
        if not p.exists():
            errors.append(f"missing:{rel}")
            continue
        actual = sha256_file(p)
        rows.append({"path": rel, "expected": expected, "actual": actual})
        if not expected.startswith(PLACEHOLDER_PREFIX) and actual != expected:
            errors.append(f"hash_mismatch:{rel}:expected={expected}:actual={actual}")

    state_root = compute_state_root(rows)
    expected_root = manifest.get("expected_state_root", "")
    if expected_root and not expected_root.startswith(PLACEHOLDER_PREFIX) and state_root != expected_root:
        errors.append(f"state_root_mismatch:expected={expected_root}:actual={state_root}")

    result = {
        "framework": manifest.get("framework"),
        "authority": False,
        "state_root": state_root,
        "inputs": rows,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
