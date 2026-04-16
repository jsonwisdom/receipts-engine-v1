#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path("analysis")
ARTIFACTS = ROOT / "artifacts"
PATTERNS = ROOT / "patterns"

WEIGHTS = {"P1": 3, "P2": 3, "P3": 2}


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_ranked_artifacts() -> list[dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}

    for artifact_path in sorted(ARTIFACTS.glob("A*.json")):
        data = load_json(artifact_path, {})
        artifact_id = data.get("id")
        if not artifact_id:
            continue
        artifacts[artifact_id] = {
            "topic": data.get("topic", "unclassified"),
            "patterns": [],
            "score": 0,
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

    ranked = sorted(
        artifacts.items(),
        key=lambda kv: (-kv[1]["score"], kv[0]),
    )

    return [
        {
            "artifact": artifact_id,
            "topic": details["topic"],
            "patterns": details["patterns"],
            "score": details["score"],
        }
        for artifact_id, details in ranked
    ]


def main() -> None:
    print(json.dumps({"ranked_artifacts": build_ranked_artifacts()}, indent=2))


if __name__ == "__main__":
    main()
