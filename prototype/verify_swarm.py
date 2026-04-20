import hashlib
import json

def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def merkle_hash(leaves):
    if not leaves:
        return sha256(b"")
    nodes = [leaf if isinstance(leaf, bytes) else bytes.fromhex(leaf) for leaf in leaves]
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])
        nodes = [sha256(nodes[i] + nodes[i+1]) for i in range(0, len(nodes), 2)]
    return nodes[0]

# --- PLACEHOLDERS (to be replaced with real crypto/logic) ---
def verify_legality_basis(lb): return True
def verify_node_hashes(node): return True
def verify_clock_proof(node): return True
def calculate_clock_skew(node): return node.get("clock_skew_ms", 0)
def is_jammed_or_spoofed(node): return node.get("communications_state", {}).get("link_quality") in ["degraded", "jammed"]
def has_valid_human_resignature(node): return bool(node.get("human_hook", {}).get("signature"))
def has_valid_fallback_token(node, receipt): return bool(node.get("fallback_authority_token"))
def has_lethal_authority(node): return node.get("communications_state", {}).get("autonomy_fallback_mode") != "observe_only"
def verify_quorum_attestations(atts): return True

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

    if not verify_quorum_attestations(receipt["aggregated_epoch"]["quorum_attestations"]):
        return "invalid: quorum_attestations_failed"

    return "valid: lawful_swarm_receipt_verified"
