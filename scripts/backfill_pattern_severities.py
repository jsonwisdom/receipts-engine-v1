#!/usr/bin/env python3
"""
Backfill missing severity fields in analysis/pattern JSON files.
Safe to run multiple times — only adds severity if missing or invalid.
Default: P2
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

VALID_SEVERITIES = {"P0", "P1", "P2", "P3"}
DEFAULT_SEVERITY = "P2"
PATTERNS_DIR = Path("analysis") / "patterns"


def process_pattern_file(filepath: Path) -> Tuple[bool, str]:
    try:
        with filepath.open("r", encoding="utf-8") as f:
            data = json.load(f)

        severity = data.get("severity")
        if severity in VALID_SEVERITIES:
            return False, f"already set to {severity}"

        changed = "severity" not in data or severity not in VALID_SEVERITIES
        old = data.get("severity")
        data["severity"] = DEFAULT_SEVERITY
        filepath.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        if old is None:
            return changed, f"added severity {DEFAULT_SEVERITY}"
        return changed, f"fixed invalid severity {old!r} -> {DEFAULT_SEVERITY}"
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    except Exception as e:
        return False, f"error: {e}"


def main() -> None:
    if not PATTERNS_DIR.exists():
        print(f"ERROR: patterns directory not found: {PATTERNS_DIR}")
        raise SystemExit(1)

    pattern_files = sorted(PATTERNS_DIR.glob("P*.json"))
    if not pattern_files:
        print(f"WARN: no pattern JSON files found in {PATTERNS_DIR}")
        return

    changed_count = 0
    print(f"Scanning {len(pattern_files)} pattern files in {PATTERNS_DIR}...")
    for filepath in pattern_files:
        changed, message = process_pattern_file(filepath)
        if changed:
            changed_count += 1
        print(f"- {filepath.name}: {message}")

    print()
    print(f"Done. Updated {changed_count} file(s).")
    print("Next steps:")
    print("1. Review changes: git diff analysis/patterns/")
    print("2. Promote obvious P0/P1 patterns manually")
    print("3. Commit before enabling strict mode")


if __name__ == "__main__":
    main()
