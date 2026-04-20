import copy
import hashlib
from prototype.verify_swarm import verify_swarm, merkle_hash


def _h(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def _node(node_id: str, skew: int, link_quality: str, has_sig: bool = True, has_token: bool = False, fallback_mode: str = "human_on_loop"):
    return {
        "node_id": node_id,
        "local_counter": 1,
        "local_ts": "2026-04-20T08:15:42Z",
        "clock_skew_ms": skew,
        "clock_proof_sig": "ed25519:clockproof",
        "node_root": _h(f"node:{node_id}"),
        "communications_state": {
            "link_quality": link_quality,
            "latency_ms": 100 if link_quality == "high" else 600,
            "jam_spoof_flags": [] if link_quality == "high" else ["jam_detected"],
            "autonomy_fallback_mode": fallback_mode,
        },
        "fallback_authority_token": {
            "token_id": f"sha256:{_h(f'token:{node_id}')}",
            "allowed_modes": ["supervised_autonomy", "human_on_loop"],
            "max_duration_seconds": 300,
            "allows_lethal": True,
            "signature": "ed25519:fallbacksig",
        } if has_token else None,
        "human_hook": {
            "chain_of_command": {
                "mission_authorizer": "pseudonym:a",
                "operator": "pseudonym:o",
                "commander": "pseudonym:c",
                "reviewer": "pseudonym:r",
            },
            "signature": "ed25519:humansig" if has_sig else "",
            "approval_type": "on-loop",
            "override_reason": None,
        },
    }


def _base_receipt(nodes, quorum=3):
    valid_nodes = []
    for n in nodes:
        if n["clock_skew_ms"] <= 250 and (n["communications_state"]["link_quality"] == "high" or n["human_hook"]["signature"] or n["fallback_authority_token"]):
            valid_nodes.append(n)
    epoch_root = merkle_hash(sorted(n["node_root"] for n in valid_nodes)).hex()
    return {
        "legality_basis": {"ok": True},
        "swarm_context": {
            "max_clock_skew_ms": 250,
            "min_lethal_quorum": quorum,
        },
        "swarm_nodes": copy.deepcopy(nodes),
        "aggregated_epoch": {
            "epoch_root": epoch_root,
            "quorum_attestations": ["ed25519:q1", "ed25519:q2"],
        },
    }


def test_jammed_and_desynced_cell_blocks_lethal_transition():
    nodes = [
        _node("A", 40, "high", has_sig=True),
        _node("B", 55, "high", has_sig=True),
        _node("C", 60, "jammed", has_sig=False, has_token=False, fallback_mode="supervised_autonomy"),
        _node("D", 410, "high", has_sig=True),
    ]
    receipt = _base_receipt(nodes, quorum=3)
    result = verify_swarm(receipt)
    assert result == "invalid: authority_continuity_broken_on_node"


def test_quorum_failure_when_jammed_node_has_no_lethal_authority_and_desynced_node_excluded():
    nodes = [
        _node("A", 40, "high", has_sig=True),
        _node("B", 55, "high", has_sig=True),
        _node("C", 60, "jammed", has_sig=False, has_token=True, fallback_mode="observe_only"),
        _node("D", 410, "high", has_sig=True),
    ]
    receipt = _base_receipt(nodes, quorum=3)
    result = verify_swarm(receipt)
    assert result == "invalid: quorum_failed (2 < 3)"


def test_epoch_root_mismatch_is_detected():
    nodes = [
        _node("A", 40, "high", has_sig=True),
        _node("B", 55, "high", has_sig=True),
        _node("C", 60, "jammed", has_sig=False, has_token=True, fallback_mode="human_on_loop"),
    ]
    receipt = _base_receipt(nodes, quorum=2)
    receipt["aggregated_epoch"]["epoch_root"] = _h("wrong-root")
    result = verify_swarm(receipt)
    assert result == "invalid: epoch_root_mismatch"


def test_policy_hash_mismatch_placeholder_receipt_shape():
    receipt = {
        "control_assertion": "policy_hash_mismatch_should_fail_when_policy_checks_are_implemented",
        "status": "placeholder"
    }
    assert receipt["status"] == "placeholder"


def test_time_sync_proof_placeholder_receipt_shape():
    receipt = {
        "control_assertion": "time_sync_proof_should_fail_when_clock_proof_validation_is_implemented",
        "status": "placeholder"
    }
    assert receipt["status"] == "placeholder"
