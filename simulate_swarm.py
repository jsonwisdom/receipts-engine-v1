#!/usr/bin/env python3
"""
simulate_swarm.py — Live demo of fail-closed behavior under jammed + desynced UWS swarm conditions.
"""

from prototype.verify_swarm import verify_swarm
from tests.adversarial_spoof_test import node, receipt


def simulate_jammed_desynced_swarm():
    print("=== UWS Swarm Fail-Closed Demo ===\n")

    clean = receipt([node('A'), node('B'), node('C')], quorum=2)
    print("Clean swarm:", verify_swarm(clean))

    jammed_token = {
        'public_key': 'ed25519:pub',
        'signature': 'ed25519:toksig',
        'issued_at': '2026-04-20T08:00:00Z',
        'max_duration_seconds': 10,
        'allowed_modes': ['human_on_loop'],
        'allows_lethal': False
    }

    jammed = receipt([
        node('A', sig='bad', link='jammed', token=jammed_token),
        node('B'),
        node('C', skew=400)
    ], quorum=2)
    print("Jammed + desynced swarm:", verify_swarm(jammed))


if __name__ == "__main__":
    simulate_jammed_desynced_swarm()
