#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INGEST = ROOT / "ingest.py"
DETECT = ROOT / "detect_patterns.py"
QUERY = ROOT / "query.py"
CAMPAIGN_MAP = ROOT / "campaign_map.json"
PATTERNS = ROOT / "patterns"
INDEX = ROOT / "index.json"


def run_step(cmd: list[str], title: str) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(f"[{title}] failed\n")
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_campaign_routes() -> dict:
    campaign = load_json(CAMPAIGN_MAP, {"rails": [], "routing_rule": {"if_pattern_contains": {}}})
    index = load_json(INDEX, {"patterns": []})

    pattern_names = []
    for pid in index.get("patterns", []):
        p = load_json(PATTERNS / f"{pid}.json", {})
        if p and p.get("name"):
            pattern_names.append(p["name"])

    matched_pillars = []
    for pname in pattern_names:
        for pillar in campaign.get("routing_rule", {}).get("if_pattern_contains", {}).get(pname, []):
            if pillar not in matched_pillars:
                matched_pillars.append(pillar)

    recommended_outputs = []
    recommended_cta = []
    for rail in campaign.get("rails", []):
        if rail.get("pillar") in matched_pillars:
            for artifact_type in rail.get("artifact_types", []):
                if artifact_type not in recommended_outputs:
                    recommended_outputs.append(artifact_type)
            cta = rail.get("cta")
            if cta and cta not in recommended_cta:
                recommended_cta.append(cta)

    return {
        "patterns_detected": pattern_names,
        "pillars_detected": matched_pillars,
        "recommended_output": recommended_outputs,
        "cta": recommended_cta,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to intake JSON")
    args = parser.parse_args()

    ingest_out = run_step([sys.executable, str(INGEST), args.input], "ingest")
    detect_out = run_step([sys.executable, str(DETECT)], "detect_patterns")
    query_out = run_step([sys.executable, str(QUERY)], "query")
    campaign_out = build_campaign_routes()

    result = {
        "ingest": json.loads(ingest_out),
        "detect_patterns": json.loads(detect_out),
        "query_output": query_out,
        "campaign": campaign_out,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
