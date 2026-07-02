from pathlib import Path

from vsp001_replay_slice import compute_receipt, load_snapshot, run

SNAPSHOT = Path(__file__).parent / "data" / "vsp001_row16.json"


def test_vsp001_row16_replay_digest_matches():
    snapshot = load_snapshot(str(SNAPSHOT))
    output1, digest1 = compute_receipt(snapshot)
    output2, digest2 = compute_receipt(snapshot)

    assert output1 == output2
    assert digest1 == digest2
    assert len(digest1) == 64
    assert digest1 == digest1.lower()
    assert all(ch in "0123456789abcdef" for ch in digest1)


def test_vsp001_row16_cli_run_returns_digest():
    digest = run(str(SNAPSHOT))
    assert len(digest) == 64
    assert all(ch in "0123456789abcdef" for ch in digest)
