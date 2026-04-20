import copy
import hashlib
from datetime import datetime, timedelta, timezone

from prototype.verify_swarm import verify_swarm, merkle_hash


def h(x):
    return hashlib.sha256(x.encode()).hexdigest()


def iso_z(dt):
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def node(node_id, sig='valid', token=None, skew=0, link='high', policy_hash='sha256:policy-ok'):
    return {
        'node_id': node_id,
        'local_counter': 1,
        'local_ts': '2026-04-20T08:15:42Z',
        'clock_skew_ms': skew,
        'last_sync_ref': 'sync-1',
        'clock_proof': {'public_key': 'ed25519:pub'},
        'clock_proof_sig': 'ed25519:clocksig' if sig == 'valid' else 'ed25519:bad',
        'node_root': h('node:' + node_id),
        'policy_hash': policy_hash,
        'communications_state': {
            'link_quality': link,
            'latency_ms': 100 if link == 'high' else 700,
            'jam_spoof_flags': [] if link == 'high' else ['spoof_detected'],
            'autonomy_fallback_mode': 'human_on_loop'
        },
        'human_hook': {
            'public_key': 'ed25519:pub',
            'signature': 'ed25519:humansig' if sig == 'valid' else 'ed25519:bad',
            'chain_of_command': {'mission_authorizer': 'a', 'operator': 'o', 'commander': 'c', 'reviewer': 'r'},
            'approval_type': 'on-loop'
        },
        'fallback_authority_token': token
    }


def receipt(nodes, quorum=2):
    roots = sorted(n['node_root'] for n in nodes if n['clock_skew_ms'] <= 250)
    return {
        'legality_basis': {'rules_basis': {'target_classification_policy_hash': 'sha256:policy-ok'}},
        'swarm_context': {'max_clock_skew_ms': 250, 'min_lethal_quorum': quorum},
        'swarm_nodes': copy.deepcopy(nodes),
        'aggregated_epoch': {
            'epoch_root': merkle_hash(roots).hex(),
            'quorum_attestations': [
                {'public_key': 'ed25519:pub', 'signature': 'ed25519:qsig'},
                {'public_key': 'ed25519:pub', 'signature': 'ed25519:qsig2'}
            ]
        }
    }


def test_fake_human_signature_fails_closed():
    r = receipt([node('A', sig='bad'), node('B')], quorum=2)
    assert verify_swarm(r).startswith('invalid:')


def test_replayed_expired_fallback_token_fails():
    now = datetime.now(timezone.utc)
    token = {
        'public_key': 'ed25519:pub',
        'signature': 'ed25519:toksig',
        'issued_at': iso_z(now - timedelta(hours=1)),
        'max_duration_seconds': 30,
        'allowed_modes': ['human_on_loop'],
        'allows_lethal': True
    }
    r = receipt([node('A', sig='bad', token=token, link='jammed'), node('B')], quorum=2)
    assert verify_swarm(r) == 'invalid: authority_continuity_broken_on_node'


def test_cross_swarm_policy_injection_fails():
    r = receipt([node('A', policy_hash='sha256:wrong'), node('B')], quorum=2)
    assert verify_swarm(r) == 'invalid: policy_hash_mismatch'


def test_desynced_node_plus_quorum_drop_fails_closed():
    r = receipt([
        node('A'),
        node('B'),
        node('C', skew=600),
    ], quorum=3)
    assert verify_swarm(r).startswith('invalid: quorum_failed')
