import base64
import hashlib
import json
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except Exception:  # pragma: no cover
    Ed25519PublicKey = None


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def parse_hash(value: str) -> bytes:
    if value.startswith("sha256:"):
        value = value.split(":", 1)[1]
    return bytes.fromhex(value)


def merkle_hash(leaves):
    if not leaves:
        return sha256(b"")
    nodes = [leaf if isinstance(leaf, bytes) else parse_hash(leaf) for leaf in leaves]
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])
        nodes = [sha256(nodes[i] + nodes[i + 1]) for i in range(0, len(nodes), 2)]
    return nodes[0]


def parse_ts(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def strip_sig_prefix(value: str) -> str:
    return value.split(":", 1)[1] if ":" in value else value


def verify_ed25519_signature(public_key_b64: str, message: bytes, signature_b64: str) -> bool:
    if Ed25519PublicKey is None:
        return False
    try:
        pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(strip_sig_prefix(public_key_b64)))
        pub.verify(base64.b64decode(strip_sig_prefix(signature_b64)), message)
        return True
    except Exception:
        return False


def decision_envelope(node):
    return {
        "node_id": node.get("node_id"),
        "node_root": node.get("node_root"),
        "communications_state": node.get("communications_state"),
        "policy_hash": node.get("policy_hash"),
        "local_counter": node.get("local_counter"),
        "local_ts": node.get("local_ts"),
    }


def clock_envelope(node):
    return {
        "node_id": node.get("node_id"),
        "local_counter": node.get("local_counter"),
        "local_ts": node.get("local_ts"),
        "last_sync_ref": node.get("last_sync_ref"),
    }


def verify_legality_basis(lb):
    return bool(lb) and bool(lb.get("rules_basis"))


def verify_node_hashes(node):
    try:
        parse_hash(node["node_root"])
        return True
    except Exception:
        return False


def verify_clock_proof(node):
    proof = node.get("clock_proof") or {}
    pub = proof.get("public_key")
    sig = node.get("clock_proof_sig")
    if not pub or not sig:
        return False
    return verify_ed25519_signature(pub, canonical_json(clock_envelope(node)), sig)


def calculate_clock_skew(node):
    return int(node.get("clock_skew_ms", 0))


def is_jammed_or_spoofed(node):
    comms = node.get("communications_state", {})
    return comms.get("link_quality") in ["degraded", "jammed"] or bool(comms.get("jam_spoof_flags"))


def policy_hash_matches(node, receipt):
    expected = receipt.get("legality_basis", {}).get("rules_basis", {}).get("target_classification_policy_hash")
    actual = node.get("policy_hash", expected)
    return bool(expected) and actual == expected


def time_sync_proof_valid(node, receipt):
    max_skew = receipt.get("swarm_context", {}).get("max_clock_skew_ms", 0)
    return calculate_clock_skew(node) <= max_skew


def has_valid_human_resignature(node):
    human = node.get("human_hook", {})
    sig = human.get("signature")
    pub = human.get("public_key")
    if not sig or not pub:
        return False
    return verify_ed25519_signature(pub, canonical_json(decision_envelope(node)), sig)


def fallback_token_within_window(node):
    token = node.get("fallback_authority_token") or {}
    issued_at = token.get("issued_at")
    max_duration = token.get("max_duration_seconds")
    local_ts = node.get("local_ts")
    if not issued_at or max_duration is None or not local_ts:
        return False
    delta = (parse_ts(local_ts) - parse_ts(issued_at)).total_seconds()
    return 0 <= delta <= int(max_duration)


def has_valid_fallback_token(node, receipt):
    token = node.get("fallback_authority_token") or {}
    pub = token.get("public_key")
    sig = token.get("signature")
    if not pub or not sig:
        return False
    if not fallback_token_within_window(node):
        return False
    allowed_modes = token.get("allowed_modes", [])
    mode = node.get("communications_state", {}).get("autonomy_fallback_mode")
    if mode not in allowed_modes:
        return False
    if not policy_hash_matches(node, receipt):
        return False
    if not time_sync_proof_valid(node, receipt):
        return False
    envelope = {
        "node_id": node.get("node_id"),
        "policy_hash": node.get("policy_hash"),
        "allowed_modes": allowed_modes,
        "max_duration_seconds": token.get("max_duration_seconds"),
        "allows_lethal": token.get("allows_lethal"),
        "issued_at": token.get("issued_at"),
    }
    return verify_ed25519_signature(pub, canonical_json(envelope), sig)


def has_lethal_authority(node):
    mode = node.get("communications_state", {}).get("autonomy_fallback_mode")
    if mode == "observe_only":
        return False
    token = node.get("fallback_authority_token") or {}
    if is_jammed_or_spoofed(node) and token:
        return bool(token.get("allows_lethal"))
    return True


def verify_quorum_attestations(receipt, valid_nodes):
    attestations = receipt.get("aggregated_epoch", {}).get("quorum_attestations", [])
    payload = canonical_json({
        "epoch_root": receipt.get("aggregated_epoch", {}).get("epoch_root"),
        "ordered_node_roots": sorted(n["node_root"] for n in valid_nodes),
    })
    valid = 0
    for att in attestations:
        pub = att.get("public_key") if isinstance(att, dict) else None
        sig = att.get("signature") if isinstance(att, dict) else None
        if pub and sig and verify_ed25519_signature(pub, payload, sig):
            valid += 1
    return valid >= receipt.get("swarm_context", {}).get("min_lethal_quorum", 1)


def verify_swarm(receipt):
    if not verify_legality_basis(receipt.get("legality_basis")):
        return "invalid: legality_basis_failed"

    max_skew = receipt["swarm_context"]["max_clock_skew_ms"]
    min_quorum = receipt["swarm_context"]["min_lethal_quorum"]
    valid_nodes = []

    for node in receipt.get("swarm_nodes", []):
        if not verify_node_hashes(node) or not verify_clock_proof(node):
            return "invalid: node_integrity_failed"

        skew = calculate_clock_skew(node)
        if skew > max_skew:
            node["communications_state"]["autonomy_fallback_mode"] = "observe_only"
            continue

        if not policy_hash_matches(node, receipt):
            return "invalid: policy_hash_mismatch"

        if not time_sync_proof_valid(node, receipt):
            return "invalid: time_sync_proof_failed"

        if is_jammed_or_spoofed(node):
            if not (has_valid_human_resignature(node) or has_valid_fallback_token(node, receipt)):
                return "invalid: authority_continuity_broken_on_node"

        valid_nodes.append(node)

    authorized = [n for n in valid_nodes if has_lethal_authority(n)]
    if len(authorized) < min_quorum:
        return f"invalid: quorum_failed ({len(authorized)} < {min_quorum})"

    node_roots = sorted(n["node_root"] for n in valid_nodes)
    computed_epoch = merkle_hash(node_roots)
    if computed_epoch.hex() != receipt["aggregated_epoch"]["epoch_root"]:
        return "invalid: epoch_root_mismatch"

    if not verify_quorum_attestations(receipt, valid_nodes):
        return "invalid: quorum_attestations_failed"

    return "valid: lawful_swarm_receipt_verified"
