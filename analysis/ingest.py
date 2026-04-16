#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
CLAIMS = ROOT / "claims"
SOURCES = ROOT / "sources"
ATTESTATIONS = ROOT / "attestations"
PATTERNS = ROOT / "patterns"
INDEX = ROOT / "index.json"

DIRS = [ARTIFACTS, CLAIMS, SOURCES, ATTESTATIONS, PATTERNS]


def ensure_dirs() -> None:
    for d in DIRS:
        d.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def next_id(prefix: str, folder: Path) -> str:
    nums = []
    for f in folder.glob(f"{prefix}*.json"):
        m = re.fullmatch(rf"{prefix}(\d+)\.json", f.name)
        if m:
            nums.append(int(m.group(1)))
    return f"{prefix}{max(nums, default=0) + 1}"


def append_unique(lst: list[str], value: str) -> None:
    if value and value not in lst:
        lst.append(value)


def ingest(input_path: Path) -> dict[str, str]:
    ensure_dirs()
    payload = load_json(input_path, None)
    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")

    artifact_id = payload.get("id") or next_id("A", ARTIFACTS)
    topic = payload.get("topic", "unclassified")
    artifact = {
        "id": artifact_id,
        "topic": topic,
        "type": payload.get("type", ""),
        "link": payload.get("link", ""),
        "date": payload.get("date", ""),
        "speakers": payload.get("speakers", []),
        "verdict": payload.get("verdict", ""),
        "score": payload.get("score", 0),
        "created_at": now_iso(),
    }
    save_json(ARTIFACTS / f"{artifact_id}.json", artifact)

    saved_claim_ids: list[str] = []
    for claim in payload.get("claims", []):
        cid = claim.get("id") or next_id("C", CLAIMS)
        path = CLAIMS / f"{cid}.json"
        existing = load_json(path, {})
        data = {
            "id": cid,
            "text": claim["text"],
            "type": claim.get("type", ""),
            "status": claim.get("status", ""),
            "sources": claim.get("sources", existing.get("sources", [])),
            "used_in": existing.get("used_in", []),
            "updated_at": now_iso(),
        }
        append_unique(data["used_in"], artifact_id)
        save_json(path, data)
        saved_claim_ids.append(cid)

    saved_source_ids: list[str] = []
    for source in payload.get("sources", []):
        sid = source.get("id") or next_id("S", SOURCES)
        save_json(SOURCES / f"{sid}.json", {
            "id": sid,
            "type": source.get("type", ""),
            "link": source.get("link", ""),
            "reliability": source.get("reliability", ""),
            "notes": source.get("notes", ""),
            "updated_at": now_iso(),
        })
        saved_source_ids.append(sid)

    saved_pattern_ids: list[str] = []
    for pattern in payload.get("patterns", []):
        pid = pattern.get("id") or next_id("P", PATTERNS)
        path = PATTERNS / f"{pid}.json"
        existing = load_json(path, {})
        detected_in = existing.get("detected_in", [])
        append_unique(detected_in, artifact_id)
        save_json(path, {
            "id": pid,
            "name": pattern["name"],
            "description": pattern.get("description", ""),
            "detected_in": detected_in,
            "strength": pattern.get("strength", ""),
            "updated_at": now_iso(),
        })
        saved_pattern_ids.append(pid)

    vid = next_id("V", ATTESTATIONS)
    save_json(ATTESTATIONS / f"{vid}.json", {
        "id": vid,
        "artifact": artifact_id,
        "claims_verified": saved_claim_ids,
        "result": payload.get("verdict", ""),
        "analyst": payload.get("analyst", "jaywisdom"),
        "timestamp": now_iso(),
    })

    index = load_json(INDEX, {"topics": {}, "patterns": [], "claims": [], "sources": [], "artifacts": []})
    index["topics"].setdefault(topic, [])
    append_unique(index["topics"][topic], artifact_id)
    append_unique(index["artifacts"], artifact_id)
    for cid in saved_claim_ids:
        append_unique(index["claims"], cid)
    for pid in saved_pattern_ids:
        append_unique(index["patterns"], pid)
    for sid in saved_source_ids:
        append_unique(index["sources"], sid)
    save_json(INDEX, index)

    return {"artifact_id": artifact_id, "topic": topic, "attestation_id": vid}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to intake JSON")
    args = parser.parse_args()
    result = ingest(Path(args.input))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
