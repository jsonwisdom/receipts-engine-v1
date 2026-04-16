import json

rows = []
with open("court.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

rows.sort(key=lambda x: (x["blockNumber"], x["logIndex"]))

with open("COURT_LEDGER.md", "w") as out:
    out.write("# Computer Wisdom Court Ledger\n\n")
    out.write(f"**Emitter:** `{rows[0]['contract']}`\n\n" if rows else "")
    out.write(f"**Total Proofs:** {len(rows)}\n\n")

    for i, r in enumerate(rows, 1):
        out.write(f"## Entry {i}\n")
        out.write(f"- **agentId:** `{r['agentId']}`\n")
        out.write(f"- **tradeId:** `{r['tradeId']}`\n")
        out.write(f"- **commitmentHash:** `{r['commitmentHash']}`\n")
        out.write(f"- **tx:** `{r['transactionHash']}`\n")
        out.write(f"- **block:** `{r['blockNumber']}`\n")
        out.write(f"- **logIndex:** `{r['logIndex']}`\n")
        out.write(f"- **uri:** `{r['uri']}`\n\n")

print("wrote COURT_LEDGER.md")
