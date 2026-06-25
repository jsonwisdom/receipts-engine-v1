#!/usr/bin/env python3
"""
Signal Core Replay Gauntlet v0.1

Runs deterministic claim graph canonicalization tests before any sealer consumes
claim graph data.

Authority: NONE
No truth arbitration.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "canonicalizer"))

from canonicalize_claim_graph import canonicalize_claim_graph, sha256_hex, stable_json  # noqa: E402


BASE_HASH = "sha256:62c4bfbb991eb382629a62455c23d4dd71c58ebfd5d12797e39707606feb7e46"


def canonical_hash(graph_path: Path) -> str:
    canonical = canonicalize_claim_graph(str(graph_path), None)
    return sha256_hex(stable_json(canonical).encode("utf-8"))


def edge_pairs(graph: Dict[str, Any]) -> Iterable[tuple[str, str]]:
    for edge in graph.get("edges", []):
        if isinstance(edge, dict) and edge.get("type") == "depends_on":
            source = edge.get("from")
            target = edge.get("to")
            if source and target:
                yield str(source), str(target)

    for claim in graph.get("claims", []):
        claim_id = claim.get("claim_id") or claim.get("id")
        if not claim_id:
            continue
        for dep in claim.get("dependencies", []) or []:
            yield str(claim_id), str(dep)


def assert_acyclic(graph: Dict[str, Any]) -> None:
    adjacency: Dict[str, Set[str]] = {}
    for source, target in edge_pairs(graph):
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set())

    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError("cycle detected")
        if node in visited:
            return
        visiting.add(node)
        for nxt in adjacency.get(node, set()):
            visit(nxt)
        visiting.remove(node)
        visited.add(node)

    for node in list(adjacency):
        visit(node)


def run_case(test: Dict[str, Any], tests_dir: Path) -> bool:
    vector_path = tests_dir / test["vector"]
    expect = test["expect"]

    try:
        raw_graph = json.loads(vector_path.read_text(encoding="utf-8"))
        assert_acyclic(raw_graph)
        actual_hash = canonical_hash(vector_path)

        if expect == "MATCH_HASH":
            ok = actual_hash == test["expected_hash"]
        elif expect == "NEW_HASH":
            ok = actual_hash == test["expected_hash"] and actual_hash != test["must_not_match_hash"]
        else:
            ok = False

        print(f"{test['id']} {test['name']}: {'PASS' if ok else 'FAIL'} {actual_hash}")
        return ok

    except Exception as exc:  # noqa: BLE001 - CLI boundary
        message = str(exc)
        if expect in {"SECURITY_EXCEPTION", "INVALID_GRAPH_STRUCTURE"} and test.get("expected_error") in message:
            print(f"{test['id']} {test['name']}: PASS expected_error={message}")
            return True
        print(f"{test['id']} {test['name']}: FAIL unexpected_error={message}")
        return False


def main() -> int:
    tests_dir = Path(__file__).resolve().parent
    manifest = json.loads((tests_dir / "manifest.json").read_text(encoding="utf-8"))

    if manifest.get("authority") != "NONE":
        print("FAIL manifest authority must be NONE", file=sys.stderr)
        return 1

    results: List[bool] = []
    for test in manifest["tests"]:
        results.append(run_case(test, tests_dir))

    passed = sum(1 for result in results if result)
    total = len(results)
    print(f"Replay Gauntlet: {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
