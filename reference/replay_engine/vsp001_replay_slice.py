#!/usr/bin/env python3
"""Minimal VSP-001 Row 16 replay determinism proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any

getcontext().prec = 28
FOUR_PLACES = Decimal("0.0001")
LEGAL_INPUT_KEYS = [
    "wind_mean_mph",
    "wind_gust_mph",
    "humidity_pct",
    "temp_c",
    "distance_to_sensitive_m",
    "boom_height_in",
    "droplet_size_um",
]


def normalize(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return format(obj.quantize(FOUR_PLACES, rounding=ROUND_HALF_UP), "f")
    if isinstance(obj, dict):
        return {str(k): normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    return obj


def canonical_serialize(obj: Any) -> bytes:
    return json.dumps(
        normalize(obj),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def sha256_hex(obj: Any) -> str:
    return hashlib.sha256(canonical_serialize(obj)).hexdigest().lower()


def d(snapshot: dict[str, Any], key: str) -> Decimal:
    value = snapshot["inputs"].get(key)
    if value is None:
        raise ValueError(f"EVIDENCE_GAP: {key}")
    return Decimal(str(value))


def legal_inputs(snapshot: dict[str, Any]) -> dict[str, Decimal]:
    return {key: d(snapshot, key) for key in LEGAL_INPUT_KEYS}


def drift_score(inputs: dict[str, Decimal]) -> Decimal:
    weighted_wind = Decimal("0.70") * inputs["wind_mean_mph"] + Decimal("0.30") * inputs["wind_gust_mph"]
    humidity_factor = Decimal("1.00") - inputs["humidity_pct"] / Decimal("200.00")
    temp_factor = Decimal("1.00") + (inputs["temp_c"] - Decimal("20.00")) / Decimal("100.00")
    boom_factor = inputs["boom_height_in"] / Decimal("24.00")
    distance_factor = Decimal("200.00") / inputs["distance_to_sensitive_m"]
    droplet_factor = Decimal("250.00") / inputs["droplet_size_um"]
    raw = weighted_wind * humidity_factor * temp_factor * boom_factor * distance_factor * droplet_factor
    return (raw / Decimal("24.2577")).quantize(FOUR_PLACES, rounding=ROUND_HALF_UP)


def apply_wr003(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot["consensus_state"] != "PASS":
        score = None
        decision = "DENY"
        error_state = "CONSENSUS_FAILED"
    else:
        score = drift_score(legal_inputs(snapshot))
        threshold = Decimal(snapshot["expected"]["threshold"])
        decision = "DENY" if score >= threshold else "PERMIT"
        error_state = "NONE"

    return {
        "snapshot_id": snapshot["snapshot_id"],
        "row_id": snapshot["row_id"],
        "engine_version": snapshot["engine_version"],
        "rule_version": snapshot["rule_version"],
        "schema_version": snapshot["schema_version"],
        "consensus_state": snapshot["consensus_state"],
        "legal_input_keys": LEGAL_INPUT_KEYS,
        "snapshot_hash": sha256_hex(snapshot),
        "decision": decision,
        "drift_score": score,
        "threshold": Decimal(snapshot["expected"]["threshold"]),
        "grade": snapshot["expected"]["grade"],
        "error_state": error_state,
        "dominant_uncertainty": snapshot["expected"]["dominant_uncertainty"],
        "invariants": snapshot["constitutional_invariants"],
    }


def compute_receipt(snapshot: dict[str, Any]) -> tuple[dict[str, Any], str]:
    output = apply_wr003(snapshot)
    return output, sha256_hex(output)


def load_snapshot(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=Decimal)


def run(snapshot_path: str) -> str:
    snapshot = load_snapshot(snapshot_path)
    output1, digest1 = compute_receipt(snapshot)
    output2, digest2 = compute_receipt(snapshot)
    print(f"First run SHA-256: {digest1}")
    print(f"Replay SHA-256:    {digest2}")
    if canonical_serialize(output1) != canonical_serialize(output2) or digest1 != digest2:
        raise AssertionError("RECONSTRUCTION_FAILURE")
    print("VERIFIED: same snapshot + rule + serializer = same SHA-256")
    return digest1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="reference/replay_engine/data/vsp001_row16.json")
    args = parser.parse_args()
    run(args.snapshot)


if __name__ == "__main__":
    main()
