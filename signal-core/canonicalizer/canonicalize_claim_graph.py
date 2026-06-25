#!/usr/bin/env python3
"""
Signal Core Claim Graph Canonicalizer v0.1

Purpose:
- Normalize claim graphs before sealing.
- Enforce deterministic ordering over claims, dependencies, evidence references,
  and provenance fields.
- Produce stable canonical JSON bytes for repeatable hashing.

This is a structural tool only.
It does not decide truth.
Authority is always NONE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


AUTHORITY = "NONE"
DEFAULT_VERSION = "v0.1"


def stable_json(value: Any) -> str:
    """Deterministic JSON fallback. Replace with RFC8785/JCS for production sealing."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def normalize_pointer(pointer: Any) -> Any:
    """Normalize evidence/source pointers without inventing missing meaning."""
    if isinstance(pointer, dict):
        return {k: normalize_pointer(v) for k, v in sorted(pointer.items())}
    if isinstance(pointer, list):
        return sorted((normalize_pointer(v) for v in pointer), key=stable_json)
    return pointer


def normalize_provenance(prov: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Stable provenance fields."""
    if not prov:
        return {}
    return {k: normalize_pointer(v) for k, v in sorted(prov.items())}


def stable_sort_claims(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort claims by id, then hash, then full canonical JSON."""
    def sort_key(claim: Dict[str, Any]) -> str:
        return str(claim.get("id") or claim.get("claim_id") or claim.get("hash") or stable_json(claim))

    return sorted(claims, key=sort_key)


def stable_sort_edges(edges: Any) -> Any:
    """Stable-sort graph edges/dependencies while preserving plain scalar lists."""
    if isinstance(edges, list):
        return sorted((normalize_pointer(edge) for edge in edges), key=stable_json)
    return edges


def normalize_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}

    for key, value in sorted(claim.items()):
        if key == "provenance":
            normalized[key] = normalize_provenance(value)
        elif key in {"dependencies", "edges", "sources", "evidence", "provenance_refs"}:
            normalized[key] = stable_sort_edges(value)
        else:
            normalized[key] = normalize_pointer(value)

    return normalized


def canonicalize_claim_graph(graph_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    graph = json.loads(Path(graph_path).read_text(encoding="utf-8"))

    claims = [normalize_claim(claim) for claim in stable_sort_claims(graph.get("claims", []))]

    canonical_graph: Dict[str, Any] = {
        "authority": graph.get("authority", AUTHORITY),
        "version": graph.get("version", DEFAULT_VERSION),
        "claims": claims,
    }

    for key, value in sorted(graph.items()):
        if key in {"authority", "version", "claims"}:
            continue
        if key in {"edges", "dependencies"}:
            canonical_graph[key] = stable_sort_edges(value)
        else:
            canonical_graph[key] = normalize_pointer(value)

    if canonical_graph["authority"] != AUTHORITY:
        raise ValueError("claim graph authority must be NONE")

    canonical_bytes = stable_json(canonical_graph).encode("utf-8")
    canonical_hash = sha256_hex(canonical_bytes)

    if output_path:
        Path(output_path).write_text(json.dumps(canonical_graph, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Canonical claim graph -> {output_path}")
        print(f"claim_graph_hash={canonical_hash}")
    else:
        print(json.dumps(canonical_graph, indent=2, sort_keys=True, ensure_ascii=False))
        print(f"claim_graph_hash={canonical_hash}", file=sys.stderr)

    return canonical_graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonicalize a Signal Core claim graph.")
    parser.add_argument("graph", help="Input raw claim graph JSON")
    parser.add_argument("output", nargs="?", help="Optional output path for canonical JSON")
    args = parser.parse_args()

    try:
        canonicalize_claim_graph(args.graph, args.output)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
