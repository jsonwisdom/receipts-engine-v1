#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

FEEDBACK_PATH = Path("analysis") / "audit_feedback.json"


def load_feedback(path: Path = FEEDBACK_PATH) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def format_comment(feedback: dict[str, Any]) -> str:
    p0_count = feedback.get("p0_count", 0)
    p1_count = feedback.get("p1_count", 0)
    p2_count = feedback.get("p2_count", 0)
    p1_delta = feedback.get("p1_delta", 0)
    p2_delta = feedback.get("p2_delta", 0)
    p0_zero_days = feedback.get("P0_zero_days", 0)
    p1_trend = feedback.get("P1_trend", "unknown")
    signal_keeper = "yes" if feedback.get("signal_keeper", False) else "no"
    badges = feedback.get("badges_awarded", [])
    badges_text = ", ".join(badges) if badges else "none"

    return f"""## 📊 Audit Feedback (non-blocking)

| Metric | Value |
|--------|-------|
| **P0 (critical)** | {p0_count} |
| **P1 (review)** | {p1_count} (Δ {p1_delta:+d}) |
| **P2 (debt)** | {p2_count} (Δ {p2_delta:+d}) |
| **P0-zero streak** | {p0_zero_days} |
| **P1 trend** | {p1_trend} |
| **Signal Keeper** | {signal_keeper} |
| **Badges** | {badges_text} |

_This feedback is informational only. Merge gate unaffected._
"""


def main() -> None:
    feedback = load_feedback()
    if not feedback:
        print("No audit_feedback.json found. Skipping comment generation.")
        return

    comment = format_comment(feedback)
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"comment_body<<EOF\n{comment}\nEOF\n")
    else:
        print(comment)


if __name__ == "__main__":
    main()
