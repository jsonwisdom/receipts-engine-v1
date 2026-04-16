#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path("analysis")
ARTIFACTS = ROOT / "artifacts"
PATTERNS = ROOT / "patterns"
INDEX = ROOT / "index.json"

PATTERN_RULES = {
    "hero_villain": {
        "description": "Frames one side as strong truth-teller and the other as weak, corrupt, or villainous.",
        "strength": "high",
        "keywords": [
            "hero", "villain", "pathetic", "weak", "coward", "truth-teller",
            "real men", "radical", "lying", "dishonest"
        ],
    },
    "fear_amplification": {
        "description": "Uses threat, chaos, invasion, collapse, or emergency language to intensify perceived danger.",
        "strength": "medium",
        "keywords": [
            "chaos", "threat", "invasion", "danger", "crisis", "collapse",
            "destroying", "civil war", "violent", "magnet"
        ],
    },
    "loaded_labels": {
        "description": "Uses emotionally loaded labels instead of neutral description.",
        "strength": "medium",
        "keywords": [
            "communist", "radical", "america last", "crazy", "pathetic",
            "gestapo", "traitor", "extremist"
        ],
    },
    "omission_of_context": {
        "description": "Presents real quotes or events while dropping legal, historical, or full-quote context.",
        "strength": "high",
        "keywords": [
            "out of context", "omission", "partial", "excerpt", "clipped",
            "without context", "selective", "full context"
        ],
    },
}


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_unique(lst: list[str], value: str) -> None:
    if value not in lst:
        lst.append(value)


def artifact_text(artifact: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in artifact.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    parts.append(item)
    return "\n".join(parts).lower()


def detect_for_artifact(artifact: dict[str, Any]) -> list[str]:
    text = artifact_text(artifact)
    detected: list[str] = []
    for pattern_name, rule in PATTERN_RULES.items():
        for keyword in rule["keywords"]:
            if re.search(rf"\b{re.escape(keyword.lower())}\b", text):
                detected.append(pattern_name)
                break
    return detected


def next_pattern_id(existing_paths: list[Path]) -> str:
    nums: list[int] = []
    for path in existing_paths:
        m = re.fullmatch(r"P(\d+)\.json", path.name)
        if m:
            nums.append(int(m.group(1)))
    return f"P{max(nums, default=0) + 1}"


def ensure_pattern(pattern_name: str, artifact_id: str) -> str:
    existing_files = list(PATTERNS.glob("P*.json"))
    for path in existing_files:
        data = load_json(path, {})
        if data.get("name") == pattern_name:
            detected_in = data.get("detected_in", [])
            append_unique(detected_in, artifact_id)
            data["detected_in"] = detected_in
            save_json(path, data)
            return data["id"]

    pid = next_pattern_id(existing_files)
    rule = PATTERN_RULES[pattern_name]
    data = {
        "id": pid,
        "name": pattern_name,
        "description": rule["description"],
        "detected_in": [artifact_id],
        "strength": rule["strength"],
    }
    save_json(PATTERNS / f"{pid}.json", data)
    return pid


def rebuild_index(pattern_ids: list[str]) -> None:
    index = load_json(INDEX, {"topics": {}, "patterns": [], "claims": [], "sources": [], "artifacts": []})
    for pid in pattern_ids:
        append_unique(index.setdefault("patterns", []), pid)
    save_json(INDEX, index)


def main() -> None:
    artifact_files = sorted(ARTIFACTS.glob("A*.json"))
    if not artifact_files:
        print(json.dumps({"artifacts_scanned": 0, "patterns_detected": 0}, indent=2))
        return

    created_or_updated: list[str] = []
    scanned = 0
    matches = 0

    for artifact_path in artifact_files:
        artifact = load_json(artifact_path, {})
        artifact_id = artifact.get("id")
        if not artifact_id:
            continue
        scanned += 1
        detected = detect_for_artifact(artifact)
        if not detected:
            continue
        matches += len(detected)
        for pattern_name in detected:
            pid = ensure_pattern(pattern_name, artifact_id)
            created_or_updated.append(pid)

    rebuild_index(created_or_updated)

    print(json.dumps({
        "artifacts_scanned": scanned,
        "patterns_detected": matches,
        "pattern_ids_updated": sorted(set(created_or_updated)),
    }, indent=2))


if __name__ == "__main__":
    main()
