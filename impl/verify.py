import json, hashlib, sys

def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))

def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def run(inputs: dict) -> dict:
    eligible = bool(inputs["eligibility_flags"]["eligible"])
    proofs = inputs["attendance_proof"]
    prior_state = inputs.get("prior_state")

    if not eligible:
        decision = "DENY"
    elif len(proofs) == 0:
        decision = "HOLD"
    else:
        decision = "APPROVE"

    receipt_payload = {
        "eligibility_flags": inputs["eligibility_flags"],
        "attendance_proof": proofs,
        "prior_state": prior_state,
        "decision": decision,
    }
    receipt_hash = sha256_str(canon(receipt_payload))
    new_state_hash = sha256_str(canon({"prior_state": prior_state, "receipt_hash": receipt_hash}))
    return {"decision": decision, "receipt_hash": receipt_hash, "new_state_hash": new_state_hash}

def run_tests(path: str):
    with open(path, "r") as f:
        vectors = json.load(f)
    passed = 0
    for i, case in enumerate(vectors, 1):
        out = run(case["input"])
        assert out["decision"] == case["expected"]["decision"], f"case {i} failed"
        passed += 1
    print(f"ALL PASS ({passed}/{len(vectors)})")

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--test":
        run_tests(sys.argv[2])
