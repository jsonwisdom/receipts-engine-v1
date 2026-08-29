# VSP-001 replay slice

Invariant: same snapshot plus same rule plus same serializer produces the same SHA-256 hex digest.

Snapshot path: reference/replay_engine/data/vsp001_row16.json

Script path: reference/replay_engine/vsp001_replay_slice.py

Test path: reference/replay_engine/test_vsp001_replay_slice.py

Run the script with Python from the repository root. Run the test with pytest from reference/replay_engine.

Scope: this is a reference slice only. Production Genesis still requires real signatures, immutable storage, and CI logs.
