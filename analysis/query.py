#!/usr/bin/env python3
from pathlib import Path
import json
from collections import defaultdict

ROOT = Path("analysis")
INDEX = ROOT / "index.json"
ARTIFACTS = ROOT / "artifacts"
CLAIMS = ROOT / "claims"
PATTERNS = ROOT / "patterns"


def load_json(p: Path, default=None):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def main():
    idx = load_json(INDEX, {"topics": {}, "patterns": [], "claims": []})

    print("🔥 MN_IMMIGRATION NARRATIVE CORE v1\n")

    print("PATTERNS DETECTED:")
    for pid in idx.get("patterns", []):
        p = load_json(PATTERNS / f"{pid}.json", {})
        if p:
            arts = p.get("detected_in", [])
            print(f"  • {p['name']} ({p.get('strength','')}) → {len(arts)} artifacts")

    print("\nCLAIMS STATUS:")
    status_map = defaultdict(list)
    for cid in idx.get("claims", []):
        c = load_json(CLAIMS / f"{cid}.json", {})
        if c:
            status_map[c.get("status", "unknown")].append(c["text"][:80])

    for st, texts in status_map.items():
        print(f"  {st.upper()}: {len(texts)}")
        for t in texts[:3]:
            print(f"    - {t}...")

    print(f"\nARTIFACTS in mn_immigration: {len(idx['topics'].get('mn_immigration', []))}")


if __name__ == "__main__":
    main()
