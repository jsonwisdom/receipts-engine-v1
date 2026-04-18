#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path("analysis")
ARTIFACTS = ROOT / "artifacts"
PATTERNS = ROOT / "patterns"
HIGH_PRIORITY_FILE = ROOT / "high_priority_audits.json"

WEIGHTS = {
    "P0": 10,
    "P1": 7,
    "P2": 4,
    "P3": 1,
}

TIERS = {
    "P0": 9,
    "P1": 6,
    "P2": 3,
    "P3": 0,
}


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def assign_tier(score: int) -> str:
    if score >= TIERS["P0"]:
        return "P0"
    if score >= TIERS["P1"]:
        return "P1"
    if score >= TIERS["P2"]:
        return "P2"
    return "P3"


def build_ranked_artifacts() -> list[dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}

    for artifact_path in sorted(ARTIFACTS.glob("A*.json")):
        data = load_json(artifact_path, {})
        artifact_id = data.get("id")
        if not artifact_id:
            continue
        artifacts[artifact_id] = {
            "artifact": artifact_id,
            "topic": data.get("topic", "unclassified"),
            "patterns": [],
            "score": 0,
            "tier": "P3",
        }

    for pattern_path in sorted(PATTERNS.glob("P*.json")):
        data = load_json(pattern_path, {})
        pattern_id = data.get("id")
        if not pattern_id:
            continue
        for artifact_id in data.get("detected_in", []):
            artifact = artifacts.get(artifact_id)
            if artifact is None:
                continue
            artifact["patterns"].append(pattern_id)
            artifact["score"] += WEIGHTS.get(pattern_id, 1)

    ranked = []
    for artifact_id, details in sorted(
        artifacts.items(),
        key=lambda kv: (-kv[1]["score"], kv[0]),
    ):
        details["tier"] = assign_tier(details["score"])
        ranked.append(
            {
                "artifact": artifact_id,
                "topic": details["topic"],
                "patterns": details["patterns"],
                "score": details["score"],
                "tier": details["tier"],
            }
        )

    return ranked


def write_tiered_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    tier_groups = {
        "P0": [item for item in results if item["tier"] == "P0"],
        "P1": [item for item in results if item["tier"] == "P1"],
        "P2": [item for item in results if item["tier"] == "P2"],
        "P3": [item for item in results if item["tier"] == "P3"],
    }

    payload = {
        "tiers": TIERS,
        "counts": {tier: len(items) for tier, items in tier_groups.items()},
        "high_priority": tier_groups["P0"] + tier_groups["P1"],
        "p0_critical": tier_groups["P0"],
        "p1_review": tier_groups["P1"],
        "p2_debt": tier_groups["P2"],
        "p3_info": tier_groups["P3"],
        "all_findings": results,
    }

    HIGH_PRIORITY_FILE.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    return payload


def main() -> None:
    ranked_artifacts = build_ranked_artifacts()
    tiered_report = write_tiered_report(ranked_artifacts)

    print(
        json.dumps(
            {
                "ranked_artifacts": ranked_artifacts,
                "high_priority_report": {
                    "counts": tiered_report["counts"],
                    "file": str(HIGH_PRIORITY_FILE),
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
