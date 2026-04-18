#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path("analysis")
HIGH_PRIORITY_FILE = ROOT / "high_priority_audits.json"
FEEDBACK_FILE = ROOT / "audit_feedback.json"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_feedback(current_report: dict[str, Any], baseline_report: dict[str, Any] | None) -> dict[str, Any]:
    baseline_report = baseline_report or {}
    current_counts = current_report.get("counts", {})
    baseline_counts = baseline_report.get("counts", {})

    p0_current = int(current_counts.get("P0", 0))
    p1_current = int(current_counts.get("P1", 0))
    p2_current = int(current_counts.get("P2", 0))

    p0_baseline = int(baseline_counts.get("P0", 0))
    p1_baseline = int(baseline_counts.get("P1", 0))
    p2_baseline = int(baseline_counts.get("P2", 0))

    clean_run_increment = 1 if p0_current == 0 else 0

    badges: list[str] = []
    if p0_current == 0:
        badges.append("Zero P0 Guardian")
    if p1_current <= p1_baseline:
        badges.append("Signal Keeper")
    if p2_current < p2_baseline:
        badges.append("Debt Reducer")

    return {
        "version": 1,
        "policy_state": "observing",
        "source": str(HIGH_PRIORITY_FILE),
        "p0_count": p0_current,
        "p1_count": p1_current,
        "p2_count": p2_current,
        "p0_delta": p0_current - p0_baseline,
        "p1_delta": p1_current - p1_baseline,
        "p2_delta": p2_current - p2_baseline,
        "P0_zero_days": clean_run_increment,
        "P1_trend": "down" if p1_current < p1_baseline else "flat" if p1_current == p1_baseline else "up",
        "badges_awarded": badges,
        "signal_keeper": p0_current == 0 and p1_current <= p1_baseline,
    }


def write_feedback(feedback: dict[str, Any], output_path: Path = FEEDBACK_FILE) -> dict[str, Any]:
    output_path.write_text(json.dumps(feedback, indent=2) + "\n", encoding="utf-8")
    return feedback
